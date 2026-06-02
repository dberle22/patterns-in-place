WITH target_cbsa AS (
  SELECT
    '12060' AS cbsa_code,
    'Atlanta-Sandy Springs-Roswell, GA' AS cbsa_name
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'tract'
),
tract_base AS (
  SELECT
    'map_affordability_outliers_within_cbsa' AS question_id,
    'tract' AS geo_level,
    a.geo_id,
    a.geo_name,
    '2024_snapshot' AS time_window,
    a.value_to_income AS metric_value,
    'Home value to household income ratio' AS metric_label,
    'gold.affordability_wide + foundation.market_tract_geometry' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    t.cbsa_name AS group,
    a.value_to_income >= quantile_cont(a.value_to_income, 0.95) OVER () AS highlight_flag,
    g.geom_wkt
  FROM gold.affordability_wide a
  JOIN foundation.market_tract_geometry g
    ON a.geo_id = g.tract_geoid
  JOIN target_cbsa t
    ON g.cbsa_code = t.cbsa_code
  WHERE a.geo_level = 'tract'
    AND a.year = (SELECT year FROM latest_year)
    AND a.value_to_income IS NOT NULL
)
SELECT *
FROM tract_base;
