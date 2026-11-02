-- Map 2 v2: the Hudson River as OSM waterway lines from the same verified Infrastructure
-- consumer artifact as map2_infrastructure.sql. Drawing only; not a hydrography layer.
SELECT source_record_key, source_name, geometry AS geom_wkb
FROM read_parquet('__INFRASTRUCTURE_PATH__')
WHERE market_id = '36' AND market_boundary_geo_level = 'state'
  AND record_status = 'retained'
  AND feature_type = 'river'
  AND source_name = 'Hudson River'
ORDER BY source_record_key;
