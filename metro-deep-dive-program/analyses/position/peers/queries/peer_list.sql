-- Long peer surface for the selected CBSA across cross-frame and frame-specific peers.

WITH peer_list AS (
  SELECT 'cross_frame' AS peer_type, 1 AS peer_rank, cbsa_code, cbsa_name, top10_peer_1_cbsa_code AS peer_cbsa_code, top10_peer_1_cbsa_name AS peer_cbsa_name, top10_peer_1_similarity AS similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 2, cbsa_code, cbsa_name, top10_peer_2_cbsa_code, top10_peer_2_cbsa_name, top10_peer_2_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 3, cbsa_code, cbsa_name, top10_peer_3_cbsa_code, top10_peer_3_cbsa_name, top10_peer_3_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 4, cbsa_code, cbsa_name, top10_peer_4_cbsa_code, top10_peer_4_cbsa_name, top10_peer_4_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 5, cbsa_code, cbsa_name, top10_peer_5_cbsa_code, top10_peer_5_cbsa_name, top10_peer_5_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 6, cbsa_code, cbsa_name, top10_peer_6_cbsa_code, top10_peer_6_cbsa_name, top10_peer_6_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 7, cbsa_code, cbsa_name, top10_peer_7_cbsa_code, top10_peer_7_cbsa_name, top10_peer_7_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 8, cbsa_code, cbsa_name, top10_peer_8_cbsa_code, top10_peer_8_cbsa_name, top10_peer_8_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 9, cbsa_code, cbsa_name, top10_peer_9_cbsa_code, top10_peer_9_cbsa_name, top10_peer_9_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'cross_frame', 10, cbsa_code, cbsa_name, top10_peer_10_cbsa_code, top10_peer_10_cbsa_name, top10_peer_10_similarity FROM mart_intelligence.intelligence_cross_frame WHERE cbsa_code = '__CBSA_CODE__'

  UNION ALL SELECT 'character', 1, cbsa_code, cbsa_name, top10_peer_1_cbsa_code, top10_peer_1_cbsa_name, top10_peer_1_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 2, cbsa_code, cbsa_name, top10_peer_2_cbsa_code, top10_peer_2_cbsa_name, top10_peer_2_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 3, cbsa_code, cbsa_name, top10_peer_3_cbsa_code, top10_peer_3_cbsa_name, top10_peer_3_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 4, cbsa_code, cbsa_name, top10_peer_4_cbsa_code, top10_peer_4_cbsa_name, top10_peer_4_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 5, cbsa_code, cbsa_name, top10_peer_5_cbsa_code, top10_peer_5_cbsa_name, top10_peer_5_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 6, cbsa_code, cbsa_name, top10_peer_6_cbsa_code, top10_peer_6_cbsa_name, top10_peer_6_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 7, cbsa_code, cbsa_name, top10_peer_7_cbsa_code, top10_peer_7_cbsa_name, top10_peer_7_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 8, cbsa_code, cbsa_name, top10_peer_8_cbsa_code, top10_peer_8_cbsa_name, top10_peer_8_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 9, cbsa_code, cbsa_name, top10_peer_9_cbsa_code, top10_peer_9_cbsa_name, top10_peer_9_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'character', 10, cbsa_code, cbsa_name, top10_peer_10_cbsa_code, top10_peer_10_cbsa_name, top10_peer_10_similarity FROM mart_intelligence.intelligence_character WHERE cbsa_code = '__CBSA_CODE__'

  UNION ALL SELECT 'livability', 1, cbsa_code, cbsa_name, top10_peer_1_cbsa_code, top10_peer_1_cbsa_name, top10_peer_1_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 2, cbsa_code, cbsa_name, top10_peer_2_cbsa_code, top10_peer_2_cbsa_name, top10_peer_2_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 3, cbsa_code, cbsa_name, top10_peer_3_cbsa_code, top10_peer_3_cbsa_name, top10_peer_3_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 4, cbsa_code, cbsa_name, top10_peer_4_cbsa_code, top10_peer_4_cbsa_name, top10_peer_4_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 5, cbsa_code, cbsa_name, top10_peer_5_cbsa_code, top10_peer_5_cbsa_name, top10_peer_5_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 6, cbsa_code, cbsa_name, top10_peer_6_cbsa_code, top10_peer_6_cbsa_name, top10_peer_6_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 7, cbsa_code, cbsa_name, top10_peer_7_cbsa_code, top10_peer_7_cbsa_name, top10_peer_7_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 8, cbsa_code, cbsa_name, top10_peer_8_cbsa_code, top10_peer_8_cbsa_name, top10_peer_8_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 9, cbsa_code, cbsa_name, top10_peer_9_cbsa_code, top10_peer_9_cbsa_name, top10_peer_9_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'livability', 10, cbsa_code, cbsa_name, top10_peer_10_cbsa_code, top10_peer_10_cbsa_name, top10_peer_10_similarity FROM mart_intelligence.intelligence_livability WHERE cbsa_code = '__CBSA_CODE__'

  UNION ALL SELECT 'opportunity', 1, cbsa_code, cbsa_name, top10_peer_1_cbsa_code, top10_peer_1_cbsa_name, top10_peer_1_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 2, cbsa_code, cbsa_name, top10_peer_2_cbsa_code, top10_peer_2_cbsa_name, top10_peer_2_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 3, cbsa_code, cbsa_name, top10_peer_3_cbsa_code, top10_peer_3_cbsa_name, top10_peer_3_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 4, cbsa_code, cbsa_name, top10_peer_4_cbsa_code, top10_peer_4_cbsa_name, top10_peer_4_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 5, cbsa_code, cbsa_name, top10_peer_5_cbsa_code, top10_peer_5_cbsa_name, top10_peer_5_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 6, cbsa_code, cbsa_name, top10_peer_6_cbsa_code, top10_peer_6_cbsa_name, top10_peer_6_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 7, cbsa_code, cbsa_name, top10_peer_7_cbsa_code, top10_peer_7_cbsa_name, top10_peer_7_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 8, cbsa_code, cbsa_name, top10_peer_8_cbsa_code, top10_peer_8_cbsa_name, top10_peer_8_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 9, cbsa_code, cbsa_name, top10_peer_9_cbsa_code, top10_peer_9_cbsa_name, top10_peer_9_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
  UNION ALL SELECT 'opportunity', 10, cbsa_code, cbsa_name, top10_peer_10_cbsa_code, top10_peer_10_cbsa_name, top10_peer_10_similarity FROM mart_intelligence.intelligence_opportunity WHERE cbsa_code = '__CBSA_CODE__'
)
SELECT *
FROM peer_list
WHERE peer_cbsa_code IS NOT NULL
ORDER BY peer_type, peer_rank;
