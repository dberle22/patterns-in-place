# Data Dictionary: staging BLS LAUS Family

## Overview
- Schema: `staging`
- Family: `BLS LAUS`
- Contract scope: source/theme family contract covering 1 materialized table(s) produced by [`scripts/etl/staging/get_bls_laus.R`](../../../scripts/etl/staging/get_bls_laus.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County | `bls_laus_county` | County-level Local Area Unemployment Statistics landing table |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 12
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `geo_level`, `geo_id`, `period`

## Shared Columns
- `geo_level`, `geo_id`, `state_fips_code`, `county_fips_code`, `county_name`, `period`, `labor_force`, `employed`, `unemployed`, `unemployment_rate_percent`, `src`, `version`

## Lineage
- [`scripts/etl/staging/get_bls_laus.R`](../../../scripts/etl/staging/get_bls_laus.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
