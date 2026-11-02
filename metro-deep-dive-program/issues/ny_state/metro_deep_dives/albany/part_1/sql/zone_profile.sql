-- What each Phase 7 zone type looks like in raw terms: median tract values for every zoned
-- tract in the US and for the metro. Inputs are raw (no imputation, no polarity flip).
WITH tracts AS (
  SELECT z.zone_type, i.*  -- i.cbsa_code is the tract's CBSA
  FROM mart_intelligence.intelligence_zones AS z
  JOIN gold.intelligence_zone_inputs AS i ON i.tract_geoid = z.tract_geoid
),
scoped AS (
  SELECT 'US' AS scope, * FROM tracts
  UNION ALL BY NAME
  SELECT 'Albany' AS scope, * FROM tracts WHERE cbsa_code = '__CBSA_CODE__'
)
SELECT
  scope,
  zone_type,
  COUNT(*) AS tracts,
  median(pov_rate) AS pov_rate,
  median(pct_ba_plus) AS pct_ba_plus,
  median(median_hh_income) AS median_hh_income,
  median(owner_occ_rate) AS owner_occ_rate,
  median(pct_same_house) AS pct_same_house,
  median(pct_age_over_64) AS pct_age_over_64,
  median(pop_weighted_density_sqmi) AS density_sqmi
FROM scoped
GROUP BY ALL
ORDER BY zone_type, scope DESC
