# Data Dictionary: gold.housing_core_wide

## Overview
- **Table**: `gold.housing_core_wide`
- **Purpose**: Curated housing mart that combines ACS housing and income context with HUD rent benchmarks and BPS permit activity.
- **Row count**: 1,020,930
- **KPI applicability**: Gold output table with inherited and derived housing affordability / supply metrics.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on April 10, 2026: rows=1,020,930; distinct PK=1,020,930; duplicates=0
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: 9 geo levels; 115,976 distinct `geo_id`
  - `zcta` 433,172
  - `place` 397,094
  - `tract` 135,851
  - `county` 41,870
  - `cbsa` 12,085
  - `state` 676
  - `division` 117
  - `region` 52
  - `us` 13

## Column Groups
- **Keys and core context**: `geo_level`, `geo_id`, `geo_name`, `year`, `pop_total`
- **Housing stock and occupancy**: `hu_total`, `occ_total`, `occ_occupied`, `occ_vacant`, `vacancy_rate`, `occupancy_rate`
- **Tenure**: `tenure_total`, `owner_occupied`, `renter_occupied`, `owner_occ_rate`, `renter_occ_rate`
- **Cost and burden**: `median_gross_rent`, `annualized_median_rent`, `median_home_value`, `median_owner_costs_mortgage`, `median_owner_costs_no_mortgage`, `rent_burden_total`, `rent_burden_30plus`, `rent_burden_50plus`, `pct_rent_burden_30plus`, `pct_rent_burden_50plus`
- **Income context**: `median_hh_income`, `per_capita_income`, `pov_rate`, `gini_index`, household income band shares
- **Derived affordability metrics**: `rent_to_income`, `value_to_income`
- **HUD benchmark rents**: `fmr_0br` to `fmr_4br`, `rent50_0br` to `rent50_4br`, `fmr_gap_2br_vs_median_rent`, `rent50_gap_2br_vs_median_rent`
- **Permit and supply indicators**: `permits_total_*`, `permits_multifam_*`, `permits_avg_units_per_*`, `permits_share_*`, `permits_structure_mix`, `permits_per_1000_*`, `multifam_permits_per_1000_housing_units`
- **Structure mix**: `struct_*`, `pct_struct_*`, `pct_struct_multifam`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- `rent_to_income` is null in 186,918 rows, which is expected where either ACS median rent or ACS median household income is missing.
- HUD benchmark rent fields remain sparse in the first pass: `fmr_2br` is null in 996,133 rows because HUD coverage is narrower and mostly 2023-only.
- BPS supply fields are also sparse outside supported BPS geographies: `permits_total_units` is null in 801,419 rows.
- The SQL currently stabilizes `silver.hud_*` and `silver.bps_wide` duplicates with grouped rollups before joining.

## Lineage
1. **Primary build script**: [scripts/etl/gold/gold_housing_core.sql]
2. **Primary upstreams**:
   - `silver.housing_kpi`
   - `silver.income_kpi`
   - `silver.hud_fmr_wide`
   - `silver.hud_rent50_wide`
   - `silver.bps_wide`
   - `silver.age_kpi`

## Known Gaps / To-Dos
- Zillow supplement metrics are intentionally excluded from this first-pass core mart.
- HUD and BPS coverage should be documented as partial by geography and year in downstream consumption.
- Consider adding explicit source-vintage columns for the HUD and BPS inputs if downstream users need clearer provenance.
