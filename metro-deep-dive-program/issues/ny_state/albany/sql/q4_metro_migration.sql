-- IRS SOI county-to-county migration for the metros in __CBSA_CODES__, years __YEAR_FROM__–__YEAR_TO__
-- (year = destination tax year; 2022 = moves between the 2021 and 2022 filings).
-- direction 'in': people moving into a member county from a county outside that metro; 'out': the reverse.
-- People = exemptions (an approximation of persons); households = returns.
-- County pairs only: IRS suppresses pairs under 20 returns, so these sums undercount small, scattered flows.
WITH members AS (
  SELECT cbsa_code, county_geoid FROM silver.xwalk_cbsa_county WHERE cbsa_code IN (__CBSA_CODES__)
),
flows AS (
  -- Origin and destination are stored the right way round since the 2026-10-26 fix
  -- (foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md); the notebook's guard fails if that regresses.
  SELECT year, origin_geo_id, dest_geo_id, n_returns, n_exemptions, agi
  FROM silver.irs_migration_flows
  WHERE geo_level = 'county' AND year BETWEEN __YEAR_FROM__ AND __YEAR_TO__
)
SELECT m.cbsa_code, 'in' AS direction, f.year, f.origin_geo_id AS other_county_geoid,
       f.n_returns AS households, f.n_exemptions AS people, f.agi
FROM flows AS f
JOIN members AS m ON f.dest_geo_id = m.county_geoid
LEFT JOIN members AS same ON same.cbsa_code = m.cbsa_code AND same.county_geoid = f.origin_geo_id
WHERE same.county_geoid IS NULL
UNION ALL
SELECT m.cbsa_code, 'out', f.year, f.dest_geo_id, f.n_returns, f.n_exemptions, f.agi
FROM flows AS f
JOIN members AS m ON f.origin_geo_id = m.county_geoid
LEFT JOIN members AS same ON same.cbsa_code = m.cbsa_code AND same.county_geoid = f.dest_geo_id
WHERE same.county_geoid IS NULL
