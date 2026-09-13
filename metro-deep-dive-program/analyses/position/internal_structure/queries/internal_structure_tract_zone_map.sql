-- Current Geography products are approved for this consumer while the
-- Geography contract is updated. Zone types remain upstream Phase 7 labels.
SELECT z.tract_geoid, z.zone_type, z.county_geoid, z.county_name,
       g.geom_wkb AS geometry_wkb
FROM mart_intelligence.intelligence_zones AS z
JOIN geo.tracts_all_us AS g USING (tract_geoid)
WHERE z.cbsa_code = '__CBSA_CODE__';
