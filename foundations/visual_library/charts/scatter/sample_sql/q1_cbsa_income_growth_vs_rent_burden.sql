-- Q1: Which CBSAs have high income growth but comparatively low rent burden?
--
-- Parameter decisions (edit in `params` CTE below):
-- 1) snapshot_year: year used for endpoint/snapshot values
-- 2) base_year: year used for growth baseline
-- 3) target_geo_id + target_geo_level: optional row highlight target
--
-- To update for a different geography reference:
-- - Set target_geo_level to `cbsa`, `county`, `zcta`, etc.
-- - Set target_geo_id to the matching geoid for that level.

WITH params AS (
  SELECT
    2023::INTEGER AS snapshot_year,
    2018::INTEGER AS base_year,
    'cbsa'::VARCHAR AS target_geo_level,
    '48900'::VARCHAR AS target_geo_id
),
cbsa_meta AS (
  SELECT
    c.cbsa_code AS geo_id,
    c.cbsa_name AS geo_name,
    s.census_division,
    ROW_NUMBER() OVER (PARTITION BY c.cbsa_code ORDER BY c.county_geoid) AS rn
  FROM metro_deep_dive.silver.xwalk_cbsa_county c
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region s
    ON c.state_fips = s.state_fips
),
cbsa_meta_dedup AS (
  SELECT geo_id, geo_name, census_division
  FROM cbsa_meta
  WHERE rn = 1
),
cbsa_income AS (
  SELECT geo_id, geo_name, year, income_pc_growth_5yr
  FROM metro_deep_dive.gold.economics_income_wide
  WHERE geo_level = 'cbsa'
),
cbsa_housing AS (
  SELECT geo_id, year, pct_rent_burden_30plus, hu_total
  FROM metro_deep_dive.gold.affordability_wide
  WHERE geo_level = 'cbsa'
)
SELECT
  'cbsa'::VARCHAR AS geo_level,
  snap.geo_id,
  COALESCE(m.geo_name, snap.geo_name) AS geo_name,
  '2018_to_2023_growth'::VARCHAR AS time_window,
  snap.income_pc_growth_5yr * 100.0 AS x_value,
  hsnap.pct_rent_burden_30plus * 100.0 AS y_value,
  'Per Capita Income Growth (5Y, %)'::VARCHAR AS x_label,
  'Rent Burden 30%+ (2023, %)'::VARCHAR AS y_label,
  'income_growth_5y_pct'::VARCHAR AS x_metric_id,
  'rent_burden_30plus_pct'::VARCHAR AS y_metric_id,
  m.census_division AS "group",
  hsnap.hu_total::DOUBLE AS size_value,
  CASE
    WHEN (SELECT target_geo_level FROM params) = 'cbsa'
     AND snap.geo_id = (SELECT target_geo_id FROM params)
    THEN TRUE ELSE FALSE
  END AS label_flag,
  'silver.income_kpi + silver.housing_kpi + silver.xwalk_cbsa_county + silver.xwalk_state_region'::VARCHAR AS source,
  '2026-03-04'::VARCHAR AS vintage,
  NULL::VARCHAR AS note
FROM cbsa_income snap
JOIN cbsa_income base
  ON snap.geo_id = base.geo_id
 AND base.year = (SELECT base_year FROM params)
JOIN cbsa_housing hsnap
  ON snap.geo_id = hsnap.geo_id
 AND hsnap.year = (SELECT snapshot_year FROM params)
LEFT JOIN cbsa_meta_dedup m
  ON snap.geo_id = m.geo_id
WHERE snap.year = (SELECT snapshot_year FROM params)
  AND base.income_pc_growth_5yr IS NOT NULL
  AND snap.income_pc_growth_5yr IS NOT NULL
  AND isfinite(base.income_pc_growth_5yr)
  AND isfinite(snap.income_pc_growth_5yr)
  AND hsnap.pct_rent_burden_30plus IS NOT NULL;
