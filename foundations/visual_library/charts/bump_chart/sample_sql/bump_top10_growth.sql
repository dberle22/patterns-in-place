-- Q1: Which CBSAs moved into the top 10 for 5-year population growth?

WITH cbsa_years AS (
  SELECT
    p.geo_level,
    p.geo_id,
    p.geo_name,
    p.year,
    p.pop_growth_5yr
  FROM metro_deep_dive.gold.population_demographics p
  WHERE p.geo_level = 'cbsa'
    AND p.year BETWEEN 2018 AND 2024
    AND p.pop_growth_5yr IS NOT NULL
)
SELECT
  'bump_top10_growth'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  year AS period,
  'pop_growth_5yr'::VARCHAR AS metric_id,
  '5-Year Population Growth'::VARCHAR AS metric_label,
  pop_growth_5yr::DOUBLE AS metric_value,
  'gold.population_demographics'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  'All CBSAs'::VARCHAR AS "group",
  geo_id = '48900' AS highlight_flag,
  FALSE AS peer_flag,
  NULL::DOUBLE AS rank,
  'Ranks are computed across all CBSAs for each year; displayed entities are selected from the latest-year top 10.'::VARCHAR AS note
FROM cbsa_years
ORDER BY geo_name, year;
