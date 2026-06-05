# Track 5 Handoff — Opportunity Zones + FHFA Underserved Areas

Read `PLATFORM_COMPLETION_PLAN.md` (Track 5) and `AGENTS.md` before starting. The decisions below are final — do not re-research them.

## Decisions

- **OZ source:** HUD CDFI Fund CSV (~8,764 tracts, no API key). Zero-pad `geoid` to 11 digits.
- **FHFA Underserved source:** `https://www.fhfa.gov/data/underserved-areas` — current year only. Columns: `tract_geoid`, `year`, `is_underserved`, `is_low_income_area`, `is_minority_area`, `is_disaster_area`.
- **Silver OZ:** Full tract coverage (`is_opportunity_zone = TRUE/FALSE`, ~85K rows, no `year`). Derive county + CBSA rollups (`oz_tract_count`, `total_tract_count`, `pct_oz_tracts`) via `silver.xwalk_tract_county` + `silver.xwalk_cbsa_county`.
- **Silver FHFA Underserved:** `geo_level + geo_id + year` grain. Same county + CBSA rollup pattern.
- **Gold:** New table `gold.dim_policy_designations`. Do NOT modify `gold.dim_geo`.

## Style references

- Staging: `foundations/etl/staging/get_chr.R`
- Silver: `foundations/etl/silver/fhfa_hpi_silver.R`
- Gold: `foundations/etl/gold/gold_housing_market_wide.sql`
- Dict: any existing `.yml` + `.md` pair in `layers/silver/` or `layers/gold/`

## Stop points

**After staging** — report row counts for both tables and confirm tract FIPS zero-padding is clean.

**After Silver** — report row counts by `geo_level` for both tables and match rate for the tract → county → CBSA joins.

**After Gold + pipeline wiring** — report Gold row counts by `geo_level`, spot-check a known OZ-heavy metro, confirm `pipeline_manifest.yml` sequence is correct, and mark tasks 5.2a–5.9 complete in `PLATFORM_COMPLETION_PLAN.md`.
