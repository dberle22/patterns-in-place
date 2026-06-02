-- Q4: Are Sweet Spot markets outliers on affordability relative to all CBSAs?

WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM foundation.cbsa_features
  WHERE median_home_value IS NOT NULL
),
cbsa_base AS (
  SELECT
    f.*,
    f.cbsa_type = 'Metro Area'
      AND f.national_pop_growth_5yr_pctl >= 0.90
      AND f.national_home_value_pctl <= 0.85 AS sweet_spot_flag
  FROM foundation.cbsa_features f
  WHERE f.year = (SELECT year FROM latest_year)
    AND f.primary_state_abbr NOT IN ('AK', 'HI', 'PR')
    AND f.median_home_value IS NOT NULL
)
SELECT
  'boxplot_sweet_spot_affordability_outliers'::VARCHAR AS question_id,
  'cbsa'::VARCHAR AS geo_level,
  cbsa_code AS geo_id,
  cbsa_name AS geo_name,
  '2024_snapshot'::VARCHAR AS time_window,
  'median_home_value'::VARCHAR AS metric_id,
  'Median home value ($)'::VARCHAR AS metric_label,
  median_home_value::DOUBLE AS metric_value,
  cbsa_type AS "group",
  sweet_spot_flag AS highlight_flag,
  sweet_spot_flag AND national_pop_growth_5yr_pctl >= 0.95 AS label_flag,
  pop_total::DOUBLE AS weight_value,
  NULL::DOUBLE AS benchmark_value,
  'foundation.cbsa_features'::VARCHAR AS source,
  CAST(year AS VARCHAR) AS vintage,
  'Sweet Spot proxy: metro areas with 5-year population-growth percentile >= 90 and home-value percentile <= 85.'::VARCHAR AS note
FROM cbsa_base;
