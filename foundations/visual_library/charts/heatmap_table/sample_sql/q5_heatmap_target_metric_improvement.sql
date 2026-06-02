-- Q5: Which metrics improved most in the target CBSA over time?

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
target_years AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year,
    p.pop_growth_5yr,
    a.median_hh_income,
    p.pct_ba_plus,
    l.pct_unemployment_rate,
    a.pct_rent_burden_30plus,
    a.value_to_income,
    a.permits_per_1000_population
  FROM gold.affordability_wide a
  LEFT JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN gold.economics_labor_wide l
    ON a.geo_level = l.geo_level
   AND a.geo_id = l.geo_id
   AND a.year = l.year
  WHERE a.geo_level = 'cbsa'
    AND a.geo_id = (SELECT target_geo_id FROM target_cbsa)
    AND a.year BETWEEN 2013 AND 2023
),
metric_long AS (
  SELECT 'heatmap_target_metric_improvement'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2013-2023 metric history'::VARCHAR AS time_window, year::VARCHAR AS period, 1 AS metric_order, 'pop_growth_5yr'::VARCHAR AS metric_id, 'Population growth (5yr)'::VARCHAR AS metric_label, 'Growth'::VARCHAR AS metric_group, pop_growth_5yr::DOUBLE AS metric_value, 'higher_is_better'::VARCHAR AS direction FROM target_years
  UNION ALL
  SELECT 'heatmap_target_metric_improvement', geo_level, geo_id, geo_name, '2013-2023 metric history', year::VARCHAR, 2, 'median_hh_income', 'Median household income', 'Prosperity', median_hh_income::DOUBLE, 'higher_is_better' FROM target_years
  UNION ALL
  SELECT 'heatmap_target_metric_improvement', geo_level, geo_id, geo_name, '2013-2023 metric history', year::VARCHAR, 3, 'pct_ba_plus', 'Adults with BA+', 'Talent', pct_ba_plus::DOUBLE, 'higher_is_better' FROM target_years
  UNION ALL
  SELECT 'heatmap_target_metric_improvement', geo_level, geo_id, geo_name, '2013-2023 metric history', year::VARCHAR, 4, 'pct_unemployment_rate', 'Unemployment rate', 'Labor', pct_unemployment_rate::DOUBLE, 'lower_is_better' FROM target_years
  UNION ALL
  SELECT 'heatmap_target_metric_improvement', geo_level, geo_id, geo_name, '2013-2023 metric history', year::VARCHAR, 5, 'pct_rent_burden_30plus', 'Rent-burdened renter share', 'Affordability', pct_rent_burden_30plus::DOUBLE, 'lower_is_better' FROM target_years
  UNION ALL
  SELECT 'heatmap_target_metric_improvement', geo_level, geo_id, geo_name, '2013-2023 metric history', year::VARCHAR, 6, 'value_to_income', 'Home value-to-income', 'Affordability', value_to_income::DOUBLE, 'lower_is_better' FROM target_years
  UNION ALL
  SELECT 'heatmap_target_metric_improvement', geo_level, geo_id, geo_name, '2013-2023 metric history', year::VARCHAR, 7, 'permits_per_1000_population', 'Permits per 1,000 residents', 'Supply', permits_per_1000_population::DOUBLE, 'higher_is_better' FROM target_years
),
scored AS (
  SELECT
    *,
    FIRST_VALUE(metric_value) OVER (PARTITION BY metric_id ORDER BY period) AS start_value,
    FIRST_VALUE(metric_value) OVER (PARTITION BY metric_id ORDER BY period DESC) AS end_value
  FROM metric_long
),
improvement AS (
  SELECT
    *,
    CASE
      WHEN direction = 'lower_is_better' THEN start_value - end_value
      ELSE end_value - start_value
    END AS improvement_score
  FROM scored
)
SELECT
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  period,
  metric_id,
  metric_label,
  metric_value,
  'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  metric_group,
  direction,
  TRUE AS highlight_flag,
  metric_order,
  improvement_score AS row_order,
  CASE
    WHEN metric_value IS NULL THEN NULL
    WHEN metric_id = 'median_hh_income' THEN '$' || CAST(ROUND(metric_value, 0) AS VARCHAR)
    WHEN metric_id IN ('pop_growth_5yr', 'pct_ba_plus', 'pct_unemployment_rate', 'pct_rent_burden_30plus') THEN CAST(ROUND(metric_value * 100, 1) AS VARCHAR) || '%'
    ELSE CAST(ROUND(metric_value, 1) AS VARCHAR)
  END AS value_label,
  'Rows are ordered by 2013-2023 improvement after applying metric direction; fill normalizes each metric over the target CBSA history.'::VARCHAR AS note
FROM improvement
ORDER BY row_order DESC NULLS LAST, metric_order, period;
