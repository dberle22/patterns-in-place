source(here::here("foundations", "loaders", "_shared_intelligence_loader.R"))

livability_peers <- build_peer_wide(
  "exploration/intelligence_framework/phase_3_livability_calibration/outputs/livability_phase3_similarity_top10.csv"
)

write_intelligence_datamart(
  parquet_rel_path = "exploration/intelligence_framework/phase_3_livability_calibration/outputs/livability_scores.parquet",
  table_name = "intelligence_livability",
  transform_fn = function(df) {
    df |>
      left_join(livability_peers, by = "cbsa_code") |>
      mutate(
        livability_cluster = livability_cluster_name,
        livability_percentile_rank = as.integer(round(livability_percentile)),
        affordability_score = subject_score_affordability,
        health_and_safety_score = subject_score_health_and_safety,
        access_and_infrastructure_score = subject_score_access_and_infrastructure,
        physical_environment_score = subject_score_physical_environment
      )
  }
)
