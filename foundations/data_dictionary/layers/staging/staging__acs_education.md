# Data Dictionary: staging ACS Education Family

## Overview
- Schema: `staging`
- Family: `ACS Education`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_edu.R`](../../../scripts/etl/staging/get_acs_edu.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_edu_us` | ACS 5-year wide landing |
| Region | `acs_edu_region` | ACS 5-year wide landing |
| Division | `acs_edu_division` | ACS 5-year wide landing |
| State | `acs_edu_state` | ACS 5-year wide landing |
| County | `acs_edu_county` | ACS 5-year wide landing |
| Place | `acs_edu_place` | ACS 5-year wide landing |
| ZCTA | `acs_edu_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_edu_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_edu_tract_fl`, `acs_edu_tract_ga`, `acs_edu_tract_nc`, `acs_edu_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 53
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `edu_total_25pE`, `edu_total_25pM`, `edu_no_schoolingE`, `edu_no_schoolingM`, `edu_nurseryE`, `edu_nurseryM`, `edu_kindergartenE`, `edu_kindergartenM`, `edu_grade1E`, `edu_grade1M`, `edu_grade2E`, `edu_grade2M`, `edu_grade3E`, `edu_grade3M`, `edu_grade4E`, `edu_grade4M`, `edu_grade5E`, `edu_grade5M`, `edu_grade6E`, `edu_grade6M`, `edu_grade7E`, `edu_grade7M`, `edu_grade8E`, `edu_grade8M`, `edu_grade9E`, `edu_grade9M`, `edu_grade10E`, `edu_grade10M`, `edu_grade11E`, `edu_grade11M`, `edu_grade12_no_diplomaE`, `edu_grade12_no_diplomaM`, `edu_hs_diplomaE`, `edu_hs_diplomaM`, `edu_ged_alt_credentialE`, `edu_ged_alt_credentialM`, `edu_some_college_lt1yrE`, `edu_some_college_lt1yrM`, `edu_some_college_ge1yrE`, `edu_some_college_ge1yrM`, `edu_associatesE`, `edu_associatesM`, `edu_bachelorsE`, `edu_bachelorsM`, `edu_mastersE`, `edu_mastersM`, `edu_professionalE`, `edu_professionalM`, `edu_doctorateE`, `edu_doctorateM`

## Lineage
- [`scripts/etl/staging/get_acs_edu.R`](../../../scripts/etl/staging/get_acs_edu.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
