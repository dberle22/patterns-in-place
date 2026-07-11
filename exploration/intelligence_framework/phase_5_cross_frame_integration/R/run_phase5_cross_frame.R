library(here)
library(DBI)
library(duckdb)
library(dplyr)
library(purrr)
library(tidyr)
library(stringr)
library(glue)
library(readr)
library(arrow)
library(cluster)
library(tibble)

if (Sys.getenv("DB_PATH") == "" && file.exists(here(".Renviron"))) {
  readRenviron(here(".Renviron"))
}

source(here("exploration/intelligence_framework/R/utils.R"))
source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/phase5_helpers.R"))
source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/phase5_config.R"))
source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/phase5_input_audit.R"))
source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/phase5_redundancy.R"))
source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/phase5_modeling.R"))
source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/phase5_overlap.R"))
source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/phase5_hypotheses.R"))

write_phase5_outputs <- function(input_bundle, redundancy_bundle, modeling_bundle, final_model_bundle, overlap_bundle, hypothesis_bundle, config) {
  readr::write_csv(
    input_bundle$frame_coverage,
    file.path(config$output_dir, "cross_frame_phase5_input_audit.csv")
  )
  readr::write_csv(
    input_bundle$missing_from_scores,
    file.path(config$output_dir, "cross_frame_phase5_missing_from_scores.csv")
  )
  readr::write_csv(
    input_bundle$feature_spec,
    file.path(config$output_dir, "cross_frame_phase5_feature_spec.csv")
  )
  arrow::write_parquet(
    input_bundle$combined_model_df,
    file.path(config$output_dir, "cross_frame_phase5_combined_input_matrix.parquet")
  )
  arrow::write_parquet(
    input_bundle$context_bundle,
    file.path(config$output_dir, "cross_frame_phase5_context_bundle.parquet")
  )
  readr::write_csv(
    redundancy_bundle$standardization_audit,
    file.path(config$output_dir, "cross_frame_phase5_standardization_audit.csv")
  )
  readr::write_csv(
    redundancy_bundle$redundant_pairs,
    file.path(config$output_dir, "cross_frame_phase5_redundant_pairs.csv")
  )
  readr::write_csv(
    redundancy_bundle$pca_variance,
    file.path(config$output_dir, "cross_frame_phase5_pca_variance.csv")
  )
  readr::write_csv(
    redundancy_bundle$pca_loadings,
    file.path(config$output_dir, "cross_frame_phase5_pca_loadings.csv")
  )
  readr::write_csv(
    redundancy_bundle$kpi_decisions,
    file.path(config$output_dir, "cross_frame_phase5_kpi_decisions.csv")
  )
  readr::write_csv(
    redundancy_bundle$recommended_metric_set,
    file.path(config$output_dir, "cross_frame_phase5_recommended_metric_set.csv")
  )
  readr::write_csv(
    modeling_bundle$candidate_metric_sets,
    file.path(config$output_dir, "cross_frame_phase5_candidate_metric_sets.csv")
  )
  readr::write_csv(
    modeling_bundle$calibration_summary,
    file.path(config$output_dir, "cross_frame_phase5_cluster_count_calibration_comparison.csv")
  )
  readr::write_csv(
    modeling_bundle$calibration_sizes,
    file.path(config$output_dir, "cross_frame_phase5_cluster_count_sizes_comparison.csv")
  )
  readr::write_csv(
    final_model_bundle$cluster_name_map,
    file.path(config$output_dir, "cross_frame_phase5_cluster_name_map.csv")
  )
  readr::write_csv(
    final_model_bundle$cluster_centroids,
    file.path(config$output_dir, "cross_frame_phase5_cluster_centroids.csv")
  )
  readr::write_csv(
    final_model_bundle$cluster_metric_extremes,
    file.path(config$output_dir, "cross_frame_phase5_cluster_metric_extremes.csv")
  )
  readr::write_csv(
    final_model_bundle$cluster_representatives,
    file.path(config$output_dir, "cross_frame_phase5_cluster_representatives.csv")
  )
  readr::write_csv(
    final_model_bundle$gmm_hybrids,
    file.path(config$output_dir, "cross_frame_phase5_gmm_hybrids.csv")
  )
  readr::write_csv(
    final_model_bundle$gmm_cluster_summary,
    file.path(config$output_dir, "cross_frame_phase5_gmm_summary.csv")
  )
  readr::write_csv(
    final_model_bundle$similarity_top10,
    file.path(config$output_dir, "cross_frame_phase5_similarity_top10.csv")
  )
  readr::write_csv(
    overlap_bundle$overlap_flags,
    file.path(config$output_dir, "cross_frame_phase5_overlap_flags.csv")
  )
  readr::write_csv(
    overlap_bundle$overlap_summary,
    file.path(config$output_dir, "cross_frame_phase5_overlap_summary.csv")
  )
  readr::write_csv(
    overlap_bundle$cluster_overlap_summary,
    file.path(config$output_dir, "cross_frame_phase5_cluster_overlap_summary.csv")
  )
  readr::write_csv(
    hypothesis_bundle$frame_alignment_scatter,
    file.path(config$output_dir, "cross_frame_phase5_frame_alignment_scatter.csv")
  )
  readr::write_csv(
    hypothesis_bundle$frame_alignment_summary,
    file.path(config$output_dir, "cross_frame_phase5_frame_alignment_summary.csv")
  )
  readr::write_csv(
    hypothesis_bundle$frame_alignment_outliers,
    file.path(config$output_dir, "cross_frame_phase5_frame_alignment_outliers.csv")
  )
  readr::write_csv(
    hypothesis_bundle$candidate_list,
    file.path(config$output_dir, "cross_frame_phase5_candidate_list.csv")
  )
  arrow::write_parquet(
    final_model_bundle$cross_frame_scores,
    file.path(config$output_dir, "cross_frame_scores.parquet")
  )
}

run_phase5_cross_frame <- function(config = phase5_cross_frame_config()) {
  con <- db_connect()
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  input_bundle <- build_phase5_input_audit_bundle(con, config)
  redundancy_bundle <- build_phase5_redundancy_bundle(input_bundle, config)
  modeling_bundle <- build_phase5_cluster_calibration_bundle(redundancy_bundle, config)
  final_model_bundle <- build_phase5_final_model_bundle(input_bundle, redundancy_bundle, modeling_bundle, config)
  overlap_bundle <- build_phase5_overlap_bundle(final_model_bundle$cross_frame_scores)
  hypothesis_bundle <- build_phase5_hypothesis_bundle(final_model_bundle$cross_frame_scores)

  write_phase5_outputs(
    input_bundle,
    redundancy_bundle,
    modeling_bundle,
    final_model_bundle,
    overlap_bundle,
    hypothesis_bundle,
    config
  )

  message(
    sprintf(
      "Phase 5 build complete: %d candidate KPIs reduced to %d lean KPIs and %d moderate KPIs using %d retained PCs (%.1f%% cumulative variance).",
      nrow(input_bundle$feature_spec),
      sum(modeling_bundle$candidate_metric_sets$metric_set == "lean_18_kpi_set" & modeling_bundle$candidate_metric_sets$keep_for_candidate),
      sum(modeling_bundle$candidate_metric_sets$metric_set == "moderate_35_kpi_set" & modeling_bundle$candidate_metric_sets$keep_for_candidate),
      redundancy_bundle$retained_pc_count,
      100 * redundancy_bundle$pca_variance$cumulative_variance[redundancy_bundle$retained_pc_count]
    )
  )

  invisible(
    list(
      config = config,
      input = input_bundle,
      redundancy = redundancy_bundle,
      modeling = modeling_bundle,
      final_model = final_model_bundle,
      overlap = overlap_bundle,
      hypotheses = hypothesis_bundle
    )
  )
}

if (sys.nframe() == 0) {
  run_phase5_cross_frame()
}
