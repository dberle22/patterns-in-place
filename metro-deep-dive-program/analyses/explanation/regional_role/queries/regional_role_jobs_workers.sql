-- 2023 LODES workplace jobs and resident workers are descriptive balances,
-- not observed commuting flows or inflow/outflow measures.
WITH members AS (
  SELECT member_cbsa_code, member_role, distance_miles FROM mart_geography.region_lens_membership
  WHERE target_cbsa_code = '__CBSA_CODE__' AND lens_id = '__LENS_ID__' AND parameter_value = '__PARAMETER_VALUE__'
)
SELECT members.member_cbsa_code, geography.geo_name AS member_cbsa_name, members.member_role,
       members.distance_miles, labor.year, labor.jobs_total, labor.workers_total,
       labor.jobs_minus_workers, labor.jobs_to_workers_ratio
FROM members INNER JOIN gold.dim_geo AS geography
  ON geography.geo_level = 'cbsa' AND geography.geo_id = members.member_cbsa_code
LEFT JOIN gold.economics_lodes_wide AS labor
  ON labor.geo_level = 'cbsa' AND labor.geo_id = members.member_cbsa_code AND labor.year = 2023
ORDER BY members.member_role DESC, labor.jobs_minus_workers DESC NULLS LAST, geography.geo_name;
