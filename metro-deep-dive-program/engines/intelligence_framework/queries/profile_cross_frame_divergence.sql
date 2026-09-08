-- Query the promoted Phase 5 divergence surface.
-- This is not the Phase 6 candidate shortlist. It is the DuckDB-backed
-- overlap and disagreement layer already carried on intelligence_cross_frame.

SELECT
  cbsa_code,
  cbsa_name,
  combined_cluster,
  character_percentile_rank,
  livability_percentile_rank,
  opportunity_percentile_rank,
  top_frame,
  bottom_frame,
  frame_percentile_gap,
  frame_percentile_sd,
  mean_frame_percentile,
  overlap_profile,
  half_alignment,
  signature
FROM mart_intelligence.intelligence_cross_frame
WHERE overlap_profile = 'highly_divergent'
ORDER BY frame_percentile_gap DESC;
