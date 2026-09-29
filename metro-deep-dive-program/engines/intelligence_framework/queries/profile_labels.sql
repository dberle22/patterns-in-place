-- Headline identity surface for one metro or the full national frame.
-- Replace the WHERE clause when using this in a notebook.

SELECT
  cf.cbsa_code,
  cf.cbsa_name,
  c.character_cluster_name AS character_cluster,
  l.livability_cluster_name AS livability_cluster,
  o.opportunity_cluster_name AS opportunity_cluster,
  cf.combined_cluster AS cross_frame_cluster,
  c.character_percentile_rank,
  l.livability_percentile_rank,
  o.opportunity_percentile_rank,
  cf.cross_frame_percentile_rank,
  cf.top_frame,
  cf.bottom_frame,
  cf.frame_percentile_gap,
  cf.overlap_profile,
  cf.signature
FROM mart_intelligence.intelligence_cross_frame AS cf
LEFT JOIN mart_intelligence.intelligence_character AS c
  ON cf.cbsa_code = c.cbsa_code
LEFT JOIN mart_intelligence.intelligence_livability AS l
  ON cf.cbsa_code = l.cbsa_code
LEFT JOIN mart_intelligence.intelligence_opportunity AS o
  ON cf.cbsa_code = o.cbsa_code
WHERE cf.cbsa_code = '40060';
