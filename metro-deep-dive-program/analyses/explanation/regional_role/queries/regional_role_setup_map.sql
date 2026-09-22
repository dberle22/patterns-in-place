-- Display geometry only: membership construction occurs upstream in mart_geography.
SELECT membership.member_cbsa_code,
       member.geo_name AS member_cbsa_name,
       membership.member_role,
       membership.distance_miles,
       geometry.geom_wkb
FROM mart_geography.region_lens_membership AS membership
INNER JOIN gold.dim_geo AS member
  ON member.geo_level = 'cbsa' AND member.geo_id = membership.member_cbsa_code
INNER JOIN geo.cbsas AS geometry
  ON geometry.cbsa_code = membership.member_cbsa_code
WHERE membership.target_cbsa_code = '__CBSA_CODE__'
  AND membership.lens_id = '__LENS_ID__'
  AND membership.parameter_value = '__PARAMETER_VALUE__';
