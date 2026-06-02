# Data Dictionary: staging BPS Family

## Overview
- Schema: `staging`
- Family: `BPS`
- Contract scope: source/theme family contract covering 5 materialized table(s) produced by [`scripts/etl/staging/get_bps.R`](../../../scripts/etl/staging/get_bps.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Region | `bps_region` | Regional permit summary |
| Division | `bps_division` | Division permit summary |
| State | `bps_state` | State permit summary |
| County | `bps_county` | County permit summary with county identifiers |
| Place | `bps_place` | Place permit summary with place and county identifiers |

## Contract Summary
- This group has multiple contract variants across tables.
- Variant count: 5
  - Variant 1: 22 columns (1 table(s))
    - Tables: `bps_division`
  - Variant 2: 22 columns (1 table(s))
    - Tables: `bps_region`
  - Variant 3: 22 columns (1 table(s))
    - Tables: `bps_state`
  - Variant 4: 26 columns (1 table(s))
    - Tables: `bps_county`
  - Variant 5: 30 columns (1 table(s))
    - Tables: `bps_place`
- Common key columns used across the family: `LOCATION_TYPE`, `YEAR`, `PERIOD`

## Shared Columns
- `FILE_NAME`, `LOCATION_TYPE`, `PERIOD`, `SURVEY_DATE`, `YEAR`, `TOTAL_BLDGS`, `TOTAL_UNITS`, `TOTAL_VALUE`, `BLDGS_1_UNIT`, `BLDGS_2_UNITS`, `BLDGS_3_4_UNITS`, `BLDGS_5_UNITS`, `UNITS_1_UNIT`, `UNITS_2_UNITS`, `UNITS_3_4_UNITS`, `UNITS_5_UNITS`, `VALUE_1_UNIT`, `VALUE_2_UNITS`, `VALUE_3_4_UNITS`, `VALUE_5_UNITS`

## Lineage
- [`scripts/etl/staging/get_bps.R`](../../../scripts/etl/staging/get_bps.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
