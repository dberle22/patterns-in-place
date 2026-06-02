# Data Dictionary: staging IRS Migration Family

## Overview
- Schema: `staging`
- Family: `IRS Migration`
- Contract scope: source/theme family contract covering 2 materialized table(s) produced by [`scripts/etl/staging/get_irs_migration.R`](../../../scripts/etl/staging/get_irs_migration.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Coverage Matrix
This family is not replicated by a single geography ladder; the matrix below lists the materialized contract slices that roll into the same source/theme dictionary.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County inflow | `irs_inflow_migration_county` | County-destination inflow records |
| State inflow | `irs_inflow_migration_state` | State-destination inflow records |

## Contract Summary
- This group has multiple contract variants across tables.
- Variant count: 2
  - Variant 1: 11 columns (1 table(s))
    - Tables: `irs_inflow_migration_state`
  - Variant 2: 15 columns (1 table(s))
    - Tables: `irs_inflow_migration_county`
- Common key columns used across the family: `flow_id`, `year`

## Shared Columns
- `flow_id`, `year`, `origin_year`, `dest_year`, `dest_state_fips`, `origin_state_fips`, `n_returns`, `n_exemptions`, `agi_thousands`, `agi`

## Lineage
- [`scripts/etl/staging/get_irs_migration.R`](../../../scripts/etl/staging/get_irs_migration.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
