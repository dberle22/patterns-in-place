-- Q2: For counties in the target CBSA, which dimensions are strongest versus weakest?

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year FROM gold.affordability_wide WHERE geo_level = 'county'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.population_demographics WHERE geo_level = 'county'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.economics_labor_wide WHERE geo_level = 'county'
  )
),
target_division AS (
  SELECT MIN(s.census_division) AS census_division
  FROM silver.xwalk_cbsa_county x
  LEFT JOIN silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  WHERE x.cbsa_code = (SELECT target_geo_id FROM target_cbsa)
),
display_counties AS (
  SELECT DISTINCT county_geoid AS geo_id
  FROM silver.xwalk_cbsa_county
  WHERE cbsa_code = (SELECT target_geo_id FROM target_cbsa)
),
universe_counties AS (
  SELECT DISTINCT x.county_geoid AS geo_id
  FROM silver.xwalk_cbsa_county x
  LEFT JOIN silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  WHERE s.census_division = (SELECT census_division FROM target_division)
),
county_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    p.pop_growth_5yr,
    a.median_hh_income,
    p.pct_ba_plus,
    l.pct_unemployment_rate,
    a.pct_rent_burden_30plus,
    a.permits_per_1000_population,
    a.geo_id IN (SELECT geo_id FROM display_counties) AS display_flag
  FROM gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  JOIN universe_counties u
    ON a.geo_id = u.geo_id
  LEFT JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN gold.economics_labor_wide l
    ON a.geo_level = l.geo_level
   AND a.geo_id = l.geo_id
   AND a.year = l.year
  WHERE a.geo_level = 'county'
),
metric_long AS (
  SELECT 'heatmap_county_dimension_compare'::VARCHAR AS question_id, geo_level, geo_id, geo_name, 'latest county profile'::VARCHAR AS time_window, 1 AS metric_order, 'pop_growth_5yr'::VARCHAR AS metric_id, 'Population growth (5yr)'::VARCHAR AS metric_label, 'Growth'::VARCHAR AS metric_group, pop_growth_5yr::DOUBLE AS metric_value, 'higher_is_better'::VARCHAR AS direction, display_flag FROM county_base
  UNION ALL
  SELECT 'heatmap_county_dimension_compare', geo_level, geo_id, geo_name, 'latest county profile', 2, 'median_hh_income', 'Median household income', 'Prosperity', median_hh_income::DOUBLE, 'higher_is_better', display_flag FROM county_base
  UNION ALL
  SELECT 'heatmap_county_dimension_compare', geo_level, geo_id, geo_name, 'latest county profile', 3, 'pct_ba_plus', 'Adults with BA+', 'Talent', pct_ba_plus::DOUBLE, 'higher_is_better', display_flag FROM county_base
  UNION ALL
  SELECT 'heatmap_county_dimension_compare', geo_level, geo_id, geo_name, 'latest county profile', 4, 'pct_unemployment_rate', 'Unemployment rate', 'Labor', pct_unemployment_rate::DOUBLE, 'lower_is_better', display_flag FROM county_base
  UNION ALL
  SELECT 'heatmap_county_dimension_compare', geo_level, geo_id, geo_name, 'latest county profile', 5, 'pct_rent_burden_30plus', 'Rent-burdened renter share', 'Affordability', pct_rent_burden_30plus::DOUBLE, 'lower_is_better', display_flag FROM county_base
  UNION ALL
  SELECT 'heatmap_county_dimension_compare', geo_level, geo_id, geo_name, 'latest county profile', 6, 'permits_per_1000_population', 'Permits per 1,000 residents', 'Supply', permits_per_1000_population::DOUBLE, 'higher_is_better', display_flag FROM county_base
)
SELECT
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  metric_id,
  metric_label,
  metric_value,
  'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + silver.xwalk_cbsa_county'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  metric_group,
  direction,
  display_flag,
  metric_order,
  CASE
    WHEN metric_value IS NULL THEN NULL
    WHEN metric_id = 'median_hh_income' THEN '$' || CAST(ROUND(metric_value, 0) AS VARCHAR)
    WHEN metric_id IN ('pop_growth_5yr', 'pct_ba_plus', 'pct_unemployment_rate', 'pct_rent_burden_30plus') THEN CAST(ROUND(metric_value * 100, 1) AS VARCHAR) || '%'
    ELSE CAST(ROUND(metric_value, 1) AS VARCHAR)
  END AS value_label,
  'Percentiles normalize against the South Atlantic county universe; displayed rows are counties in the Wilmington, NC CBSA.'::VARCHAR AS note
FROM metric_long
ORDER BY metric_order, geo_name;
