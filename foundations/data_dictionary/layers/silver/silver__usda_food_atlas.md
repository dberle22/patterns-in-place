# Data Dictionary: silver.usda_food_atlas

## Overview
- **Table**: `silver.usda_food_atlas`
- **Purpose**: Tract-native USDA Food Access Research Atlas baseline table with derived county and CBSA rollups for food-desert designation and low-access population burden.
- **Time coverage**: 2019 only

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**:
  - `tract`
  - `county`
  - `cbsa`
- **Key QA**: the Silver script stops if any county GEOID derived from the tract key fails to resolve to `silver.xwalk_county_state`, then checks for duplicate `geo_level + geo_id + year` rows before writing.

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Population burden counts**: `population_total`, `population_low_access_1`, `population_low_access_1_10`, `population_low_income_low_access_1`, `population_low_income_low_access_1_10`
- **Tract-count diagnostics**: `total_tract_count`, `lila_tract_count_1_10`, `low_income_tract_count`, `low_access_tract_count_1_10`
- **Designation shares**: `pct_lila_tracts_1_and_10`, `pct_low_income_tracts`, `pct_low_access_tracts_1_and_10`
- **Population burden shares**: `pct_population_low_access_1`, `pct_population_low_access_1_10`, `pct_population_low_income_low_access_1`, `pct_population_low_income_low_access_1_10`
- **Context fields**: `poverty_rate`, `median_family_income`

## Aggregation Rules
- The source is already published at census-tract grain, so tract rows remain source-native in Silver.
- County rollups are derived directly from the first 5 digits of `tract_geoid`.
  - This keeps the tract source faithful and avoids forcing a tract-vintage normalization step just to reach counties.
- CBSA rollups are derived from county rows via `silver.xwalk_cbsa_county`.
- Metric families use simple, explicit rules:
  - population burden counts are summed across tracts
  - tract designation counts are summed across tracts
  - tract designation shares are computed as tract counts divided by total tract count
  - population burden shares are recomputed as summed burden divided by summed population
  - `poverty_rate` and `median_family_income` use population-weighted means as tract-context fields

## Data Quality Notes
- The USDA Atlas is a single-vintage baseline (`2019`), not a recurring annual panel.
- The underlying Atlas uses `2010` tract polygons.
  - Silver intentionally avoids remapping those tract IDs to a newer tract backbone in the first pass.
  - County rollups are still reliable because they come straight from the tract GEOID prefix.
- The tract rows in this table are source-native rather than canonical-tract-backbone enforced.
- The first-pass county contract keeps the 8 legacy Connecticut county GEOIDs through an explicit manual lookup so the USDA rollups align with the current county geography contract used elsewhere in Foundations.
- Alaska county-equivalent `02261` is excluded from county and CBSA rollups because the current county crosswalk no longer carries that retired geography.
- CBSA coverage depends on county-to-CBSA crosswalk coverage in `silver.xwalk_cbsa_county`.

## Lineage
1. `foundations/etl/staging/get_usda_food_atlas.R` downloads the USDA workbook, reads the tract table, normalizes the approved compact field set, and writes `staging.usda_food_atlas`.
2. `foundations/etl/silver/usda_food_atlas_silver.R` keeps tract rows source-native, derives county GEOIDs from tract prefixes, rolls counties to CBSAs, recomputes tract-share and population-burden rates, and writes `silver.usda_food_atlas`.

## Known Gaps / To-Dos
- This first-pass Silver contract keeps only tract, county, and CBSA rows.
- If we later need a stricter current-vintage tract backbone, we should handle that as a separate geography-bridge project rather than pushing it into this baseline food-access table.
