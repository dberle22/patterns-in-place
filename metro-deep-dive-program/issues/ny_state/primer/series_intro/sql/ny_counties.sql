-- NY counties, display geometry (2024 Census cartographic, shoreline clipped).
SELECT
  county_geoid,
  county_name,
  land_area_sqmi,
  geom_wkb
FROM geo.counties
WHERE state_fips = '36'
ORDER BY county_geoid
