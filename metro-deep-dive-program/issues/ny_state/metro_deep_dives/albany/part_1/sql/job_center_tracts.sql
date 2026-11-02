-- Every metro tract with 2023 LODES workplace jobs and Q2's reviewed job-center flags.
-- component_place_name: the Census Place holding the largest population-weighted share
-- of the component's center-tract jobs (Q6's association rule). Used for labels only.
WITH tracts AS (
  SELECT
    tract_geoid,
    jobs_total,
    workers_total,
    land_area_sqmi,
    is_recommended_center,
    recommended_cluster_id AS component_id,
    center_role
  FROM mart_explanation_q2.job_center_candidates_v0
  WHERE cbsa_code = '__CBSA_CODE__'
),
component_place AS (
  SELECT
    t.component_id,
    a.target_geo_id AS place_geoid,
    SUM(t.jobs_total * a.weight) AS allocated_jobs
  FROM tracts AS t
  JOIN silver.xwalk_allocation AS a
    ON a.source_geo_id = t.tract_geoid
  WHERE t.is_recommended_center
    AND a.source_geo_level = 'tract'
    AND a.target_geo_level = 'place'
    AND a.weight_basis = 'population'
  GROUP BY 1, 2
  QUALIFY ROW_NUMBER() OVER (PARTITION BY t.component_id ORDER BY allocated_jobs DESC, place_geoid) = 1
)
SELECT
  t.*,
  p.NAME AS component_place_name,
  g.geom_wkb
FROM tracts AS t
LEFT JOIN component_place AS cp
  ON cp.component_id = t.component_id
LEFT JOIN geo.places_display AS p
  ON p.place_geoid = cp.place_geoid
JOIN geo.tracts_all_us AS g
  ON g.tract_geoid = t.tract_geoid
ORDER BY t.jobs_total DESC
