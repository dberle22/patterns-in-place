# Data Dictionary: staging HUD FMR Family

## Overview
- Schema: `staging`
- Family: `HUD FMR`
- Contract scope: source/theme family contract covering 3 materialized table(s) produced by [`scripts/etl/staging/get_hud_fmr.R`](../../../scripts/etl/staging/get_hud_fmr.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Coverage Matrix
This family is not replicated by a single geography ladder; the matrix below lists the materialized contract slices that roll into the same source/theme dictionary.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County FMR | `hud_fmr_county` | Fair Market Rent county-area landing table |
| ZIP FMR | `hud_fmr_zip` | ZIP-level small area FMR landing table |
| County rent50 | `hud_rent50_county` | 50th percentile rent companion table |

## Contract Summary
- This group has multiple contract variants across tables.
- Variant count: 3
  - Variant 1: 11 columns (1 table(s))
    - Tables: `hud_fmr_zip`
  - Variant 2: 14 columns (1 table(s))
    - Tables: `hud_fmr_county`
  - Variant 3: 15 columns (1 table(s))
    - Tables: `hud_rent50_county`
- Common key columns used across the family: `hud_area_code`, `period`

## Shared Columns
- `hud_area_code`, `hud_area_name`, `period`

## Lineage
- [`scripts/etl/staging/get_hud_fmr.R`](../../../scripts/etl/staging/get_hud_fmr.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
