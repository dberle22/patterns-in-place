# Data Dictionary: staging ACS Age Family

## Overview
- Schema: `staging`
- Family: `ACS Age`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_age.R`](../../../scripts/etl/staging/get_acs_age.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_age_us` | ACS 5-year wide landing |
| Region | `acs_age_region` | ACS 5-year wide landing |
| Division | `acs_age_division` | ACS 5-year wide landing |
| State | `acs_age_state` | ACS 5-year wide landing |
| County | `acs_age_county` | ACS 5-year wide landing |
| Place | `acs_age_place` | ACS 5-year wide landing |
| ZCTA | `acs_age_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_age_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_age_tract_fl`, `acs_age_tract_ga`, `acs_age_tract_nc`, `acs_age_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 103
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `pop_totalE`, `pop_totalM`, `median_age.E`, `median_age.M`, `pop_male_totalE`, `pop_male_totalM`, `pop_age_male_under5E`, `pop_age_male_under5M`, `pop_age_male_5_9E`, `pop_age_male_5_9M`, `pop_age_male_10_14E`, `pop_age_male_10_14M`, `pop_age_male_15_17E`, `pop_age_male_15_17M`, `pop_age_male_18_19E`, `pop_age_male_18_19M`, `pop_age_male_20E`, `pop_age_male_20M`, `pop_age_male_21E`, `pop_age_male_21M`, `pop_age_male_22_24E`, `pop_age_male_22_24M`, `pop_age_male_25_29E`, `pop_age_male_25_29M`, `pop_age_male_30_34E`, `pop_age_male_30_34M`, `pop_age_male_35_39E`, `pop_age_male_35_39M`, `pop_age_male_40_44E`, `pop_age_male_40_44M`, `pop_age_male_45_49E`, `pop_age_male_45_49M`, `pop_age_male_50_54E`, `pop_age_male_50_54M`, `pop_age_male_55_59E`, `pop_age_male_55_59M`, `pop_age_male_60_61E`, `pop_age_male_60_61M`, `pop_age_male_62_64E`, `pop_age_male_62_64M`, `pop_age_male_65_66E`, `pop_age_male_65_66M`, `pop_age_male_67_69E`, `pop_age_male_67_69M`, `pop_age_male_70_74E`, `pop_age_male_70_74M`, `pop_age_male_75_79E`, `pop_age_male_75_79M`, `pop_age_male_80_84E`, `pop_age_male_80_84M`, `pop_age_male_85_plusE`, `pop_age_male_85_plusM`, `pop_female_totalE`, `pop_female_totalM`, `pop_age_female_under5E`, `pop_age_female_under5M`, `pop_age_female_5_9E`, `pop_age_female_5_9M`, `pop_age_female_10_14E`, `pop_age_female_10_14M`, `pop_age_female_15_17E`, `pop_age_female_15_17M`, `pop_age_female_18_19E`, `pop_age_female_18_19M`, `pop_age_female_20E`, `pop_age_female_20M`, `pop_age_female_21E`, `pop_age_female_21M`, `pop_age_female_22_24E`, `pop_age_female_22_24M`, `pop_age_female_25_29E`, `pop_age_female_25_29M`, `pop_age_female_30_34E`, `pop_age_female_30_34M`, `pop_age_female_35_39E`, `pop_age_female_35_39M`, `pop_age_female_40_44E`, `pop_age_female_40_44M`, `pop_age_female_45_49E`, `pop_age_female_45_49M`, `pop_age_female_50_54E`, `pop_age_female_50_54M`, `pop_age_female_55_59E`, `pop_age_female_55_59M`, `pop_age_female_60_61E`, `pop_age_female_60_61M`, `pop_age_female_62_64E`, `pop_age_female_62_64M`, `pop_age_female_65_66E`, `pop_age_female_65_66M`, `pop_age_female_67_69E`, `pop_age_female_67_69M`, `pop_age_female_70_74E`, `pop_age_female_70_74M`, `pop_age_female_75_79E`, `pop_age_female_75_79M`, `pop_age_female_80_84E`, `pop_age_female_80_84M`, `pop_age_female_85_plusE`, `pop_age_female_85_plusM`

## Lineage
- [`scripts/etl/staging/get_acs_age.R`](../../../scripts/etl/staging/get_acs_age.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
