# Data Dictionary: silver.chr_health_outcomes

## Overview
- **Table**: `silver.chr_health_outcomes`
- **Purpose**: Standardized CHR health, safety, education, and environment table at county grain with derived CBSA rollups.
- **Row count**: 40,610
- **Time coverage**: `2016-2025` in the current landed historical panel.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**:
  - `county`: 31,423 rows
  - `cbsa`: 9,187 rows
- **Key QA**: live duplicate check on `geo_level + geo_id + year` returned zero duplicates.

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **Health outcomes**: `life_expectancy`, `premature_death_rate`, `premature_age_adjusted_mortality`, `child_mortality_rate`, `infant_mortality_rate`
- **Health behavior and access**: `drug_overdose_death_rate`, `poor_mental_health_days`, `adult_obesity`, `physical_inactivity`, `pct_uninsured_adults`, `primary_care_ratio`, `mental_health_provider_ratio`, `preventable_hospital_stay_rate`
- **Social and economic context**: `food_insecurity_rate`, `social_associations_per_10k`, `child_care_cost_burden_rate`, `hs_graduation_rate`
- **Physical environment**: `air_pollution_pm25`, `adverse_climate_events`, `pct_access_to_parks`
- **Safety and education**: `homicide_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`, `reading_score_index`, `math_score_index`

## Data Quality Notes
- County rows come from the curated `staging.chr_health_rankings_history` annual panel. The staged national and state summary rows are intentionally excluded from this analytical surface.
- Provider access fields use CHR's published ratio helper columns (`population:provider`) rather than the paired per-100k raw values, because the ratio form is the approved downstream analytical contract.
- CBSA rows are derived from counties using `silver.xwalk_cbsa_county` plus ACS `silver.age_kpi` weights.
  - Total population weights are used for the general rates and ratios.
  - School-age population weights are used for `reading_score_index` and `math_score_index`.
- Some measures are meaningfully sparse across the landed `2016-2025` panel:
  - `infant_mortality_rate` is null in 21,114 rows
  - `drug_overdose_death_rate` is null in 15,016 rows
  - `child_mortality_rate` is null in 12,435 rows
  - `reading_score_index` is null in 19,581 rows
- `air_pollution_pm25` and `adverse_climate_events` are intentional lagged holdover fields pending direct EPA and FEMA/environment source coverage in later tracks.
- `adverse_climate_events` and `pct_access_to_parks` are structurally unavailable for much of the earlier panel and remain null in most pre-introduction years.

## Lineage
1. `foundations/etl/staging/get_chr.R` resolves annual CHR analytic CSV downloads for `2016-2025`, preserves the source-faithful `2025` wide staging table, and writes the curated county-only historical panel `staging.chr_health_rankings_history`.
2. `foundations/etl/silver/chr_silver.R` reads the curated annual panel, selects the approved 25-measure CHR contract, normalizes county names from crosswalk metadata, derives CBSA rows with `silver.xwalk_cbsa_county` plus ACS population weights, and writes `silver.chr_health_outcomes`.

## Known Gaps / To-Dos
- The current CHR Silver contract now uses annual analytic backfill for `2016-2025`; the provider Trends CSV remains deferred as an optional helper only.
- `air_pollution_pm25` and `adverse_climate_events` should be revisited after EPA and FEMA tracks land direct primary-source coverage.
- CHR does not publish CBSA-native rows, so all CBSA values here are derived rollups rather than source rows.
