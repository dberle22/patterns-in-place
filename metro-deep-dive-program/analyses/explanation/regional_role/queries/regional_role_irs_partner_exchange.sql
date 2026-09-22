-- Roll county IRS migration flows to target-CBSA partner categories. County endpoints
-- outside a CBSA remain visible; IRS migration is not commuting.
WITH active_members AS (
  SELECT member_cbsa_code FROM mart_geography.region_lens_membership
  WHERE target_cbsa_code = '__CBSA_CODE__' AND lens_id = '__LENS_ID__' AND parameter_value = '__PARAMETER_VALUE__'
),
flows AS (
  SELECT flow.year, flow.origin_geo_id, flow.origin_geo_name, flow.dest_geo_id, flow.dest_geo_name,
         flow.n_returns, flow.n_exemptions, flow.agi, origin.cbsa_code AS origin_cbsa_code,
         destination.cbsa_code AS dest_cbsa_code
  FROM silver.irs_migration_flows AS flow
  LEFT JOIN silver.xwalk_cbsa_county AS origin ON origin.county_geoid = flow.origin_geo_id
  LEFT JOIN silver.xwalk_cbsa_county AS destination ON destination.county_geoid = flow.dest_geo_id
  WHERE flow.geo_level = 'county' AND flow.year = __MIGRATION_YEAR__
),
target_flows AS (
  SELECT *,
         CASE WHEN origin_cbsa_code = '__CBSA_CODE__' AND dest_cbsa_code = '__CBSA_CODE__' THEN 'within_target_cbsa'
              WHEN dest_cbsa_code = '__CBSA_CODE__' THEN 'inbound'
              WHEN origin_cbsa_code = '__CBSA_CODE__' THEN 'outbound' END AS direction,
         CASE WHEN origin_cbsa_code = '__CBSA_CODE__' THEN dest_cbsa_code
              WHEN dest_cbsa_code = '__CBSA_CODE__' THEN origin_cbsa_code END AS partner_cbsa_code,
         CASE WHEN origin_cbsa_code = '__CBSA_CODE__' THEN dest_geo_name
              WHEN dest_cbsa_code = '__CBSA_CODE__' THEN origin_geo_name END AS partner_county_name
  FROM flows WHERE origin_cbsa_code = '__CBSA_CODE__' OR dest_cbsa_code = '__CBSA_CODE__'
)
SELECT direction,
       CASE WHEN direction = 'within_target_cbsa' THEN 'within_target_cbsa'
            WHEN partner_cbsa_code IS NULL THEN 'non_cbsa_county'
            WHEN partner_cbsa_code IN (SELECT member_cbsa_code FROM active_members) THEN 'inside_active_lens'
            ELSE 'outside_active_lens' END AS partner_context,
       partner_cbsa_code, COALESCE(partner_geo.geo_name, partner_county_name) AS partner_name,
       SUM(n_returns) AS returns, SUM(n_exemptions) AS exemptions, SUM(agi) AS agi,
       COUNT(*) AS county_flow_rows
FROM target_flows LEFT JOIN gold.dim_geo AS partner_geo
  ON partner_geo.geo_level = 'cbsa' AND partner_geo.geo_id = partner_cbsa_code
GROUP BY 1,2,3,4 ORDER BY returns DESC NULLS LAST, partner_name;
