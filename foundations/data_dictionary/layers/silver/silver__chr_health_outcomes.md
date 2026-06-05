# Data Dictionary: silver.chr_health_outcomes

## Overview
- **Table**: `silver.chr_health_outcomes`
- **Purpose**: Standardized CHR health, safety, education, and environment table at county grain with derived CBSA rollups.
- **Row count**: 4,077
- **Time coverage**: 2025 only in the current first-pass CHR contract.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**:
  - `county`: 3,152 rows
  - `cbsa`: 925 rows
- **Key QA**: live duplicate check on `geo_level + geo_id + year` returned zero duplicates.

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Health outcomes**: `life_expectancy`, `premature_death_rate`, `premature_age_adjusted_mortality`, `child_mortality_rate`, `infant_mortality_rate`
- **Health behavior and access**: `drug_overdose_death_rate`, `pct_uninsured_adults`, `primary_care_ratio`, `mental_health_provider_ratio`, `preventable_hospital_stay_rate`
- **Social and economic context**: `food_insecurity_rate`, `social_associations_per_10k`, `child_care_cost_burden_rate`, `hs_graduation_rate`
- **Physical environment**: `air_pollution_pm25`, `adverse_climate_events`, `pct_access_to_parks`
- **Safety and education**: `homicide_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`, `reading_score_index`, `math_score_index`

## Data Quality Notes
- County rows come directly from CHR county and county-equivalent observations. The staged national and state summary rows are intentionally excluded from this analytical surface.
- Provider access fields use CHR's published ratio helper columns (`population:provider`) rather than the paired per-100k raw values, because the ratio form is the approved downstream analytical contract.
- CBSA rows are derived from counties using `silver.xwalk_cbsa_county` plus ACS `silver.age_kpi` weights.
  - Total population weights are used for the general rates and ratios.
  - School-age population weights are used for `reading_score_index` and `math_score_index`.
- Some measures are meaningfully sparse in the live 2025 release:
  - `infant_mortality_rate` is null in 2,230 rows
  - `drug_overdose_death_rate` is null in 1,204 rows
  - `child_mortality_rate` is null in 1,128 rows
  - `reading_score_index` is null in 696 rows
- `air_pollution_pm25` and `adverse_climate_events` are intentional lagged holdover fields pending direct EPA and FEMA/environment source coverage in later tracks.

## Lineage
1. `foundations/etl/staging/get_chr.R` downloads the live CHR analytic CSV, removes the repeated embedded header artifact, preserves the source-wide wide staging surface, and writes `staging.chr_health_rankings`.
2. `foundations/etl/silver/chr_silver.R` filters staging to county rows, selects the approved 22-measure CHR contract, normalizes county names from crosswalk metadata, derives CBSA rows with `silver.xwalk_cbsa_county` plus ACS population weights, and writes `silver.chr_health_outcomes`.

## Known Gaps / To-Dos
- The current CHR Silver contract is a single-year 2025 snapshot. Multi-year extension via the Trends CSV remains deferred.
- `air_pollution_pm25` and `adverse_climate_events` should be revisited after EPA and FEMA tracks land direct primary-source coverage.
- CHR does not publish CBSA-native rows, so all CBSA values here are derived rollups rather than source rows.
