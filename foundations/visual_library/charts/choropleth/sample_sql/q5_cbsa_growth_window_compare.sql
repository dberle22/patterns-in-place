WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.population_demographics
  WHERE geo_level = 'cbsa'
),
cbsa_base AS (
  SELECT
    p.geo_id,
    p.geo_name,
    CAST(p.year AS VARCHAR) AS vintage,
    p.pop_growth_5yr,
    p.pop_growth_10yr,
    f.census_region AS region_group,
    f.primary_state_abbr,
    g.geom_wkt
  FROM gold.population_demographics p
  JOIN foundation.market_cbsa_geometry g
    ON p.geo_id = g.cbsa_code
  LEFT JOIN foundation.cbsa_features f
    ON p.geo_id = f.cbsa_code
   AND p.year = f.year
  WHERE p.geo_level = 'cbsa'
    AND p.year = (SELECT year FROM latest_year)
    AND COALESCE(f.primary_state_abbr, '') NOT IN ('AK', 'HI', 'PR')
),
window_compare AS (
  SELECT
    'map_growth_window_compare' AS question_id,
    'cbsa' AS geo_level,
    geo_id,
    geo_name,
    '2019_to_2024_growth' AS time_window,
    pop_growth_5yr AS metric_value,
    'Population growth (%)' AS metric_label,
    'gold.population_demographics + foundation.market_cbsa_geometry' AS source,
    vintage,
    region_group AS "group",
    geom_wkt
  FROM cbsa_base
  WHERE pop_growth_5yr IS NOT NULL

  UNION ALL

  SELECT
    'map_growth_window_compare' AS question_id,
    'cbsa' AS geo_level,
    geo_id,
    geo_name,
    '2014_to_2024_growth' AS time_window,
    pop_growth_10yr AS metric_value,
    'Population growth (%)' AS metric_label,
    'gold.population_demographics + foundation.market_cbsa_geometry' AS source,
    vintage,
    region_group AS "group",
    geom_wkt
  FROM cbsa_base
  WHERE pop_growth_10yr IS NOT NULL
)
SELECT *
FROM window_compare;
