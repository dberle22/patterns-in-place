SELECT cbsa_code, assignment_status, COUNT(*) AS poi_count
FROM mart_poi.poi_geography_assignment
WHERE cbsa_code='__CBSA_CODE__' AND geo_level='place'
GROUP BY 1,2 ORDER BY 1,2;
