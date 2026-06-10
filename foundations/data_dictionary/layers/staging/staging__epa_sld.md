# Data Dictionary: staging EPA Smart Location Database

## Overview
- Schema: `staging`
- Family: `EPA Smart Location Database`
- Contract scope: source-family staging contract for the compact block-group SLD table produced by [`foundations/etl/staging/get_epa_sld.R`](../../../etl/staging/get_epa_sld.R)
- Documentation rule: the current SLD ingest lands as one compact table because we intentionally narrowed the wide EPA delivery to the geography helpers and highest-signal built-form indicators approved for Track 9

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| National block-group SLD release | `epa_sld` | One row per census block group from the direct EPA CSV, with canonical block-group GEOIDs reconstructed from component geography fields because the delivered `GEOID10` / `GEOID20` values are scientific-notation strings |

## Contract Summary
- All staged SLD rows live in one table.
- Grain: one row per `bg_geoid`
- Geography scope: national census block groups
- Current initial scope: EPA Smart Location Database version `3.0`, vintage year `2021`
- Current landed shape: `220,740` rows, `31` columns
- The staging contract keeps the geography backbone, rollup helpers, `TotEmp` for exact employment-density recomputation, and the compact set of walkability / transit / accessibility measures approved for the first modeled pass

## Shared Columns
- Time field:
  - `year`
- Canonical geography helpers:
  - `state_fips`
  - `county_fips`
  - `tract_code`
  - `block_group_code`
  - `bg_geoid`
  - `bg_geoid_2020`
- Raw provenance helpers:
  - `source_geoid10_raw`
  - `source_geoid20_raw`
- Metro helpers:
  - `cbsa_code`
  - `cbsa_name`
- Denominator and scale fields:
  - `total_population`
  - `total_employment`
  - `housing_units`
  - `households`
  - `land_acres_unprotected`
- Built-form and accessibility fields:
  - `walkability_index`
  - `employment_housing_mix`
  - `employment_mix`
  - `street_intersection_density`
  - `auto_oriented_intersection_share`
  - `transit_service_density`
  - `transit_frequency_peak`
  - `distance_to_transit`
  - `jobs_access_45min_transit`
  - `workers_access_45min_transit`
  - `jobs_access_45min_auto`
  - `workers_access_45min_auto`
  - `employment_density_gross`
  - `population_density_gross`
  - `housing_density_gross`

## Lineage
- [`foundations/etl/staging/get_epa_sld.R`](../../../etl/staging/get_epa_sld.R) downloads the direct EPA SLD CSV (`EPA_SmartLocationDatabase_V3_Jan_2021_Final.csv`), reads only the approved compact field set, forces component geography fields to character, reconstructs canonical block-group GEOIDs, validates the rebuilt keys, and writes `staging.epa_sld`.
- The provider-level source notes, keep/drop rationale, and tract-vs-county modeling decision live in [`../../sources/source__epa_smart_location.md`](../../sources/source__epa_smart_location.md).

## Data Quality Notes
- The delivered EPA CSV writes `GEOID10` and `GEOID20` in scientific notation.
  - Staging does not trust those raw values as join keys.
  - Instead, it reconstructs `bg_geoid` from `STATEFP + COUNTYFP + TRACTCE + BLKGRPCE`.
- `bg_geoid` must be unique and 12 digits after reconstruction.
- `state_fips`, `county_fips`, and `tract_code` are retained as text helpers so Silver can derive tract or county IDs without re-parsing the raw source.
- `bg_geoid_2020` is currently staged as a preserved helper field rather than a modeled geography key.
- `TotEmp` is retained in staging specifically so Silver can recompute `employment_density_gross` exactly rather than carrying forward a weighted average of block-group density values.
- Transit-related metrics are expected to have uneven coverage because EPA's SLD transit fields depend on GTFS availability.

## Known Gaps / To-Dos
- The current staging contract keeps only the approved compact subset of the full `117`-column EPA CSV. If a later transportation analysis needs additional SLD variables, we can extend staging without changing the raw download path.
- The CSV-only path is sufficient for county modeling, but tract-level canonical recovery is still unresolved from the delivered file alone.
  - A future tract fix should use the official Census 2010/2020 tract relationship files or the geodatabase-based SLD delivery.
- The first-pass Silver contract now derives county, CBSA, and state rows from staging while tract recovery remains incomplete and not trustworthy enough for modeled use today.
