# Data Dictionary: staging FHFA Underserved Areas

## Overview
- Schema: `staging`
- Family: `FHFA Underserved Areas`
- Contract scope: source-family staging contract for the latest FHFA low-income areas file produced by [`foundations/etl/staging/get_fhfa_underserved.R`](../../../etl/staging/get_fhfa_underserved.R)
- Documentation rule: FHFA currently lands as one normalized tract table for the latest release year, so this file is the canonical staging contract for the full ingest

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Current-year tract designations | `fhfa_underserved` | One row per `tract_geoid + year`, normalized from FHFA’s fixed-width low-income areas file |

## Contract Summary
- Grain: one row per `tract_geoid + year`
- Geography scope: tract-level FHFA low-income / minority / disaster-area designations for the latest available yearly file
- Current scope: latest available yearly release only in the first-pass Track 5 contract
- Shape expectation: approximately national tract coverage plus Puerto Rico rows and a few special geography cases

## Shared Columns
- `tract_geoid`
- `year`
- `is_underserved`
- `is_low_income_area`
- `is_minority_area`
- `is_disaster_area`

## Lineage
- [`foundations/etl/staging/get_fhfa_underserved.R`](../../../etl/staging/get_fhfa_underserved.R) resolves the latest FHFA yearly ZIP from the public page, extracts the fixed-width text file, normalizes tract identifiers, derives booleans from `LYA`, `MIN_TRCT`, and `DDA`, collapses any split-tract duplicates, and writes `staging.fhfa_underserved`.
- Provider-level context and downstream modeling decisions live in [`../../sources/source__opportunity_zones.md`](../../sources/source__opportunity_zones.md).

## Data Quality Notes
- Validate uniqueness at `tract_geoid + year`.
- Confirm `tract_geoid` is always an 11-digit zero-padded Census tract identifier.
- FHFA uses annual geography and ACS inputs that can create special split-tract records. The current staging contract collapses those to one tract row so the downstream crosswalk-backed rollups remain deterministic.

## Known Gaps / To-Dos
- The current staging contract is current-year only by design. Multi-year backfill can be added later if Gold consumers need a panel.
- Puerto Rico and other edge-case tracts should be counted during Silver validation because the current tract backbone does not include every FHFA source geography.
