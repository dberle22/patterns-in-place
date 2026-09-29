-- Membership provenance for one target across all declared Regional Role lenses.
SELECT membership.target_cbsa_code,
       target.geo_name AS target_cbsa_name,
       membership.lens_id,
       membership.lens_version,
       membership.parameter_name,
       membership.parameter_value,
       membership.member_cbsa_code,
       member.geo_name AS member_cbsa_name,
       membership.member_role,
       membership.distance_miles,
       membership.membership_source,
       membership.boundary_vintage,
       membership.method_version
FROM mart_geography.region_lens_membership AS membership
INNER JOIN gold.dim_geo AS target
  ON target.geo_level = 'cbsa' AND target.geo_id = membership.target_cbsa_code
INNER JOIN gold.dim_geo AS member
  ON member.geo_level = 'cbsa' AND member.geo_id = membership.member_cbsa_code
WHERE membership.target_cbsa_code = '__CBSA_CODE__'
  AND (
    membership.lens_id <> 'cbsa_centroid_250mi'
    OR membership.parameter_value IN ('200', '250', '300')
  )
ORDER BY membership.lens_id, TRY_CAST(membership.parameter_value AS INTEGER), member.geo_name;
