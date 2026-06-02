WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'county'
),
county_base AS (
  SELECT
    'map_rent_burden_clusters' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    '2024_snapshot' AS time_window,
    a.pct_rent_burden_30plus AS metric_value,
    'Rent-burdened renter households (%)' AS metric_label,
    'Affordability wide; county geometry' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    c.STATE_NAME AS group,
    ST_AsText(c.geom) AS geom_wkt
  FROM gold.affordability_wide a
  JOIN geo.counties c
    ON a.geo_id = c.county_geoid
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_year)
    AND a.pct_rent_burden_30plus IS NOT NULL
    AND c.STUSPS NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM county_base;
