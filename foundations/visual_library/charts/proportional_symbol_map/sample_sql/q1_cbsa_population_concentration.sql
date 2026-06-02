WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.population_demographics
  WHERE geo_level = 'cbsa'
),
metro_base AS (
  SELECT
    'bubble_population_concentration' AS question_id,
    p.geo_level,
    p.geo_id,
    p.geo_name,
    CAST(p.year AS VARCHAR) || '_snapshot' AS time_window,
    p.pop_total AS size_value,
    'Population' AS size_label,
    'gold.population_demographics + foundation.market_cbsa_geometry' AS source,
    CAST(p.year AS VARCHAR) AS vintage,
    COALESCE(f.census_region, 'Unclassified') AS color_group,
    p.pop_total >= quantile_cont(p.pop_total, 0.98) OVER () AS label_flag,
    ST_X(ST_PointOnSurface(ST_GeomFromText(g.geom_wkt))) AS lon,
    ST_Y(ST_PointOnSurface(ST_GeomFromText(g.geom_wkt))) AS lat
  FROM gold.population_demographics p
  JOIN foundation.market_cbsa_geometry g
    ON p.geo_id = g.cbsa_code
  LEFT JOIN foundation.cbsa_features f
    ON p.geo_id = f.cbsa_code
   AND p.year = f.year
  WHERE p.geo_level = 'cbsa'
    AND p.year = (SELECT year FROM latest_year)
    AND p.pop_total IS NOT NULL
    AND COALESCE(f.primary_state_abbr, '') NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM metro_base;
