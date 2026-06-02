# Data Dictionary: gold.affordability_wide

## Overview
- **Table**: `gold.affordability_wide`
- **Purpose**: Consolidated affordability mart that combines housing costs, housing stress, income context, and RPP-adjusted income where available.
- **Row count**: 1,020,930
- **KPI applicability**: Gold output table for affordability analysis and future normalization work.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on April 10, 2026: rows=1,020,930; distinct PK=1,020,930; duplicates=0
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: 9 geo levels; 115,976 distinct `geo_id`

## Column Groups
- **Keys and base context**: `geo_level`, `geo_id`, `geo_name`, `year`, `pop_total`, `hu_total`
- **Housing cost inputs**: `median_gross_rent`, `annualized_median_rent`, `median_home_value`, `vacancy_rate`, `owner_occ_rate`, `renter_occ_rate`
- **Income inputs**: `median_hh_income`, `acs_income_pc`, `calc_income_pc`, `income_pc_growth_*`, `income_pc_cagr_*`, `pi_wage_share`
- **RPP context**: `rpp_real_pc_income`, `rpp_all_items`, `rpp_price_deflator`
- **Affordability outputs**: `rent_to_income`, `value_to_income`, `pct_rent_burden_30plus`, `pct_rent_burden_50plus`, `rent_to_rpp_income`, `value_to_rpp_income`
- **HUD reference rents**: `fmr_2br`, `rent50_2br`, `fmr_gap_2br_vs_median_rent`, `rent50_gap_2br_vs_median_rent`
- **Supply context**: `permits_per_1000_housing_units`, `permits_per_1000_population`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- `rpp_real_pc_income` is null in 1,002,526 rows; RPP context currently lands mostly for `cbsa` rows and a subset of county rows through CBSA/state backfill logic.
- `rent_to_rpp_income` is null in 1,002,541 rows because it depends on both RPP coverage and non-null rent values.
- Current non-null RPP coverage by geo level:
  - `county`: 13,884 rows
  - `cbsa`: 4,520 rows
  - `state`: 0 rows
- The zero state coverage indicates an identifier mismatch between affordability output `state` `geo_id` values and MARPP state IDs; treat state-level RPP fields as incomplete in the current snapshot.

## Lineage
1. **Primary build script**: [scripts/etl/gold/gold_affordability_wide.sql]
2. **Primary upstreams**:
   - `gold.housing_core_wide`
   - `gold.economics_income_wide`
   - `silver.bea_regional_marpp_wide`
   - `silver.xwalk_cbsa_county`
   - `silver.xwalk_county_state`

## Known Gaps / To-Dos
- State-level RPP backfill is not landing in the current snapshot because of a geo ID alignment issue.
- RPP coverage does not yet extend to tract, place, zcta, region, division, or US rows.
- This table is the right place to add normalized affordability fields later, but it does not currently include z-scores or percentile-style outputs.
