-- Where each New York county's residents work, summed to the CBSA of the work county:
-- 2023 LODES county OD (all jobs, JT00 / S000). Work counties in no CBSA are 'none'.
-- Feeds the statewide "which metro pulls each county" and "how far each metro reaches" views.
WITH od AS (
  SELECT home_county_geoid, work_county_geoid, jobs_all
  FROM silver.lehd_lodes_od_county
  WHERE year = 2023 AND segment = 'S000' AND transformation_version = 'lodes_od_county_v1'
    AND home_county_geoid LIKE '36%'
),
xw AS (
  SELECT county_geoid, cbsa_code, cbsa_name, cbsa_type
  FROM silver.xwalk_cbsa_county
)
SELECT
  od.home_county_geoid,
  home.cbsa_code AS home_cbsa_code,
  COALESCE(work.cbsa_code, 'none') AS work_cbsa_code,
  COALESCE(work.cbsa_name, 'Not in a CBSA') AS work_cbsa_name,
  work.cbsa_type AS work_cbsa_type,
  od.home_county_geoid = od.work_county_geoid AS same_county,
  SUM(od.jobs_all) AS jobs
FROM od
LEFT JOIN xw AS home ON home.county_geoid = od.home_county_geoid
LEFT JOIN xw AS work ON work.county_geoid = od.work_county_geoid
GROUP BY ALL
ORDER BY od.home_county_geoid, jobs DESC
