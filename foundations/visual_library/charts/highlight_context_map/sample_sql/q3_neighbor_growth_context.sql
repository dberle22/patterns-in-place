WITH target_county AS (
  SELECT
    county_geoid,
    county_name,
    STATE_NAME
  FROM geo.counties
  WHERE county_name = 'Fulton'
    AND STUSPS = 'GA'
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.population_demographics
  WHERE geo_level = 'county'
),
neighbor_ring AS (
  SELECT c.county_geoid
  FROM geo.counties c
  CROSS JOIN target_county t
  JOIN geo.counties tc
    ON tc.county_geoid = t.county_geoid
  WHERE c.county_geoid <> t.county_geoid
    AND ST_Touches(c.geom, tc.geom)
),
county_base AS (
  SELECT
    'highlight_neighbor_growth' AS question_id,
    p.geo_level,
    p.geo_id,
    p.geo_name,
    '2014_to_2024_growth' AS time_window,
    p.pop_growth_10yr AS metric_value,
    'Population growth over 10 years (%)' AS metric_label,
    'gold.population_demographics + geo.counties' AS source,
    CAST(p.year AS VARCHAR) AS vintage,
    c.STATE_NAME AS context_group,
    p.geo_id = t.county_geoid AS highlight_flag,
    p.geo_id IN (SELECT county_geoid FROM neighbor_ring) AS neighbor_flag,
    p.geo_id = t.county_geoid AS label_flag,
    ST_AsText(c.geom) AS geom_wkt
  FROM gold.population_demographics p
  JOIN geo.counties c
    ON p.geo_id = c.county_geoid
  CROSS JOIN target_county t
  WHERE p.geo_level = 'county'
    AND p.year = (SELECT year FROM latest_year)
    AND p.pop_growth_10yr IS NOT NULL
    AND c.STUSPS = 'GA'
)
SELECT *
FROM county_base;
