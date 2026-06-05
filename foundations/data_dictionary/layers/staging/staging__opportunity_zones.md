# Data Dictionary: staging Opportunity Zones

## Overview
- Schema: `staging`
- Family: `Opportunity Zones`
- Contract scope: source-family staging contract for the official CDFI Fund Opportunity Zone ArcGIS layer response produced by [`foundations/etl/staging/get_opportunity_zones.R`](../../../etl/staging/get_opportunity_zones.R)
- Documentation rule: the source is a small static tract list, so this file is the canonical staging contract for the full ingest

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Designated tract list | `opportunity_zones` | One row per designated tract from the official CDFI Fund ArcGIS layer |

## Contract Summary
- Grain: one row per `tract_geoid`
- Geography scope: designated Opportunity Zone tracts from the official national list
- Current scope: static designation list queried from the official CDFI Fund ArcGIS layer
- Shape expectation: approximately `8,700` designated tracts

## Shared Columns
- `state_name`
- `county_name`
- `tract_geoid`
- `nmtc_qualified`
- `data_source`
- `is_opportunity_zone`

## Lineage
- [`foundations/etl/staging/get_opportunity_zones.R`](../../../etl/staging/get_opportunity_zones.R) queries the official CDFI ArcGIS layer for designated tracts, normalizes the response fields, zero-pads `tract_geoid`, validates uniqueness, and writes `staging.opportunity_zones`.
- Provider-level context and downstream modeling decisions live in [`../../sources/source__opportunity_zones.md`](../../sources/source__opportunity_zones.md).

## Data Quality Notes
- Validate uniqueness at `tract_geoid`; staging should be a simple designated-tract allowlist.
- Confirm `tract_geoid` is always an 11-digit zero-padded Census tract identifier.
- Keep `nmtc_qualified` and `data_source` in staging even though downstream Silver only needs the designation flag; they are useful provenance when reconciling edge-case tracts.

## Known Gaps / To-Dos
- Staging retains designated tracts only. Full tract coverage is introduced in `silver.opportunity_zones` using the tract crosswalk backbone.
- Vintage mismatches between the 2018 designation list and the current tract crosswalk should be counted during Silver validation.
