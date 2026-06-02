WITH target_zctas AS (
  SELECT DISTINCT zip_geoid AS geo_id
  FROM metro_deep_dive.silver.xwalk_zcta_cbsa
  WHERE cbsa_geoid = '48900'
),
endpoints AS (
  SELECT
    a.geo_id,
    MAX(CASE WHEN a.year = 2019 THEN a.value_to_income END) AS start_value,
    MAX(CASE WHEN a.year = 2024 THEN a.value_to_income END) AS end_value
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN target_zctas z
    ON a.geo_id = z.geo_id
  WHERE a.geo_level = 'zcta'
    AND a.year IN (2019, 2024)
    AND a.value_to_income IS NOT NULL
  GROUP BY 1
),
selected_geos AS (
  SELECT
    geo_id,
    ROW_NUMBER() OVER (ORDER BY ABS(end_value - start_value) DESC, geo_id) AS display_rank
  FROM endpoints
  WHERE start_value IS NOT NULL
    AND end_value IS NOT NULL
  QUALIFY display_rank <= 18
)
SELECT
  'slope_zcta_value_to_income_change' AS question_id,
  a.geo_level,
  a.geo_id,
  a.geo_name,
  a.year AS period,
  'value_to_income' AS metric_id,
  'Home Value-to-Income Ratio' AS metric_label,
  a.value_to_income::DOUBLE AS metric_value,
  'gold.affordability_wide' AS source,
  '2026-04-16' AS vintage,
  'ZCTAs within Wilmington, NC CBSA' AS "group",
  FALSE AS highlight_flag,
  NULL::VARCHAR AS benchmark_label,
  NULL::DOUBLE AS rank,
  'Top ZCTA movers selected by absolute 2019-2024 change in home value-to-income ratio.' AS note
FROM metro_deep_dive.gold.affordability_wide a
JOIN selected_geos s
  ON a.geo_id = s.geo_id
WHERE a.geo_level = 'zcta'
  AND a.year IN (2019, 2024)
  AND a.value_to_income IS NOT NULL
ORDER BY s.display_rank, a.geo_name, a.year;
