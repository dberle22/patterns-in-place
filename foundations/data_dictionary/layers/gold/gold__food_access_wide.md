# Data Dictionary: gold.food_access_wide

## Overview
- **Table**: `gold.food_access_wide`
- **Purpose**: Dedicated USDA Food Access Research Atlas baseline mart for tract, county, and CBSA food-desert designation and low-access population burden.
- **KPI applicability**: Gold output table for a one-time `2019` food-access baseline rather than a recurring annual panel.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current scope**:
  - `geo_level = tract`, `county`, `cbsa`
  - `year = 2019`

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Population burden counts**: `population_total`, `population_low_access_1`, `population_low_access_1_10`, `population_low_income_low_access_1`, `population_low_income_low_access_1_10`
- **Tract-count diagnostics**: `total_tract_count`, `lila_tract_count_1_10`, `low_income_tract_count`, `low_access_tract_count_1_10`
- **Designation shares**: `pct_lila_tracts_1_and_10`, `pct_low_income_tracts`, `pct_low_access_tracts_1_and_10`
- **Population burden shares**: `pct_population_low_access_1`, `pct_population_low_access_1_10`, `pct_population_low_income_low_access_1`, `pct_population_low_income_low_access_1_10`
- **Context fields**: `poverty_rate`, `median_family_income`

## Data Quality Notes
- This table is intentionally separate from `gold.transport_built_form_wide`.
  - The USDA Atlas is a sparse, single-vintage (`2019`) baseline source.
  - Keeping it separate avoids implying that food-access fields are part of the recurring ACS transport panel.
- Tract rows remain source-native to the Atlas rather than being forced onto a newer tract backbone in the first pass.
- County rollups are derived directly from tract GEOID prefixes, which is the most reliable way to preserve the Atlas geography while still getting stable county summaries.
- CBSA rollups inherit county-to-CBSA coverage from `silver.xwalk_cbsa_county`.
- The first-pass county rollup keeps the 8 legacy Connecticut county GEOIDs via an explicit manual lookup and excludes Alaska county-equivalent `02261` for the same geography-contract reasons documented in Silver.

## Lineage
1. `foundations/etl/staging/get_usda_food_atlas.R` downloads the USDA workbook, reads the tract table, normalizes the approved compact field set, and writes `staging.usda_food_atlas`.
2. `foundations/etl/silver/usda_food_atlas_silver.R` keeps tract rows source-native, derives county and CBSA rollups, recomputes tract-share and population-burden rates, and writes `silver.usda_food_atlas`.
3. `foundations/etl/gold/gold_food_access_wide.sql` promotes the modeled baseline directly into `gold.food_access_wide`.

## Known Gaps / To-Dos
- This Gold contract is intentionally limited to the `2019` Atlas baseline.
- If USDA publishes a newer Atlas release later, the staging and Silver contracts should be refreshed before this Gold table is widened into a time series.
