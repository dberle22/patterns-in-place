# IRS direction fix rerun (2026-10): run one Intelligence Framework phase into
# a side-by-side output folder, without touching the canonical outputs/.
#
# Usage, from the repo root (one phase per R process, because the phases define
# helper functions with the same names):
#   Rscript exploration/intelligence_framework/irs_fix_rerun_2026-10/irs_fix_rerun_phase.R <phase> <mode> [gdp_frozen]
#     phase: 2 | 4 | 5
#     mode:  control | fixed
#     gdp_frozen (optional, phases 4 and 5): the promotion run. See below.
#
# - control: current code, with the IRS columns read from the before snapshot
#   of gold.migration_wide (the reversed values the current marts were built
#   from). Every other input still comes from gold. This should reproduce the
#   current marts, which separates the effect of the fix from other drift.
# - fixed: current code and current (fixed) gold.
#
# Outputs land in <phase folder>/outputs_irs_fix_2026-10/<mode>/. Phase 5 reads
# the Phase 2 and Phase 4 outputs from the same mode folder, and the canonical
# Phase 3 Livability outputs (Livability has no IRS input).
#
# gdp_frozen (Dan, 2026-10-26: ship the IRS fix alone; the BEA GDP refresh waits
# for a broader GDP and clustering refresh):
# - The three Opportunity inputs that moved with the BEA county GDP refresh are
#   read from the current mart (the before snapshot of intelligence_opportunity)
#   instead of gold, so the only input change is IRS.
# - Published cluster names are carried forward by cluster ID. With GDP frozen,
#   control reproduces the current marts and the fix leaves every membership
#   unchanged, so each k-means cluster is the same set of metros as today. The
#   rule-based namers would otherwise move names between unchanged clusters
#   (see IRS_FIX_RERUN_REVIEW.md). The run stops if any membership differs.
# - Outputs go to <mode>_gdp_frozen/. Phase 2 has no GDP input, so Phase 5 reads
#   Phase 2 from the plain <mode>/ folder.
#
# Spec: foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md, Parts B and C.

args <- commandArgs(trailingOnly = TRUE)
stopifnot(
  length(args) %in% c(2, 3),
  args[[1]] %in% c("2", "4", "5"),
  args[[2]] %in% c("control", "fixed"),
  length(args) == 2 || (args[[3]] == "gdp_frozen" && args[[1]] %in% c("4", "5"))
)
phase <- args[[1]]
mode <- args[[2]]
gdp_frozen <- length(args) == 3

rerun_dir_name <- file.path("outputs_irs_fix_2026-10", if (gdp_frozen) paste0(mode, "_gdp_frozen") else mode)
snapshot_dir <- here::here("foundations", "etl", "data", "snapshots", "irs_direction_fix_2026-10", "before")
snapshot_path <- file.path(snapshot_dir, "gold__migration_wide_irs.parquet")
opportunity_mart_snapshot <- file.path(snapshot_dir, "mart_intelligence__intelligence_opportunity.parquet")
if (mode == "control") stopifnot(file.exists(snapshot_path))
if (gdp_frozen) stopifnot(file.exists(opportunity_mart_snapshot))

# The Opportunity KPIs sourced from BEA county GDP (gold.economics_industry_wide).
gdp_metric_ids <- c("productivity_growth_5yr", "industry_concentration_hhi", "pct_real_gdp_information")

framework_dir <- here::here("exploration", "intelligence_framework")
phase_dirs <- c(
  "2" = file.path(framework_dir, "phase_2_character_calibration"),
  "4" = file.path(framework_dir, "phase_4_opportunity_calibration"),
  "5" = file.path(framework_dir, "phase_5_cross_frame_integration")
)
rerun_output_dir <- function(phase_id) {
  if (phase_id == "2") return(file.path(phase_dirs[[phase_id]], "outputs_irs_fix_2026-10", mode))
  file.path(phase_dirs[[phase_id]], rerun_dir_name)
}

# Control input override ----
# Phases 2 and 4 pull each KPI with the same "latest non-null year per CBSA"
# query. For IRS columns in control mode, run that query against the snapshot
# parquet instead of gold.migration_wide. The snapshot keeps geo_level, geo_id
# and year, so the year selection is identical.
pull_irs_from_snapshot <- function(con, metric_id, source_column) {
  sql <- sprintf(
    "with ranked as (
       select
         geo_id,
         cast(%s as double) as metric_value,
         year as source_year,
         row_number() over (
           partition by geo_id
           order by case when %s is not null then 0 else 1 end, year desc
         ) as rn
       from read_parquet('%s')
       where geo_level = 'cbsa'
     )
     select geo_id, metric_value, source_year
     from ranked
     where rn = 1",
    source_column, source_column, snapshot_path
  )

  DBI::dbGetQuery(con, sql) |>
    dplyr::rename(
      cbsa_code = geo_id,
      !!metric_id := metric_value,
      !!paste0(metric_id, "_source_year") := source_year
    )
}

wrap_pull <- function(original_pull) {
  # force() captures the original now; R's lazy arguments would otherwise
  # resolve to the wrapper after it replaces the global name.
  force(original_pull)
  function(con, metric_id, source_table, source_column) {
    if (mode == "control" && source_table == "migration_wide" && startsWith(source_column, "irs_")) {
      message(sprintf("  [control] %s read from the before snapshot", source_column))
      return(pull_irs_from_snapshot(con, metric_id, source_column))
    }
    if (gdp_frozen && metric_id %in% gdp_metric_ids) {
      message(sprintf("  [gdp_frozen] %s read from the current mart", metric_id))
      return(pull_from_opportunity_mart(metric_id))
    }
    original_pull(con, metric_id, source_table, source_column)
  }
}

# GDP freeze ----
# The mart row carries the value and source year each metro used in the June
# build, in the same columns the pull returns.
pull_from_opportunity_mart <- function(metric_id) {
  arrow::read_parquet(opportunity_mart_snapshot) |>
    dplyr::select(cbsa_code, dplyr::all_of(c(metric_id, paste0(metric_id, "_source_year")))) |>
    dplyr::mutate(
      cbsa_code = as.character(cbsa_code),
      !!metric_id := as.double(.data[[metric_id]]),
      !!paste0(metric_id, "_source_year") := as.integer(.data[[paste0(metric_id, "_source_year")]])
    )
}

# Name pinning ----
# Replace the rule-based names in a phase's model bundle with the published
# names for the same cluster ID. Applied by value lookup to every table in the
# bundle, so downstream tables (hypotheses, overlap, Phase 5 inputs) inherit
# the pinned names. Interpretation text moves with the name only where it is
# hand-written per name (Opportunity); cross-frame interpretations are
# generated from the cluster's own averages and are left as computed.
pin_cluster_names <- function(bundle, scores_name, kmeans_col, name_col, canonical_scores, canonical_name_map,
                              pin_interpretation) {
  current <- bundle[[scores_name]] |> dplyr::select(cbsa_code, kmeans = dplyr::all_of(kmeans_col))
  published <- arrow::read_parquet(canonical_scores) |>
    dplyr::transmute(cbsa_code = as.character(cbsa_code), kmeans_published = .data[[kmeans_col]])
  membership <- dplyr::inner_join(current, published, by = "cbsa_code")
  stopifnot(nrow(membership) == nrow(current))
  if (any(membership$kmeans != membership$kmeans_published)) {
    stop("Name pinning: k-means membership differs from the published run; pinning by ID is not valid.")
  }

  rule_map <- bundle$cluster_name_map |>
    dplyr::select(kmeans = dplyr::all_of(kmeans_col), rule_name = dplyr::all_of(name_col), rule_interp = cluster_interpretation)
  pinned_map <- readr::read_csv(canonical_name_map, show_col_types = FALSE) |>
    dplyr::select(kmeans = dplyr::all_of(kmeans_col), pinned_name = dplyr::all_of(name_col), pinned_interp = cluster_interpretation)
  map <- dplyr::inner_join(rule_map, pinned_map, by = "kmeans")
  stopifnot(nrow(map) == nrow(rule_map), !anyDuplicated(map$pinned_name))
  name_lookup <- stats::setNames(map$pinned_name, map$rule_name)
  interp_lookup <- stats::setNames(map$pinned_interp, map$rule_interp)

  changed <- map |> dplyr::filter(rule_name != pinned_name)
  if (nrow(changed) > 0) {
    message("  [names] pinned to the published names:")
    message(paste(sprintf("    cluster %s: %s -> %s", changed$kmeans, changed$rule_name, changed$pinned_name), collapse = "\n"))
  } else {
    message("  [names] rule-based names already match the published names")
  }

  relabel <- function(x) {
    if (is.data.frame(x)) {
      if (name_col %in% names(x)) x[[name_col]] <- unname(name_lookup[x[[name_col]]])
      if (pin_interpretation && "cluster_interpretation" %in% names(x)) {
        x$cluster_interpretation <- unname(interp_lookup[x$cluster_interpretation])
      }
      return(x)
    }
    if (is.list(x)) return(lapply(x, relabel))
    x
  }
  relabel(bundle)
}

# Output redirect ----
# Each config function builds output_dir from a fixed path; wrap it so the run
# writes to the rerun folder instead. The canonical folder is left as it is.
wrap_config <- function(original_config, out_dir) {
  force(original_config)
  force(out_dir)
  function(...) {
    config <- original_config(...)
    config$output_dir <- out_dir
    dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
    config
  }
}

if (phase == "2") {
  source(here::here("exploration/intelligence_framework/phase_2_character_calibration/R/run_phase2_character.R"))
  phase2_pull_metric <- wrap_pull(phase2_pull_metric)
  phase2_character_config <- wrap_config(phase2_character_config, rerun_output_dir("2"))
  invisible(run_phase2_character_checkpoint5())
}

if (phase == "4") {
  source(here::here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/run_phase4_opportunity.R"))
  phase4_pull_metric <- wrap_pull(phase4_pull_metric)
  phase4_opportunity_config <- wrap_config(phase4_opportunity_config, rerun_output_dir("4"))
  if (gdp_frozen) {
    original_phase4_model <- build_phase4_model_bundle
    build_phase4_model_bundle <- function(...) {
      pin_cluster_names(
        original_phase4_model(...),
        scores_name = "opportunity_scores",
        kmeans_col = "opportunity_kmeans_cluster",
        name_col = "opportunity_cluster_name",
        canonical_scores = file.path(phase_dirs[["4"]], "outputs", "opportunity_scores.parquet"),
        canonical_name_map = file.path(phase_dirs[["4"]], "outputs", "opportunity_phase4_cluster_name_map.csv"),
        pin_interpretation = TRUE
      )
    }
  }
  invisible(run_phase4_opportunity_checkpoint2())
}

if (phase == "5") {
  source(here::here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/run_phase5_cross_frame.R"))
  # Phase 5 already takes output_dir_name; point its Character and Opportunity
  # inputs at the same mode's rerun outputs. Livability stays canonical.
  config <- phase5_cross_frame_config(output_dir_name = rerun_dir_name)
  config$frames <- config$frames |>
    dplyr::mutate(
      score_path = dplyr::case_when(
        frame_id == "character" ~ file.path(rerun_output_dir("2"), "character_scores.parquet"),
        frame_id == "opportunity" ~ file.path(rerun_output_dir("4"), "opportunity_scores.parquet"),
        TRUE ~ score_path
      ),
      decision_path = dplyr::case_when(
        frame_id == "character" ~ file.path(rerun_output_dir("2"), "character_phase2_clustering_metric_decisions.csv"),
        frame_id == "opportunity" ~ file.path(rerun_output_dir("4"), "opportunity_phase4_clustering_metric_decisions.csv"),
        TRUE ~ decision_path
      )
    )
  stopifnot(all(file.exists(config$frames$score_path)))
  if (gdp_frozen) {
    original_phase5_model <- build_phase5_final_model_bundle
    build_phase5_final_model_bundle <- function(...) {
      pin_cluster_names(
        original_phase5_model(...),
        scores_name = "cross_frame_scores",
        kmeans_col = "cross_frame_kmeans_cluster",
        name_col = "cross_frame_cluster_name",
        canonical_scores = file.path(phase_dirs[["5"]], "outputs", "cross_frame_scores.parquet"),
        canonical_name_map = file.path(phase_dirs[["5"]], "outputs", "cross_frame_phase5_cluster_name_map.csv"),
        pin_interpretation = FALSE
      )
    }
  }
  invisible(run_phase5_cross_frame(config))
}

message(sprintf("IRS fix rerun: phase %s, %s%s, written to %s", phase, mode, if (gdp_frozen) " (GDP frozen)" else "", rerun_output_dir(phase)))
