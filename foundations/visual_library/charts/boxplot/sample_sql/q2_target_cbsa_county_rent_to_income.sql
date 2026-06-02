-- Q2: For counties in the target CBSA, what is the distribution of median rent-to-income?

WITH target_cbsa AS (
  SELECT '12060'::VARCHAR AS target_geo_id, 'Atlanta-Sandy Springs-Roswell, GA'::VARCHAR AS target_name
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'county'
    AND rent_to_income IS NOT NULL
),
target_counties AS (
  SELECT DISTINCT
    county_geoid,
    state_name
  FROM silver.xwalk_cbsa_county
  WHERE cbsa_code = (SELECT target_geo_id FROM target_cbsa)
)
SELECT
  'boxplot_target_cbsa_county_rent_to_income'::VARCHAR AS question_id,
  a.geo_level,
  a.geo_id,
  a.geo_name,
  '2024_snapshot'::VARCHAR AS time_window,
  'rent_to_income'::VARCHAR AS metric_id,
  'Median rent-to-income ratio (%)'::VARCHAR AS metric_label,
  a.rent_to_income::DOUBLE AS metric_value,
  tc.state_name AS "group",
  a.geo_name LIKE 'Fulton County%' AS highlight_flag,
  a.geo_name LIKE 'Fulton County%' AS label_flag,
  NULL::DOUBLE AS weight_value,
  NULL::DOUBLE AS benchmark_value,
  'gold.affordability_wide + silver.xwalk_cbsa_county'::VARCHAR AS source,
  CAST(a.year AS VARCHAR) AS vintage,
  'Target CBSA is Atlanta-Sandy Springs-Roswell, GA; grouped by county state.'::VARCHAR AS note
FROM gold.affordability_wide a
JOIN target_counties tc
  ON a.geo_id = tc.county_geoid
WHERE a.geo_level = 'county'
  AND a.year = (SELECT year FROM latest_year)
  AND a.rent_to_income IS NOT NULL;
