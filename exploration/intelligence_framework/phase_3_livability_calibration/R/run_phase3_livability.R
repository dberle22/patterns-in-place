library(here)
library(DBI)
library(duckdb)
library(dplyr)
library(tidyr)
library(purrr)
library(stringr)
library(readr)
library(arrow)
library(yaml)
library(cluster)
library(tibble)

if (Sys.getenv("DB_PATH") == "" && file.exists(here(".Renviron"))) {
  readRenviron(here(".Renviron"))
}

source(here("exploration/intelligence_framework/R/utils.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_helpers.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_config.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_catalog_audit.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_frame_build.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_imputation.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_redundancy.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_modeling.R"))
source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/phase3_hypotheses.R"))

write_phase3_outputs <- function(bundle, config) {
  readr::write_csv(bundle$catalog$polarity_audit, file.path(config$output_dir, "livability_phase3_polarity_flags.csv"))
  arrow::write_parquet(bundle$frame, file.path(config$output_dir, "livability_phase3_kpi_frame.parquet"))
  readr::write_csv(bundle$imputation$metric_completeness, file.path(config$output_dir, "livability_phase3_metric_completeness.csv"))
  arrow::write_parquet(bundle$imputation$metric_completeness, file.path(config$output_dir, "livability_phase3_metric_completeness.parquet"))
  readr::write_csv(bundle$imputation$imputation_audit, file.path(config$output_dir, "livability_phase3_imputation_audit.csv"))
  readr::write_csv(bundle$imputation$imputed_cells, file.path(config$output_dir, "livability_phase3_imputed_cells.csv"))
  arrow::write_parquet(bundle$imputation$livability_model_df, file.path(config$output_dir, "livability_phase3_kpi_frame_imputed.parquet"))
  readr::write_csv(bundle$redundancy$redundant_pairs, file.path(config$output_dir, "livability_phase3_redundant_pairs.csv"))
  readr::write_csv(bundle$redundancy$pca_variance, file.path(config$output_dir, "livability_phase3_pca_variance.csv"))
  readr::write_csv(bundle$redundancy$pca_loadings, file.path(config$output_dir, "livability_phase3_pca_loadings.csv"))
  readr::write_csv(config$clustering_metric_decisions, file.path(config$output_dir, "livability_phase3_clustering_metric_decisions.csv"))
  readr::write_csv(bundle$model$standardization_audit, file.path(config$output_dir, "livability_phase3_standardization_audit.csv"))
  readr::write_csv(bundle$model$cluster_diagnostics, file.path(config$output_dir, "livability_phase3_cluster_diagnostics.csv"))
  readr::write_csv(bundle$model$cluster_count_calibration, file.path(config$output_dir, "livability_phase3_cluster_count_calibration.csv"))
  readr::write_csv(bundle$model$cluster_count_sizes, file.path(config$output_dir, "livability_phase3_cluster_count_sizes.csv"))
  readr::write_csv(bundle$model$k5_to_k6_changed_metros, file.path(config$output_dir, "livability_phase3_k5_to_k6_changed_metros.csv"))
  readr::write_csv(bundle$model$k5_to_k6_split_summary, file.path(config$output_dir, "livability_phase3_k5_to_k6_split_summary.csv"))
  readr::write_csv(bundle$model$gmm_cluster_summary, file.path(config$output_dir, "livability_phase3_gmm_summary.csv"))
  arrow::write_parquet(bundle$model$livability_scores, file.path(config$output_dir, "livability_scores.parquet"))
  readr::write_csv(bundle$model$cluster_centroids_output, file.path(config$output_dir, "livability_phase3_cluster_centroids.csv"))
  readr::write_csv(bundle$model$cluster_representatives, file.path(config$output_dir, "livability_phase3_cluster_representatives.csv"))
  readr::write_csv(bundle$model$gmm_hybrids, file.path(config$output_dir, "livability_phase3_gmm_hybrids.csv"))
  readr::write_csv(bundle$model$similarity_top10, file.path(config$output_dir, "livability_phase3_similarity_top10.csv"))
  readr::write_csv(bundle$hypotheses$health_affordability_test, file.path(config$output_dir, "livability_phase3_health_affordability_scatter.csv"))
  readr::write_csv(bundle$hypotheses$health_affordability_outliers, file.path(config$output_dir, "livability_phase3_health_affordability_outliers.csv"))
  readr::write_csv(bundle$hypotheses$environment_axis_test, file.path(config$output_dir, "livability_phase3_environment_axis_scatter.csv"))
  readr::write_csv(bundle$hypotheses$environment_axis_outliers, file.path(config$output_dir, "livability_phase3_environment_axis_outliers.csv"))
}

run_phase3_livability <- function() {
  config <- phase3_livability_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  catalog <- build_phase3_catalog_bundle(config)
  livability_frame <- build_phase3_livability_frame(con)
  imputation <- build_phase3_imputation_bundle(livability_frame, catalog$catalog_check, config)
  redundancy <- build_phase3_redundancy_bundle(imputation$livability_model_df, config)
  model <- build_phase3_model_bundle(
    livability_model_df = imputation$livability_model_df,
    livability_frame = catalog$livability_frame,
    catalog_check = catalog$catalog_check,
    config = config
  )
  hypotheses <- build_phase3_hypothesis_bundle(model$livability_scores)

  bundle <- list(
    config = config,
    catalog = catalog,
    frame = livability_frame,
    imputation = imputation,
    redundancy = redundancy,
    model = model,
    hypotheses = hypotheses
  )

  write_phase3_outputs(bundle, config)
  bundle
}

if (sys.nframe() == 0) {
  invisible(run_phase3_livability())
}
