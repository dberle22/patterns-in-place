# Data Dictionary: gold.health_wide

## Overview
- **Table**: `gold.health_wide`
- **Purpose**: Curated health, safety, education, and environment mart for the CHR-first livability health surface at county + CBSA grain.
- **Row count**: 4,077
- **KPI applicability**: Gold output table for health-oriented livability analysis and downstream scoring work.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on June 4, 2026: rows=4,077; distinct PK=4,077; duplicates=0
- **Time coverage**: `year` min=2025, max=2025
- **Geo coverage**: 2 geo levels; 4,077 distinct `geo_id`
  - `county`: 3,152
  - `cbsa`: 925

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Health outcomes**: `life_expectancy`, `premature_death_rate`, `premature_age_adjusted_mortality`, `child_mortality_rate`, `infant_mortality_rate`
- **Health behavior and access**: `drug_overdose_death_rate`, `pct_uninsured_adults`, `primary_care_ratio`, `mental_health_provider_ratio`, `preventable_hospital_stay_rate`
- **Social and economic context**: `food_insecurity_rate`, `social_associations_per_10k`, `child_care_cost_burden_rate`, `hs_graduation_rate`
- **Physical environment**: `air_pollution_pm25`, `adverse_climate_events`, `pct_access_to_parks`
- **Safety and education**: `homicide_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`, `reading_score_index`, `math_score_index`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- This first-pass Gold mart is intentionally the approved CHR Silver contract carried through directly at county + CBSA grain.
- Provider access fields use CHR's published ratio helper columns (`population:provider`) rather than per-100k raw values.
- `air_pollution_pm25` and `adverse_climate_events` remain lagged holdover fields pending direct EPA and FEMA/environment source coverage in later tracks.
- Some measures remain sparse in the live 2025 source release:
  - `infant_mortality_rate` is null in 2,230 rows
  - `drug_overdose_death_rate` is null in 1,204 rows
  - `child_mortality_rate` is null in 1,128 rows
  - `reading_score_index` is null in 696 rows

## Lineage
1. **Primary build script**: [gold_health_wide.sql](/Users/danberle/Documents/projects/patterns_in_place/foundations/etl/gold/gold_health_wide.sql)
2. **Primary upstreams**:
   - `silver.chr_health_outcomes`

## Known Gaps / To-Dos
- The current Gold contract is a single-year 2025 snapshot until the CHR Trends path is intentionally modeled.
- `air_pollution_pm25` and `adverse_climate_events` should be revisited once direct EPA and FEMA/environment tables exist.
- This table is intentionally CHR-first for now; future primary-source enrichments may extend or replace specific columns without changing the grain.
