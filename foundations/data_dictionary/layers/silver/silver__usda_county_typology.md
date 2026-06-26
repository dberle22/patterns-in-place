# Data Dictionary: silver.usda_county_typology

## Overview
- **Table**: `silver.usda_county_typology`
- **Purpose**: County-equivalent USDA ERS classification dimension that widens the long RUCC and County Typology staging tables into one analytical row per FIPS.
- **Status**: materialized from the current `2023` RUCC plus `2025` County Typology staging path.
- **Row count**: `3,243`
- **KPI applicability**: not a KPI table.

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id`
- **Primary key candidate**: (`geo_level`, `geo_id`)
- **Current geography coverage**: `county`
- **Current time treatment**: static dimension with source-vintage columns rather than a recurring year field

Live profile after materialization:
- distinct `geo_id` values: `3,243`
- rows with `has_rucc = TRUE`: `3,235`
- rows with `has_typology = TRUE`: `3,152`
- rows on the current county-equivalent backbone: `3,235`
- rows outside the current backbone: `8`
- rows with typology sentinel exceptions: `33`

## Why Silver Stops At County-Equivalent Rows

This is intentional.

- RUCC already uses the current Connecticut planning-region backbone.
- County Typology still mixes Connecticut planning regions and legacy counties depending on the attribute family.
- That means any CBSA aggregation would require a choice about how to reconcile two different county backbones.

The current table therefore keeps the county-equivalent dimension clean and explicit, then defers CBSA summarization to Gold where weighted-vs-unweighted rollup logic is an analytical decision instead of a hidden Silver transform.

## Contract Summary
- Input staging tables:
  - `staging.usda_rucc`
  - `staging.usda_county_typology`
- Backbone helper:
  - `gold.dim_geo`
- Scope rule:
  - keep the full FIPS union of the two ERS source families
  - keep one county-equivalent row per `geo_id`
  - preserve rows that only appear in one source family
  - flag rows that fall outside the current county-equivalent backbone instead of silently dropping them

## Column Groups
- **Keys and geography**: `geo_level`, `geo_id`, `geo_name`, `state_fips`, `state_abbr`
- **Source coverage flags**: `has_rucc`, `has_typology`, `in_current_county_backbone`
- **RUCC fields**: `rucc_vintage_year`, `rucc_2023_code`, `rucc_2023_description`, `population_2020`
- **County Typology flags**: `metro2023_flag`, `high_*`, `housing_stress_flag`, `low_*`, `nonspecialized_flag`, `population_loss_flag`, `retirement_destination_flag`, `persistent_poverty_flag`
- **County Typology coded fields**: `persistent_poverty_raw`, `industry_dependence_raw`, `industry_dependence_code`, `industry_dependence_label`
- **Exception audit**: `has_typology_exception_values`

## Coverage Exceptions We Keep Visible

### RUCC-only rows

The `91` RUCC-only rows are territory and outlying-area keys that County Typology does not classify.

### County Typology-only rows

The `8` County Typology-only rows are the legacy Connecticut counties:
- `09001`
- `09003`
- `09005`
- `09007`
- `09009`
- `09011`
- `09013`
- `09015`

These are intentionally retained with `in_current_county_backbone = FALSE` rather than being silently remapped or dropped.

### Typology sentinel-value rows

The current live table carries `33` rows with nonstandard typology sentinel values:
- `Industry_Dependence_2025 = 99` appears on `9` rows
- `Persistent_Poverty_1721 = -1` appears on `24` rows
- `Persistent_Poverty_1721 = 99` appears on `9` rows

Those rows remain queryable through:
- `persistent_poverty_raw`
- `industry_dependence_raw`
- `has_typology_exception_values`

## Gold Handoff

### County-native Gold use
- add direct county-equivalent enrichments such as:
  - `rucc_2023_code`
  - `rucc_2023_description`
  - `persistent_poverty_flag`
  - `retirement_destination_flag`
  - `industry_dependence_label`

### CBSA Gold use
- derive CBSA summaries in Gold only
- use the common county-equivalent backbone subset only
- document the aggregation rules explicitly
- recommended RUCC summary fields:
  - population-weighted dominant RUCC code
  - population-weighted RUCC mean
  - unweighted county-mode RUCC code
  - county count and population coverage diagnostics

That keeps Silver source-close and makes metro-level classification an explicit downstream modeling choice.

## Data Quality Notes
- Validate uniqueness at `geo_level + geo_id`.
- Confirm the live table keeps the full `3,243`-FIPS union of the two ERS source families.
- Confirm `3,235` rows resolve to the current county-equivalent backbone.
- Confirm the `8` legacy Connecticut county rows remain visible and flagged.
- Treat `industry_dependence_label` as a mapping derived from the published ERS category ordering rather than as a separately published source column.

## Lineage
1. [`foundations/etl/staging/get_usda_ers_typology.R`](../../../etl/staging/get_usda_ers_typology.R) downloads the two live ERS CSVs and lands them source-faithfully in staging.
2. [`foundations/etl/silver/usda_ers_typology_silver.R`](../../../etl/silver/usda_ers_typology_silver.R) widens each source family, standardizes the classification fields, joins the current county-equivalent backbone, preserves coverage and exception flags, and writes `silver.usda_county_typology`.

## Known Gaps / To-Dos
- Add the current first-pass Gold enrichment path for county rows.
- If we want CBSA rows, build them in Gold with the common-backbone-only rule and document the weighted rollup logic explicitly.
- Decide whether the `8` legacy Connecticut county rows should remain visible in final Gold outputs or stay as Silver-only audit rows.
