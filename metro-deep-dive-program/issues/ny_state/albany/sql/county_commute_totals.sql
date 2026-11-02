-- Every US county's resident jobs (by home) and workplace jobs (by work), 2023 LODES OD
-- (all jobs, JT00 / S000), with its CBSA/CSA membership and a display centroid for distance.
WITH od AS (
  SELECT home_county_geoid, work_county_geoid, jobs_all
  FROM silver.lehd_lodes_od_county
  WHERE year = 2023 AND segment = 'S000' AND transformation_version = 'lodes_od_county_v1'
),
home AS (SELECT home_county_geoid AS county_geoid, SUM(jobs_all) AS resident_jobs FROM od GROUP BY 1),
work AS (SELECT work_county_geoid AS county_geoid, SUM(jobs_all) AS workplace_jobs FROM od GROUP BY 1)
SELECT
  g.county_geoid,
  g.county_name,
  g.STUSPS AS state_abbr,
  home.resident_jobs,
  work.workplace_jobs,
  x.cbsa_code,
  x.cbsa_name,
  x.county_flag,
  x.csa_code,
  x.csa_name,
  ST_X(ST_Centroid(g.geom)) AS lon,
  ST_Y(ST_Centroid(g.geom)) AS lat
FROM geo.counties AS g
LEFT JOIN home ON home.county_geoid = g.county_geoid
LEFT JOIN work ON work.county_geoid = g.county_geoid
LEFT JOIN silver.xwalk_cbsa_county AS x ON x.county_geoid = g.county_geoid
ORDER BY g.county_geoid
