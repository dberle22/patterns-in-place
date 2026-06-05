# Source Spec: BPS

## 1. Overview

- Source: U.S. Census Bureau Building Permits Survey
- Access pattern: compiled CSV landing file
- Primary dependency: local raw BPS file plus DuckDB path
- Scope in Foundations: BPS supplies annual permit counts, units, and values across multiple geography levels, then feeds one wide Silver table with direct measures and structure-mix derivations.
- Documentation goal: this file is the provider-level spec for BPS as it is currently modeled in Foundations.

## 2. Coverage Matrix

This source spec covers the BPS topic groups currently documented in the data dictionary.

| Topic group | Staging family contracts | Silver outputs |
| --- | --- | --- |
| Building permits | [../layers/staging/staging__bps.md](../layers/staging/staging__bps.md) | `silver.bps_wide` |

## 3. Source Contract

- Provider: U.S. Census Bureau Building Permits Survey
- Retrieval interface in current coverage: compiled CSV file
- Common request pattern: annual BPS file is read from the raw-data directory and split into geography-specific staging tables
- Common geography pattern: region, division, state, county, and place at ingest time; CBSA is derived in Silver from county rows
- Common time pattern: annual observations, currently 1980 through 2024 in the Silver table contract

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_bps.R](../../etl/staging/get_bps.R)

| Topic group | Source file / subject area | Staging ingest entrypoint |
| --- | --- | --- |
| Building permits | permit buildings, units, and value totals by structure size | [../../etl/staging/get_bps.R](../../etl/staging/get_bps.R) |

## 4. Staging Shape

Common BPS staging pattern:
- one staging family contract
- one materialized table per geography slice
- direct annual measures for totals, one-unit buildings, small multifamily buildings, and large multifamily buildings

Shared staging columns across the family:
- `FILE_NAME`
- `LOCATION_TYPE`
- `PERIOD`
- `SURVEY_DATE`
- `YEAR`
- `TOTAL_BLDGS`
- `TOTAL_UNITS`
- `TOTAL_VALUE`
- `BLDGS_1_UNIT`
- `BLDGS_2_UNITS`
- `BLDGS_3_4_UNITS`
- `BLDGS_5_UNITS`
- `UNITS_1_UNIT`
- `UNITS_2_UNITS`
- `UNITS_3_4_UNITS`
- `UNITS_5_UNITS`
- `VALUE_1_UNIT`
- `VALUE_2_UNITS`
- `VALUE_3_4_UNITS`
- `VALUE_5_UNITS`

| Topic group | Staging family | Coverage shape |
| --- | --- | --- |
| Building permits | `staging__bps` | region, division, state, county, and place materializations with county and place variants carrying more identifiers |

## 5. Staging To Silver

Common BPS handoff pattern:
1. Read each geography-specific staging table.
2. Normalize geography fields into the shared Silver contract.
3. Select direct permit measures into a common wide schema.
4. Derive multifamily totals, simple averages, shares, and a structure-mix label.
5. Rebuild CBSA rows from county staging using the county-to-CBSA crosswalk.
6. Union all slices into one analytical Silver table.

| Topic group | Silver handoff | Special path |
| --- | --- | --- |
| Building permits | `staging__bps` -> `silver.bps_wide` | CBSA rows are aggregated from county staging rather than ingested as a separate staging table |

## 6. Transformation Notes

| Topic group | Silver-table role | Derivation logic |
| --- | --- | --- |
| Building permits | standardized annual permit table across all supported geographies | derives `units_multifam`, `bldgs_multifam`, `value_multifam`, average units per building, multifamily shares, one-unit share, five-plus-unit share, and a simple `structure_mix` label |

Additional BPS-wide transform notes:
- Region, division, state, county, and place rows are mostly pass-through after name and type normalization.
- CBSA rows are built by summing county permit measures before derived fields are calculated.
- Place and county staging inputs include extra local identifiers, but the Silver table keeps only the normalized geography contract plus metrics.

## 7. Data Quality Expectations

| Topic group | Non-boilerplate checks worth preserving |
| --- | --- |
| Building permits | review the current duplicate-key issue in `silver.bps_wide`; confirm whether duplicates reflect true multiple place identities, stale source duplication, or an incomplete geography contract; monitor denominator-driven nulls in average and share fields where total buildings or units equal zero |

## 8. Operational Notes

- Staging entrypoint:
  [../../etl/staging/get_bps.R](../../etl/staging/get_bps.R)
- Silver model entrypoint:
  [../../etl/silver/bps_silver.R](../../etl/silver/bps_silver.R)
- Required local environment wiring:
  `DATA` for the compiled BPS CSV and `DB_PATH` for DuckDB materialization
- Current documentation pattern:
  staging remains family-contract based, Silver remains table-contract based, and this file sits above both as the provider-level spec

## 9. Known Gaps

- The current staging family contract does not mention the derived CBSA slice even though it is a major part of the Silver handoff.
- `silver.bps_wide` currently fails the provisional uniqueness check on `geo_level + geo_id + period`, so the modeled geography contract still needs hardening.
- The source spec does not attempt to preserve every raw BPS location code nuance; those details remain in staging and ETL.
