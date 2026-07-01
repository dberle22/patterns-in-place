library(here)
library(DBI)
library(duckdb)
library(dplyr)
library(tidyr)
library(purrr)
library(stringr)
library(readr)
library(arrow)
library(tibble)
library(cluster)

if (Sys.getenv("DB_PATH") == "" && file.exists(here(".Renviron"))) {
  readRenviron(here(".Renviron"))
}

source(here("exploration/intelligence_framework/R/utils.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_helpers.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_config.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_tract_frame_build.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_imputation.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_national_cluster.R"))
source(here("exploration/intelligence_framework/phase_7_zone_methodology/R/phase7_scoring.R"))

write_phase7_outputs <- function(bundle, config) {
  readr::write_csv(
    config$expected_kpis,
    file.path(config$output_dir, "phase7_expected_kpis.csv")
  )
  readr::write_csv(
    config$clustering_metric_decisions,
    file.path(config$output_dir, "phase7_clustering_metric_decisions.csv")
  )
  arrow::write_parquet(
    bundle$frame$tract_frame,
    file.path(config$output_dir, "phase7_tract_frame.parquet")
  )
  readr::write_csv(
    bundle$frame$coverage_audit,
    file.path(config$output_dir, "phase7_coverage_audit.csv")
  )
  readr::write_csv(
    bundle$imputation$metric_completeness,
    file.path(config$output_dir, "phase7_metric_completeness.csv")
  )
  readr::write_csv(
    bundle$imputation$missing_tracts_long,
    file.path(config$output_dir, "phase7_missing_tracts_long.csv")
  )
  readr::write_csv(
    bundle$imputation$imputation_log,
    file.path(config$output_dir, "phase7_imputation_log.csv")
  )
  readr::write_csv(
    bundle$imputation$imputed_cells,
    file.path(config$output_dir, "phase7_imputed_cells.csv")
  )
  arrow::write_parquet(
    bundle$imputation$phase7_model_df,
    file.path(config$output_dir, "phase7_tract_frame_imputed.parquet")
  )
  readr::write_csv(
    bundle$model$standardization_audit,
    file.path(config$output_dir, "phase7_standardization_audit.csv")
  )
  readr::write_csv(
    bundle$model$cluster_count_calibration,
    file.path(config$output_dir, "phase7_cluster_calibration.csv")
  )
  readr::write_csv(
    bundle$model$cluster_count_sizes,
    file.path(config$output_dir, "phase7_cluster_count_sizes.csv")
  )
  readr::write_csv(
    bundle$model$provisional_label_map,
    file.path(config$output_dir, "phase7_provisional_zone_type_map.csv")
  )
  readr::write_csv(
    bundle$model$cluster_centroids,
    file.path(config$output_dir, "phase7_cluster_centroids.csv")
  )
  readr::write_csv(
    bundle$model$representative_tracts,
    file.path(config$output_dir, "phase7_representative_tracts.csv")
  )
  readr::write_csv(
    bundle$model$gmm_cluster_summary,
    file.path(config$output_dir, "phase7_gmm_summary.csv")
  )
  readr::write_csv(
    bundle$model$light_validation,
    file.path(config$output_dir, "phase7_light_validation_spot_checks.csv")
  )
  arrow::write_parquet(
    bundle$scores$zone_scores,
    file.path(config$output_dir, "zone_scores.parquet")
  )
}

run_phase7_zone_model <- function() {
  config <- phase7_zone_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  frame <- build_phase7_tract_frame(con = con, config = config)
  imputation <- build_phase7_imputation_bundle(
    tract_frame = frame$tract_frame,
    coverage_audit = frame$coverage_audit,
    config = config
  )
  model <- build_phase7_national_cluster_bundle(
    phase7_model_df = imputation$phase7_model_df,
    config = config
  )
  scores <- build_phase7_scoring_bundle(
    phase7_model_df = imputation$phase7_model_df,
    cluster_bundle = model,
    config = config
  )

  bundle <- list(
    config = config,
    frame = frame,
    imputation = imputation,
    model = model,
    scores = scores
  )

  write_phase7_outputs(bundle, config)
  bundle
}

if (sys.nframe() == 0) {
  invisible(run_phase7_zone_model())
}
