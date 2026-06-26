# Data Dictionary: silver.lehd_lodes_rac

## Overview
- **Table**: `silver.lehd_lodes_rac`
- **Purpose**: Silver labor-geography table that standardizes staged LODES RAC tract rows, preserves tract as the canonical base, and derives county, CBSA, state, and division rollups for downstream neighborhood opportunity and jobs-housing relationship analysis.
- **Status**: materialized from the current tract-first staging implementation.
- **Row count**: `88,158`

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year`
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Current geography coverage**: `tract`, `county`, `cbsa`, `state`, and `division`
- **Current time coverage**: `year` min=`2023`, max=`2023`

## Contract Summary
- Input: `staging.lehd_lodes_rac`
- Base geography: tract
- Geography policy:
  - keep tract as the canonical Silver base geography
  - validate tract rows against `silver.xwalk_tract_county`
  - derive `county`, `cbsa`, `state`, and `division` from the validated tract base rather than from separate published geography files
  - exclude Alaska `02261` and any non-platform tract geographies consistent with broader geography policy
- Analytical surface:
  - preserve total resident workers
  - preserve age bands
  - preserve earnings bands
  - preserve broad industry sectors
  - preserve education bands
- Defer from the first canonical Silver contract:
  - race / ethnicity
  - sex

## Recommended Canonical Columns
- Geography: `geo_level`, `geo_id`, `geo_name`
- Time: `year`
- Core worker totals:
  - `workers_total`
- Age composition:
  - `workers_age_29_or_younger`
  - `workers_age_30_54`
  - `workers_age_55_plus`
- Earnings composition:
  - `workers_earnings_low`
  - `workers_earnings_mid`
  - `workers_earnings_high`
- Education composition:
  - `workers_edu_less_than_hs`
  - `workers_edu_hs_or_some_college`
  - `workers_edu_bachelors_or_advanced`
  - `workers_edu_not_available`
- Broad industry sectors:
  - resident-worker equivalents of the retained `CNS*` sector counts

## Source Mappings
- `workers_total` <- `C000`
- age bands <- `CA01`, `CA02`, `CA03`
- earnings bands <- `CE01`, `CE02`, `CE03`
- education bands <- `CD01`, `CD02`, `CD03`, `CD04`
- tract geography key <- `tract_geoid`

## Recommended Derived Measures
- `pct_workers_age_29_or_younger` = `workers_age_29_or_younger / workers_total`
- `pct_workers_age_30_54` = `workers_age_30_54 / workers_total`
- `pct_workers_age_55_plus` = `workers_age_55_plus / workers_total`
- `pct_workers_earnings_low` = `workers_earnings_low / workers_total`
- `pct_workers_earnings_mid` = `workers_earnings_mid / workers_total`
- `pct_workers_earnings_high` = `workers_earnings_high / workers_total`
- sector shares recomputed from tract totals rather than copied from staging

## Standardization Rules
- Set `geo_level = 'tract'` and `geo_id = tract_geoid`.
- Join tract metadata from the canonical geography backbone so `geo_name` and geography validation do not depend on staged helper columns alone.
- Rename the raw `C*` payload into analytical names that can be understood without consulting LODES documentation.
- Drop row-level helper geography and release metadata fields after rollups; managed crosswalks and source documentation remain the authoritative place for that context.

## Rollup Plan
- Keep tract as the source-of-truth base.
- Build county rows by summing validated tract rows by `county_geoid + year`.
- Build CBSA rows by summing validated tract rows after joining the tract-to-county backbone to `silver.xwalk_cbsa_county`.
- Build state rows by summing tract or county rows to `state_fips + year`.
- Build division rows by joining state rows to `silver.xwalk_state_region`.
- Recompute shares after each rollup from the rolled-up totals rather than averaging tract shares.
- Exclude staged tract rows that fail canonical geography validation from the rolled-up outputs until the crosswalk issue is resolved.
- Expect CBSA totals to be lower than county/state/division totals because non-metro counties do not belong to any CBSA and therefore stay out of the CBSA rollup.

Expected geography pattern in Silver:
- `tract`: canonical neighborhood base
- `county`: tract-derived
- `cbsa`: tract-derived through county membership
- `state`: tract-derived
- `division`: state-derived

## Gold Handoff
- Primary Gold home: `gold.economics_lodes_wide`
- Intended Gold use:
  - residential labor composition inputs for Deep Dive zone analysis
  - denominator-side context for comparing where workers live versus where jobs are located
  - joined jobs-versus-resident-workers comparison once RAC is paired with WAC

## Data Quality Notes
- Validate uniqueness at `geo_level + geo_id + year`.
- Confirm every tract row intended for retained Silver output maps to `silver.xwalk_tract_county`.
- Confirm `workers_total` and all retained count columns are non-negative.
- Current live staging validation found `1` RAC tract row missing from `silver.xwalk_tract_county`:
  - `12057980100` in Florida
- Silver should exclude or explicitly quarantine that unmatched tract before county / CBSA / state / division rollups so geography totals remain governed.
- RAC intentionally lacks WAC-only firm age and firm size fields; do not fabricate parallel columns in Silver.
- Current landed Silver coverage:
  - `tract`: `84,029` rows / `84,029` geographies
  - `county`: `3,144` rows / `3,144` geographies
  - `cbsa`: `925` rows / `925` geographies
  - `state`: `51` rows / `51` geographies
  - `division`: `9` rows / `9` geographies

## Lineage
1. [`foundations/etl/staging/get_lehd_lodes.R`](../../../etl/staging/get_lehd_lodes.R) lands the tract-level RAC staging table.
2. [`foundations/etl/silver/lehd_lodes_silver.R`](../../../etl/silver/lehd_lodes_silver.R) normalizes the staged tract rows, renames the retained analytical fields, validates geography coverage, derives county / CBSA / state / division rollups from the tract base, and writes `silver.lehd_lodes_rac`.

## Known Gaps / To-Dos
- Decide the exact industry rollup strategy for `CNS01-20`: preserve the full published matrix in Silver or collapse immediately to broader platform families.
- Decide whether any race / ethnicity / sex fields should survive into the canonical analytical surface or remain staging-only.
- Add the YAML companion if we decide to keep YAML as a required artifact for this table family.
