source(here::here("foundations", "loaders", "_shared_intelligence_loader.R"))

cross_frame_peers <- build_peer_wide(
  "exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_phase5_similarity_top10.csv"
)

cross_frame_overlap <- read_optional_csv(
  "exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_phase5_overlap_flags.csv"
) |>
  mutate(cbsa_code = as.character(cbsa_code)) |>
  select(
    cbsa_code,
    top_frame,
    top_frame_percentile,
    bottom_frame,
    bottom_frame_percentile,
    frame_percentile_gap,
    frame_percentile_sd,
    mean_frame_percentile,
    same_top_half_all_frames,
    same_bottom_half_all_frames,
    overlap_profile,
    half_alignment,
    signature
  )

write_intelligence_datamart(
  parquet_rel_path = "exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_scores.parquet",
  table_name = "intelligence_cross_frame",
  transform_fn = function(df) {
    df |>
      left_join(cross_frame_peers, by = "cbsa_code") |>
      left_join(cross_frame_overlap, by = "cbsa_code") |>
      mutate(
        combined_cluster = cross_frame_cluster_name,
        cross_frame_percentile_rank = as.integer(round(cross_frame_percentile)),
        character_percentile_rank = as.integer(round(character__character_percentile)),
        livability_percentile_rank = as.integer(round(livability__livability_percentile)),
        opportunity_percentile_rank = as.integer(round(opportunity__opportunity_percentile))
      )
  }
)
