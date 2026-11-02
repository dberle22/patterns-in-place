-- One display point per Census Place in the metro, with the OMB 2023 principal-city flag.
-- Representative points on display geometry: for drawing labels only.
SELECT
  m.place_geoid,
  d.NAME AS place_name,
  pc.primary_city IS NOT NULL AS is_principal_city,
  ST_AsWKB(ST_PointOnSurface(d.geom)) AS geom_wkb
FROM mart_geography.place_to_cbsa_membership AS m
JOIN geo.places_display AS d
  ON d.place_geoid = m.place_geoid
LEFT JOIN silver.xwalk_cbsa_primary_city AS pc
  ON pc.cbsa_code = m.target_geo_id
 AND pc.state_fips || pc.place_fips = m.place_geoid
WHERE m.target_geo_id = '__CBSA_CODE__'
  AND m.weight_basis = 'population'
ORDER BY d.NAME
