WITH target_cbsa AS (
  SELECT '48900' AS target_geo_id
),
target_counties AS (
  SELECT DISTINCT county_geoid AS geo_id
  FROM metro_deep_dive.silver.xwalk_cbsa_county
  WHERE cbsa_code = (SELECT target_geo_id FROM target_cbsa)
),
endpoints AS (
  SELECT
    a.geo_id,
    MAX(CASE WHEN a.year = 2018 THEN a.pct_rent_burden_30plus END) AS start_value,
    MAX(CASE WHEN a.year = 2023 THEN a.pct_rent_burden_30plus END) AS end_value
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN target_counties c
    ON a.geo_id = c.geo_id
  WHERE a.geo_level = 'county'
    AND a.year IN (2018, 2023)
    AND a.pct_rent_burden_30plus IS NOT NULL
  GROUP BY 1
),
selected_geos AS (
  SELECT geo_id
  FROM endpoints
  WHERE start_value IS NOT NULL
    AND end_value IS NOT NULL
)
SELECT
  'slope_county_rent_burden' AS question_id,
  a.geo_level,
  a.geo_id,
  a.geo_name,
  a.year AS period,
  'pct_rent_burden_30plus' AS metric_id,
  'Rent-Burdened Renter Households' AS metric_label,
  a.pct_rent_burden_30plus::DOUBLE AS metric_value,
  'gold.affordability_wide' AS source,
  '2026-04-16' AS vintage,
  'Wilmington, NC counties' AS "group",
  FALSE AS highlight_flag,
  NULL::VARCHAR AS benchmark_label,
  NULL::DOUBLE AS rank,
  'Rent burden is the share of renter households spending at least 30 percent of income on rent.' AS note
FROM metro_deep_dive.gold.affordability_wide a
JOIN selected_geos s
  ON a.geo_id = s.geo_id
WHERE a.geo_level = 'county'
  AND a.year IN (2018, 2023)
  AND a.pct_rent_burden_30plus IS NOT NULL
ORDER BY a.geo_name, a.year;
