-- Place-to-place flows touching a list of Census Places (__PLACE_GEOIDS__): 2023 LODES OD
-- aggregated to places (JT00 / S000). A home or work block outside every Census Place
-- carries a status instead of a place, and its county is unknown at this grain.
SELECT
  od.home_place_geoid,
  od.home_place_status,
  od.work_place_geoid,
  od.work_place_status,
  SUM(od.jobs) AS jobs
FROM silver.lehd_lodes_od_place AS od
WHERE od.job_type = 'JT00' AND od.segment = 'S000' AND od.transformation_version = 'lodes_od_place_v2'
  AND (od.home_place_geoid IN (__PLACE_GEOIDS__) OR od.work_place_geoid IN (__PLACE_GEOIDS__))
GROUP BY ALL
