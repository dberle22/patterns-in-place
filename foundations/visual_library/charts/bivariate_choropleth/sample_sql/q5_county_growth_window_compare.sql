WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'county'
),
county_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    CAST(a.year AS VARCHAR) AS vintage,
    p.pop_growth_5yr,
    p.pop_growth_10yr,
    1.0 / NULLIF(a.value_to_income, 0) AS affordability_value,
    c.STATE_NAME AS state_name,
    ST_AsText(c.geom) AS geom_wkt
  FROM gold.affordability_wide a
  JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  JOIN geo.counties c
    ON a.geo_id = c.county_geoid
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_year)
    AND a.value_to_income IS NOT NULL
    AND c.STUSPS NOT IN ('AK', 'HI', 'PR')
),
window_compare AS (
  SELECT
    'bivar_growth_window_compare' AS question_id,
    geo_level,
    geo_id,
    geo_name,
    '2019_to_2024_growth' AS time_window,
    pop_growth_5yr AS x_value,
    affordability_value AS y_value,
    '5-year population growth' AS x_label,
    'Relative affordability' AS y_label,
    'gold.population_demographics + gold.affordability_wide + geo.counties' AS source,
    vintage,
    state_name AS "group",
    FALSE AS highlight_flag,
    geom_wkt,
    'Affordability is encoded as the inverse of home value to household income so higher bins mean more affordable.' AS note
  FROM county_base
  WHERE pop_growth_5yr IS NOT NULL

  UNION ALL

  SELECT
    'bivar_growth_window_compare' AS question_id,
    geo_level,
    geo_id,
    geo_name,
    '2014_to_2024_growth' AS time_window,
    pop_growth_10yr AS x_value,
    affordability_value AS y_value,
    '10-year population growth' AS x_label,
    'Relative affordability' AS y_label,
    'gold.population_demographics + gold.affordability_wide + geo.counties' AS source,
    vintage,
    state_name AS "group",
    FALSE AS highlight_flag,
    geom_wkt,
    'Affordability is encoded as the inverse of home value to household income so higher bins mean more affordable.' AS note
  FROM county_base
  WHERE pop_growth_10yr IS NOT NULL
)
SELECT *
FROM window_compare;
