-- Q5: How does the distribution of income growth differ by CBSA type?

WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'cbsa'
    AND income_pc_cagr_5yr IS NOT NULL
),
cbsa_type_lookup AS (
  SELECT
    cbsa_code,
    cbsa_type,
    primary_state_abbr
  FROM foundation.cbsa_features
  WHERE year = (SELECT year FROM latest_year)
)
SELECT
  'boxplot_income_growth_by_cbsa_type'::VARCHAR AS question_id,
  a.geo_level,
  a.geo_id,
  a.geo_name,
  '2018_to_2023_cagr'::VARCHAR AS time_window,
  'income_pc_cagr_5yr'::VARCHAR AS metric_id,
  'Per-capita income CAGR, 5-year (%)'::VARCHAR AS metric_label,
  a.income_pc_cagr_5yr::DOUBLE AS metric_value,
  l.cbsa_type AS "group",
  a.geo_id = '48900' AS highlight_flag,
  a.geo_id = '48900' AS label_flag,
  NULL::DOUBLE AS weight_value,
  NULL::DOUBLE AS benchmark_value,
  'gold.affordability_wide + foundation.cbsa_features'::VARCHAR AS source,
  CAST(a.year AS VARCHAR) AS vintage,
  'CBSA types are Metro Area and Micro Area; highlighted point is Wilmington, NC.'::VARCHAR AS note
FROM gold.affordability_wide a
JOIN cbsa_type_lookup l
  ON a.geo_id = l.cbsa_code
WHERE a.geo_level = 'cbsa'
  AND a.year = (SELECT year FROM latest_year)
  AND a.income_pc_cagr_5yr IS NOT NULL
  AND l.primary_state_abbr NOT IN ('AK', 'HI', 'PR');
