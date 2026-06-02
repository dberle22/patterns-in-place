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
    p.pop_growth_5yr,
    a.median_hh_income,
    p.pct_ba_plus,
    l.pct_unemployment_rate,
    a.pct_rent_burden_30plus,
    a.permits_per_1000_population,
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
  WHERE a.geo_level = 'cbsa'
),
canonical_metrics AS (
  SELECT 'strip_score_driver_scan'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2023 profile vs CBSA median'::VARCHAR AS time_window, 1 AS metric_order, 'pop_growth_5yr'::VARCHAR AS metric_id, 'Population growth (5yr)'::VARCHAR AS metric_label, 'Growth'::VARCHAR AS metric_group, pop_growth_5yr::DOUBLE AS metric_value, 'higher_is_better'::VARCHAR AS direction, highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_score_driver_scan', geo_level, geo_id, geo_name, '2023 profile vs CBSA median', 2, 'median_hh_income', 'Median household income', 'Prosperity', median_hh_income::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_score_driver_scan', geo_level, geo_id, geo_name, '2023 profile vs CBSA median', 3, 'pct_ba_plus', 'Adults with BA+', 'Talent', pct_ba_plus::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_score_driver_scan', geo_level, geo_id, geo_name, '2023 profile vs CBSA median', 4, 'pct_unemployment_rate', 'Unemployment rate', 'Labor', pct_unemployment_rate::DOUBLE, 'lower_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_score_driver_scan', geo_level, geo_id, geo_name, '2023 profile vs CBSA median', 5, 'pct_rent_burden_30plus', 'Rent-burdened renter share', 'Affordability', pct_rent_burden_30plus::DOUBLE, 'lower_is_better', highlight_flag
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_score_driver_scan', geo_level, geo_id, geo_name, '2023 profile vs CBSA median', 6, 'permits_per_1000_population', 'Permits per 1,000 residents', 'Supply', permits_per_1000_population::DOUBLE, 'higher_is_better', highlight_flag
  FROM cbsa_base
),
metric_benchmarks AS (
  SELECT
    metric_id,
    MEDIAN(metric_value) AS benchmark_value
  FROM canonical_metrics
  GROUP BY 1
)
SELECT
  m.question_id,
  m.geo_level,
  m.geo_id,
  m.geo_name,
  m.time_window,
  m.metric_id,
  m.metric_label,
  m.metric_value,
  'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  m.metric_group,
  m.direction,
  b.benchmark_value::DOUBLE AS benchmark_value,
  'CBSA median'::VARCHAR AS benchmark_label,
  m.highlight_flag,
  m.metric_order,
  'Benchmark marker shows the national CBSA median for each KPI.'::VARCHAR AS note
FROM canonical_metrics m
LEFT JOIN metric_benchmarks b
  ON m.metric_id = b.metric_id
ORDER BY m.metric_order, m.geo_id;
