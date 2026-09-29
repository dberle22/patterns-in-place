-- POI coverage is reported before category comparisons. Retained records remain
-- visible whether their governed taxonomy mapping is complete or not.
SELECT p.record_status, p.mapping_status, a.assignment_status,
       COUNT(*) AS place_count
FROM mart_poi.poi_classified_place AS p
LEFT JOIN mart_poi.poi_geography_assignment AS a
  ON p.cbsa_code = a.cbsa_code
 AND p.source_record_key = a.source_record_key
 AND a.geo_level = 'tract'
WHERE p.cbsa_code = '__CBSA_CODE__'
GROUP BY p.record_status, p.mapping_status, a.assignment_status
ORDER BY place_count DESC, p.record_status, p.mapping_status;
