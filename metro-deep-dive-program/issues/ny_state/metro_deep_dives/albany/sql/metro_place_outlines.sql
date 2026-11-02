-- Census Place outlines in the metro (display geometry, lightly simplified), with
-- population, kind (city / CDP / village) and the OMB 2023 principal-city flag.
-- Drawing only (R11): measures come from analysis tables.
SELECT
  m.place_geoid,
  d.NAME AS place_name,
  CASE d.LSAD WHEN '25' THEN 'city' WHEN '57' THEN 'CDP' WHEN '47' THEN 'village' ELSE d.LSAD END AS place_kind,
  m.target_numerator AS population_in_metro,
  pc.primary_city IS NOT NULL AS is_principal_city,
  ST_AsWKB(ST_SimplifyPreserveTopology(d.geom, 0.0002)) AS geom_wkb
FROM mart_geography.place_to_cbsa_membership AS m
JOIN geo.places_display AS d
  ON d.place_geoid = m.place_geoid
LEFT JOIN silver.xwalk_cbsa_primary_city AS pc
  ON pc.cbsa_code = m.target_geo_id
 AND pc.state_fips || pc.place_fips = m.place_geoid
WHERE m.target_geo_id = '__CBSA_CODE__'
  AND m.weight_basis = 'population'
ORDER BY m.target_numerator DESC NULLS LAST
