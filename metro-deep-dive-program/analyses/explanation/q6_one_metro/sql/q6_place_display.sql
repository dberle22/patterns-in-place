SELECT profile.place_geoid, profile.place_name, profile.direct_population, display.geom_wkb
FROM (
  WITH membership AS (
    SELECT place_geoid FROM mart_geography.place_to_cbsa_membership
    WHERE target_geo_id='__CBSA_CODE__' AND weight_basis='population'
  )
  SELECT membership.place_geoid, population.geo_name AS place_name, population.pop_total AS direct_population
  FROM membership JOIN gold.population_demographics AS population
    ON population.geo_id=membership.place_geoid AND lower(population.geo_level)='place' AND population.year=2024
) AS profile
JOIN geo.places_display AS display USING (place_geoid);
