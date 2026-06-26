# Data Dictionary: staging USDA ERS RUCC

## Overview
- Schema: `staging`
- Family: `USDA ERS Rural-Urban Continuum Codes`
- Contract scope: source-faithful long staging table produced by [`foundations/etl/staging/get_usda_ers_typology.R`](../../../etl/staging/get_usda_ers_typology.R)
- Documentation rule: this contract covers the current `2023` RUCC CSV landing only

## Contract Summary
- Materialized table: `usda_rucc`
- Current first-pass scope: the live `2023` ERS Rural-Urban Continuum Codes CSV
- Grain: one row per `fips + attribute`
- Native geography: county or county-equivalent
- Current landed volume:
  - `9,703` data rows
  - `3,235` distinct county-equivalent FIPS keys
- Expected attribute set:
  - `Description`
  - `Population_2020`
  - `RUCC_2023`

## Why There Are Multiple Rows Per FIPS

The RUCC CSV is not delivered as one wide county row. ERS publishes the file in a compact long layout with one row per county-equivalent plus attribute name:

- one row for `Population_2020`
- one row for `RUCC_2023`
- one row for `Description`

That is the right shape to keep in staging because it preserves the published file exactly. Silver owns the widening step.

## Shared Columns
- `vintage_year`: fixed `2023`
- `fips`: 5-character county or county-equivalent FIPS key
- `state_abbr`: USPS-style state or territory abbreviation from the source file
- `county_name`: provider-published county or county-equivalent name
- `attribute`: source attribute name
- `value_raw`: source value preserved as text
- `value_numeric`: numeric parse helper where the source value is numeric
- `source_file`: cached local CSV filename
- `source_url`: live ERS download URL used for the load

## Coverage Notes
- The file includes counties and county-equivalents in the `50` States, `DC`, Puerto Rico, and other outlying territories.
- Connecticut is already represented with planning-region county-equivalents rather than legacy counties.
- Two American Samoa entities (`60030`, `60040`) are present in the file but do not have a `RUCC_2023` code row.
  - That exception is preserved as part of the source contract and checked explicitly by the staging script.

## What The Current Staging Script Cleans

The script intentionally does only the minimum work needed to make the file reproducible and queryable:

1. Downloads the live RUCC CSV and caches it locally.
2. Standardizes the headers with `janitor::clean_names()`.
3. Pads the FIPS key to a 5-character text field.
4. Preserves the published `attribute` / `value` layout.
5. Adds a numeric parse helper in `value_numeric`.
6. Adds source-file and source-URL provenance.
7. Validates:
  - 5-digit FIPS format
  - uniqueness at `fips + attribute`
  - the expected 3-attribute set
  - the expected `3,233` `RUCC_2023` rows and the known American Samoa exception

What it intentionally does **not** do:
- no widening into one county row
- no geography normalization beyond 5-digit FIPS preservation
- no current-backbone filtering
- no dropping of territories

## Recommended Keep Vs Drop Path For Silver

### Keep in staging exactly as-is
- `fips`
- `state_abbr`
- `county_name`
- `attribute`
- `value_raw`
- `value_numeric`
- `source_file`
- `source_url`

### Silver should do next
- pivot the three attributes into one wide county row
- treat `RUCC_2023` as the coded numeric field
- preserve the source description text alongside the code
- decide whether county-only, county-plus-CBSA, or Gold-dimension enrichment is the next modeled surface

## Lineage
- [`foundations/etl/staging/get_usda_ers_typology.R`](../../../etl/staging/get_usda_ers_typology.R) downloads the live ERS RUCC CSV, normalizes the county-equivalent FIPS key, preserves the published long shape, validates the known row-count contract, and writes `staging.usda_rucc`.

## Data Quality Notes
- Verify uniqueness at `fips + attribute`.
- Verify the expected attribute set remains exactly:
  - `Description`
  - `Population_2020`
  - `RUCC_2023`
- Verify `fips` remains a 5-character text field with leading zeros preserved.
- Preserve the American Samoa missing-code exception rather than treating it as a generic load failure.

## Known Gaps / To-Dos
- The staging contract intentionally leaves RUCC wide-row modeling to Silver.
- If ERS publishes a future RUCC release, this contract should be updated with the new vintage and row counts rather than overwritten silently.
