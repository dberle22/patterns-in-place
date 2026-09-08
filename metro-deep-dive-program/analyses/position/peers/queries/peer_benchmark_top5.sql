-- Compare the selected CBSA to its top 5 cross-frame peers.

WITH top_peers AS (
  SELECT
    top10_peer_1_cbsa_code AS peer_cbsa_code, 1 AS peer_rank
  FROM mart_intelligence.intelligence_cross_frame
  WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL
  SELECT top10_peer_2_cbsa_code, 2 FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL
  SELECT top10_peer_3_cbsa_code, 3 FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL
  SELECT top10_peer_4_cbsa_code, 4 FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL
  SELECT top10_peer_5_cbsa_code, 5 FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
),
comparison_set AS (
  SELECT
    cf.cbsa_code,
    cf.cbsa_name,
    'target' AS entity_role,
    0 AS peer_rank,
    c.character_cluster_name AS character_cluster,
    l.livability_cluster_name AS livability_cluster,
    o.opportunity_cluster_name AS opportunity_cluster,
    cf.combined_cluster,
    cf.character_percentile_rank,
    cf.livability_percentile_rank,
    cf.opportunity_percentile_rank,
    cf.cross_frame_percentile_rank
  FROM mart_intelligence.intelligence_cross_frame AS cf
  LEFT JOIN mart_intelligence.intelligence_character AS c
    ON cf.cbsa_code = c.cbsa_code
  LEFT JOIN mart_intelligence.intelligence_livability AS l
    ON cf.cbsa_code = l.cbsa_code
  LEFT JOIN mart_intelligence.intelligence_opportunity AS o
    ON cf.cbsa_code = o.cbsa_code
  WHERE cf.cbsa_code = '__CBSA_CODE__'

  UNION ALL

  SELECT
    cf.cbsa_code,
    cf.cbsa_name,
    'peer' AS entity_role,
    tp.peer_rank,
    c.character_cluster_name AS character_cluster,
    l.livability_cluster_name AS livability_cluster,
    o.opportunity_cluster_name AS opportunity_cluster,
    cf.combined_cluster,
    cf.character_percentile_rank,
    cf.livability_percentile_rank,
    cf.opportunity_percentile_rank,
    cf.cross_frame_percentile_rank
  FROM top_peers AS tp
  JOIN mart_intelligence.intelligence_cross_frame AS cf
    ON tp.peer_cbsa_code = cf.cbsa_code
  LEFT JOIN mart_intelligence.intelligence_character AS c
    ON cf.cbsa_code = c.cbsa_code
  LEFT JOIN mart_intelligence.intelligence_livability AS l
    ON cf.cbsa_code = l.cbsa_code
  LEFT JOIN mart_intelligence.intelligence_opportunity AS o
    ON cf.cbsa_code = o.cbsa_code
)
SELECT *
FROM comparison_set
ORDER BY peer_rank, cbsa_name;
