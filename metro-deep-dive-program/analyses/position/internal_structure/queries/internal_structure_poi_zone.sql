-- A POI is assigned to a tract by Geography, then grouped by its stored Phase
-- 7 zone. Point counts are never allocated into Census Places with tract weights.
WITH zone_population AS (
    SELECT z.zone_type, SUM(p.pop_total) AS zone_population
    FROM mart_intelligence.intelligence_zones AS z
    JOIN gold.population_demographics AS p
      ON z.tract_geoid = p.geo_id
     AND p.geo_level = 'tract'
     AND p.year = 2024
    WHERE z.cbsa_code = '__CBSA_CODE__'
    GROUP BY z.zone_type
)
SELECT p.category, p.sub_category, z.zone_type,
       COUNT(*) AS place_count,
       zp.zone_population,
       COUNT(*) * 10000.0 / NULLIF(zp.zone_population, 0) AS places_per_10000_residents
FROM mart_poi.poi_classified_place AS p
JOIN mart_poi.poi_geography_assignment AS a
  ON p.cbsa_code = a.cbsa_code
 AND p.source_record_key = a.source_record_key
 AND a.geo_level = 'tract'
 AND a.assignment_status = 'assigned'
JOIN mart_intelligence.intelligence_zones AS z
  ON a.geo_id = z.tract_geoid
 AND z.cbsa_code = '__CBSA_CODE__'
JOIN zone_population AS zp ON z.zone_type = zp.zone_type
WHERE p.cbsa_code = '__CBSA_CODE__'
  AND p.record_status = 'retained'
  AND p.mapping_status IN ('mapped', 'overridden')
GROUP BY p.category, p.sub_category, z.zone_type, zp.zone_population
ORDER BY place_count DESC, p.category, z.zone_type;
