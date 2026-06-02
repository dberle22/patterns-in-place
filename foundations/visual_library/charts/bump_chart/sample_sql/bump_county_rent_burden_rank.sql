-- Q4: Which counties within the CBSA rose fastest in rent-burden rank?

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
target_counties AS (
  SELECT DISTINCT county_geoid AS geo_id
  FROM metro_deep_dive.silver.xwalk_cbsa_county
  WHERE cbsa_code = (SELECT target_geo_id FROM target_cbsa)
),
county_values AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year,
    a.pct_rent_burden_30plus,
    ROW_NUMBER() OVER (PARTITION BY a.year ORDER BY a.pct_rent_burden_30plus DESC, a.geo_name, a.geo_id) AS rent_burden_rank
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN target_counties c
    ON a.geo_id = c.geo_id
  WHERE a.geo_level = 'county'
    AND a.year BETWEEN 2013 AND 2024
    AND a.pct_rent_burden_30plus IS NOT NULL
),
endpoints AS (
  SELECT
    geo_id,
    MAX(CASE WHEN year = 2013 THEN rent_burden_rank END) AS start_rank,
    MAX(CASE WHEN year = 2024 THEN rent_burden_rank END) AS end_rank
  FROM county_values
  GROUP BY 1
),
rank_movers AS (
  SELECT
    geo_id,
    start_rank - end_rank AS rank_change,
    ROW_NUMBER() OVER (ORDER BY start_rank - end_rank DESC NULLS LAST, geo_id) AS mover_order
  FROM endpoints
)
SELECT
  'bump_county_rent_burden_rank'::VARCHAR AS question_id,
  v.geo_level,
  v.geo_id,
  v.geo_name,
  v.year AS period,
  'pct_rent_burden_30plus'::VARCHAR AS metric_id,
  'Rent-Burdened Renter Share'::VARCHAR AS metric_label,
  v.pct_rent_burden_30plus::DOUBLE AS metric_value,
  'gold.affordability_wide + silver.xwalk_cbsa_county'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  'Counties within Wilmington, NC CBSA'::VARCHAR AS "group",
  m.mover_order <= 2 AS highlight_flag,
  TRUE AS peer_flag,
  v.rent_burden_rank::DOUBLE AS rank,
  'Rank 1 is the highest rent-burden share among target-CBSA counties; highlighted counties have the largest 2013-2024 rank improvement.'::VARCHAR AS note
FROM county_values v
LEFT JOIN rank_movers m
  ON v.geo_id = m.geo_id
ORDER BY v.geo_name, v.year;
