library(here)
library(DBI)
library(duckdb)
library(dplyr)
library(tidyr)
library(readr)
library(arrow)
library(stringr)
library(tibble)

if (Sys.getenv("DB_PATH") == "" && file.exists(here(".Renviron"))) {
  readRenviron(here(".Renviron"))
}

source(here("exploration/intelligence_framework/R/utils.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_helpers.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_config.R"))

build_phase7_zcta_rollup <- function(con, config) {
  zone_scores_path <- file.path(config$output_dir, "zone_scores.parquet")

  if (!file.exists(zone_scores_path)) {
    stop(
      sprintf("Run the tract model first; missing %s", zone_scores_path),
      call. = FALSE
    )
  }

  # The ZCTA rollup is intentionally downstream of the tract model. We preserve
  # the tract labels exactly as produced in Sprint 2 and only summarize them
  # through the HUD tract-to-ZCTA population weights.
  tract_zones <- arrow::read_parquet(zone_scores_path) |>
    as.data.frame() |>
    dplyr::select(tract_geoid, zone_type) |>
    dplyr::mutate(tract_geoid = as.character(tract_geoid))

  zcta_crosswalk <- DBI::dbGetQuery(
    con,
    "
    SELECT
      zip_geoid,
      tract_geoid,
      zip_pref_city,
      zip_pref_state,
      rel_weight_pop,
      vintage,
      source
    FROM silver.xwalk_zcta_tract
    "
  ) |>
    dplyr::mutate(
      zip_geoid = as.character(zip_geoid),
      tract_geoid = as.character(tract_geoid)
    ) |>
    dplyr::filter(rel_weight_pop > 0)

  zcta_tract_assignments <- zcta_crosswalk |>
    dplyr::inner_join(tract_zones, by = "tract_geoid")

  zcta_zone_weights <- zcta_tract_assignments |>
    dplyr::group_by(zip_geoid, zone_type) |>
    dplyr::summarise(
      zone_weight = sum(rel_weight_pop, na.rm = TRUE),
      contributing_tract_count = dplyr::n_distinct(tract_geoid),
      .groups = "drop"
    )

  zcta_metadata <- zcta_tract_assignments |>
    dplyr::group_by(zip_geoid) |>
    dplyr::summarise(
      zcta_city = dplyr::first(zip_pref_city),
      zcta_state = dplyr::first(zip_pref_state),
      source_vintage = max(vintage, na.rm = TRUE),
      source = dplyr::first(source),
      tract_count = dplyr::n_distinct(tract_geoid),
      total_weighted_population = sum(rel_weight_pop, na.rm = TRUE),
      .groups = "drop"
    )

  ranked_zone_weights <- zcta_zone_weights |>
    dplyr::group_by(zip_geoid) |>
    dplyr::mutate(
      zone_share = zone_weight / sum(zone_weight, na.rm = TRUE)
    ) |>
    dplyr::arrange(zip_geoid, dplyr::desc(zone_share), zone_type, .by_group = TRUE) |>
    dplyr::mutate(zone_rank = dplyr::row_number()) |>
    dplyr::ungroup()

  lead_zone_summary <- ranked_zone_weights |>
    dplyr::filter(zone_rank <= 2L) |>
    dplyr::select(zip_geoid, zone_rank, zone_type, zone_share) |>
    tidyr::pivot_wider(
      names_from = zone_rank,
      values_from = c(zone_type, zone_share),
      names_glue = "{.value}_{zone_rank}"
    ) |>
    dplyr::rename(
      dominant_zone_type = zone_type_1,
      dominant_zone_share = zone_share_1,
      secondary_zone_type = zone_type_2,
      secondary_zone_share = zone_share_2
    )

  share_column_lookup <- tibble::tibble(
    zone_type = config$draft_zone_labels,
    share_column = paste0(
      "share_",
      vapply(config$draft_zone_labels, phase7_slugify_zone_type, character(1))
    )
  )

  share_wide <- ranked_zone_weights |>
    dplyr::select(zip_geoid, zone_type, zone_share) |>
    dplyr::right_join(
      tidyr::expand_grid(
        zip_geoid = unique(zcta_metadata$zip_geoid),
        zone_type = config$draft_zone_labels
      ),
      by = c("zip_geoid", "zone_type")
    ) |>
    dplyr::mutate(zone_share = tidyr::replace_na(zone_share, 0)) |>
    dplyr::left_join(share_column_lookup, by = "zone_type") |>
    dplyr::select(zip_geoid, share_column, zone_share) |>
    tidyr::pivot_wider(
      names_from = share_column,
      values_from = zone_share
    )

  zcta_rollup <- zcta_metadata |>
    dplyr::left_join(lead_zone_summary, by = "zip_geoid") |>
    dplyr::left_join(share_wide, by = "zip_geoid") |>
    dplyr::mutate(
      is_mixed_zone = dominant_zone_share <= 0.5,
      primary_zone_type = dplyr::if_else(
        is_mixed_zone,
        "Mixed Zone",
        dominant_zone_type
      )
    ) |>
    dplyr::relocate(
      zip_geoid,
      zcta_city,
      zcta_state,
      primary_zone_type,
      is_mixed_zone,
      dominant_zone_type,
      dominant_zone_share,
      secondary_zone_type,
      secondary_zone_share
    ) |>
    dplyr::arrange(zip_geoid)

  rollup_audit <- zcta_rollup |>
    dplyr::summarise(
      zcta_count = dplyr::n(),
      mixed_zone_count = sum(is_mixed_zone, na.rm = TRUE),
      dominant_zone_count = sum(!is_mixed_zone, na.rm = TRUE),
      mixed_zone_share = mean(is_mixed_zone, na.rm = TRUE),
      min_dominant_share = min(dominant_zone_share, na.rm = TRUE),
      median_dominant_share = stats::median(dominant_zone_share, na.rm = TRUE),
      max_dominant_share = max(dominant_zone_share, na.rm = TRUE)
    )

  zone_mix_distribution <- zcta_rollup |>
    dplyr::count(primary_zone_type, name = "zcta_count") |>
    dplyr::mutate(zcta_share = zcta_count / sum(zcta_count))

  list(
    zcta_rollup = zcta_rollup,
    rollup_audit = rollup_audit,
    zone_mix_distribution = zone_mix_distribution
  )
}

write_phase7_zcta_outputs <- function(bundle, config) {
  arrow::write_parquet(
    bundle$zcta_rollup,
    file.path(config$output_dir, "zone_scores_zcta.parquet")
  )
  readr::write_csv(
    bundle$rollup_audit,
    file.path(config$output_dir, "phase7_zcta_rollup_audit.csv")
  )
  readr::write_csv(
    bundle$zone_mix_distribution,
    file.path(config$output_dir, "phase7_zcta_zone_mix_distribution.csv")
  )
}

run_phase7_zcta_rollup <- function() {
  config <- phase7_zone_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  bundle <- build_phase7_zcta_rollup(con = con, config = config)
  write_phase7_zcta_outputs(bundle, config)
  bundle
}

if (sys.nframe() == 0) {
  invisible(run_phase7_zcta_rollup())
}
