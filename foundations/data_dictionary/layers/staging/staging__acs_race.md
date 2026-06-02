# Data Dictionary: staging ACS Race Family

## Overview
- Schema: `staging`
- Family: `ACS Race`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_race.R`](../../../scripts/etl/staging/get_acs_race.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_race_us` | ACS 5-year wide landing |
| Region | `acs_race_region` | ACS 5-year wide landing |
| Division | `acs_race_division` | ACS 5-year wide landing |
| State | `acs_race_state` | ACS 5-year wide landing |
| County | `acs_race_county` | ACS 5-year wide landing |
| Place | `acs_race_place` | ACS 5-year wide landing |
| ZCTA | `acs_race_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_race_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_race_tract_fl`, `acs_race_tract_ga`, `acs_race_tract_nc`, `acs_race_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 21
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `pop_total_b03002E`, `pop_total_b03002M`, `white_nonhispE`, `white_nonhispM`, `black_nonhispE`, `black_nonhispM`, `amind_nonhispE`, `amind_nonhispM`, `asian_nonhispE`, `asian_nonhispM`, `pacisl_nonhispE`, `pacisl_nonhispM`, `other_nonhispE`, `other_nonhispM`, `two_plus_nonhispE`, `two_plus_nonhispM`, `hispanic_anyE`, `hispanic_anyM`

## Lineage
- [`scripts/etl/staging/get_acs_race.R`](../../../scripts/etl/staging/get_acs_race.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
