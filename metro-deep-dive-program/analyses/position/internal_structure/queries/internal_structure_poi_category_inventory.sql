-- Categories remain the POI engine's governed labels; analysis controls only
-- filter this inventory and do not create a new taxonomy.
SELECT p.category, p.sub_category, p.mapping_status,
       COUNT(*) AS place_count
FROM mart_poi.poi_classified_place AS p
WHERE p.cbsa_code = '__CBSA_CODE__'
  AND p.record_status = 'retained'
GROUP BY p.category, p.sub_category, p.mapping_status
ORDER BY place_count DESC, p.category, p.sub_category;
