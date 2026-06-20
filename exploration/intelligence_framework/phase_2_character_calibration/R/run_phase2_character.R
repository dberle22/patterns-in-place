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
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_helpers.R"))
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_config.R"))
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_catalog_audit.R"))
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_frame_build.R"))
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_imputation.R"))
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_redundancy.R"))
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_modeling.R"))
source(here("exploration/intelligence_framework/phase_2_character_calibration/R/phase2_hypotheses.R"))

write_phase2_checkpoint1_outputs <- function(bundle, config) {
  readr::write_csv(
    bundle$catalog$catalog_check,
    file.path(config$output_dir, "character_phase2_catalog_check.csv")
  )
  readr::write_csv(
    bundle$catalog$polarity_audit,
    file.path(config$output_dir, "character_phase2_polarity_flags.csv")
  )
  readr::write_csv(
    config$clustering_metric_decisions,
    file.path(config$output_dir, "character_phase2_clustering_metric_decisions.csv")
  )
}

run_phase2_character_checkpoint1 <- function() {
  config <- phase2_character_config()
  catalog <- build_phase2_catalog_bundle(config)

  bundle <- list(
    config = config,
    catalog = catalog
  )

  write_phase2_checkpoint1_outputs(bundle, config)
  bundle
}

write_phase2_checkpoint2_outputs <- function(bundle, config) {
  write_phase2_checkpoint1_outputs(bundle, config)
  arrow::write_parquet(
    bundle$frame,
    file.path(config$output_dir, "character_phase2_kpi_frame.parquet")
  )
  readr::write_csv(
    bundle$imputation$metric_completeness,
    file.path(config$output_dir, "character_phase2_metric_completeness.csv")
  )
  arrow::write_parquet(
    bundle$imputation$metric_completeness,
    file.path(config$output_dir, "character_phase2_metric_completeness.parquet")
  )
  readr::write_csv(
    bundle$imputation$imputation_audit,
    file.path(config$output_dir, "character_phase2_imputation_audit.csv")
  )
  readr::write_csv(
    bundle$imputation$missing_cbsas_long,
    file.path(config$output_dir, "character_phase2_missing_cbsas_long.csv")
  )
  readr::write_csv(
    bundle$imputation$imputation_sensitive_metros,
    file.path(config$output_dir, "character_phase2_imputation_sensitive_metros.csv")
  )
  readr::write_csv(
    bundle$imputation$imputed_cells,
    file.path(config$output_dir, "character_phase2_imputed_cells.csv")
  )
  arrow::write_parquet(
    bundle$imputation$character_model_df,
    file.path(config$output_dir, "character_phase2_kpi_frame_imputed.parquet")
  )
}

run_phase2_character_checkpoint2 <- function() {
  config <- phase2_character_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  catalog <- build_phase2_catalog_bundle(config)
  frame <- build_phase2_character_frame(
    con = con,
    catalog_check = catalog$catalog_check
  )
  imputation <- build_phase2_imputation_bundle(
    character_frame = frame,
    catalog_check = catalog$catalog_check,
    config = config
  )

  bundle <- list(
    config = config,
    catalog = catalog,
    frame = frame,
    imputation = imputation
  )

  write_phase2_checkpoint2_outputs(bundle, config)
  bundle
}

write_phase2_checkpoint3_outputs <- function(bundle, config) {
  write_phase2_checkpoint2_outputs(bundle, config)
  readr::write_csv(
    bundle$redundancy$full_metric_set,
    file.path(config$output_dir, "character_phase2_full_metric_set.csv")
  )
  readr::write_csv(
    bundle$redundancy$pca_recommended_metric_set,
    file.path(config$output_dir, "character_phase2_pca_recommended_metric_set.csv")
  )
  readr::write_csv(
    bundle$redundancy$redundant_pairs,
    file.path(config$output_dir, "character_phase2_redundant_pairs.csv")
  )
  readr::write_csv(
    bundle$redundancy$pca_variance,
    file.path(config$output_dir, "character_phase2_pca_variance.csv")
  )
  readr::write_csv(
    bundle$redundancy$pca_loadings,
    file.path(config$output_dir, "character_phase2_pca_loadings.csv")
  )
}

run_phase2_character_checkpoint3 <- function() {
  config <- phase2_character_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  catalog <- build_phase2_catalog_bundle(config)
  frame <- build_phase2_character_frame(
    con = con,
    catalog_check = catalog$catalog_check
  )
  imputation <- build_phase2_imputation_bundle(
    character_frame = frame,
    catalog_check = catalog$catalog_check,
    config = config
  )
  redundancy <- build_phase2_redundancy_bundle(
    character_model_df = imputation$character_model_df,
    catalog_check = catalog$catalog_check,
    config = config
  )

  bundle <- list(
    config = config,
    catalog = catalog,
    frame = frame,
    imputation = imputation,
    redundancy = redundancy
  )

  write_phase2_checkpoint3_outputs(bundle, config)
  bundle
}

write_phase2_checkpoint4_outputs <- function(bundle, config) {
  write_phase2_checkpoint3_outputs(bundle, config)
  readr::write_csv(
    bundle$model$standardization_audit,
    file.path(config$output_dir, "character_phase2_standardization_audit.csv")
  )
  readr::write_csv(
    bundle$model$cluster_count_calibration,
    file.path(config$output_dir, "character_phase2_cluster_count_calibration.csv")
  )
  readr::write_csv(
    bundle$model$cluster_count_sizes,
    file.path(config$output_dir, "character_phase2_cluster_count_sizes.csv")
  )
  readr::write_csv(
    bundle$model$cluster_assignments,
    file.path(config$output_dir, "character_phase2_k_comparison_cluster_assignments.csv")
  )
  readr::write_csv(
    bundle$model$representative_metros,
    file.path(config$output_dir, "character_phase2_k_comparison_representative_metros.csv")
  )
}

run_phase2_character_checkpoint4 <- function() {
  config <- phase2_character_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  catalog <- build_phase2_catalog_bundle(config)
  frame <- build_phase2_character_frame(
    con = con,
    catalog_check = catalog$catalog_check
  )
  imputation <- build_phase2_imputation_bundle(
    character_frame = frame,
    catalog_check = catalog$catalog_check,
    config = config
  )
  redundancy <- build_phase2_redundancy_bundle(
    character_model_df = imputation$character_model_df,
    catalog_check = catalog$catalog_check,
    config = config
  )
  model <- build_phase2_model_bundle(
    character_model_df = imputation$character_model_df,
    character_frame = catalog$character_frame,
    catalog_check = catalog$catalog_check,
    config = config
  )

  bundle <- list(
    config = config,
    catalog = catalog,
    frame = frame,
    imputation = imputation,
    redundancy = redundancy,
    model = model
  )

  write_phase2_checkpoint4_outputs(bundle, config)
  bundle
}

write_phase2_checkpoint5_outputs <- function(bundle, config) {
  write_phase2_checkpoint4_outputs(bundle, config)
  readr::write_csv(
    bundle$model$cluster_name_map,
    file.path(config$output_dir, "character_phase2_cluster_name_map.csv")
  )
  readr::write_csv(
    bundle$model$cluster_metric_extremes,
    file.path(config$output_dir, "character_phase2_cluster_metric_extremes.csv")
  )
  readr::write_csv(
    bundle$model$gmm_cluster_summary,
    file.path(config$output_dir, "character_phase2_gmm_summary.csv")
  )
  readr::write_csv(
    bundle$model$cluster_centroids_output,
    file.path(config$output_dir, "character_phase2_cluster_centroids.csv")
  )
  readr::write_csv(
    bundle$model$cluster_representatives,
    file.path(config$output_dir, "character_phase2_cluster_representatives.csv")
  )
  readr::write_csv(
    bundle$model$gmm_hybrids,
    file.path(config$output_dir, "character_phase2_gmm_hybrids.csv")
  )
  readr::write_csv(
    bundle$model$similarity_top10,
    file.path(config$output_dir, "character_phase2_similarity_top10.csv")
  )
  arrow::write_parquet(
    bundle$model$character_scores,
    file.path(config$output_dir, "character_scores.parquet")
  )
  readr::write_csv(
    bundle$hypotheses$size_dominance_test,
    file.path(config$output_dir, "character_phase2_size_dominance_scatter.csv")
  )
  readr::write_csv(
    bundle$hypotheses$size_dominance_summary,
    file.path(config$output_dir, "character_phase2_size_dominance_summary.csv")
  )
  readr::write_csv(
    bundle$hypotheses$size_dominance_outliers,
    file.path(config$output_dir, "character_phase2_size_dominance_outliers.csv")
  )
  readr::write_csv(
    bundle$hypotheses$cluster_shift_test,
    file.path(config$output_dir, "character_phase2_connectedness_cluster_shift.csv")
  )
  readr::write_csv(
    bundle$hypotheses$cluster_shift_summary,
    file.path(config$output_dir, "character_phase2_connectedness_cluster_shift_summary.csv")
  )
  readr::write_csv(
    bundle$hypotheses$cluster_shift_outliers,
    file.path(config$output_dir, "character_phase2_connectedness_cluster_shift_outliers.csv")
  )
}

run_phase2_character_checkpoint5 <- function() {
  config <- phase2_character_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  catalog <- build_phase2_catalog_bundle(config)
  frame <- build_phase2_character_frame(
    con = con,
    catalog_check = catalog$catalog_check
  )
  imputation <- build_phase2_imputation_bundle(
    character_frame = frame,
    catalog_check = catalog$catalog_check,
    config = config
  )
  redundancy <- build_phase2_redundancy_bundle(
    character_model_df = imputation$character_model_df,
    catalog_check = catalog$catalog_check,
    config = config
  )
  model <- build_phase2_model_bundle(
    character_model_df = imputation$character_model_df,
    character_frame = catalog$character_frame,
    catalog_check = catalog$catalog_check,
    config = config
  )
  hypotheses <- build_phase2_hypothesis_bundle(
    character_scores = model$character_scores,
    model = model,
    con = con,
    config = config
  )

  bundle <- list(
    config = config,
    catalog = catalog,
    frame = frame,
    imputation = imputation,
    redundancy = redundancy,
    model = model,
    hypotheses = hypotheses
  )

  write_phase2_checkpoint5_outputs(bundle, config)
  bundle
}

if (sys.nframe() == 0) {
  invisible(run_phase2_character_checkpoint5())
}
