# Data Dictionary: staging USDA ERS County Typology

## Overview
- Schema: `staging`
- Family: `USDA ERS County Typology Codes`
- Contract scope: source-faithful long staging table produced by [`foundations/etl/staging/get_usda_ers_typology.R`](../../../etl/staging/get_usda_ers_typology.R)
- Documentation rule: this contract covers the current `2025` County Typology CSV landing only

## Contract Summary
- Materialized table: `usda_county_typology`
- Current first-pass scope: the live `2025` ERS County Typology CSV
- Grain: one row per `fips + attribute`
- Native geography: county or county-equivalent
- Current landed volume:
  - `40,976` data rows
  - `3,152` distinct county-equivalent FIPS keys
- Expected attribute count: `13`

## Why There Are Multiple Rows Per FIPS

ERS publishes County Typology in the same compact long style as RUCC. Each county-equivalent repeats across many attributes:

- economic concentration flags such as `High_Farming_2025`
- categorical codes such as `Industry_Dependence_2025`
- demographic challenge flags such as `Low_Employment_2025`

That long `attribute` / `value` layout is exactly what staging should preserve. The modeled county-wide row belongs in Silver.

## Shared Columns
- `vintage_year`: fixed `2025`
- `fips`: 5-character county or county-equivalent FIPS key
- `state_abbr`: USPS-style state abbreviation from the source file
- `county_name`: provider-published county or county-equivalent name
- `metro2023`: source metro/nonmetro indicator published on every row for the county-equivalent
- `attribute`: source attribute name
- `value_raw`: source value preserved as text
- `value_numeric`: numeric parse helper where the source value is numeric
- `publication_date`: provider-published publication note
- `source_note`: provider-published source note
- `source_file`: cached local CSV filename
- `source_url`: live ERS download URL used for the load

## Expected Attribute Set
- `High_Farming_2025`
- `High_Government_2025`
- `High_Manufacturing_2025`
- `High_Mining_2025`
- `High_Recreation_2025`
- `Housing_Stress_2025`
- `Industry_Dependence_2025`
- `Low_Employment_2025`
- `Low_PostSecondary_Ed_2025`
- `Nonspecialized_2025`
- `Persistent_Poverty_1721`
- `Population_Loss_2025`
- `Retirement_Destination_2025`

## Coverage Notes
- The file excludes U.S. territories.
- The file mixes Connecticut geography depending on the attribute family:
  - ACS-based attributes use `9` planning regions
  - BEA / migration / older-ACS based attributes still use the `8` legacy counties
- That means the staging table intentionally preserves both the planning-region and legacy-county FIPS keys where ERS publishes them.
- This is the main reason Silver should widen first and reconcile geography only deliberately.

## What The Current Staging Script Cleans

The script intentionally keeps this table very close to the source file:

1. Downloads the live County Typology CSV and caches it locally.
2. Standardizes the headers with `janitor::clean_names()`.
3. Pads the FIPS key to a 5-character text field.
4. Preserves the published `attribute` / `value` layout.
5. Parses `metro2023` and `value_numeric` as numeric helpers.
6. Preserves the provider publication and source-note text.
7. Adds source-file and source-URL provenance.
8. Validates:
  - 5-digit FIPS format
  - uniqueness at `fips + attribute`
  - the expected 13-attribute set
  - the expected `3,152` distinct FIPS keys

What it intentionally does **not** do:
- no widening into one county row
- no coercion of the coded typology fields into final business labels
- no geography reconciliation between Connecticut planning regions and legacy counties
- no filtering to the current `gold.dim_geo` county backbone

## Recommended Keep Vs Drop Path For Silver

### Keep in staging exactly as-is
- `fips`
- `state_abbr`
- `county_name`
- `metro2023`
- `attribute`
- `value_raw`
- `value_numeric`
- `publication_date`
- `source_note`
- `source_file`
- `source_url`

### Silver should do next
- pivot the 13 attributes into one wide county row
- normalize binary flags to `0` / `1` / `NULL`
- preserve the coded `Industry_Dependence_2025` field and map it to labels
- decide how to represent sentinel values such as `99` and `-1`
- decide how to handle the mixed Connecticut geography without hiding it

## Lineage
- [`foundations/etl/staging/get_usda_ers_typology.R`](../../../etl/staging/get_usda_ers_typology.R) downloads the live County Typology CSV, normalizes the county-equivalent FIPS key, preserves the published long shape, validates the expected attribute set and row counts, and writes `staging.usda_county_typology`.

## Data Quality Notes
- Verify uniqueness at `fips + attribute`.
- Verify the expected 13-attribute set is unchanged.
- Verify `fips` remains a 5-character text field with leading zeros preserved.
- Preserve mixed Connecticut geography source-faithfully; do not silently collapse the legacy county rows into planning regions in staging.
- Treat `value_numeric` as a helper only. Final business interpretation belongs in Silver.

## Known Gaps / To-Dos
- The current contract does not assign final semantics to sentinel values like `99` and `-1`; Silver should handle them intentionally and document the result.
- A future ERS release could change the geography backbone or add/remove typology attributes, so this contract should be re-verified rather than assumed stable.
