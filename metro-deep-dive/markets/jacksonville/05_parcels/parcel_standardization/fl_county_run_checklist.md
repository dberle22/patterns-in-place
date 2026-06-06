# Florida County Parcel Run Checklist

This checklist tracks the Florida counties needed for the current ROF markets:

- `gainesville_fl`
- `jacksonville_fl`
- `orlando_fl`

## Key Conventions

- `county_tag` should use the Florida parcel source county code, not county FIPS.
- Example: Alachua is `county_geoid = 12001` but `county_tag = co_11`.
- The current manual script example still shows `county_tag <- "alachua_fl"`. For
  this workflow, use stable `co_<source_county_id>` tags instead.
- Geometry should remain in county `.RDS` artifacts under
  `outputs/fl_all_v2/county_outputs/<county_tag>/`.
- A county is not complete until these three files exist:
  - `parcel_geometries_raw.rds`
  - `parcel_geometries_analysis.rds`
  - `parcel_geometry_join_qa.rds`

## Required Workflow Adjustments

- [ ] Update the manual county operator steps so `county_tag` is always the
  stable source-code tag, not a market-style key like `alachua_fl`.
- [ ] Add or document a publish step from the manual ETL output into the
  standardized Section 05 handoff:
  `outputs/fl_all_v2/county_outputs/<county_tag>/...`
- [ ] Refresh aggregate outputs after each county run:
  - `parcel_ingest_manifest.rds`
  - `parcel_geometry_join_qa_county_summary.rds`
- [ ] Keep `repair_invalid_geom <- FALSE` by default and only enable it for
  counties that show real geometry failures during QA.
- [ ] Record both source county code and normalized geography keys in run notes
  so county lineage stays easy to reconcile upstream.

## County Checklist

| Market | County | county_geoid | source_county_id | county_tag | Tabular status | Geometry status | Next action | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gainesville_fl | Alachua | 12001 | 11 | `co_11` | Present in statewide standardized attributes | Present | Complete | QA artifact exists and passes. Ignore the empty `co_01` stub folder. |
| gainesville_fl | Gilchrist | 12041 | 31 | `co_31` | Present in statewide standardized attributes | Missing | Run manual county ETL and publish outputs | No `county_outputs/co_31/` geometry artifacts on disk yet. |
| gainesville_fl | Levy | 12075 | 48 | `co_48` | Present in statewide standardized attributes | Missing | Run manual county ETL and publish outputs | No `county_outputs/co_48/` geometry artifacts on disk yet. |
| jacksonville_fl | Baker | 12003 | 12 | `co_12` | Present in statewide standardized attributes | Present | Rerun and review QA | Current county QA fails with `unmatched_rate_analysis = 0.013638843`. |
| jacksonville_fl | Clay | 12019 | 20 | `co_20` | Present in statewide standardized attributes | Present | Complete | Current county QA passes. |
| jacksonville_fl | Duval | 12031 | 26 | `co_26` | Present in statewide standardized attributes | Present | Complete | Current county QA passes. Largest county by parcel count, so use as the reference performance baseline. |
| jacksonville_fl | Nassau | 12089 | 55 | `co_55` | Present in statewide standardized attributes | Present | Complete | Current county QA passes. |
| jacksonville_fl | St. Johns | 12109 | 65 | `co_65` | Present in statewide standardized attributes | Present | Rerun and review QA | Current county QA fails with `unmatched_rate_analysis = 0.026991136`. |
| orlando_fl | Lake | 12069 | 45 | `co_45` | Present in statewide standardized attributes | Missing | Run manual county ETL and publish outputs | No `county_outputs/co_45/` geometry artifacts on disk yet. |
| orlando_fl | Orange | 12095 | 58 | `co_58` | Present in statewide standardized attributes | Missing | Run manual county ETL and publish outputs | No `county_outputs/co_58/` geometry artifacts on disk yet. |
| orlando_fl | Osceola | 12097 | 59 | `co_59` | Present in statewide standardized attributes | Missing | Run manual county ETL and publish outputs | No `county_outputs/co_59/` geometry artifacts on disk yet. |
| orlando_fl | Seminole | 12117 | 69 | `co_69` | Present in statewide standardized attributes | Missing | Run manual county ETL and publish outputs | No `county_outputs/co_69/` geometry artifacts on disk yet. |

## Immediate Priority Order

- [ ] Rerun `co_65` St. Johns and inspect why the unmatched analysis rate is
  above threshold.
- [ ] Rerun `co_12` Baker and inspect why the unmatched analysis rate is above
  threshold.
- [ ] Build missing Gainesville counties:
  - [ ] `co_31` Gilchrist
  - [ ] `co_48` Levy
- [ ] Build missing Orlando counties:
  - [ ] `co_45` Lake
  - [ ] `co_58` Orange
  - [ ] `co_59` Osceola
  - [ ] `co_69` Seminole

## Current On-Disk Snapshot

- Geometry outputs present:
  - `co_11`
  - `co_12`
  - `co_20`
  - `co_26`
  - `co_55`
  - `co_65`
- Empty stub folder:
  - `co_01`
- Current QA failures in `parcel_geometry_join_qa_county_summary.rds`:
  - `co_12`
  - `co_65`
