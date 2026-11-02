-- Tract-to-tract 2023 LODES OD for flows touching the metro (engines/commute_sheds,
-- either_endpoint scope: work tract in the metro OR home tract in the metro).
-- __JOB_TYPE__: JT00 all jobs, JT02 private. Summed across source parts (main, aux).
-- Blocks the engine couldn't map to a tract are excluded here; the coverage table counts them.
WITH flows AS (
  SELECT home_tract_geoid, work_tract_geoid, SUM(jobs) AS jobs
  FROM silver.lehd_lodes_od_tract_metro
  WHERE cbsa_code = '__CBSA_CODE__' AND relationship_scope = 'either_endpoint' AND year = 2023
    AND job_type = '__JOB_TYPE__' AND home_tract_status = 'matched' AND work_tract_status = 'matched'
  GROUP BY ALL
)
SELECT
  f.home_tract_geoid,
  f.work_tract_geoid,
  f.jobs,
  substr(f.home_tract_geoid, 1, 5) AS home_county_geoid,
  substr(f.work_tract_geoid, 1, 5) AS work_county_geoid,
  ST_X(ST_Centroid(ST_GeomFromWKB(h.geom_wkb))) AS home_lon,
  ST_Y(ST_Centroid(ST_GeomFromWKB(h.geom_wkb))) AS home_lat,
  ST_X(ST_Centroid(ST_GeomFromWKB(w.geom_wkb))) AS work_lon,
  ST_Y(ST_Centroid(ST_GeomFromWKB(w.geom_wkb))) AS work_lat
FROM flows AS f
LEFT JOIN geo.tracts_all_us AS h ON h.tract_geoid = f.home_tract_geoid
LEFT JOIN geo.tracts_all_us AS w ON w.tract_geoid = f.work_tract_geoid
