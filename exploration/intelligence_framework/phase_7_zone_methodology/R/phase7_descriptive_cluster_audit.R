library(here)
library(DBI)
library(dplyr)
library(readr)
library(arrow)

if (Sys.getenv("DB_PATH") == "" && file.exists(here(".Renviron"))) {
  readRenviron(here(".Renviron"))
}

source(here("exploration/intelligence_framework/R/utils.R"))

build_phase7_descriptive_cluster_audit <- function(
  con,
  zone_scores_path = here("exploration/intelligence_framework/phase_7_zone_methodology/outputs/zone_scores.parquet"),
  descriptive_sql_path = here("exploration/intelligence_framework/phase_7_zone_methodology/sql/phase7_descriptive_cluster_audit.sql")
) {
  output_dir <- here("exploration/intelligence_framework/phase_7_zone_methodology/outputs")
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  # The descriptive tract frame is a held-out interpretive overlay. It should
  # be safe to recompute independently because it does not feed the cluster fit.
  descriptive_sql <- readr::read_file(descriptive_sql_path)
  descriptive_tract_frame <- DBI::dbGetQuery(con, descriptive_sql)

  zone_scores <- arrow::read_parquet(zone_scores_path)

  descriptive_joined <- zone_scores |>
    dplyr::select(
      tract_geoid,
      cbsa_code,
      county_geoid,
      geo_name,
      cbsa_name,
      county_name,
      zone_type,
      zone_kmeans_cluster
    ) |>
    dplyr::left_join(
      descriptive_tract_frame,
      by = c("tract_geoid", "cbsa_code", "county_geoid", "geo_name", "cbsa_name", "county_name")
    )

  descriptive_kpis <- c(
    "median_age",
    "diversity_index",
    "pct_white_nh",
    "pct_black_nh",
    "pct_asian_nh",
    "pct_hispanic",
    "median_home_value",
    "median_hh_income"
  )

  # These summaries are meant to help naming review answer "what is this tract
  # type like?" without making the output look more precise than it is.
  national_cluster_summary <- descriptive_joined |>
    dplyr::group_by(zone_kmeans_cluster, zone_type) |>
    dplyr::summarise(
      tracts_in_cluster = dplyr::n(),
      dplyr::across(
        dplyr::all_of(descriptive_kpis),
        list(
          mean = \(x) mean(x, na.rm = TRUE),
          median = \(x) stats::median(x, na.rm = TRUE),
          missing = \(x) sum(is.na(x))
        ),
        .names = "{.col}_{.fn}"
      ),
      .groups = "drop"
    ) |>
    dplyr::arrange(zone_kmeans_cluster)

  # This view keeps the cluster-by-CBSA spread visible for descriptive fields
  # so we can tell whether a label depends on just a few metros.
  cbsa_cluster_summary <- descriptive_joined |>
    dplyr::group_by(cbsa_code, cbsa_name, zone_kmeans_cluster, zone_type) |>
    dplyr::summarise(
      tracts_in_cluster = dplyr::n(),
      dplyr::across(
        dplyr::all_of(descriptive_kpis),
        \(x) stats::median(x, na.rm = TRUE),
        .names = "{.col}_median"
      ),
      .groups = "drop"
    ) |>
    dplyr::group_by(cbsa_code, cbsa_name) |>
    dplyr::mutate(
      cbsa_total_tracts = sum(tracts_in_cluster),
      cbsa_cluster_share = tracts_in_cluster / cbsa_total_tracts
    ) |>
    dplyr::ungroup() |>
    dplyr::arrange(cbsa_name, dplyr::desc(tracts_in_cluster))

  readr::write_csv(
    descriptive_tract_frame,
    file.path(output_dir, "phase7_descriptive_kpis_tract.csv")
  )
  readr::write_csv(
    national_cluster_summary,
    file.path(output_dir, "phase7_descriptive_cluster_summary.csv")
  )
  readr::write_csv(
    cbsa_cluster_summary,
    file.path(output_dir, "phase7_descriptive_cbsa_cluster_summary.csv")
  )

  list(
    descriptive_tract_frame = descriptive_tract_frame,
    descriptive_joined = descriptive_joined,
    national_cluster_summary = national_cluster_summary,
    cbsa_cluster_summary = cbsa_cluster_summary
  )
}

run_phase7_descriptive_cluster_audit <- function() {
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  build_phase7_descriptive_cluster_audit(con = con)
}

if (sys.nframe() == 0) {
  invisible(run_phase7_descriptive_cluster_audit())
}
