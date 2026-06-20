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
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_helpers.R"))
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_config.R"))
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_catalog_audit.R"))
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_frame_build.R"))
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_imputation.R"))
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_redundancy.R"))
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_modeling.R"))
source(here("exploration/intelligence_framework/phase_4_opportunity_calibration/R/phase4_hypotheses.R"))

write_phase4_checkpoint_outputs <- function(bundle, config) {
  readr::write_csv(
    bundle$catalog$catalog_check,
    file.path(config$output_dir, "opportunity_phase4_catalog_check.csv")
  )
  readr::write_csv(
    bundle$catalog$polarity_audit,
    file.path(config$output_dir, "opportunity_phase4_polarity_flags.csv")
  )
  readr::write_csv(
    config$clustering_metric_decisions,
    file.path(config$output_dir, "opportunity_phase4_clustering_metric_decisions.csv")
  )
  arrow::write_parquet(
    bundle$frame,
    file.path(config$output_dir, "opportunity_phase4_kpi_frame.parquet")
  )
  readr::write_csv(
    bundle$imputation$metric_completeness,
    file.path(config$output_dir, "opportunity_phase4_metric_completeness.csv")
  )
  arrow::write_parquet(
    bundle$imputation$metric_completeness,
    file.path(config$output_dir, "opportunity_phase4_metric_completeness.parquet")
  )
  readr::write_csv(
    bundle$imputation$imputation_audit,
    file.path(config$output_dir, "opportunity_phase4_imputation_audit.csv")
  )
  readr::write_csv(
    bundle$imputation$missing_cbsas_long,
    file.path(config$output_dir, "opportunity_phase4_missing_cbsas_long.csv")
  )
  readr::write_csv(
    bundle$imputation$imputation_sensitive_metros,
    file.path(config$output_dir, "opportunity_phase4_imputation_sensitive_metros.csv")
  )
  readr::write_csv(
    bundle$imputation$imputed_cells,
    file.path(config$output_dir, "opportunity_phase4_imputed_cells.csv")
  )
  arrow::write_parquet(
    bundle$imputation$opportunity_model_df,
    file.path(config$output_dir, "opportunity_phase4_kpi_frame_imputed.parquet")
  )
  if (!is.null(bundle$redundancy)) {
    readr::write_csv(
      bundle$redundancy$full_metric_set,
      file.path(config$output_dir, "opportunity_phase4_full_metric_set.csv")
    )
    readr::write_csv(
      bundle$redundancy$pca_recommended_metric_set,
      file.path(config$output_dir, "opportunity_phase4_pca_recommended_metric_set.csv")
    )
    readr::write_csv(
      bundle$redundancy$redundant_pairs,
      file.path(config$output_dir, "opportunity_phase4_redundant_pairs.csv")
    )
    readr::write_csv(
      bundle$redundancy$pca_variance,
      file.path(config$output_dir, "opportunity_phase4_pca_variance.csv")
    )
    readr::write_csv(
      bundle$redundancy$pca_loadings,
      file.path(config$output_dir, "opportunity_phase4_pca_loadings.csv")
    )
    readr::write_csv(
      bundle$redundancy$hclust_vs_kmeans_summary,
      file.path(config$output_dir, "opportunity_phase4_hclust_vs_kmeans_summary.csv")
    )
    readr::write_csv(
      bundle$redundancy$hclust_vs_kmeans_sizes,
      file.path(config$output_dir, "opportunity_phase4_hclust_vs_kmeans_sizes.csv")
    )
    readr::write_csv(
      bundle$redundancy$hclust_vs_kmeans_membership,
      file.path(config$output_dir, "opportunity_phase4_hclust_vs_kmeans_membership.csv")
    )
  }
  if (!is.null(bundle$model)) {
    readr::write_csv(
      bundle$model$standardization_audit,
      file.path(config$output_dir, "opportunity_phase4_standardization_audit.csv")
    )
    readr::write_csv(
      bundle$model$comparison_summary,
      file.path(config$output_dir, "opportunity_phase4_k5_k6_comparison_summary.csv")
    )
    readr::write_csv(
      bundle$model$comparison_sizes,
      file.path(config$output_dir, "opportunity_phase4_k5_k6_cluster_sizes.csv")
    )
    readr::write_csv(
      bundle$model$cluster_assignments,
      file.path(config$output_dir, "opportunity_phase4_k5_k6_cluster_assignments.csv")
    )
    readr::write_csv(
      bundle$model$cluster_centroids,
      file.path(config$output_dir, "opportunity_phase4_k5_k6_cluster_centroids.csv")
    )
    readr::write_csv(
      bundle$model$representative_metros,
      file.path(config$output_dir, "opportunity_phase4_k5_k6_representative_metros.csv")
    )
    readr::write_csv(
      bundle$model$split_summary,
      file.path(config$output_dir, "opportunity_phase4_k5_to_k6_split_summary.csv")
    )
    readr::write_csv(
      bundle$model$changed_metros_k5_k6,
      file.path(config$output_dir, "opportunity_phase4_k5_to_k6_changed_metros.csv")
    )
    readr::write_csv(
      bundle$model$cluster_name_map,
      file.path(config$output_dir, "opportunity_phase4_cluster_name_map.csv")
    )
    readr::write_csv(
      bundle$model$cluster_metric_extremes,
      file.path(config$output_dir, "opportunity_phase4_cluster_metric_extremes.csv")
    )
    readr::write_csv(
      bundle$model$gmm_cluster_summary,
      file.path(config$output_dir, "opportunity_phase4_gmm_summary.csv")
    )
    readr::write_csv(
      bundle$model$cluster_centroids_output,
      file.path(config$output_dir, "opportunity_phase4_cluster_centroids.csv")
    )
    readr::write_csv(
      bundle$model$cluster_representatives,
      file.path(config$output_dir, "opportunity_phase4_cluster_representatives.csv")
    )
    readr::write_csv(
      bundle$model$gmm_hybrids,
      file.path(config$output_dir, "opportunity_phase4_gmm_hybrids.csv")
    )
    readr::write_csv(
      bundle$model$similarity_top10,
      file.path(config$output_dir, "opportunity_phase4_similarity_top10.csv")
    )
    arrow::write_parquet(
      bundle$model$opportunity_scores,
      file.path(config$output_dir, "opportunity_scores.parquet")
    )
  }
  if (!is.null(bundle$hypotheses)) {
    readr::write_csv(
      bundle$hypotheses$industry_leading_indicator_test,
      file.path(config$output_dir, "opportunity_phase4_industry_leading_indicator_scatter.csv")
    )
    readr::write_csv(
      bundle$hypotheses$industry_leading_indicator_summary,
      file.path(config$output_dir, "opportunity_phase4_industry_leading_indicator_summary.csv")
    )
    readr::write_csv(
      bundle$hypotheses$industry_leading_indicator_outliers,
      file.path(config$output_dir, "opportunity_phase4_industry_leading_indicator_outliers.csv")
    )
    readr::write_csv(
      bundle$hypotheses$social_capital_test,
      file.path(config$output_dir, "opportunity_phase4_social_capital_scatter.csv")
    )
    readr::write_csv(
      bundle$hypotheses$social_capital_summary,
      file.path(config$output_dir, "opportunity_phase4_social_capital_summary.csv")
    )
    readr::write_csv(
      bundle$hypotheses$social_capital_outliers,
      file.path(config$output_dir, "opportunity_phase4_social_capital_outliers.csv")
    )
    readr::write_csv(
      bundle$hypotheses$signal_divergence_test,
      file.path(config$output_dir, "opportunity_phase4_signal_divergence_scatter.csv")
    )
    readr::write_csv(
      bundle$hypotheses$signal_divergence_summary,
      file.path(config$output_dir, "opportunity_phase4_signal_divergence_summary.csv")
    )
    readr::write_csv(
      bundle$hypotheses$signal_divergence_outliers,
      file.path(config$output_dir, "opportunity_phase4_signal_divergence_outliers.csv")
    )
    readr::write_csv(
      bundle$hypotheses$livability_opportunity_scatter,
      file.path(config$output_dir, "opportunity_phase4_livability_opportunity_scatter.csv")
    )
    readr::write_csv(
      bundle$hypotheses$livability_opportunity_summary,
      file.path(config$output_dir, "opportunity_phase4_livability_opportunity_summary.csv")
    )
    readr::write_csv(
      bundle$hypotheses$livability_opportunity_outliers,
      file.path(config$output_dir, "opportunity_phase4_livability_opportunity_outliers.csv")
    )
    readr::write_csv(
      bundle$hypotheses$oz_high_opportunity_context,
      file.path(config$output_dir, "opportunity_phase4_oz_high_opportunity_context.csv")
    )
  }
}

run_phase4_opportunity_checkpoint2 <- function() {
  config <- phase4_opportunity_config()
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  catalog <- build_phase4_catalog_bundle(config)
  frame <- build_phase4_opportunity_frame(
    con = con,
    catalog_check = catalog$catalog_check
  )
  imputation <- build_phase4_imputation_bundle(
    opportunity_frame = frame,
    catalog_check = catalog$catalog_check,
    config = config
  )
  redundancy <- build_phase4_redundancy_bundle(
    opportunity_model_df = imputation$opportunity_model_df,
    catalog_check = catalog$catalog_check,
    config = config
  )
  model <- build_phase4_model_bundle(
    opportunity_model_df = imputation$opportunity_model_df,
    opportunity_frame = catalog$opportunity_frame,
    catalog_check = catalog$catalog_check,
    config = config
  )
  hypotheses <- build_phase4_hypothesis_bundle(
    opportunity_scores = model$opportunity_scores,
    con = con
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

  write_phase4_checkpoint_outputs(bundle, config)
  bundle
}

if (sys.nframe() == 0) {
  invisible(run_phase4_opportunity_checkpoint2())
}
