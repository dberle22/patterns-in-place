# Data Dictionary: staging EJScreen

## Overview
- Schema: `staging`
- Family: `EPA EJScreen`
- Contract scope: source-family staging contract for the tract-only archived EJScreen table produced by [`foundations/etl/staging/get_ejscreen.R`](../../../etl/staging/get_ejscreen.R)
- Documentation rule: the first-pass EJScreen ingest intentionally lands only the tract archive, not the larger block-group files

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Tract archive | `ejscreen` | Archived 2024 Harvard Dataverse tract CSV with cleaned snake_case column names and canonical tract helper fields added during landing |

## Contract Summary
- All staged EJScreen rows live in one table.
- Grain: one row per `tract_geoid + year`
- Geography scope: tract rows only from the archived 2024 EJScreen tract CSV
- Current initial scope: `2024`
- Shape expectation: one national tract table with the full cleaned source column surface plus helper fields `tract_geoid`, `state_fips`, `county_fips`, and `year`

## Shared Columns
- Canonical tract identifiers added during staging: `tract_geoid`, `state_fips`, `county_fips`
- Source geography metadata: `state_name`, `state_abbrev`, `county_name`, `epa_region`
- Archive metadata: `year`
- Source-faithful EJScreen metrics and percentiles: all cleaned columns from the tract CSV are retained in staging for provenance, including demographic fields, environmental indicators, percentile fields, bucket fields, and shape helpers

## Lineage
- [`foundations/etl/staging/get_ejscreen.R`](../../../etl/staging/get_ejscreen.R) downloads the archived Harvard Dataverse tract CSV for EJScreen 2024, cleans the column names, pads the tract GEOID, derives state and county FIPS helpers from the tract key, validates uniqueness at `tract_geoid + year`, and writes `staging.ejscreen`.
- The provider-level archive notes and first-pass keep/drop guidance live in [`../../sources/source__epa.md`](../../sources/source__epa.md).

## Data Quality Notes
- Verify uniqueness at `tract_geoid + year`; tract staging should be one row per archived tract observation.
- Confirm `tract_geoid` is always a zero-padded 11-digit tract GEOID after ingest.
- Treat `state_fips` and `county_fips` as helper fields rather than guaranteed canonical geography keys. The archived file includes Puerto Rico and territorial rows that do not fully align to the current Foundations tract backbone.
- The staging table is intentionally broader than the first-pass Silver contract. It keeps the cleaned tract archive surface so Silver can narrow to the approved core indicators without re-downloading the source.
- Because this is an archived source rather than a live EPA endpoint, the exact archive version and file ID are part of the operational contract.

## Known Gaps / To-Dos
- The tract archive may not perfectly align to the newest tract crosswalk vintage. Silver should explicitly audit tract-key coverage before producing a modeled table.
- Block-group archive files are intentionally excluded from this first pass. Add them only if a downstream need truly requires finer geography.
