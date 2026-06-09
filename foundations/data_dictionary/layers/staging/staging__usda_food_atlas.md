# Data Dictionary: staging USDA Food Access Research Atlas

## Overview
- Schema: `staging`
- Family: `USDA Food Access Research Atlas`
- Contract scope: source-family staging contract for the compact tract table produced by [`foundations/etl/staging/get_usda_food_atlas.R`](../../../etl/staging/get_usda_food_atlas.R)
- Documentation rule: the current ingest lands as one compact tract table because the workbook already publishes the Atlas at tract grain and we only need the food-desert flags plus burden counts for downstream rollups

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| National tract Atlas release | `usda_food_atlas` | One row per 2010-vintage census tract from the current `2019` USDA Food Access Research Atlas workbook |

## Contract Summary
- All staged Food Atlas rows live in one table.
- Grain: one row per `tract_geoid + year`
- Geography scope: national census tracts
- Current initial scope: USDA Food Access Research Atlas vintage year `2019`
- Current landed shape: `72,531` rows, `37` columns
- The staging contract keeps the tract key, tract context fields, the core food-desert / low-access flags, and the population burden counts and shares we approved for the first modeled pass

## Shared Columns
- Time field:
  - `year`
- Canonical geography helpers:
  - `tract_geoid`
  - `state_name`
  - `county_name`
  - `census_tract_label`
- Tract context fields:
  - `urban_flag`
  - `population_total`
  - `housing_units_total`
  - `group_quarters_flag`
  - `group_quarters_population`
  - `group_quarters_share`
- Core designation flags:
  - `lila_1_and_10_flag`
  - `lila_half_and_10_flag`
  - `lila_1_and_20_flag`
  - `lila_vehicle_flag`
  - `low_income_flag`
  - `low_access_1_and_10_flag`
  - `low_access_half_and_10_flag`
  - `low_access_1_and_20_flag`
- Primary burden counts and shares:
  - `low_access_pop_1`
  - `low_access_pop_1_share`
  - `low_access_pop_1_10`
  - `low_access_pop_half_10`
  - `low_access_pop_1_20`
  - `low_access_low_income_pop_1`
  - `low_access_low_income_pop_1_share`
  - `low_access_low_income_pop_1_10`
  - `poverty_rate`
  - `median_family_income`
- Optional subgroup burden fields:
  - `low_access_children_1`
  - `low_access_children_1_share`
  - `low_access_seniors_1`
  - `low_access_seniors_1_share`
  - `low_access_no_vehicle_housing_1`
  - `low_access_no_vehicle_housing_1_share`
  - `low_access_snap_housing_1`
  - `low_access_snap_housing_1_share`

## Lineage
- [`foundations/etl/staging/get_usda_food_atlas.R`](../../../etl/staging/get_usda_food_atlas.R) downloads the current USDA workbook, reads the `Food Access Research Atlas` sheet, normalizes the approved compact field set, validates the tract key, and writes `staging.usda_food_atlas`.
- The provider-level source notes, keep/drop rationale, and dedicated Gold-table decision live in [`../../sources/source__usda_food_atlas.md`](../../sources/source__usda_food_atlas.md).

## Data Quality Notes
- The USDA Atlas is already tract-native, so staging keeps the 11-digit tract GEOID as text immediately and does not attempt any tract-backbone remapping.
- The source workbook is based on `2010` tract polygons even though the Atlas release year is `2019`.
- County and CBSA rollups should be derived downstream from the tract keys, not added to staging upstream.
- The subgroup burden fields are kept only where they are trivial to preserve from the workbook and do not complicate the core food-desert contract.

## Known Gaps / To-Dos
- The full workbook has `147` columns; the current staging contract intentionally keeps only the compact food-access slice approved for Track 20.
- If we later need GIS joins or source-side schema QA, the ERS ArcGIS service remains the right fallback.
