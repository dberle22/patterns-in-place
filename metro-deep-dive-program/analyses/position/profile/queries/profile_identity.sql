-- Headline Act 1 identity surface for a selected CBSA.

SELECT
  cf.cbsa_code,
  cf.cbsa_name,
  c.character_cluster_name AS character_cluster,
  l.livability_cluster_name AS livability_cluster,
  o.opportunity_cluster_name AS opportunity_cluster,
  cf.combined_cluster AS cross_frame_cluster,
  cf.top_frame,
  cf.bottom_frame,
  cf.overlap_profile,
  cf.signature
FROM mart_intelligence.intelligence_cross_frame AS cf
LEFT JOIN mart_intelligence.intelligence_character AS c
  ON cf.cbsa_code = c.cbsa_code
LEFT JOIN mart_intelligence.intelligence_livability AS l
  ON cf.cbsa_code = l.cbsa_code
LEFT JOIN mart_intelligence.intelligence_opportunity AS o
  ON cf.cbsa_code = o.cbsa_code
WHERE cf.cbsa_code = '__CBSA_CODE__';
