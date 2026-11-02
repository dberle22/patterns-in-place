-- Q2's tract input (analyses/explanation/q2_job_proximity/queries/q2_job_concentration_tracts.sql)
-- for one CBSA, on ALL jobs (LODES JT00: jobs_all_total / workers_all_total) instead of the
-- warehouse default private jobs (JT02: jobs_total / workers_total). Columns keep Q2's names so
-- Q2's apply_method() runs unchanged. Albany sensitivity only; Q2's national mart is untouched.
WITH market_counties AS (
  SELECT DISTINCT cbsa_code, cbsa_name, county_geoid
  FROM silver.xwalk_cbsa_county
  WHERE cbsa_code = '__CBSA_CODE__'
)
SELECT
  mc.cbsa_code,
  mc.cbsa_name,
  w.geo_id AS tract_geoid,
  w.year AS wac_year,
  w.jobs_all_total AS jobs_total,
  r.workers_all_total AS workers_total,
  w.jobs_total AS private_jobs,
  g.land_area_sqmi,
  g.geom_wkb
FROM silver.lehd_lodes_wac AS w
JOIN geo.tracts_all_us AS g ON g.tract_geoid = w.geo_id
JOIN market_counties AS mc ON mc.county_geoid = g.county_geoid
LEFT JOIN silver.lehd_lodes_rac AS r
  ON r.geo_level = 'tract' AND r.geo_id = w.geo_id AND r.year = w.year
WHERE w.geo_level = 'tract' AND w.year = 2023 AND w.jobs_all_total IS NOT NULL
ORDER BY w.jobs_all_total DESC
