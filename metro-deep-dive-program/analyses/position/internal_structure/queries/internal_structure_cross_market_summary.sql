-- This is a coverage and scale comparison, not a cross-market ranking or a
-- normalized access measure. It supports the Part 2 portability review.
WITH poi_summary AS (
    SELECT p.cbsa_code,
           COUNT(*) FILTER (WHERE p.record_status = 'retained') AS retained_poi_count,
           COUNT(*) FILTER (WHERE p.record_status = 'retained' AND p.mapping_status IN ('mapped', 'overridden')) AS mapped_poi_count
    FROM mart_poi.poi_classified_place AS p
    GROUP BY p.cbsa_code
),
zone_summary AS (
    SELECT cbsa_code, COUNT(*) AS tract_count, COUNT(DISTINCT zone_type) AS zone_type_count
    FROM mart_intelligence.intelligence_zones
    GROUP BY cbsa_code
)
SELECT z.cbsa_code, z.tract_count, z.zone_type_count,
       p.retained_poi_count, p.mapped_poi_count,
       p.mapped_poi_count * 1.0 / NULLIF(p.retained_poi_count, 0) AS mapped_poi_share
FROM zone_summary AS z
LEFT JOIN poi_summary AS p USING (cbsa_code)
ORDER BY z.cbsa_code;
