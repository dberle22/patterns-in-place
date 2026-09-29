-- Direction is home Place -> work Place. JT02 is intentionally excluded
-- because it is a subset of JT00 rather than an additive second measure.
WITH work_places AS (
  SELECT place_geoid FROM mart_geography.place_to_cbsa_membership
  WHERE target_geo_id='__CBSA_CODE__' AND weight_basis='population'
)
SELECT od.work_place_geoid, COALESCE(work_geo.geo_name, od.work_place_geoid) AS work_place_name,
       od.home_place_geoid, od.home_place_status,
       COALESCE(home_geo.geo_name, od.home_place_geoid) AS home_place_name,
       SUM(od.jobs) AS jobs
FROM silver.lehd_lodes_od_place AS od
JOIN work_places ON work_places.place_geoid=od.work_place_geoid
LEFT JOIN silver.dim_geo AS work_geo ON work_geo.geo_level='place' AND work_geo.geo_id=od.work_place_geoid
LEFT JOIN silver.dim_geo AS home_geo ON home_geo.geo_level='place' AND home_geo.geo_id=od.home_place_geoid
WHERE od.job_type='JT00' AND od.segment='S000' AND od.transformation_version='lodes_od_place_v2'
GROUP BY 1,2,3,4,5
ORDER BY jobs DESC;
