-- Metro tracts: residents (ACS 2020–24 5-year, 2024), all jobs at tract workplaces (LODES WAC JT00,
-- 2023) and land area. The denominators for Q3e's activity classes (POIs per resident, jobs per resident).
SELECT
  g.tract_geoid,
  g.land_area_sqmi,
  p.pop_total AS residents,
  w.jobs_all_total AS jobs
FROM geo.tracts_all_us AS g
JOIN silver.xwalk_cbsa_county AS x ON x.county_geoid = g.county_geoid AND x.cbsa_code = '__CBSA_CODE__'
LEFT JOIN gold.population_demographics AS p ON p.geo_level = 'tract' AND p.geo_id = g.tract_geoid AND p.year = 2024
LEFT JOIN silver.lehd_lodes_wac AS w ON w.geo_level = 'tract' AND w.geo_id = g.tract_geoid AND w.year = 2023
