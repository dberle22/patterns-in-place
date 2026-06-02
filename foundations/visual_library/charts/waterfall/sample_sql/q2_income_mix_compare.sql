WITH target AS (
  SELECT '48900'::VARCHAR AS geo_id
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.economics_income_wide
  WHERE geo_level = 'cbsa'
    AND pi_total IS NOT NULL
    AND pi_wages_salary IS NOT NULL
),
target_region AS (
  SELECT f.census_region
  FROM foundation.cbsa_features f
  JOIN latest_year y
    ON f.year = y.year
  WHERE f.cbsa_code = (SELECT geo_id FROM target)
),
target_row AS (
  SELECT
    i.geo_level,
    i.geo_id,
    i.geo_name,
    i.year,
    i.pi_total,
    i.pi_wages_salary,
    i.pi_total - i.pi_wages_salary AS pi_nonwage,
    i.pop_total,
    'Target CBSA' AS benchmark_label,
    1 AS panel_order
  FROM gold.economics_income_wide i
  JOIN latest_year y
    ON i.year = y.year
  WHERE i.geo_level = 'cbsa'
    AND i.geo_id = (SELECT geo_id FROM target)
),
region_row AS (
  SELECT
    'cbsa' AS geo_level,
    'south_benchmark' AS geo_id,
    'South regional CBSA benchmark' AS geo_name,
    y.year,
    SUM(i.pi_total) AS pi_total,
    SUM(i.pi_wages_salary) AS pi_wages_salary,
    SUM(i.pi_total - i.pi_wages_salary) AS pi_nonwage,
    SUM(i.pop_total) AS pop_total,
    'South regional benchmark' AS benchmark_label,
    2 AS panel_order
  FROM gold.economics_income_wide i
  JOIN foundation.cbsa_features f
    ON i.geo_id = f.cbsa_code
   AND i.year = f.year
  JOIN latest_year y
    ON i.year = y.year
  WHERE i.geo_level = 'cbsa'
    AND f.census_region = (SELECT census_region FROM target_region)
    AND i.pi_total IS NOT NULL
    AND i.pi_wages_salary IS NOT NULL
    AND i.pop_total IS NOT NULL
  GROUP BY y.year
),
combined AS (
  SELECT * FROM target_row
  UNION ALL
  SELECT * FROM region_row
)
SELECT
  'waterfall_income_mix_compare' AS question_id,
  geo_level,
  geo_id,
  geo_name,
  CAST(year AS VARCHAR) || ' per-capita mix' AS time_window,
  'Personal income per capita' AS total_label,
  'wages_salary' AS component_id,
  'Wages and salaries' AS component_label,
  pi_wages_salary / NULLIF(pop_total, 0) AS component_value,
  'gold.economics_income_wide; foundation.cbsa_features' AS source,
  '2026-04-16' AS vintage,
  NULL::INTEGER AS start_period,
  year AS end_period,
  NULL::DOUBLE AS component_delta,
  '$ per resident' AS unit_label,
  'Earnings' AS component_group,
  benchmark_label,
  benchmark_label = 'Target CBSA' AS highlight_flag,
  1 AS sort_order,
  'Regional benchmark is a population-weighted South CBSA aggregate in the latest income year.' AS note
FROM combined

UNION ALL

SELECT
  'waterfall_income_mix_compare',
  geo_level,
  geo_id,
  geo_name,
  CAST(year AS VARCHAR) || ' per-capita mix',
  'Personal income per capita',
  'nonwage_income',
  'Non-wage income',
  pi_nonwage / NULLIF(pop_total, 0),
  'gold.economics_income_wide; foundation.cbsa_features',
  '2026-04-16',
  NULL::INTEGER,
  year,
  NULL::DOUBLE,
  '$ per resident',
  'Other income',
  benchmark_label,
  benchmark_label = 'Target CBSA',
  2,
  'Non-wage income is calculated as total personal income minus wages and salaries.'
FROM combined
ORDER BY benchmark_label, sort_order;
