-- Direct point-in-Place assignments only; no tract allocation is used here.
SELECT place.geo_name AS place_name, SUM(1) AS poi_count
FROM mart_poi.poi_geography_assignment AS assignment
JOIN mart_poi.poi_classified_place AS poi
  ON poi.cbsa_code=assignment.cbsa_code AND poi.source_record_key=assignment.source_record_key
JOIN gold.population_demographics AS place
  ON place.geo_id=assignment.geo_id AND lower(place.geo_level)='place' AND place.year=2024
WHERE assignment.cbsa_code='__CBSA_CODE__' AND assignment.geo_level='place'
  AND assignment.assignment_status='assigned'
GROUP BY 1 ORDER BY poi_count DESC;
