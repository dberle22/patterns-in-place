-- 2023 LODES OD between counties (all jobs, JT00 / S000), for every flow that starts or
-- ends in the metro. Counts are jobs, not workers: someone with two jobs counts twice.
-- Residents working in other states come from those states' aux files (49 states loaded).
WITH metro AS (
  SELECT county_geoid, county_flag
  FROM mart_explanation_q6.cbsa_county_context
  WHERE cbsa_code = '__CBSA_CODE__'
)
SELECT
  od.home_county_geoid,
  od.home_county_name,
  home.county_flag AS home_flag,
  od.work_county_geoid,
  od.work_county_name,
  work.county_flag AS work_flag,
  SUM(od.jobs_all) AS jobs,
  SUM(od.jobs_private) AS private_jobs
FROM silver.lehd_lodes_od_county AS od
LEFT JOIN metro AS home
  ON home.county_geoid = od.home_county_geoid
LEFT JOIN metro AS work
  ON work.county_geoid = od.work_county_geoid
WHERE od.year = 2023
  AND od.segment = 'S000'
  AND od.transformation_version = 'lodes_od_county_v1'
  AND (home.county_geoid IS NOT NULL OR work.county_geoid IS NOT NULL)
GROUP BY ALL
ORDER BY jobs DESC
