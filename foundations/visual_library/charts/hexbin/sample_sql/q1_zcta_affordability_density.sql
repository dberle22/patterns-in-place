-- Q1: Across all ZCTAs, where do most neighborhoods sit on income vs rent burden?

WITH region_lookup AS (
  SELECT
    zc.zip_geoid AS geo_id,
    MIN(sr.census_region) AS census_region
  FROM metro_deep_dive.silver.xwalk_zcta_county zc
  LEFT JOIN metro_deep_dive.silver.xwalk_county_state cs
    ON zc.county_geoid = cs.county_geoid
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region sr
    ON cs.state_fip = sr.state_fips
  GROUP BY 1
)
SELECT
  'hexbin_affordability_density'::VARCHAR AS question_id,
  a.geo_level,
  a.geo_id,
  a.geo_name,
  '2023_snapshot'::VARCHAR AS time_window,
  a.median_hh_income::DOUBLE AS x_value,
  a.pct_rent_burden_30plus::DOUBLE AS y_value,
  'Median Household Income (2023, $)'::VARCHAR AS x_label,
  'Rent-Burdened Households (2023, %)'::VARCHAR AS y_label,
  rl.census_region AS "group",
  NULL::DOUBLE AS weight_value,
  FALSE AS highlight_flag,
  'gold.affordability_wide + silver.xwalk_zcta_county + silver.xwalk_county_state + silver.xwalk_state_region'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  'Unweighted national ZCTA snapshot.'::VARCHAR AS note
FROM metro_deep_dive.gold.affordability_wide a
LEFT JOIN region_lookup rl
  ON a.geo_id = rl.geo_id
WHERE a.geo_level = 'zcta'
  AND a.year = 2023
  AND a.median_hh_income IS NOT NULL
  AND a.pct_rent_burden_30plus IS NOT NULL;
