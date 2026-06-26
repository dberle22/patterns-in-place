source(here::here("foundations", "loaders", "_shared_intelligence_loader.R"))

character_peers <- build_peer_wide(
  "exploration/intelligence_framework/phase_2_character_calibration/outputs/character_phase2_similarity_top10.csv"
)

write_intelligence_datamart(
  parquet_rel_path = "exploration/intelligence_framework/phase_2_character_calibration/outputs/character_scores.parquet",
  table_name = "intelligence_character",
  transform_fn = function(df) {
    df |>
      left_join(character_peers, by = "cbsa_code") |>
      mutate(
        character_cluster = character_cluster_name,
        character_percentile_rank = as.integer(round(character_percentile)),
        demographics_score = subject_score_demographics,
        social_fabric_score = subject_score_social_fabric
      )
  }
)
