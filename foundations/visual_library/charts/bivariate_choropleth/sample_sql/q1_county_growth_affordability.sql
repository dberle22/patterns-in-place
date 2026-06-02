WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'county'
),
county_base AS (
  SELECT
    'bivar_growth_affordability_counties' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    '2014_to_2024_growth' AS time_window,
    p.pop_growth_10yr AS x_value,
    1.0 / NULLIF(a.value_to_income, 0) AS y_value,
    '10-year population growth' AS x_label,
    'Relative affordability' AS y_label,
    'gold.population_demographics + gold.affordability_wide + geo.counties' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    c.STATE_NAME AS "group",
    FALSE AS highlight_flag,
    ST_AsText(c.geom) AS geom_wkt,
    'Affordability is encoded as the inverse of home value to household income so higher bins mean more affordable.' AS note
  FROM gold.affordability_wide a
  JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  JOIN geo.counties c
    ON a.geo_id = c.county_geoid
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_year)
    AND p.pop_growth_10yr IS NOT NULL
    AND a.value_to_income IS NOT NULL
    AND c.STUSPS NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM county_base;
