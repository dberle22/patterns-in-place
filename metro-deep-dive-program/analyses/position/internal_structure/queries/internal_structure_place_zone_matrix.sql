-- Retain the allocation quality and both denominators so the same evidence can
-- answer either "how is a Place composed?" or "where is a zone located?".
WITH market_tracts AS (
    SELECT tract_geoid, zone_type
    FROM mart_intelligence.intelligence_zones
    WHERE cbsa_code = '__CBSA_CODE__'
),
place_edges AS (
    SELECT source_geo_id AS tract_geoid, target_geo_id AS place_id, weight, quality_flag
    FROM mart_geography.allocation_edges
    WHERE source_geo_level = 'tract' AND target_geo_level = 'place'
      AND weight_basis = 'population' AND weight > 0
),
matrix AS (
    SELECT pe.place_id, i.display_name AS place_name, mt.zone_type,
           SUM(pe.weight) AS allocated_tract_equivalents,
           MAX(pe.quality_flag) AS allocation_quality
    FROM market_tracts AS mt
    JOIN place_edges AS pe ON mt.tract_geoid = pe.tract_geoid
    JOIN mart_geography.identity_current AS i ON i.geo_level = 'place' AND i.geo_id = pe.place_id
    GROUP BY pe.place_id, i.display_name, mt.zone_type
)
SELECT *,
       allocated_tract_equivalents / SUM(allocated_tract_equivalents) OVER (PARTITION BY place_id) AS share_within_place,
       allocated_tract_equivalents / SUM(allocated_tract_equivalents) OVER (PARTITION BY zone_type) AS share_of_market_zone
FROM matrix
ORDER BY place_name, zone_type;
