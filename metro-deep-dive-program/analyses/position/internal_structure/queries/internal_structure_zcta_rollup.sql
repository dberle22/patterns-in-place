-- ZCTA membership is established through population-basis tract edges. The
-- stored ZCTA classification remains a weighted tract rollup, never a USPS ZIP label.
WITH market_zctas AS (
    SELECT DISTINCT a.target_geo_id AS zip_geoid
    FROM mart_geography.allocation_edges AS a
    JOIN mart_geography.rollup_tract_to_cbsa AS r ON a.source_geo_id = r.tract_geoid
    WHERE r.cbsa_code = '__CBSA_CODE__'
      AND a.source_geo_level = 'tract' AND a.target_geo_level = 'zcta'
      AND a.weight_basis = 'population' AND a.weight > 0
)
SELECT mz.zip_geoid, i.display_name AS zcta_name, z.primary_zone_type,
       z.dominant_zone_type, z.dominant_zone_share, z.secondary_zone_type,
       z.secondary_zone_share, z.is_mixed_zone, z.tract_count,
       z.total_weighted_population, z.source_vintage, z.source
FROM market_zctas AS mz
LEFT JOIN mart_intelligence.intelligence_zones_zcta AS z USING (zip_geoid)
LEFT JOIN mart_geography.identity_current AS i ON i.geo_level = 'zcta' AND i.geo_id = mz.zip_geoid
ORDER BY z.total_weighted_population DESC NULLS LAST, mz.zip_geoid;
