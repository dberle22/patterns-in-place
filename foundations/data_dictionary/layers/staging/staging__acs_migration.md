# Data Dictionary: staging ACS Migration Family

## Overview
- Schema: `staging`
- Family: `ACS Migration`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_migration.R`](../../../scripts/etl/staging/get_acs_migration.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_migration_us` | ACS 5-year wide landing |
| Region | `acs_migration_region` | ACS 5-year wide landing |
| Division | `acs_migration_division` | ACS 5-year wide landing |
| State | `acs_migration_state` | ACS 5-year wide landing |
| County | `acs_migration_county` | ACS 5-year wide landing |
| Place | `acs_migration_place` | ACS 5-year wide landing |
| ZCTA | `acs_migration_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_migration_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_migration_tract_fl`, `acs_migration_tract_ga`, `acs_migration_tract_nc`, `acs_migration_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 23
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `mig_totalE`, `mig_totalM`, `mig_same_houseE`, `mig_same_houseM`, `mig_moved_same_cntyE`, `mig_moved_same_cntyM`, `mig_moved_same_stE`, `mig_moved_same_stM`, `mig_moved_diff_stE`, `mig_moved_diff_stM`, `mig_moved_abroadE`, `mig_moved_abroadM`, `pop_nativity_totalE`, `pop_nativity_totalM`, `pop_nativeE`, `pop_nativeM`, `pop_foreign_bornE`, `pop_foreign_bornM`, `pop_foreign_born_citizenE`, `pop_foreign_born_citizenM`

## Lineage
- [`scripts/etl/staging/get_acs_migration.R`](../../../scripts/etl/staging/get_acs_migration.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
