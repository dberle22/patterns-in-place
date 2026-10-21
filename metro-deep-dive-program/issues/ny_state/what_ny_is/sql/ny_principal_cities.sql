-- Map 2 orientation dots use the principal cities of each NY-touching metro.
-- The crosswalk can name several cities per CBSA; retain them all for review.
-- These are representative points on Census display geometry, suitable for
-- drawing only. They are not city halls, job centers or analytical centroids.
SELECT
    p.cbsa_code,
    p.primary_city,
    p.state_fips || p.place_fips AS place_geoid,
    p.vintage AS cbsa_vintage,
    g.boundary_vintage AS place_boundary_vintage,
    ST_Y(ST_PointOnSurface(g.geom)) AS lat,
    ST_X(ST_PointOnSurface(g.geom)) AS lon,
    ST_AsWKB(ST_PointOnSurface(g.geom)) AS geom_wkb
FROM silver.xwalk_cbsa_primary_city AS p
JOIN silver.xwalk_cbsa_state AS s
  ON s.cbsa_code = p.cbsa_code AND s.state_fips = '36'
JOIN geo.places_display AS g
  ON g.place_geoid = p.state_fips || p.place_fips
WHERE p.cbsa_type = 'Metropolitan Statistical Area'
  AND p.state_fips = '36'
ORDER BY p.cbsa_code;
