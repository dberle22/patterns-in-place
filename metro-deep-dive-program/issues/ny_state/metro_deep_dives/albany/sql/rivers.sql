-- Hudson and Mohawk river lines from the verified NY Infrastructure consumer artifact
-- (same handoff as What NY Is Map 2). Drawing only; not a hydrography layer.
SELECT source_record_key, source_name, geometry AS geom_wkb
FROM read_parquet('__INFRASTRUCTURE_PATH__')
WHERE market_id = '36' AND market_boundary_geo_level = 'state'
  AND record_status = 'retained'
  AND feature_type = 'river'
  AND source_name IN ('Hudson River', 'Mohawk River')
ORDER BY source_record_key
