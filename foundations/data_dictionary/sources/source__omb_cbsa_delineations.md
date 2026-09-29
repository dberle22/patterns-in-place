# Source Spec: OMB CBSA Delineations

## Purpose

OMB bulletins provide the authoritative county-to-CBSA assignments used by the
geography engine.

## Contract

- OMB Bulletin 23-01, issued July 21, 2023, is the approved current vintage.
- Store each future approved bulletin as a new `boundary_vintage`; never update
  or delete historical assignments in place.
- `mart_geography` selects one explicitly approved current bulletin while
  retaining prior vintages for audit and temporal harmonization.
