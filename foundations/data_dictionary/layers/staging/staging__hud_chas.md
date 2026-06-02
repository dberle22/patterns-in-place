# Data Dictionary: staging HUD CHAS Family

## Overview
- Schema: `staging`
- Family: `HUD CHAS`
- Contract scope: source/theme family contract covering 3 materialized table(s) produced by [`scripts/etl/staging/get_hud_chas.R`](../../../scripts/etl/staging/get_hud_chas.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| State | `hud_chas_state` | Comprehensive Housing Affordability Strategy tabulation |
| County | `hud_chas_county` | Comprehensive Housing Affordability Strategy tabulation |
| Place | `hud_chas_place` | Comprehensive Housing Affordability Strategy tabulation |

## Contract Summary
- This group has multiple contract variants across tables.
- Variant count: 3
  - Variant 1: 16 columns (1 table(s))
    - Tables: `hud_chas_state`
  - Variant 2: 17 columns (1 table(s))
    - Tables: `hud_chas_place`
  - Variant 3: 17 columns (1 table(s))
    - Tables: `hud_chas_county`
- Common key columns used across the family: `geoid`, `variable`, `year`, `geo_level`

## Shared Columns
- `source`, `sumlevel`, `geoid`, `name`, `st`, `variable`, `estimate`, `line_type`, `tenure`, `household_income`, `household_type`, `cost_burden`, `chas_period`, `year`, `geo_level`

## Lineage
- [`scripts/etl/staging/get_hud_chas.R`](../../../scripts/etl/staging/get_hud_chas.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
