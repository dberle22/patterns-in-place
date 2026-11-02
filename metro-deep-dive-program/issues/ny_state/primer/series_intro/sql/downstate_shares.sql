-- Downstate vs Rest of State: population (ACS 2020-24, counties) and land area, with shares.
-- Parameters (replaced in the notebook): __DOWNSTATE__, __SEED_PATH__ (see benchmark_stack_up.sql).
-- County population is complete; the tract table is missing 14 Suffolk tracts, so don't sum tracts.
WITH seed AS (
  SELECT
    county_geoid,
    CASE WHEN __DOWNSTATE__ THEN 'Downstate' ELSE 'Rest of State' END AS geography
  FROM read_csv('__SEED_PATH__', types = {'county_geoid': 'VARCHAR'})
),
parts AS (
  SELECT s.geography, SUM(p.pop_total) AS pop, SUM(c.land_area_sqmi) AS land_sqmi
  FROM seed AS s
  JOIN gold.population_demographics AS p
    ON p.geo_id = s.county_geoid AND p.geo_level = 'county' AND p.year = 2024
  JOIN geo.counties AS c ON c.county_geoid = s.county_geoid
  GROUP BY ALL
)
SELECT
  geography,
  pop,
  land_sqmi,
  pop / SUM(pop) OVER () AS pop_share,
  land_sqmi / SUM(land_sqmi) OVER () AS land_share
FROM parts
ORDER BY geography
