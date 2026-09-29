-- OMB county flags are sourced context. They never enter the Place decision.
SELECT cbsa_code, cbsa_name, county_geoid, county_name, state_name,
       county_flag, vintage AS omb_vintage, source
FROM silver.xwalk_cbsa_county
WHERE cbsa_code = '__CBSA_CODE__'
ORDER BY county_flag, county_name;
