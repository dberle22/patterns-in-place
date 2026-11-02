-- Print clearance for the Phase 7 zone type names used in the metro.
SELECT zone_type, zone_type_name_status, COUNT(*) AS tracts
FROM mart_intelligence.intelligence_zones
WHERE cbsa_code = '__CBSA_CODE__'
GROUP BY ALL
ORDER BY tracts DESC
