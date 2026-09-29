-- Frame percentile surface for a selected CBSA.

SELECT
  cbsa_code,
  cbsa_name,
  'character' AS frame_id,
  character_percentile_rank AS percentile_rank
FROM mart_intelligence.intelligence_cross_frame
WHERE cbsa_code = '__CBSA_CODE__'

UNION ALL

SELECT
  cbsa_code,
  cbsa_name,
  'livability' AS frame_id,
  livability_percentile_rank AS percentile_rank
FROM mart_intelligence.intelligence_cross_frame
WHERE cbsa_code = '__CBSA_CODE__'

UNION ALL

SELECT
  cbsa_code,
  cbsa_name,
  'opportunity' AS frame_id,
  opportunity_percentile_rank AS percentile_rank
FROM mart_intelligence.intelligence_cross_frame
WHERE cbsa_code = '__CBSA_CODE__'

UNION ALL

SELECT
  cbsa_code,
  cbsa_name,
  'cross_frame' AS frame_id,
  cross_frame_percentile_rank AS percentile_rank
FROM mart_intelligence.intelligence_cross_frame
WHERE cbsa_code = '__CBSA_CODE__';
