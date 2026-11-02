-- POI counts by tract and governed category, from the Albany POI engine run's local
-- artifacts (__POI_RUN_DIR__) until the run is published to the mart.
SELECT
  g.geo_id AS tract_geoid,
  COALESCE(c.category, 'Unclassified') AS category,
  COUNT(*) AS pois
FROM read_parquet('__POI_RUN_DIR__/classified/poi_classified_place.parquet') AS c
JOIN read_parquet('__POI_RUN_DIR__/geography/poi_geography_assignment.parquet') AS g
  ON g.source_record_key = c.source_record_key
 AND g.geo_level = 'tract'
 AND g.assignment_status = 'assigned'
GROUP BY ALL
