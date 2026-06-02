# Data Dictionary: staging ACS Transportation Family

## Overview
- Schema: `staging`
- Family: `ACS Transportation`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_transport.R`](../../../scripts/etl/staging/get_acs_transport.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_transport_us` | ACS 5-year wide landing |
| Region | `acs_transport_region` | ACS 5-year wide landing |
| Division | `acs_transport_division` | ACS 5-year wide landing |
| State | `acs_transport_state` | ACS 5-year wide landing |
| County | `acs_transport_county` | ACS 5-year wide landing |
| Place | `acs_transport_place` | ACS 5-year wide landing |
| ZCTA | `acs_transport_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_transport_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_transport_tract_fl`, `acs_transport_tract_ga`, `acs_transport_tract_nc`, `acs_transport_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 39
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `commute_workers_totalE`, `commute_workers_totalM`, `commute_car_truck_vanE`, `commute_car_truck_vanM`, `commute_drove_aloneE`, `commute_drove_aloneM`, `commute_carpoolE`, `commute_carpoolM`, `commute_public_transE`, `commute_public_transM`, `commute_taxicabE`, `commute_taxicabM`, `commute_motorcycleE`, `commute_motorcycleM`, `commute_bicycleE`, `commute_bicycleM`, `commute_walkedE`, `commute_walkedM`, `commute_otherE`, `commute_otherM`, `commute_worked_homeE`, `commute_worked_homeM`, `veh_total_hhE`, `veh_total_hhM`, `veh_0E`, `veh_0M`, `veh_1E`, `veh_1M`, `veh_2E`, `veh_2M`, `veh_3E`, `veh_3M`, `veh_4_plusE`, `veh_4_plusM`, `total_travel_timeE`, `total_travel_timeM`

## Lineage
- [`scripts/etl/staging/get_acs_transport.R`](../../../scripts/etl/staging/get_acs_transport.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
