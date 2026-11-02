-- POI points for quick dot maps: name, governed category and sub-category, lon/lat.
SELECT source_name, category, sub_category, longitude, latitude
FROM read_parquet('__POI_RUN_DIR__/classified/poi_classified_place.parquet')
WHERE mapping_status = 'mapped'
