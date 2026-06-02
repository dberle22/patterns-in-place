# Data Dictionary: staging BEA CAINC1 Family

## Overview
- Schema: `staging`
- Family: `BEA CAINC1`
- Contract scope: source/theme family contract covering 3 materialized table(s) produced by [`scripts/etl/staging/get_bea.R`](../../../scripts/etl/staging/get_bea.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| CBSA | `bea_regional_cbsa_cainc1` | Regional personal income headline series by metropolitan area |
| County | `bea_regional_county_cainc1` | Regional personal income headline series by county |
| State | `bea_regional_state_cainc1` | Regional personal income headline series by state |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 12
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `table`, `geo_level`, `geo_id`, `period`, `line_code`

## Shared Columns
- `code`, `table`, `geo_level`, `geo_id`, `geo_name`, `period`, `line_code`, `unit_raw`, `unit_mult`, `value_raw`, `value`, `note_ref`

## Lineage
- [`scripts/etl/staging/get_bea.R`](../../../scripts/etl/staging/get_bea.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
