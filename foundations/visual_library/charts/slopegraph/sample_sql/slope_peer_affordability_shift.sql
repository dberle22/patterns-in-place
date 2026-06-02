WITH selected_geos AS (
  SELECT '48900' AS geo_id, TRUE AS highlight_flag UNION ALL
  SELECT '16740' AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '39580' AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '20500' AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '34820' AS geo_id, FALSE AS highlight_flag UNION ALL
  SELECT '49180' AS geo_id, FALSE AS highlight_flag
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
    AND a.year IN (2019, 2024)
    AND a.value_to_income IS NOT NULL
)
SELECT
  'slope_peer_affordability_shift' AS question_id,
  geo_level,
  geo_id,
  geo_name,
  year AS period,
  'value_to_income' AS metric_id,
  'Home Value-to-Income Ratio' AS metric_label,
  value_to_income::DOUBLE AS metric_value,
  'gold.affordability_wide' AS source,
  '2026-04-16' AS vintage,
  'Selected Carolina and coastal peers' AS "group",
  highlight_flag,
  NULL::VARCHAR AS benchmark_label,
  RANK() OVER (PARTITION BY year ORDER BY value_to_income ASC, geo_name)::DOUBLE AS rank,
  'Lower rank indicates a lower home value-to-income ratio within the selected peer set.' AS note
FROM peer_values
ORDER BY geo_name, year;
