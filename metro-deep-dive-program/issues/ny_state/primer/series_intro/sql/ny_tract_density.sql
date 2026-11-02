-- NY tract population density, ACS 2020-24 5-year, on shoreline-clipped tract shapes.
-- Left join from geometry so tracts with no population row stay on the map as "no data"
-- (14 Suffolk tracts as of 2026-10-18; see foundations/ROADMAP.md).
SELECT
  t.tract_geoid,
  t.county_geoid,
  t.land_area_sqmi,
  p.pop_total,
  p.pop_total / NULLIF(t.land_area_sqmi, 0) AS pop_per_sqmi,
  t.geom_wkb
FROM geo.tracts_all_us AS t
LEFT JOIN gold.population_demographics AS p
  ON p.geo_id = t.tract_geoid
 AND p.geo_level = 'tract'
 AND p.year = 2024
WHERE t.state_fips = '36'
ORDER BY t.tract_geoid
