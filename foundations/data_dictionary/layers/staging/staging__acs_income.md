# Data Dictionary: staging ACS Income Family

## Overview
- Schema: `staging`
- Family: `ACS Income`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_income.R`](../../../scripts/etl/staging/get_acs_income.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_income_us` | ACS 5-year wide landing |
| Region | `acs_income_region` | ACS 5-year wide landing |
| Division | `acs_income_division` | ACS 5-year wide landing |
| State | `acs_income_state` | ACS 5-year wide landing |
| County | `acs_income_county` | ACS 5-year wide landing |
| Place | `acs_income_place` | ACS 5-year wide landing |
| ZCTA | `acs_income_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_income_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_income_tract_fl`, `acs_income_tract_ga`, `acs_income_tract_nc`, `acs_income_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 47
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `median_hh_incomeE`, `median_hh_incomeM`, `per_capita_incomeE`, `per_capita_incomeM`, `pov_universeE`, `pov_universeM`, `pov_belowE`, `pov_belowM`, `hh_inc_totalE`, `hh_inc_totalM`, `hh_inc_lt10kE`, `hh_inc_lt10kM`, `hh_inc_10k_15kE`, `hh_inc_10k_15kM`, `hh_inc_15k_20kE`, `hh_inc_15k_20kM`, `hh_inc_20k_25kE`, `hh_inc_20k_25kM`, `hh_inc_25k_30kE`, `hh_inc_25k_30kM`, `hh_inc_30k_35kE`, `hh_inc_30k_35kM`, `hh_inc_35k_40kE`, `hh_inc_35k_40kM`, `hh_inc_40k_45kE`, `hh_inc_40k_45kM`, `hh_inc_45k_50kE`, `hh_inc_45k_50kM`, `hh_inc_50k_60kE`, `hh_inc_50k_60kM`, `hh_inc_60k_75kE`, `hh_inc_60k_75kM`, `hh_inc_75k_100kE`, `hh_inc_75k_100kM`, `hh_inc_100k_125kE`, `hh_inc_100k_125kM`, `hh_inc_125k_150kE`, `hh_inc_125k_150kM`, `hh_inc_150k_200kE`, `hh_inc_150k_200kM`, `hh_inc_200k_plusE`, `hh_inc_200k_plusM`, `gini_indexE`, `gini_indexM`

## Lineage
- [`scripts/etl/staging/get_acs_income.R`](../../../scripts/etl/staging/get_acs_income.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
