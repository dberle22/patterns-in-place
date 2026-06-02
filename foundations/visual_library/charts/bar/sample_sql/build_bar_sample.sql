-- Build canonical bar chart test datasets from gold-layer marts.
-- Includes:
--   1. bar_top_growth_cbsas: Top CBSAs by 5-year per-capita income growth.
--   2. bar_county_affordability: County rent-to-income ranking within Wilmington, NC (CBSA 48900).

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
latest_cbsa_growth_year AS (
  SELECT MAX(year) AS year
  FROM metro_deep_dive.gold.economics_income_wide
  WHERE geo_level = 'cbsa'
    AND income_pc_growth_5yr IS NOT NULL
),
latest_target_county_year AS (
  SELECT MAX(a.year) AS year
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN metro_deep_dive.silver.xwalk_cbsa_county x
    ON a.geo_id = x.county_geoid
  JOIN target_cbsa t
    ON x.cbsa_code = t.target_geo_id
  WHERE a.geo_level = 'county'
    AND a.rent_to_income IS NOT NULL
),
cbsa_division_lookup AS (
  SELECT
    c.cbsa_code AS geo_id,
    s.census_division AS division,
    ROW_NUMBER() OVER (PARTITION BY c.cbsa_code ORDER BY c.county_geoid) AS rn
  FROM metro_deep_dive.silver.xwalk_cbsa_county c
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region s
    ON c.state_fips = s.state_fips
),
cbsa_division_dedup AS (
  SELECT geo_id, division
  FROM cbsa_division_lookup
  WHERE rn = 1
),
cbsa_growth AS (
  SELECT
    'bar_top_growth_cbsas'::VARCHAR AS question_id,
    i.geo_level,
    i.geo_id,
    i.geo_name,
    CONCAT(CAST(i.year - 5 AS VARCHAR), '_to_', CAST(i.year AS VARCHAR), '_growth')::VARCHAR AS time_window,
    'income_pc_growth_5yr'::VARCHAR AS metric_id,
    '5-Year Per Capita Income Growth'::VARCHAR AS metric_label,
    i.income_pc_growth_5yr * 100.0 AS metric_value,
    'gold.economics_income_wide'::VARCHAR AS source,
    '2026-04-14'::VARCHAR AS vintage,
    ROW_NUMBER() OVER (ORDER BY i.income_pc_growth_5yr DESC, i.geo_name) AS rank,
    d.division AS "group",
    NULL::VARCHAR AS series,
    NULL::DOUBLE AS share_value,
    i.geo_id = (SELECT target_geo_id FROM target_cbsa) AS highlight_flag,
    NULL::DOUBLE AS benchmark_value,
    NULL::VARCHAR AS note
  FROM metro_deep_dive.gold.economics_income_wide i
  LEFT JOIN cbsa_division_dedup d
    ON i.geo_id = d.geo_id
  WHERE i.geo_level = 'cbsa'
    AND i.year = (SELECT year FROM latest_cbsa_growth_year)
    AND i.income_pc_growth_5yr IS NOT NULL
),
county_affordability AS (
  SELECT
    'bar_county_affordability'::VARCHAR AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    CONCAT(CAST(a.year AS VARCHAR), '_snapshot')::VARCHAR AS time_window,
    'rent_to_income'::VARCHAR AS metric_id,
    'Annualized Median Rent as % of Median Household Income'::VARCHAR AS metric_label,
    a.rent_to_income * 100.0 AS metric_value,
    'gold.affordability_wide'::VARCHAR AS source,
    '2026-04-14'::VARCHAR AS vintage,
    ROW_NUMBER() OVER (ORDER BY a.rent_to_income DESC, a.geo_name) AS rank,
    'Wilmington, NC counties'::VARCHAR AS "group",
    NULL::VARCHAR AS series,
    NULL::DOUBLE AS share_value,
    FALSE AS highlight_flag,
    NULL::DOUBLE AS benchmark_value,
    NULL::VARCHAR AS note
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN metro_deep_dive.silver.xwalk_cbsa_county x
    ON a.geo_id = x.county_geoid
  JOIN target_cbsa t
    ON x.cbsa_code = t.target_geo_id
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_target_county_year)
    AND a.rent_to_income IS NOT NULL
)
SELECT *
FROM cbsa_growth
UNION ALL
SELECT *
FROM county_affordability
ORDER BY question_id, rank, geo_name;
