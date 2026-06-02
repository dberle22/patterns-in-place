# Data Dictionary: staging ACS Social Infrastructure Family

## Overview
- Schema: `staging`
- Family: `ACS Social Infrastructure`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_social_infra.R`](../../../scripts/etl/staging/get_acs_social_infra.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_social_infra_us` | ACS 5-year wide landing |
| Region | `acs_social_infra_region` | ACS 5-year wide landing |
| Division | `acs_social_infra_division` | ACS 5-year wide landing |
| State | `acs_social_infra_state` | ACS 5-year wide landing |
| County | `acs_social_infra_county` | ACS 5-year wide landing |
| Place | `acs_social_infra_place` | ACS 5-year wide landing |
| ZCTA | `acs_social_infra_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_social_infra_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_social_infra_tract_fl`, `acs_social_infra_tract_ga`, `acs_social_infra_tract_nc`, `acs_social_infra_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 43
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `hh_totalE`, `hh_totalM`, `hh_familyE`, `hh_familyM`, `hh_marriedE`, `hh_marriedM`, `hh_other_familyE`, `hh_other_familyM`, `hh_nonfamilyE`, `hh_nonfamilyM`, `hh_nonfam_aloneE`, `hh_nonfam_aloneM`, `hh_nonfam_not_aloneE`, `hh_nonfam_not_aloneM`, `ins_totalE`, `ins_totalM`, `ins_u19_one_planE`, `ins_u19_one_planM`, `ins_u19_two_plansE`, `ins_u19_two_plansM`, `ins_u19_uncoveredE`, `ins_u19_uncoveredM`, `ins_19_34_one_planE`, `ins_19_34_one_planM`, `ins_19_34_two_plansE`, `ins_19_34_two_plansM`, `ins_19_34_uncoveredE`, `ins_19_34_uncoveredM`, `ins_35_64_one_planE`, `ins_35_64_one_planM`, `ins_35_64_two_plansE`, `ins_35_64_two_plansM`, `ins_35_64_uncoveredE`, `ins_35_64_uncoveredM`, `ins_65u_one_planE`, `ins_65u_one_planM`, `ins_65u_two_plansE`, `ins_65u_two_plansM`, `ins_65u_uncoveredE`, `ins_65u_uncoveredM`

## Lineage
- [`scripts/etl/staging/get_acs_social_infra.R`](../../../scripts/etl/staging/get_acs_social_infra.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
