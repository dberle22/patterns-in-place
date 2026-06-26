# Data Dictionary: staging LEHD LODES RAC

## Overview
- Schema: `staging`
- Family: `LEHD LODES`
- Contract scope: tract-level residence-area staging table produced by [`foundations/etl/staging/get_lehd_lodes.R`](../../../etl/staging/get_lehd_lodes.R)
- Documentation rule: the public upstream artifact is a block-grain RAC file, but the managed staging contract aggregates to tract during ingest and does not persist block rows

## Contract Summary
- Materialized table: `lehd_lodes_rac`
- Current first-pass scope: latest-year `LODES8` RAC, `JT02` all-private jobs, `S000` total segment
- Grain: one row per `tract_geoid + year`
- Common key columns used across the table: `state`, `state_fips`, `county_geoid`, `cbsa_code`, `tract_geoid`, `year`, `lodes_type`, `job_type`, `segment`
- Current managed time coverage: one annual snapshot; current expected first managed year is `2023`

## Scope Decisions
- Geography:
  - upstream file is block-grain RAC
  - managed staging aggregates to tract immediately after crosswalk validation
  - county and CBSA are helper columns derived from the provider crosswalk
- Job scope:
  - only `job_type = 'JT02'` all-private jobs are retained in the first pass
  - only `segment = 'S000'` is retained because that file already carries the full wide RAC payload needed downstream
- Time handling:
  - source files are annual snapshots
  - staging retains one row per tract-year
- Coverage handling:
  - RAC is currently more complete than WAC in the latest LODES release, but staging should still treat provider file availability as state-year specific rather than assumed universal

## Shared Columns
- Geography and identifiers: `state`, `state_fips`, `county_geoid`, `cbsa_code`, `tract_geoid`
- Time and source slices: `year`, `lodes_type`, `job_type`, `segment`
- Provenance: `release_vintage`, `release_format_version`, `source_createdate`, `xwalk_createdate`, `source_file`
- Core worker totals: `C000`
- Worker age bands: `CA01`, `CA02`, `CA03`
- Worker earnings bands: `CE01`, `CE02`, `CE03`
- Broad industry sectors: `CNS01` through `CNS20`
- Race / ethnicity helpers: `CR01` through `CR05`, `CR07`
- Worker sex: `CT01`, `CT02`
- Worker education: `CD01`, `CD02`, `CD03`, `CD04`
- Worker ethnicity / schooling complements: `CS01`, `CS02`

## Aggregation Rules
- Read the source block-level RAC file for one state-year.
- Validate that every `h_geocode` joins the published state `xwalk`.
- Derive `tract_geoid` from the provider crosswalk.
- Sum all numeric payload columns from block to tract.
- Carry one provenance row per tract snapshot:
  - `state`
  - `year`
  - `job_type`
  - `segment`
  - source and crosswalk createdate fields

## Lineage
- [`foundations/etl/staging/get_lehd_lodes.R`](../../../etl/staging/get_lehd_lodes.R) downloads or reuses the scoped state RAC source file and state crosswalk, validates block coverage, aggregates the RAC payload to tract, validates uniqueness at `tract_geoid + year`, and writes `staging.lehd_lodes_rac`.
- Provider-level source structure, deferred OD notes, and current latest-year caveats live in [`../../sources/source__lehd_lodes.md`](../../sources/source__lehd_lodes.md).

## Data Quality Notes
- Verify uniqueness at `tract_geoid + year`.
- Confirm `lodes_type = 'RAC'`, `job_type = 'JT02'`, and `segment = 'S000'` for all staged rows in the current first pass.
- Confirm `tract_geoid` is always an `11`-digit tract GEOID and `county_geoid` is always a `5`-digit county GEOID.
- Confirm every staged tract row is traceable to block rows that joined the provider crosswalk successfully.
- RAC does not include WAC-only firm age and firm size fields; that asymmetry is source-native and should be preserved in staging rather than forced into null placeholder columns.

## Known Gaps / To-Dos
- Document final national row count and state coverage after the first all-states run completes.
- If we later decide to keep race / ethnicity / sex in the canonical Silver surface, that should be settled in Silver rather than by changing the staging grain.
- OD remains outside this staging contract and should land as its own future source-family contract if and when Deep Dive flow work begins.
