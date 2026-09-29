-- Current tract measures are allocated with the declared population basis.
-- This is descriptive Place context, not a claim that a Place is a functional market.
WITH market_tracts AS (
    SELECT z.tract_geoid, z.zone_type
    FROM mart_intelligence.intelligence_zones AS z
    WHERE z.cbsa_code = '__CBSA_CODE__'
),
tract_metrics AS (
    SELECT p.geo_id AS tract_geoid, p.pop_total, h.hu_total
    FROM gold.population_demographics AS p
    JOIN gold.housing_core_wide AS h
      ON p.geo_level = h.geo_level AND p.geo_id = h.geo_id AND p.year = h.year
    WHERE p.geo_level = 'tract' AND p.year = 2024
),
place_edges AS (
    SELECT source_geo_id AS tract_geoid, target_geo_id AS place_id, weight, quality_flag
    FROM mart_geography.allocation_edges
    WHERE source_geo_level = 'tract' AND target_geo_level = 'place'
      AND weight_basis = 'population' AND weight > 0
)
SELECT pe.place_id, i.display_name AS place_name,
       SUM(tm.pop_total * pe.weight) AS allocated_population,
       SUM(tm.hu_total * pe.weight) AS allocated_housing_units,
       COUNT(DISTINCT pe.tract_geoid) AS contributing_tract_count,
       MAX(pe.quality_flag) AS allocation_quality,
       COUNT(DISTINCT mt.zone_type) AS zone_type_count
FROM market_tracts AS mt
JOIN place_edges AS pe ON mt.tract_geoid = pe.tract_geoid
JOIN tract_metrics AS tm ON mt.tract_geoid = tm.tract_geoid
JOIN mart_geography.identity_current AS i
  ON i.geo_level = 'place' AND i.geo_id = pe.place_id
GROUP BY pe.place_id, i.display_name
ORDER BY allocated_population DESC, place_name;
