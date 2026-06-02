WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year
    FROM gold.affordability_wide
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM gold.population_demographics
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM gold.economics_income_wide
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM gold.economics_labor_wide
    WHERE geo_level = 'cbsa'
  )
),
cbsa_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    a.median_hh_income,
    p.pct_ba_plus,
    l.pct_unemployment_rate,
    a.pct_rent_burden_30plus,
    a.permits_per_1000_population,
    p.pop_growth_5yr,
    i.income_pc_growth_5yr,
    l.lfpr_growth_5yr,
    a.geo_id = (SELECT target_geo_id FROM target_cbsa) AS highlight_flag
  FROM gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  LEFT JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN gold.economics_income_wide i
    ON a.geo_level = i.geo_level
   AND a.geo_id = i.geo_id
   AND a.year = i.year
  LEFT JOIN gold.economics_labor_wide l
    ON a.geo_level = l.geo_level
   AND a.geo_id = l.geo_id
   AND a.year = l.year
  WHERE a.geo_level = 'cbsa'
),
canonical_metrics AS (
  SELECT 'strip_level_vs_growth_compare'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2023 levels'::VARCHAR AS time_window, 1 AS metric_order, 'median_hh_income'::VARCHAR AS metric_id, 'Median household income'::VARCHAR AS metric_label, 'Prosperity'::VARCHAR AS metric_group, median_hh_income::DOUBLE AS metric_value, 'higher_is_better'::VARCHAR AS direction, highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_level_vs_growth_compare', geo_level, geo_id, geo_name, '2023 levels', 2, 'pct_ba_plus', 'Adults with BA+', 'Talent', pct_ba_plus::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_level_vs_growth_compare', geo_level, geo_id, geo_name, '2023 levels', 3, 'pct_unemployment_rate', 'Unemployment rate', 'Labor', pct_unemployment_rate::DOUBLE, 'lower_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_level_vs_growth_compare', geo_level, geo_id, geo_name, '2023 levels', 4, 'pct_rent_burden_30plus', 'Rent-burdened renter share', 'Affordability', pct_rent_burden_30plus::DOUBLE, 'lower_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_level_vs_growth_compare', geo_level, geo_id, geo_name, '2023 levels', 5, 'permits_per_1000_population', 'Permits per 1,000 residents', 'Supply', permits_per_1000_population::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_level_vs_growth_compare', geo_level, geo_id, geo_name, '2018-2023 growth', 1, 'pop_growth_5yr', 'Population growth (5yr)', 'Growth', pop_growth_5yr::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_level_vs_growth_compare', geo_level, geo_id, geo_name, '2018-2023 growth', 2, 'income_pc_growth_5yr', 'Personal income growth (5yr)', 'Growth', income_pc_growth_5yr::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_level_vs_growth_compare', geo_level, geo_id, geo_name, '2018-2023 growth', 3, 'lfpr_growth_5yr', 'Labor-force participation growth (5yr)', 'Growth', lfpr_growth_5yr::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base
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
  'gold.affordability_wide + gold.population_demographics + gold.economics_income_wide + gold.economics_labor_wide'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  metric_group,
  direction,
  highlight_flag,
  metric_order,
  'Percentiles are computed within each time window across all CBSAs in the latest common year.'::VARCHAR AS note
FROM canonical_metrics
ORDER BY time_window, metric_order, geo_id;
