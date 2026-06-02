# Data Dictionary: staging BEA Metadata Family

## Overview
- Schema: `staging`
- Family: `BEA Metadata`
- Contract scope: source/theme family contract covering 2 materialized table(s) produced by [`scripts/etl/staging/get_bea.R`](../../../scripts/etl/staging/get_bea.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Coverage Matrix
This family is not replicated by a single geography ladder; the matrix below lists the materialized contract slices that roll into the same source/theme dictionary.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Regional table registry | `bea_regional_tables` | Reference list of BEA regional tables discovered during ingest |
| Regional line-code registry | `bea_regional_line_codes` | Reference list of BEA regional line codes used by downstream staging families |

## Contract Summary
- This group has multiple contract variants across tables.
- Variant count: 2
  - Variant 1: 3 columns (1 table(s))
    - Tables: `bea_regional_tables`
  - Variant 2: 5 columns (1 table(s))
    - Tables: `bea_regional_line_codes`
- Common key columns used across the family: `dataset`

## Shared Columns
- `dataset`

## Lineage
- The ingest script derives these metadata tables during parameter discovery and currently writes them to `silver`, even though they remain documented with the BEA staging family contracts.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
