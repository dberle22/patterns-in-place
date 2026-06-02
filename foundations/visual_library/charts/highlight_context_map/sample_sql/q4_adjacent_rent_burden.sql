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
  FROM gold.affordability_wide
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
    'highlight_adjacent_rent_burden' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    '2024_snapshot' AS time_window,
    a.pct_rent_burden_30plus AS metric_value,
    'Rent-burdened renter households (%)' AS metric_label,
    'gold.affordability_wide + geo.counties' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    c.STATE_NAME AS context_group,
    a.geo_id = t.county_geoid AS highlight_flag,
    a.geo_id IN (SELECT county_geoid FROM neighbor_ring) AS neighbor_flag,
    a.geo_id = t.county_geoid AS label_flag,
    ST_AsText(c.geom) AS geom_wkt
  FROM gold.affordability_wide a
  JOIN geo.counties c
    ON a.geo_id = c.county_geoid
  CROSS JOIN target_county t
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_year)
    AND a.pct_rent_burden_30plus IS NOT NULL
    AND c.STUSPS = 'GA'
)
SELECT *
FROM county_base;
