-- Canonical line chart sample queries from gold-layer marts.
-- Includes:
--   1. line_test_single: Wilmington, NC population trend.
--   2. line_test_multi: Wilmington, NC per-capita income vs Raleigh and Charlotte.
--   3. line_test_indexed: Indexed per-capita income comparison with 2013 = 100.

WITH selected_geos AS (
  SELECT '48900'::VARCHAR AS geo_id, TRUE AS highlight_flag UNION ALL
  SELECT '16740'::VARCHAR AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '39580'::VARCHAR AS geo_id, FALSE AS highlight_flag
),
division_lookup AS (
  SELECT
    x.cbsa_code AS geo_id,
    MIN(s.census_division) AS census_division
  FROM metro_deep_dive.silver.xwalk_cbsa_county x
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  GROUP BY 1
),
single_population AS (
  SELECT
    'line_test_single'::VARCHAR AS question_id,
    p.geo_level,
    p.geo_id,
    p.geo_name,
    p.year AS period,
    'level'::VARCHAR AS time_window,
    'pop_total'::VARCHAR AS metric_id,
    'Population'::VARCHAR AS metric_label,
    p.pop_total::DOUBLE AS metric_value,
    'gold.population_demographics'::VARCHAR AS source,
    '2026-04-15'::VARCHAR AS vintage,
    NULL::VARCHAR AS "group",
    TRUE AS highlight_flag,
    NULL::DOUBLE AS benchmark_value,
    NULL::INTEGER AS index_base_period,
    NULL::VARCHAR AS note
  FROM metro_deep_dive.gold.population_demographics p
  WHERE p.geo_level = 'cbsa'
    AND p.geo_id = '48900'
    AND p.year BETWEEN 2013 AND 2023
    AND p.pop_total IS NOT NULL
),
multi_income AS (
  SELECT
    'line_test_multi'::VARCHAR AS question_id,
    i.geo_level,
    i.geo_id,
    i.geo_name,
    i.year AS period,
    'level'::VARCHAR AS time_window,
    'calc_income_pc'::VARCHAR AS metric_id,
    'Per capita income'::VARCHAR AS metric_label,
    i.calc_income_pc::DOUBLE AS metric_value,
    'gold.economics_income_wide'::VARCHAR AS source,
    '2026-04-15'::VARCHAR AS vintage,
    d.census_division AS "group",
    g.highlight_flag,
    NULL::DOUBLE AS benchmark_value,
    NULL::INTEGER AS index_base_period,
    NULL::VARCHAR AS note
  FROM metro_deep_dive.gold.economics_income_wide i
  JOIN selected_geos g
    ON i.geo_id = g.geo_id
  LEFT JOIN division_lookup d
    ON i.geo_id = d.geo_id
  WHERE i.geo_level = 'cbsa'
    AND i.year BETWEEN 2013 AND 2023
    AND i.calc_income_pc IS NOT NULL
),
indexed_income AS (
  SELECT
    'line_test_indexed'::VARCHAR AS question_id,
    i.geo_level,
    i.geo_id,
    i.geo_name,
    i.year AS period,
    'indexed'::VARCHAR AS time_window,
    'calc_income_pc'::VARCHAR AS metric_id,
    'Per capita income'::VARCHAR AS metric_label,
    i.calc_income_pc::DOUBLE AS metric_value,
    'gold.economics_income_wide'::VARCHAR AS source,
    '2026-04-15'::VARCHAR AS vintage,
    d.census_division AS "group",
    g.highlight_flag,
    NULL::DOUBLE AS benchmark_value,
    2013::INTEGER AS index_base_period,
    NULL::VARCHAR AS note
  FROM metro_deep_dive.gold.economics_income_wide i
  JOIN selected_geos g
    ON i.geo_id = g.geo_id
  LEFT JOIN division_lookup d
    ON i.geo_id = d.geo_id
  WHERE i.geo_level = 'cbsa'
    AND i.year BETWEEN 2013 AND 2023
    AND i.calc_income_pc IS NOT NULL
)
SELECT *
FROM single_population
UNION ALL
SELECT *
FROM multi_income
UNION ALL
SELECT *
FROM indexed_income
ORDER BY question_id, geo_id, period;
