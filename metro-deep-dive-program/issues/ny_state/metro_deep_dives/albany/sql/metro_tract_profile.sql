-- Metro tracts: Phase 7 zone type plus the raw values of the inputs that define it
-- (gold.intelligence_zone_inputs, before imputation and polarity), the Census Place holding
-- most of the tract's population (for reading the map; null = outside any place), and geometry.
WITH main_place AS (
  SELECT a.source_geo_id AS tract_geoid, d.NAME AS main_place, a.weight AS main_place_weight
  FROM silver.xwalk_allocation AS a
  JOIN geo.places_display AS d ON d.place_geoid = a.target_geo_id
  WHERE a.source_geo_level = 'tract' AND a.target_geo_level = 'place' AND a.weight_basis = 'population'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY a.source_geo_id ORDER BY a.weight DESC) = 1
)
SELECT
  z.tract_geoid,
  z.county_name,
  z.zone_type,
  i.pct_ba_plus,
  i.median_hh_income,
  i.pov_rate,
  i.owner_occ_rate,
  i.pct_age_over_64,
  i.pct_same_house,
  i.pop_weighted_density_sqmi,
  i.pct_commute_walk,
  i.jobs_per_resident,
  mp.main_place,
  mp.main_place_weight,
  g.geom_wkb
FROM mart_intelligence.intelligence_zones AS z
JOIN gold.intelligence_zone_inputs AS i ON i.tract_geoid = z.tract_geoid
JOIN geo.tracts_all_us AS g ON g.tract_geoid = z.tract_geoid
LEFT JOIN main_place AS mp ON mp.tract_geoid = z.tract_geoid
WHERE z.cbsa_code = '__CBSA_CODE__'
