-- US states bordering NY, display geometry, drawn as faint grey context.
SELECT
  state_fips,
  state_abbr,
  state_name,
  geom_wkb
FROM geo.states
WHERE state_abbr IN ('NJ', 'PA', 'CT', 'MA', 'VT')
ORDER BY state_abbr
