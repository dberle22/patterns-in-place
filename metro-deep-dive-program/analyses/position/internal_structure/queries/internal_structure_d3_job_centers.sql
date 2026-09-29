-- This reproduces the existing D3 review threshold against its governed LODES
-- input without recasting workplace concentration as commuting integration.
WITH latest_year AS (
    SELECT MAX(year) AS year
    FROM silver.lehd_lodes_wac
    WHERE geo_level = 'tract'
),
market_tracts AS (
    SELECT z.tract_geoid, z.zone_type, z.county_name
    FROM mart_intelligence.intelligence_zones AS z
    WHERE z.cbsa_code = '__CBSA_CODE__'
)
SELECT w.geo_id AS tract_geoid, w.geo_name AS tract_name, w.year,
       w.jobs_total, r.workers_total,
       w.jobs_total / NULLIF(r.workers_total, 0) AS jobs_to_workers_ratio,
       mt.zone_type, mt.county_name
FROM silver.lehd_lodes_wac AS w
JOIN market_tracts AS mt ON w.geo_id = mt.tract_geoid
LEFT JOIN silver.lehd_lodes_rac AS r
  ON w.geo_id = r.geo_id
 AND r.geo_level = 'tract'
 AND r.year = w.year
WHERE w.geo_level = 'tract'
  AND w.year = (SELECT year FROM latest_year)
  AND w.jobs_total >= 2500
ORDER BY w.jobs_total DESC, jobs_to_workers_ratio DESC
LIMIT 15;
