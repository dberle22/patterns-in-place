# Phase 7 labor-fix rerun: control vs fixed comparison
#
# One-off review script for PHASE7_LABOR_FIX_RERUN_SPEC.md. It reads the two
# side-by-side reruns written with PHASE7_OUTPUT_DIR:
#   outputs_rerun_2026-10/control/  current code, pre-fix tract frame (July)
#   outputs_rerun_2026-10/fixed/    current code, fixed gold.intelligence_zone_inputs
# and writes every comparison table to outputs_rerun_2026-10/comparison/.
# The numbers in PHASE7_LABOR_FIX_RERUN_REVIEW.md come from these tables.
#
# Read-only against the warehouse: it reads the promoted marts (to check the
# control reproduces them) and the raw Gold inputs (for R32 raw profiles).
#
# Run from the repo root:
#   Rscript exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_labor_fix_rerun_compare.R

suppressPackageStartupMessages({
  library(here)
  library(DBI)
  library(duckdb)
  library(dplyr)
  library(tidyr)
  library(readr)
  library(arrow)
  library(purrr)
  library(cluster)
})

if (Sys.getenv("DB_PATH") == "" && file.exists(here(".Renviron"))) {
  readRenviron(here(".Renviron"))
}

source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_helpers.R"))

phase7_dir <- here("exploration/intelligence_framework/phase_7_zone_methodology")
rerun_dir <- file.path(phase7_dir, "outputs_rerun_2026-10")
comparison_dir <- file.path(rerun_dir, "comparison")
dir.create(comparison_dir, recursive = TRUE, showWarnings = FALSE)

albany_cbsa <- "10580"
large_cbsa_min_tracts <- 100L

write_table <- function(df, name) {
  readr::write_csv(df, file.path(comparison_dir, paste0(name, ".csv")))
  df
}

show <- function(df, title) {
  cat("\n==== ", title, " ====\n", sep = "")
  print(as.data.frame(df), row.names = FALSE, digits = 4)
  invisible(df)
}

# ---------------------------------------------------------------------------
# Load both runs
# ---------------------------------------------------------------------------
# zone_scores.parquet is the tract-grain output the mart loader promotes; the
# centroid CSV carries the polarity-flipped standardized centroid per cluster
# with its automatic draft label.

read_run <- function(run) {
  run_dir <- file.path(rerun_dir, run)
  list(
    scores = arrow::read_parquet(file.path(run_dir, "zone_scores.parquet")) |>
      as.data.frame() |>
      mutate(tract_geoid = as.character(tract_geoid), cbsa_code = as.character(cbsa_code)),
    centroids = readr::read_csv(file.path(run_dir, "phase7_cluster_centroids.csv"), show_col_types = FALSE),
    calibration = readr::read_csv(file.path(run_dir, "phase7_cluster_calibration.csv"), show_col_types = FALSE),
    imputation_log = readr::read_csv(file.path(run_dir, "phase7_imputation_log.csv"), show_col_types = FALSE),
    imputed = arrow::read_parquet(file.path(run_dir, "phase7_tract_frame_imputed.parquet")) |> as.data.frame(),
    zcta = arrow::read_parquet(file.path(run_dir, "zone_scores_zcta.parquet")) |> as.data.frame()
  )
}

control <- read_run("control")
fixed <- read_run("fixed")
expected_kpis <- readr::read_csv(file.path(rerun_dir, "fixed", "phase7_expected_kpis.csv"), show_col_types = FALSE)
metric_ids <- expected_kpis$metric_id

con <- DBI::dbConnect(duckdb::duckdb(), Sys.getenv("DB_PATH"), read_only = TRUE)
on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

published <- DBI::dbGetQuery(con, "
  select tract_geoid, zone_type, zone_kmeans_cluster, character_score,
         livability_score, opportunity_score, composite_score,
         national_composite_percentile
  from mart_intelligence.intelligence_zones
")
published_zcta <- DBI::dbGetQuery(con, "
  select zip_geoid, primary_zone_type, dominant_zone_type, is_mixed_zone
  from mart_intelligence.intelligence_zones_zcta
")

# Raw (un-imputed, un-flipped) inputs for the R32 profiles. The live Gold table
# now carries the fixed unemployment rate, so "before" and "after" profiles both
# use the fixed rate, as the spec asks; only the cluster membership differs.
raw_inputs <- DBI::dbGetQuery(con, "
  select tract_geoid, pov_rate, pct_ba_plus, median_hh_income, owner_occ_rate,
         pop_weighted_density_sqmi, pct_age_over_64, pct_unemployment_rate
  from gold.intelligence_zone_inputs
")

# ---------------------------------------------------------------------------
# 1. Control reproduction
# ---------------------------------------------------------------------------
# Seeds are fixed, so the control (same code, July frame) should reproduce the
# promoted mart exactly. Anything else is run-to-run noise we must separate
# from the effect of the fix.

reproduction <- control$scores |>
  select(tract_geoid, zone_type, zone_kmeans_cluster, composite_score, national_composite_percentile) |>
  inner_join(published, by = "tract_geoid", suffix = c("_control", "_published")) |>
  summarise(
    tracts_control = nrow(control$scores),
    tracts_published = nrow(published),
    tracts_joined = n(),
    cluster_id_agreement = mean(zone_kmeans_cluster_control == zone_kmeans_cluster_published),
    zone_type_agreement = mean(zone_type_control == zone_type_published),
    max_abs_composite_diff = max(abs(composite_score_control - composite_score_published)),
    max_abs_national_pctl_diff = max(abs(national_composite_percentile_control - national_composite_percentile_published))
  ) |>
  write_table("control_reproduction") |>
  show("Control reproduction vs mart_intelligence.intelligence_zones")

# ---------------------------------------------------------------------------
# 2. Inputs: how the unemployment KPI itself changed
# ---------------------------------------------------------------------------

unemployment_input <- bind_rows(
  control$imputation_log |> mutate(run = "control"),
  fixed$imputation_log |> mutate(run = "fixed")
) |>
  filter(metric_id == "pct_unemployment_rate") |>
  select(run, missing_tracts_before, completeness_pct, fill_value) |>
  write_table("unemployment_input_summary") |>
  show("Unemployment KPI: imputation before vs after")

# ---------------------------------------------------------------------------
# 3. Calibration: is k = 7 still the best k-means silhouette?
# ---------------------------------------------------------------------------
# The model picks k from config$candidate_k (7:10) by k-means silhouette on a
# 5,000-tract sample. The K6/K7 review also looked at k = 5 and 6, so we
# recompute those here with the same sampling and seeding scheme.

calibration_compare <- bind_rows(
  control$calibration |> mutate(run = "control"),
  fixed$calibration |> mutate(run = "fixed")
) |>
  select(run, k, kmeans_avg_silhouette, hierarchical_avg_silhouette, kmeans_betweenss_ratio, kmeans_min_cluster, kmeans_clusters_under_100) |>
  arrange(k, run) |>
  write_table("calibration_compare") |>
  show("Calibration (config candidate_k 7:10)")

# Rebuild the exact clustering matrix the model used: unflipped z-scores of the
# imputed values, rows sorted by tract_geoid, 22 KPIs.
cluster_matrix <- function(imputed_df) {
  wide <- imputed_df |>
    select(tract_geoid, all_of(paste0("imputed_", metric_ids))) |>
    arrange(tract_geoid)
  m <- wide |>
    select(-tract_geoid) |>
    mutate(across(everything(), safe_zscore)) |>
    as.matrix()
  colnames(m) <- metric_ids
  m
}

extended_calibration <- function(m, run) {
  set.seed(20270701 + 5000L)
  idx <- sort(sample.int(nrow(m), 5000L))
  cm <- m[idx, , drop = FALSE]
  d <- stats::dist(cm)
  hc <- stats::hclust(d, method = "ward.D2")
  purrr::map_dfr(5:7, \(k) {
    set.seed(20270701 + k + ncol(cm))
    km <- stats::kmeans(cm, centers = k, nstart = 25, iter.max = 50)
    tibble(
      run = run,
      k = k,
      kmeans_avg_silhouette = mean(cluster::silhouette(km$cluster, d)[, 3]),
      hierarchical_avg_silhouette = mean(cluster::silhouette(flatten_cutree(hc, k), d)[, 3]),
      kmeans_betweenss_ratio = km$betweenss / km$totss
    )
  })
}

control_matrix <- cluster_matrix(control$imputed)
fixed_matrix <- cluster_matrix(fixed$imputed)

calibration_k5_7 <- bind_rows(
  extended_calibration(control_matrix, "control"),
  extended_calibration(fixed_matrix, "fixed")
) |>
  arrange(k, run) |>
  write_table("calibration_k5_to_7_side_check") |>
  show("Side check: k = 5 to 7 (k = 7 row should match the model's own calibration)")

# Full-matrix fit at the chosen k, from the model's own assignments.
full_fit <- function(m, assignments, run) {
  centers <- apply(m, 2, \(col) tapply(col, assignments, mean))
  within <- sum((m - centers[assignments, ])^2)
  total <- sum(scale(m, scale = FALSE)^2)
  tibble(run = run, total_within_ss = within, betweenss_ratio = 1 - within / total)
}

full_fit_compare <- bind_rows(
  full_fit(control_matrix, control$scores |> arrange(tract_geoid) |> pull(zone_kmeans_cluster), "control"),
  full_fit(fixed_matrix, fixed$scores |> arrange(tract_geoid) |> pull(zone_kmeans_cluster), "fixed")
) |>
  write_table("full_fit_compare") |>
  show("Full 78k-tract fit at the chosen k")

# ---------------------------------------------------------------------------
# 4. Match clusters by centroid similarity
# ---------------------------------------------------------------------------
# Cluster IDs and automatic labels can swap between runs, so pair each control
# cluster with a fixed cluster by minimising total Euclidean distance between
# centroids (flipped standardized scale). The unemployment KPI is left out of
# the distance because its meaning changed between runs; the other 21 KPIs are
# identical inputs. With k = 7 there are only 5,040 permutations, so brute force.

all_permutations <- function(v) {
  if (length(v) <= 1) return(list(v))
  out <- list()
  for (i in seq_along(v)) {
    for (p in all_permutations(v[-i])) out[[length(out) + 1]] <- c(v[i], p)
  }
  out
}

match_metrics <- setdiff(metric_ids, "pct_unemployment_rate")
control_centers <- control$centroids |> arrange(zone_kmeans_cluster)
fixed_centers <- fixed$centroids |> arrange(zone_kmeans_cluster)
stopifnot(nrow(control_centers) == nrow(fixed_centers))

control_center_matrix <- as.matrix(control_centers[, match_metrics])
fixed_center_matrix <- as.matrix(fixed_centers[, match_metrics])
k_run <- nrow(control_center_matrix)
# Rows = control clusters, columns = fixed clusters.
distance_matrix <- as.matrix(stats::dist(rbind(control_center_matrix, fixed_center_matrix)))[
  seq_len(k_run), k_run + seq_len(k_run)
]

perms <- all_permutations(seq_len(nrow(fixed_centers)))
perm_cost <- vapply(perms, \(p) sum(distance_matrix[cbind(seq_along(p), p)]), numeric(1))
best_perm <- perms[[which.min(perm_cost)]]

cluster_match <- tibble(
  control_cluster = control_centers$zone_kmeans_cluster,
  control_label = control_centers$provisional_zone_type,
  control_tracts = control_centers$tracts_in_cluster,
  fixed_cluster = fixed_centers$zone_kmeans_cluster[best_perm],
  fixed_label = fixed_centers$provisional_zone_type[best_perm],
  fixed_tracts = fixed_centers$tracts_in_cluster[best_perm],
  centroid_distance_21kpi = distance_matrix[cbind(seq_along(best_perm), best_perm)],
  next_nearest_distance = map_dbl(seq_along(best_perm), \(i) sort(distance_matrix[i, ])[2])
) |>
  mutate(
    label_same = control_label == fixed_label,
    size_change = fixed_tracts - control_tracts,
    size_change_pct = size_change / control_tracts
  ) |>
  write_table("cluster_match") |>
  show("Cluster matching (centroid similarity) and sizes")

as_tibble(round(distance_matrix, 3), .name_repair = \(x) paste0("fixed_", fixed_centers$zone_kmeans_cluster)) |>
  mutate(control_cluster = control_centers$zone_kmeans_cluster, control_label = control_centers$provisional_zone_type, .before = 1) |>
  write_table("cluster_match_distance_matrix") |>
  show("Centroid distance matrix (21 KPIs; rows control, cols fixed)")

# Cross-check: the one-to-one matching that maximises tracts kept together.
# If it agrees with the centroid matching, the pairing is not a judgment call.
overlap <- table(
  factor(control$scores |> arrange(tract_geoid) |> pull(zone_kmeans_cluster), levels = control_centers$zone_kmeans_cluster),
  factor(fixed$scores |> arrange(tract_geoid) |> pull(zone_kmeans_cluster), levels = fixed_centers$zone_kmeans_cluster)
)
perm_overlap <- vapply(perms, \(p) sum(overlap[cbind(seq_along(p), p)]), numeric(1))
best_overlap_perm <- perms[[which.max(perm_overlap)]]
show(
  tibble(
    centroid_matching_equals_overlap_matching = identical(best_perm, best_overlap_perm),
    tracts_kept_together_centroid_match = sum(overlap[cbind(seq_along(best_perm), best_perm)]),
    tracts_kept_together_overlap_match = max(perm_overlap)
  ),
  "Matching cross-check"
)

# Automatic label check: what the labeler gave each matched fixed cluster, and
# the top-scoring draft label family behind it (the labeler scores 8 families
# but only 7 map to a name; `distressed` has no name, which yields NA).
fixed_label_scores <- build_phase7_draft_label_scores(fixed$centroids) |>
  select(zone_kmeans_cluster, starts_with("label_score_")) |>
  pivot_longer(starts_with("label_score_"), names_to = "family", values_to = "score") |>
  mutate(family = sub("label_score_", "", family)) |>
  group_by(zone_kmeans_cluster) |>
  arrange(desc(score), .by_group = TRUE) |>
  summarise(top_family = first(family), top_score = first(score), second_family = nth(family, 2), .groups = "drop")

cluster_match |>
  select(control_cluster, control_label, fixed_cluster, fixed_label, label_same) |>
  left_join(fixed_label_scores, by = c("fixed_cluster" = "zone_kmeans_cluster")) |>
  write_table("label_check") |>
  show("Automatic label check on matched clusters")

# ---------------------------------------------------------------------------
# 5. Assignment stability
# ---------------------------------------------------------------------------

assign <- control$scores |>
  select(tract_geoid, cbsa_code, cbsa_name, control_cluster = zone_kmeans_cluster, control_label = zone_type) |>
  inner_join(
    fixed$scores |> select(tract_geoid, fixed_cluster = zone_kmeans_cluster, fixed_label = zone_type),
    by = "tract_geoid"
  ) |>
  left_join(cluster_match |> select(control_cluster, matched_fixed_cluster = fixed_cluster), by = "control_cluster") |>
  # Carry the published (control) name forward to its matched fixed cluster,
  # so crosstabs compare like with like despite the automatic-label swap.
  left_join(
    cluster_match |> select(fixed_cluster, fixed_matched_label = control_label),
    by = "fixed_cluster"
  ) |>
  mutate(unchanged = fixed_cluster == matched_fixed_cluster)

adjusted_rand_index <- function(a, b) {
  tab <- table(a, b)
  comb2 <- function(x) sum(x * (x - 1) / 2)
  index <- comb2(tab)
  rows <- comb2(rowSums(tab))
  cols <- comb2(colSums(tab))
  expected <- rows * cols / comb2(sum(tab))
  (index - expected) / ((rows + cols) / 2 - expected)
}

stability_national <- tibble(
  tracts = nrow(assign),
  share_unchanged = mean(assign$unchanged),
  tracts_changed = sum(!assign$unchanged),
  adjusted_rand_index = adjusted_rand_index(assign$control_cluster, assign$fixed_cluster),
  label_agreement_raw = mean(assign$control_label == assign$fixed_label)
) |>
  write_table("stability_national") |>
  show("National stability")

crosstab <- assign |>
  count(control_label, fixed_label) |>
  pivot_wider(names_from = fixed_label, values_from = n, values_fill = 0) |>
  write_table("crosstab_national_auto_labels")

crosstab_matched <- assign |>
  count(control_label, fixed_matched_label) |>
  pivot_wider(names_from = fixed_matched_label, values_from = n, values_fill = 0) |>
  write_table("crosstab_national_matched") |>
  show("Crosstab: control (rows) x fixed cluster under its matched control name (cols)")

stability_by_cluster <- assign |>
  group_by(control_cluster, control_label) |>
  summarise(
    tracts = n(),
    share_unchanged = mean(unchanged),
    top_destination_if_moved = {
      moved <- fixed_matched_label[!unchanged]
      if (length(moved) == 0) NA_character_ else names(sort(table(moved), decreasing = TRUE))[1]
    },
    .groups = "drop"
  ) |>
  write_table("stability_by_cluster") |>
  show("Stability by control cluster")

stability_by_cbsa <- assign |>
  filter(!is.na(cbsa_code)) |>
  group_by(cbsa_code, cbsa_name) |>
  summarise(tracts = n(), share_unchanged = mean(unchanged), .groups = "drop") |>
  filter(tracts >= large_cbsa_min_tracts) |>
  arrange(share_unchanged) |>
  write_table("stability_large_cbsas")

show(
  stability_by_cbsa |>
    summarise(
      large_cbsas = n(),
      min_share = min(share_unchanged),
      p10_share = quantile(share_unchanged, 0.10),
      median_share = median(share_unchanged),
      max_share = max(share_unchanged),
      cbsas_under_90pct = sum(share_unchanged < 0.90)
    ),
  "Large CBSAs (>= 100 tracts): share unchanged"
)
show(head(stability_by_cbsa, 10), "Least stable large CBSAs")
show(stability_by_cbsa |> arrange(desc(tracts)) |> head(12), "Largest CBSAs")

# ---------------------------------------------------------------------------
# 6. Centroid shifts (flipped standardized scale)
# ---------------------------------------------------------------------------

centroid_long <- function(centers, run) {
  centers |>
    select(zone_kmeans_cluster, provisional_zone_type, all_of(metric_ids)) |>
    pivot_longer(all_of(metric_ids), names_to = "metric_id", values_to = paste0("centroid_", run))
}

centroid_shift <- centroid_long(control$centroids, "control") |>
  rename(control_cluster = zone_kmeans_cluster, control_label = provisional_zone_type) |>
  left_join(cluster_match |> select(control_cluster, fixed_cluster), by = "control_cluster") |>
  left_join(
    centroid_long(fixed$centroids, "fixed") |>
      rename(fixed_cluster = zone_kmeans_cluster, fixed_label = provisional_zone_type),
    by = c("fixed_cluster", "metric_id")
  ) |>
  mutate(shift = centroid_fixed - centroid_control, abs_shift = abs(shift)) |>
  arrange(desc(abs_shift)) |>
  write_table("centroid_shift_long")

show(head(centroid_shift, 15), "Largest centroid shifts (all KPIs)")
show(
  centroid_shift |> filter(metric_id != "pct_unemployment_rate") |> head(10),
  "Largest centroid shifts excluding unemployment"
)

centroid_wide <- centroid_shift |>
  select(control_label, metric_id, centroid_control, centroid_fixed) |>
  pivot_longer(c(centroid_control, centroid_fixed), names_to = "run", values_to = "value") |>
  mutate(run = sub("centroid_", "", run)) |>
  pivot_wider(names_from = metric_id, values_from = value) |>
  arrange(control_label, run) |>
  write_table("centroids_before_after")

# ---------------------------------------------------------------------------
# 7. Raw profiles (R32)
# ---------------------------------------------------------------------------
# Medians of the actual, un-imputed rates per cluster. Both runs use the fixed
# unemployment rate, so the before/after difference is membership only.

raw_profile <- function(labels, run) {
  labels |>
    inner_join(raw_inputs, by = "tract_geoid") |>
    group_by(zone_type) |>
    summarise(
      run = run,
      tracts = n(),
      pov_rate = median(pov_rate, na.rm = TRUE),
      pct_ba_plus = median(pct_ba_plus, na.rm = TRUE),
      median_hh_income = median(median_hh_income, na.rm = TRUE),
      owner_occ_rate = median(owner_occ_rate, na.rm = TRUE),
      density_sqmi = median(pop_weighted_density_sqmi, na.rm = TRUE),
      pct_age_over_64 = median(pct_age_over_64, na.rm = TRUE),
      unemployment_rate_fixed = median(pct_unemployment_rate, na.rm = TRUE),
      .groups = "drop"
    )
}

# Keyed by matched pair: `zone_type` is the control name, and the fixed row
# profiles the fixed cluster matched to it (not the fixed automatic label).
raw_profiles <- bind_rows(
  raw_profile(assign |> select(tract_geoid, zone_type = control_label), "control"),
  raw_profile(assign |> select(tract_geoid, zone_type = fixed_matched_label), "fixed")
) |>
  arrange(zone_type, run) |>
  write_table("raw_profiles_before_after") |>
  show("Raw median profiles per matched zone type (R32)")

# ---------------------------------------------------------------------------
# 8. Scores and percentiles
# ---------------------------------------------------------------------------

score_cols <- c("character_score", "livability_score", "opportunity_score", "composite_score")
pctl_cols <- c(
  paste0("national_", c("character", "livability", "opportunity", "composite"), "_percentile"),
  paste0("cbsa_", c("character", "livability", "opportunity", "composite"), "_percentile"),
  paste0("zone_peer_", c("character", "livability", "opportunity", "composite"), "_percentile")
)

score_join <- control$scores |>
  select(tract_geoid, all_of(c(score_cols, pctl_cols))) |>
  inner_join(fixed$scores |> select(tract_geoid, all_of(c(score_cols, pctl_cols))), by = "tract_geoid", suffix = c("_c", "_f"))

score_movement <- map_dfr(c(score_cols, pctl_cols), \(col) {
  delta <- score_join[[paste0(col, "_f")]] - score_join[[paste0(col, "_c")]]
  tibble(
    measure = col,
    median_abs_change = median(abs(delta)),
    p90_abs_change = quantile(abs(delta), 0.9),
    max_abs_change = max(abs(delta)),
    share_moving_gt_10 = if (grepl("percentile", col)) mean(abs(delta) > 10) else NA_real_,
    tracts_changed = sum(abs(delta) > 1e-9)
  )
}) |>
  write_table("score_movement") |>
  show("Score and percentile movement (fixed - control)")

# ---------------------------------------------------------------------------
# 9. Albany (CBSA 10580)
# ---------------------------------------------------------------------------

albany <- assign |> filter(cbsa_code == albany_cbsa)

albany_crosstab <- albany |>
  count(control_label, fixed_matched_label) |>
  pivot_wider(names_from = fixed_matched_label, values_from = n, values_fill = 0) |>
  write_table("albany_crosstab") |>
  show("Albany (10580): control (rows) x fixed under matched name (cols)")

albany |>
  count(control_label, fixed_label) |>
  pivot_wider(names_from = fixed_label, values_from = n, values_fill = 0) |>
  write_table("albany_crosstab_auto_labels")

show(
  tibble(albany_tracts = nrow(albany), share_unchanged = mean(albany$unchanged)),
  "Albany stability"
)

albany_movers <- albany |>
  filter(!unchanged) |>
  left_join(raw_inputs, by = "tract_geoid") |>
  left_join(
    control$imputed |> select(tract_geoid, geo_name, unemp_control_imputed = imputed_pct_unemployment_rate),
    by = "tract_geoid"
  ) |>
  select(tract_geoid, geo_name, control_label, fixed_matched_label, fixed_label, unemp_control_imputed,
         unemp_fixed = pct_unemployment_rate, pov_rate, median_hh_income, pct_ba_plus, owner_occ_rate) |>
  write_table("albany_movers")
show(albany_movers, "Albany tracts that changed type")

albany_profiles <- bind_rows(
  raw_profile(albany |> select(tract_geoid, zone_type = control_label), "control"),
  raw_profile(albany |> select(tract_geoid, zone_type = fixed_matched_label), "fixed")
) |>
  arrange(zone_type, run) |>
  write_table("albany_raw_profiles") |>
  show("Albany raw profiles per zone type")

# ---------------------------------------------------------------------------
# 10. ZCTA rollup
# ---------------------------------------------------------------------------
# Two comparisons: fixed vs control (both on today's crosswalk, so the fix is
# the only difference) and fixed vs the promoted ZCTA mart (what promotion
# would actually change).

zcta_compare <- function(before, after, label) {
  before |>
    select(zip_geoid, primary_before = primary_zone_type, dominant_before = dominant_zone_type, mixed_before = is_mixed_zone) |>
    full_join(
      after |> select(zip_geoid, primary_after = primary_zone_type, dominant_after = dominant_zone_type, mixed_after = is_mixed_zone),
      by = "zip_geoid"
    ) |>
    summarise(
      comparison = label,
      zctas_before = sum(!is.na(primary_before)),
      zctas_after = sum(!is.na(primary_after)),
      zctas_in_both = sum(!is.na(primary_before) & !is.na(primary_after)),
      dominant_zone_changed = sum(dominant_before != dominant_after, na.rm = TRUE),
      primary_label_changed = sum(primary_before != primary_after, na.rm = TRUE),
      flipped_to_mixed = sum(!mixed_before & mixed_after, na.rm = TRUE),
      flipped_from_mixed = sum(mixed_before & !mixed_after, na.rm = TRUE)
    )
}

# The fixed run's automatic labels include an NA type, which the rollup cannot
# place. To measure the structural change, also roll up the fixed clusters
# under their matched control names (the same rollup code, a relabeled input).
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_zcta_rollup.R"))
matched_dir <- file.path(rerun_dir, "fixed_matched_labels")
dir.create(matched_dir, recursive = TRUE, showWarnings = FALSE)
fixed$scores |>
  select(tract_geoid, zone_kmeans_cluster) |>
  left_join(cluster_match |> select(zone_kmeans_cluster = fixed_cluster, zone_type = control_label), by = "zone_kmeans_cluster") |>
  arrow::write_parquet(file.path(matched_dir, "zone_scores.parquet"))
matched_config <- phase7_zone_config(output_dir = matched_dir)
fixed_matched_zcta <- build_phase7_zcta_rollup(con = con, config = matched_config)$zcta_rollup
arrow::write_parquet(fixed_matched_zcta, file.path(matched_dir, "zone_scores_zcta.parquet"))

zcta_changes <- bind_rows(
  zcta_compare(control$zcta, fixed$zcta, "control_vs_fixed_auto_labels"),
  zcta_compare(control$zcta, fixed_matched_zcta, "control_vs_fixed_matched_labels"),
  zcta_compare(published_zcta, control$zcta, "published_mart_vs_control")
) |>
  write_table("zcta_changes") |>
  show("ZCTA rollup changes")

zcta_mix <- bind_rows(
  control$zcta |> count(primary_zone_type) |> mutate(run = "control"),
  fixed$zcta |> count(primary_zone_type) |> mutate(run = "fixed_auto_labels"),
  fixed_matched_zcta |> count(primary_zone_type) |> mutate(run = "fixed_matched_labels")
) |>
  pivot_wider(names_from = run, values_from = n, values_fill = 0) |>
  mutate(change_matched = fixed_matched_labels - control) |>
  write_table("zcta_primary_mix") |>
  show("ZCTA primary zone mix")

cat("\nComparison tables written to", comparison_dir, "\n")
