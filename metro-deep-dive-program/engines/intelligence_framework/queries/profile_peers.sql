-- Cross-frame and frame-specific peer surface for one metro.
-- The promoted mart contract currently exposes top-10 peers only.

SELECT
  c.cbsa_code,
  c.cbsa_name,

  cf.top10_peer_1_cbsa_name AS cross_frame_peer_1,
  cf.top10_peer_1_similarity AS cross_frame_peer_1_similarity,
  cf.top10_peer_2_cbsa_name AS cross_frame_peer_2,
  cf.top10_peer_2_similarity AS cross_frame_peer_2_similarity,
  cf.top10_peer_3_cbsa_name AS cross_frame_peer_3,
  cf.top10_peer_3_similarity AS cross_frame_peer_3_similarity,

  c.top10_peer_1_cbsa_name AS character_peer_1,
  c.top10_peer_1_similarity AS character_peer_1_similarity,
  l.top10_peer_1_cbsa_name AS livability_peer_1,
  l.top10_peer_1_similarity AS livability_peer_1_similarity,
  o.top10_peer_1_cbsa_name AS opportunity_peer_1,
  o.top10_peer_1_similarity AS opportunity_peer_1_similarity
FROM mart_intelligence.intelligence_character AS c
JOIN mart_intelligence.intelligence_livability AS l
  ON c.cbsa_code = l.cbsa_code
JOIN mart_intelligence.intelligence_opportunity AS o
  ON c.cbsa_code = o.cbsa_code
JOIN mart_intelligence.intelligence_cross_frame AS cf
  ON c.cbsa_code = cf.cbsa_code
WHERE c.cbsa_code = '40060';
