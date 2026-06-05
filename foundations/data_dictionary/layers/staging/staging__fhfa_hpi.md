# Data Dictionary: staging FHFA HPI Family

## Overview
- Schema: `staging`
- Family: `FHFA HPI`
- Contract scope: source/theme family contract covering 6 materialized table(s) produced by [`foundations/etl/staging/get_fhfa.R`](../../../etl/staging/get_fhfa.R)
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially

## Coverage Matrix
This family is replicated across the published FHFA annual geography files rather than a single ladder sourced from one workbook.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| U.S. | `fhfa_hpi_us` | National annual developmental HPI rows keyed to a fixed `US` identifier |
| State | `fhfa_hpi_state` | Annual state HPI rows keyed to two-digit state FIPS |
| CBSA | `fhfa_hpi_cbsa` | Annual CBSA HPI rows keyed to FHFA CBSA code |
| County | `fhfa_hpi_county` | Annual county HPI rows keyed to five-digit county FIPS |
| ZIP5 | `fhfa_hpi_zip5` | Annual five-digit ZIP HPI rows keyed to ZIP code |
| Tract | `fhfa_hpi_tract` | Annual tract HPI rows keyed to 11-digit tract GEOID |

## Contract Summary
- This group has multiple contract variants across tables.
- Variant count: 3
  - Variant 1: 10 columns (3 table(s))
    - Tables: `fhfa_hpi_us`, `fhfa_hpi_cbsa`, `fhfa_hpi_zip5`
  - Variant 2: 11 columns (2 table(s))
    - Tables: `fhfa_hpi_county`, `fhfa_hpi_tract`
  - Variant 3: 13 columns (1 table(s))
    - Tables: `fhfa_hpi_state`
- Common key columns used across the family: `place_id`, `yr`

## Shared Columns
- Shared geography contract: `place_name`, `place_id`
- Shared time and source contract: `hpi_flavor`, `frequency`, `level`, `yr`
- Shared FHFA annual metrics: `annual_change_pct`, `hpi`, `hpi_1990_base`, `hpi_2000_base`
- Geography-specific helper fields: `state_name`, `state_abbr`, `state_fips`

## Lineage
- [`foundations/etl/staging/get_fhfa.R`](../../../etl/staging/get_fhfa.R) downloads FHFA annual HPI files for U.S., state, CBSA, county, ZIP5, and tract geographies, normalizes each file into a source-faithful annual staging table, validates the geography key shape, and writes the materialized tables listed above.

## Data Quality Notes
- Verify row uniqueness at `place_id + yr` for each staged table before Silver transforms.
- Confirm the annual geography key format by slice:
  - `fhfa_hpi_us`: fixed `US`
  - `fhfa_hpi_state`: two-digit state FIPS
  - `fhfa_hpi_cbsa`: FHFA CBSA code
  - `fhfa_hpi_county`: five-digit county FIPS
  - `fhfa_hpi_zip5`: five-digit ZIP
  - `fhfa_hpi_tract`: 11-digit tract GEOID
- Validate expected time coverage and geography coverage against the annual FHFA source files.
- Treat ZIP5 as ZIP geography in staging; any ZCTA proxy decision belongs to downstream Silver modeling, not to source landing.
- County and tract series can contain sparse or unstable rows in low-transaction areas; retain those rows in staging for source fidelity.

## Known Gaps / To-Dos
- The family contract is now broader than the first-pass Silver scope. Track 3.4 still needs an explicit decision on which staged geographies should flow into `silver.fhfa_hpi`.
- Add landed row counts and any unmatched-CBSA notes after the first full staging refresh is run and verified.
