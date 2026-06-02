-- Q3: Are top performers stable or rotating for 5-year income growth?

WITH cbsa_years AS (
  SELECT
    i.geo_level,
    i.geo_id,
    i.geo_name,
    i.year,
    i.income_pc_growth_5yr
  FROM metro_deep_dive.gold.economics_income_wide i
  WHERE i.geo_level = 'cbsa'
    AND i.year BETWEEN 2018 AND 2024
    AND i.income_pc_growth_5yr IS NOT NULL
)
SELECT
  'bump_top_performer_stability'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  year AS period,
  'income_pc_growth_5yr'::VARCHAR AS metric_id,
  '5-Year Per-Capita Income Growth'::VARCHAR AS metric_label,
  income_pc_growth_5yr::DOUBLE AS metric_value,
  'gold.economics_income_wide'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  'All CBSAs'::VARCHAR AS "group",
  geo_id = '48900' AS highlight_flag,
  FALSE AS peer_flag,
  NULL::DOUBLE AS rank,
  'Ranks are computed across all CBSAs for each year; displayed entities are latest-year top performers.'::VARCHAR AS note
FROM cbsa_years
ORDER BY geo_name, year;
