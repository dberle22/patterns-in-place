# Data Dictionary: staging Zillow ZORI Family

## Overview
- Schema: `staging`
- Family: `Zillow ZORI`
- Contract scope: source/theme family contract covering 3 materialized table(s) produced by [`scripts/etl/staging/get_zillow.R`](../../../scripts/etl/staging/get_zillow.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County | `zillow_zori_county` | Monthly observed rent index by county |
| City | `zillow_zori_city` | Monthly observed rent index by city |
| ZIP code | `zillow_zori_zip_code` | Monthly observed rent index by ZIP code |

## Contract Summary
- This group has multiple contract variants across tables.
- Variant count: 3
  - Variant 1: 9 columns (1 table(s))
    - Tables: `zillow_zori_city`
  - Variant 2: 10 columns (1 table(s))
    - Tables: `zillow_zori_zip_code`
  - Variant 3: 11 columns (1 table(s))
    - Tables: `zillow_zori_county`
- Common key columns used across the family: `region_type`, `date`

## Shared Columns
- `region_type`, `state`, `metro`, `county_name`, `date`, `year`, `month`, `zori`

## Lineage
- [`scripts/etl/staging/get_zillow.R`](../../../scripts/etl/staging/get_zillow.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
