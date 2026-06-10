# Data Dictionary: gold.health_wide

## Overview
- **Table**: `gold.health_wide`
- **Purpose**: Curated health, safety, education, and environment mart for the CHR-first livability health surface at county + CBSA grain.
- **Row count**: 40,610
- **KPI applicability**: Gold output table for health-oriented livability analysis and downstream scoring work.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on June 9, 2026: rows=40,610; distinct PK=40,610; duplicates=0
- **Time coverage**: `year` min=2016, max=2025
- **Geo coverage**: 2 geo levels; 4,084 distinct `geo_id`
  - `county`: 31,423
  - `cbsa`: 9,187

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Health outcomes**: `life_expectancy`, `life_expectancy_change_1yr`, `life_expectancy_change_5yr`, `premature_death_rate`, `premature_death_rate_change_1yr`, `premature_death_rate_change_5yr`, `premature_age_adjusted_mortality`, `child_mortality_rate`, `infant_mortality_rate`
- **Health behavior and access**: `drug_overdose_death_rate`, `poor_mental_health_days`, `poor_mental_health_days_change_5yr`, `adult_obesity`, `adult_obesity_change_5yr`, `physical_inactivity`, `physical_inactivity_change_5yr`, `pct_uninsured_adults`, `pct_uninsured_adults_change_1yr`, `pct_uninsured_adults_change_5yr`, `primary_care_ratio`, `primary_care_ratio_change_5yr`, `mental_health_provider_ratio`, `preventable_hospital_stay_rate`, `preventable_hospital_stay_rate_change_5yr`
- **Social and economic context**: `food_insecurity_rate`, `social_associations_per_10k`, `child_care_cost_burden_rate`, `hs_graduation_rate`
- **Physical environment**: `air_pollution_pm25`, `air_pollution_pm25_change_5yr`, `adverse_climate_events`, `pct_access_to_parks`
- **Safety and education**: `homicide_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`, `reading_score_index`, `math_score_index`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- This Gold mart is intentionally the approved CHR Silver contract carried through directly at county + CBSA grain.
- Derived trend columns are simple absolute deltas, not percent changes. They only populate when the same geography has a comparable observation exactly 1 or 5 years earlier.
- Provider access fields use CHR's published ratio helper columns (`population:provider`) rather than per-100k raw values.
- `air_pollution_pm25` and `adverse_climate_events` remain lagged holdover fields pending direct EPA and FEMA/environment source coverage in later tracks.
- Some measures remain sparse across the landed `2016-2025` panel:
  - `infant_mortality_rate` is null in 21,114 rows
  - `drug_overdose_death_rate` is null in 15,016 rows
  - `child_mortality_rate` is null in 12,435 rows
  - `reading_score_index` is null in 19,581 rows
- Several newer CHR measures, especially `adverse_climate_events` and `pct_access_to_parks`, are structurally null for many earlier years because CHR did not publish them consistently across the full backfill window.

## Lineage
1. **Primary build script**: [gold_health_wide.sql](../../../etl/gold/gold_health_wide.sql)
2. **Primary upstreams**:
   - `silver.chr_health_outcomes`

## Known Gaps / To-Dos
- The current Gold contract now carries the annual analytic backfill for `2016-2025`; the provider Trends CSV remains an optional future helper rather than a required Gold input.
- `air_pollution_pm25` and `adverse_climate_events` should be revisited once direct EPA and FEMA/environment tables exist.
- This table is intentionally CHR-first for now; future primary-source enrichments may extend or replace specific columns without changing the grain.
