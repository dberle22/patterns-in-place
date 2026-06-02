WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.population_demographics
  WHERE geo_level = 'county'
),
county_growth AS (
  SELECT
    'map_population_growth_corridors' AS question_id,
    p.geo_level,
    p.geo_id,
    p.geo_name,
    '2014_to_2024_growth' AS time_window,
    p.pop_growth_10yr AS metric_value,
    'Population growth over 10 years (%)' AS metric_label,
    'Population demographics; county geometry' AS source,
    CAST(p.year AS VARCHAR) AS vintage,
    c.STATE_NAME AS group,
    ST_AsText(c.geom) AS geom_wkt
  FROM gold.population_demographics p
  JOIN geo.counties c
    ON p.geo_id = c.county_geoid
  WHERE p.geo_level = 'county'
    AND p.year = (SELECT year FROM latest_year)
    AND p.pop_growth_10yr IS NOT NULL
    AND c.STUSPS NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM county_growth;
