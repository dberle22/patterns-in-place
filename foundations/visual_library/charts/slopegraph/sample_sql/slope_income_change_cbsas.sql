WITH endpoints AS (
  SELECT
    a.geo_id,
    MAX(CASE WHEN a.year = 2013 THEN a.rpp_real_pc_income END) AS start_value,
    MAX(CASE WHEN a.year = 2023 THEN a.rpp_real_pc_income END) AS end_value
  FROM metro_deep_dive.gold.affordability_wide a
  WHERE a.geo_level = 'cbsa'
    AND a.year IN (2013, 2023)
    AND a.rpp_real_pc_income IS NOT NULL
  GROUP BY 1
),
selected_geos AS (
  SELECT
    geo_id,
    ROW_NUMBER() OVER (ORDER BY ABS(end_value - start_value) DESC, geo_id) AS display_rank
  FROM endpoints
  WHERE start_value IS NOT NULL
    AND end_value IS NOT NULL
    AND start_value > 0
    AND end_value > 0
  QUALIFY display_rank <= 12
)
SELECT
  'slope_income_change_cbsas' AS question_id,
  a.geo_level,
  a.geo_id,
  a.geo_name,
  a.year AS period,
  'rpp_real_pc_income' AS metric_id,
  'Real Per Capita Income' AS metric_label,
  a.rpp_real_pc_income::DOUBLE AS metric_value,
  'gold.affordability_wide' AS source,
  '2026-04-16' AS vintage,
  'National CBSA top movers' AS "group",
  a.geo_id = '48900' AS highlight_flag,
  NULL::VARCHAR AS benchmark_label,
  NULL::DOUBLE AS rank,
  'Top movers selected by absolute 2013-2023 change in real per-capita income.' AS note
FROM metro_deep_dive.gold.affordability_wide a
JOIN selected_geos s
  ON a.geo_id = s.geo_id
WHERE a.geo_level = 'cbsa'
  AND a.year IN (2013, 2023)
  AND a.rpp_real_pc_income IS NOT NULL
ORDER BY s.display_rank, a.geo_name, a.year;
