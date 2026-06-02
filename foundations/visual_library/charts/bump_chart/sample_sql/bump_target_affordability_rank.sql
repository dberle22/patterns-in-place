-- Q2: Did the target CBSA improve in affordability rank since 2018?

WITH selected_geos AS (
  SELECT '48900'::VARCHAR AS geo_id, TRUE AS highlight_flag UNION ALL
  SELECT '16740'::VARCHAR AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '39580'::VARCHAR AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '20500'::VARCHAR AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '34820'::VARCHAR AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '49180'::VARCHAR AS geo_id, FALSE AS highlight_flag
),
peer_values AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year,
    a.value_to_income,
    g.highlight_flag
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN selected_geos g
    ON a.geo_id = g.geo_id
  WHERE a.geo_level = 'cbsa'
    AND a.year BETWEEN 2018 AND 2024
    AND a.value_to_income IS NOT NULL
)
SELECT
  'bump_target_affordability_rank'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  year AS period,
  'value_to_income'::VARCHAR AS metric_id,
  'Home Value-to-Income Ratio'::VARCHAR AS metric_label,
  value_to_income::DOUBLE AS metric_value,
  'gold.affordability_wide'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  'Selected Carolina and coastal peer CBSAs'::VARCHAR AS "group",
  highlight_flag,
  TRUE AS peer_flag,
  ROW_NUMBER() OVER (PARTITION BY year ORDER BY value_to_income ASC, geo_name, geo_id)::DOUBLE AS rank,
  'Rank 1 is the lowest home value-to-income ratio in the selected peer set.'::VARCHAR AS note
FROM peer_values
ORDER BY geo_name, year;
