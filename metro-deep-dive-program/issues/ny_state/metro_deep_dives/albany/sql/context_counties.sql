-- Counties around the metro, display geometry, drawn as faint grey context.
-- NY plus the neighboring states the Capital Region frame can reach.
SELECT
  county_geoid,
  county_name,
  state_fips,
  geom_wkb
FROM geo.counties
WHERE state_fips IN ('36', '50', '25', '09')
ORDER BY county_geoid
