-- First bridge from the Intelligence Framework into Act 4 internal structure.

SELECT
  cbsa_code,
  cbsa_name,
  zone_type,
  COUNT(*) AS tract_count,
  AVG(composite_score) AS avg_composite_score,
  AVG(national_composite_percentile) AS avg_national_percentile,
  AVG(cbsa_composite_percentile) AS avg_within_cbsa_percentile
FROM mart_intelligence.intelligence_zones
WHERE cbsa_code = '40060'
GROUP BY 1, 2, 3
ORDER BY tract_count DESC, zone_type;
