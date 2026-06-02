WITH params AS (
  SELECT '12060'::VARCHAR AS cbsa_code
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.economics_labor_wide
  WHERE geo_level = 'county'
    AND employed IS NOT NULL
),
target_counties AS (
  SELECT DISTINCT county_geoid
  FROM foundation.market_county_geometry
  WHERE cbsa_code = (SELECT cbsa_code FROM params)
),
county_base AS (
  SELECT
    'bubble_jobs_concentration' AS question_id,
    e.geo_level,
    e.geo_id,
    e.geo_name,
    CAST(e.year AS VARCHAR) || '_snapshot' AS time_window,
    e.employed AS size_value,
    'Employed residents' AS size_label,
    'gold.economics_labor_wide + geo.counties + foundation.market_county_geometry' AS source,
    CAST(e.year AS VARCHAR) AS vintage,
    c.STATE_NAME AS color_group,
    e.employed >= quantile_cont(e.employed, 0.75) OVER () AS label_flag,
    ST_X(ST_PointOnSurface(c.geom)) AS lon,
    ST_Y(ST_PointOnSurface(c.geom)) AS lat
  FROM gold.economics_labor_wide e
  JOIN target_counties tc
    ON e.geo_id = tc.county_geoid
  JOIN geo.counties c
    ON e.geo_id = c.county_geoid
  WHERE e.geo_level = 'county'
    AND e.year = (SELECT year FROM latest_year)
    AND e.employed IS NOT NULL
)
SELECT *
FROM county_base;
