WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'cbsa'
    AND rpp_real_pc_income IS NOT NULL
),
metro_benchmark AS (
  SELECT
    SUM(a.rpp_real_pc_income * f.pop_total) / SUM(f.pop_total) AS benchmark_value
  FROM gold.affordability_wide a
  JOIN foundation.cbsa_features f
    ON a.geo_id = f.cbsa_code
   AND a.year = f.year
  WHERE a.geo_level = 'cbsa'
    AND a.year = (SELECT year FROM latest_year)
    AND a.rpp_real_pc_income IS NOT NULL
    AND f.pop_total IS NOT NULL
),
metro_base AS (
  SELECT
    'map_benchmark_relative_metros' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    '2023_snapshot' AS time_window,
    a.rpp_real_pc_income AS metric_value,
    'Real per capita income relative to metro benchmark ($)' AS metric_label,
    'Affordability wide; CBSA geometry' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    b.benchmark_value,
    f.census_region AS group,
    FALSE AS highlight_flag,
    g.geom_wkt
  FROM gold.affordability_wide a
  JOIN foundation.market_cbsa_geometry g
    ON a.geo_id = g.cbsa_code
  LEFT JOIN foundation.cbsa_features f
    ON a.geo_id = f.cbsa_code
   AND a.year = f.year
  CROSS JOIN metro_benchmark b
  WHERE a.geo_level = 'cbsa'
    AND a.year = (SELECT year FROM latest_year)
    AND a.rpp_real_pc_income IS NOT NULL
    AND COALESCE(f.primary_state_abbr, '') NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM metro_base;
