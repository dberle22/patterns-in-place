-- Q3: For selected peer CBSAs, what does the full KPI profile look like in one matrix?

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year FROM gold.affordability_wide WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.population_demographics WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.economics_labor_wide WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.transport_built_form_wide WHERE geo_level = 'cbsa'
  )
),
target_division AS (
  SELECT MIN(s.census_division) AS census_division
  FROM silver.xwalk_cbsa_county x
  LEFT JOIN silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  WHERE x.cbsa_code = (SELECT target_geo_id FROM target_cbsa)
),
cbsa_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    p.pop_total,
    p.pop_growth_5yr,
    p.pct_ba_plus,
    a.median_hh_income,
    l.jobs_to_pop_ratio,
    l.pct_unemployment_rate,
    a.pct_rent_burden_30plus,
    a.value_to_income,
    a.permits_per_1000_population,
    t.mean_travel_time,
    a.geo_id = (SELECT target_geo_id FROM target_cbsa) AS highlight_flag
  FROM gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  LEFT JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN gold.economics_labor_wide l
    ON a.geo_level = l.geo_level
   AND a.geo_id = l.geo_id
   AND a.year = l.year
  LEFT JOIN gold.transport_built_form_wide t
    ON a.geo_level = t.geo_level
   AND a.geo_id = t.geo_id
   AND a.year = t.year
  WHERE a.geo_level = 'cbsa'
),
target_pop AS (
  SELECT pop_total
  FROM cbsa_base
  WHERE geo_id = (SELECT target_geo_id FROM target_cbsa)
),
division_cbsas AS (
  SELECT DISTINCT x.cbsa_code AS geo_id
  FROM silver.xwalk_cbsa_county x
  LEFT JOIN silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  WHERE s.census_division = (SELECT census_division FROM target_division)
),
display_cbsas AS (
  SELECT geo_id
  FROM cbsa_base
  WHERE geo_id IN (SELECT geo_id FROM division_cbsas)
  ORDER BY
    CASE WHEN geo_id = (SELECT target_geo_id FROM target_cbsa) THEN 0 ELSE 1 END,
    ABS(pop_total - (SELECT pop_total FROM target_pop)) NULLS LAST
  LIMIT 6
),
metric_long AS (
  SELECT 'heatmap_peer_cbsa_profile'::VARCHAR AS question_id, geo_level, geo_id, geo_name, 'latest CBSA profile'::VARCHAR AS time_window, 1 AS metric_order, 'pop_growth_5yr'::VARCHAR AS metric_id, 'Population growth (5yr)'::VARCHAR AS metric_label, 'Growth'::VARCHAR AS metric_group, pop_growth_5yr::DOUBLE AS metric_value, 'higher_is_better'::VARCHAR AS direction, highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) AS display_flag FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 2, 'pct_ba_plus', 'Adults with BA+', 'Talent', pct_ba_plus::DOUBLE, 'higher_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 3, 'median_hh_income', 'Median household income', 'Prosperity', median_hh_income::DOUBLE, 'higher_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 4, 'jobs_to_pop_ratio', 'Jobs-to-population ratio', 'Labor', jobs_to_pop_ratio::DOUBLE, 'higher_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 5, 'pct_unemployment_rate', 'Unemployment rate', 'Labor', pct_unemployment_rate::DOUBLE, 'lower_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 6, 'pct_rent_burden_30plus', 'Rent-burdened renter share', 'Affordability', pct_rent_burden_30plus::DOUBLE, 'lower_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 7, 'value_to_income', 'Home value-to-income', 'Affordability', value_to_income::DOUBLE, 'lower_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 8, 'permits_per_1000_population', 'Permits per 1,000 residents', 'Supply', permits_per_1000_population::DOUBLE, 'higher_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
  UNION ALL
  SELECT 'heatmap_peer_cbsa_profile', geo_level, geo_id, geo_name, 'latest CBSA profile', 9, 'mean_travel_time', 'Mean commute time', 'Access', mean_travel_time::DOUBLE, 'lower_is_better', highlight_flag, geo_id IN (SELECT geo_id FROM display_cbsas) FROM cbsa_base
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
  'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + gold.transport_built_form_wide'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  metric_group,
  direction,
  highlight_flag,
  display_flag,
  metric_order,
  CASE
    WHEN metric_value IS NULL THEN NULL
    WHEN metric_id = 'median_hh_income' THEN '$' || CAST(ROUND(metric_value, 0) AS VARCHAR)
    WHEN metric_id IN ('pop_growth_5yr', 'pct_ba_plus', 'jobs_to_pop_ratio', 'pct_unemployment_rate', 'pct_rent_burden_30plus') THEN CAST(ROUND(metric_value * 100, 1) AS VARCHAR) || '%'
    ELSE CAST(ROUND(metric_value, 1) AS VARCHAR)
  END AS value_label,
  'Percentiles normalize against all CBSAs; displayed rows are Wilmington plus the closest South Atlantic population peers.'::VARCHAR AS note
FROM metric_long
ORDER BY display_flag DESC, highlight_flag DESC, geo_name, metric_order;
