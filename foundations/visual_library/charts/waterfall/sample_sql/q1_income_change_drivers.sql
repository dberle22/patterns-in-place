WITH target AS (
  SELECT '48900'::VARCHAR AS geo_id
),
endpoints AS (
  SELECT
    geo_level,
    geo_id,
    geo_name,
    year,
    pi_total,
    pi_wages_salary,
    pi_total - pi_wages_salary AS pi_nonwage
  FROM gold.economics_income_wide
  WHERE geo_level = 'cbsa'
    AND geo_id = (SELECT geo_id FROM target)
    AND year IN (2013, 2023)
    AND pi_total IS NOT NULL
    AND pi_wages_salary IS NOT NULL
),
wide AS (
  SELECT
    MAX(geo_level) AS geo_level,
    geo_id,
    MAX(geo_name) AS geo_name,
    MAX(CASE WHEN year = 2013 THEN pi_total END) AS total_start,
    MAX(CASE WHEN year = 2023 THEN pi_total END) AS total_end,
    MAX(CASE WHEN year = 2013 THEN pi_wages_salary END) AS wages_start,
    MAX(CASE WHEN year = 2023 THEN pi_wages_salary END) AS wages_end,
    MAX(CASE WHEN year = 2013 THEN pi_nonwage END) AS nonwage_start,
    MAX(CASE WHEN year = 2023 THEN pi_nonwage END) AS nonwage_end
  FROM endpoints
  GROUP BY geo_id
)
SELECT
  'waterfall_income_change_drivers' AS question_id,
  geo_level,
  geo_id,
  geo_name,
  '2013-2023 change' AS time_window,
  'Net personal income change' AS total_label,
  'wages_salary' AS component_id,
  'Wages and salaries' AS component_label,
  wages_end / 1000000.0 AS component_value,
  'gold.economics_income_wide' AS source,
  '2026-04-16' AS vintage,
  2013 AS start_period,
  2023 AS end_period,
  (wages_end - wages_start) / 1000000.0 AS component_delta,
  '$ millions' AS unit_label,
  'Earnings' AS component_group,
  NULL::VARCHAR AS benchmark_label,
  TRUE AS highlight_flag,
  1 AS sort_order,
  'Non-wage income is calculated as total personal income minus wages and salaries so components add to the total change.' AS note
FROM wide

UNION ALL

SELECT
  'waterfall_income_change_drivers',
  geo_level,
  geo_id,
  geo_name,
  '2013-2023 change',
  'Net personal income change',
  'nonwage_income',
  'Non-wage income',
  nonwage_end / 1000000.0,
  'gold.economics_income_wide',
  '2026-04-16',
  2013,
  2023,
  (nonwage_end - nonwage_start) / 1000000.0,
  '$ millions',
  'Other income',
  NULL::VARCHAR,
  TRUE,
  2,
  'Non-wage income includes proprietors, dividends, transfers, and other personal income not broken out in this wide table.'
FROM wide
ORDER BY sort_order;
