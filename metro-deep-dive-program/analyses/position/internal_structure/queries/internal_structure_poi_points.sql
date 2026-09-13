-- Coordinates remain source points; the tract zone is an orientation join and
-- does not establish access, importance, or a functional center.
SELECT p.source_record_key, p.source_name, p.category, p.sub_category,
       p.longitude, p.latitude, z.zone_type
FROM mart_poi.poi_classified_place AS p
JOIN mart_poi.poi_geography_assignment AS a
  ON p.cbsa_code = a.cbsa_code
 AND p.source_record_key = a.source_record_key
 AND a.geo_level = 'tract'
 AND a.assignment_status = 'assigned'
JOIN mart_intelligence.intelligence_zones AS z
  ON a.geo_id = z.tract_geoid
 AND z.cbsa_code = '__CBSA_CODE__'
WHERE p.cbsa_code = '__CBSA_CODE__'
  AND p.record_status = 'retained'
  AND p.mapping_status IN ('mapped', 'overridden')
  AND p.longitude IS NOT NULL
  AND p.latitude IS NOT NULL;
