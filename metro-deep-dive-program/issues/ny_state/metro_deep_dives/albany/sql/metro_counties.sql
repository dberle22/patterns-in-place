-- Metro counties: OMB 2023 Central/Outlying flag (Q6 county context), ACS population
-- for 2008-12 and 2020-24 (non-overlapping 5-year windows), display geometry.
SELECT
  ctx.county_geoid,
  ctx.county_name,
  ctx.county_flag,
  p24.pop_total AS pop_2024,
  p12.pop_total AS pop_2012,
  p24.pop_total / p12.pop_total - 1 AS pop_growth,
  g.land_area_sqmi,
  g.geom_wkb
FROM mart_explanation_q6.cbsa_county_context AS ctx
JOIN geo.counties AS g
  ON g.county_geoid = ctx.county_geoid
LEFT JOIN gold.population_demographics AS p24
  ON p24.geo_level = 'county' AND p24.geo_id = ctx.county_geoid AND p24.year = 2024
LEFT JOIN gold.population_demographics AS p12
  ON p12.geo_level = 'county' AND p12.geo_id = ctx.county_geoid AND p12.year = 2012
WHERE ctx.cbsa_code = '__CBSA_CODE__'
ORDER BY ctx.county_flag, ctx.county_name
