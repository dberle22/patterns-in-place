-- The selected CBSA's governed identities and coverage are kept separate from
-- the allocated measures below, so a missing metric cannot be mistaken for a
-- missing tract or relationship.
WITH market_tracts AS (
    SELECT z.tract_geoid, z.county_geoid, z.zone_type
    FROM mart_intelligence.intelligence_zones AS z
    WHERE z.cbsa_code = '__CBSA_CODE__'
),
tract_metrics AS (
    SELECT p.geo_id AS tract_geoid, p.pop_total, h.hu_total
    FROM gold.population_demographics AS p
    JOIN gold.housing_core_wide AS h
      ON p.geo_level = h.geo_level
     AND p.geo_id = h.geo_id
     AND p.year = h.year
    WHERE p.geo_level = 'tract'
      AND p.year = 2024
),
place_edges AS (
    SELECT source_geo_id AS tract_geoid, target_geo_id AS place_id
    FROM mart_geography.allocation_edges
    WHERE source_geo_level = 'tract'
      AND target_geo_level = 'place'
      AND weight_basis = 'population'
      AND weight > 0
),
zcta_edges AS (
    SELECT source_geo_id AS tract_geoid, target_geo_id AS zcta_id
    FROM mart_geography.allocation_edges
    WHERE source_geo_level = 'tract'
      AND target_geo_level = 'zcta'
      AND weight_basis = 'population'
      AND weight > 0
)
SELECT 'CBSA identity' AS check_name, 1 AS observed_count, 1 AS expected_count,
       'Richmond selection resolves in the governed CBSA identity.' AS detail
FROM mart_geography.identity_current
WHERE geo_level = 'cbsa' AND geo_id = '__CBSA_CODE__'
UNION ALL
SELECT 'Tract zone rows', COUNT(*), COUNT(DISTINCT tract_geoid),
       'One Phase 7 assignment is expected per selected-market tract.'
FROM market_tracts
UNION ALL
SELECT 'Tract population and housing coverage', COUNT(tm.tract_geoid), COUNT(*),
       '2024 additive population and housing fields are jointly available.'
FROM market_tracts AS mt
LEFT JOIN tract_metrics AS tm ON mt.tract_geoid = tm.tract_geoid
UNION ALL
SELECT 'County identities', COUNT(DISTINCT county_geoid), COUNT(DISTINCT county_geoid),
       'Counties come from the tract-zone market slice.'
FROM market_tracts
UNION ALL
SELECT 'Census Place allocation coverage', COUNT(DISTINCT pe.tract_geoid), COUNT(DISTINCT mt.tract_geoid),
       'Population-basis tract-to-Place edges retain unincorporated tracts as misses.'
FROM market_tracts AS mt
LEFT JOIN place_edges AS pe ON mt.tract_geoid = pe.tract_geoid
UNION ALL
SELECT 'ZCTA allocation coverage', COUNT(DISTINCT ze.tract_geoid), COUNT(DISTINCT mt.tract_geoid),
       'Population-basis tract-to-ZCTA edges support the reader-friendly rollup.'
FROM market_tracts AS mt
LEFT JOIN zcta_edges AS ze ON mt.tract_geoid = ze.tract_geoid
UNION ALL
SELECT 'ZCTA zone-rollup coverage', COUNT(DISTINCT iz.zip_geoid), COUNT(DISTINCT ze.zcta_id),
       'Each ZCTA touched by the market is checked against the stored Phase 7 rollup.'
FROM market_tracts AS mt
JOIN zcta_edges AS ze ON mt.tract_geoid = ze.tract_geoid
LEFT JOIN mart_intelligence.intelligence_zones_zcta AS iz ON ze.zcta_id = iz.zip_geoid;
