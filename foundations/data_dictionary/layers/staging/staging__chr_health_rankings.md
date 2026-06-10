# Data Dictionary: staging CHR Health Rankings

## Overview
- Schema: `staging`
- Family: `County Health Rankings`
- Contract scope: source-family staging contract for the wide county analytic table produced by [`foundations/etl/staging/get_chr.R`](../../../etl/staging/get_chr.R)
- Documentation rule: CHR now lands as one source-faithful current-release table plus one curated historical county panel, so this file is the canonical staging contract for the full CHR ingest family

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County analytic release | `chr_health_rankings` | Annual CHR analytic CSV with all published measure columns retained in wide form, including raw values, numerators, denominators, CI bounds, quality fields where shipped, and selected provider-specific helper fields |
| Curated historical county panel | `chr_health_rankings_history` | Annual county and county-equivalent panel for `2016-2025` keeping only geography fields, `release_year`, `county_clustered`, and the approved CHR historical measure columns used downstream |

## Contract Summary
- `chr_health_rankings`
  - Grain: one row per `fips5 + release_year`
  - Geography scope: source-faithful analytic release rows, including national and state summary rows plus the county and county-equivalent jurisdictions that feed downstream Silver
  - Current scope: `2025` annual analytic release
  - Live landed shape on `2026-06-09`: `3,204` rows and approximately `2,388` columns
- `chr_health_rankings_history`
  - Grain: one row per `fips5 + release_year`
  - Geography scope: county and county-equivalent rows only; national and state summary rows are intentionally excluded from this curated historical panel
  - Current scope: annual releases `2016-2025`
  - Live landed shape on `2026-06-09`: `31,423` rows across `10` release years and `32` columns

## Shared Columns
- Geography identifiers: `state_fips`, `county_fips`, `fips5`, `state_abbr`, `county_name`
- Release metadata: `release_year`, `county_clustered`
- Standard measure provenance pattern:
  - `v###_rawvalue`: published raw measure value
  - `v###_numerator`: source numerator underlying the measure
  - `v###_denominator`: source denominator underlying the measure
  - `v###_cilow`, `v###_cihigh`: lower and upper confidence interval bounds when provided
  - `v###_flag`: CHR quality or suppression flag where available in the provider file
- Provider-specific helper fields that also appear in the analytic file:
  - `v###_other_data_*`: supplemental components for selected measures such as provider ratios or severe housing subcomponents
  - `v###_race_*`: race and ethnicity specific estimates for measures that CHR publishes with subgroup breakout coverage
- Curated historical measure columns in `chr_health_rankings_history`:
  - `life_expectancy`, `premature_death_rate`, `premature_age_adjusted_mortality`, `child_mortality_rate`, `infant_mortality_rate`
  - `drug_overdose_death_rate`, `poor_mental_health_days`, `adult_obesity`, `physical_inactivity`
  - `pct_uninsured_adults`, `primary_care_ratio`, `mental_health_provider_ratio`, `preventable_hospital_stay_rate`
  - `food_insecurity_rate`, `social_associations_per_10k`, `child_care_cost_burden_rate`, `hs_graduation_rate`
  - `air_pollution_pm25`, `adverse_climate_events`, `pct_access_to_parks`
  - `homicide_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`, `reading_score_index`, `math_score_index`

## Lineage
- [`foundations/etl/staging/get_chr.R`](../../../etl/staging/get_chr.R) resolves annual analytic CSV URLs from the official current-year and archive documentation pages, caches the annual files under the raw data directory, preserves the source-wide current-release measure inventory in `staging.chr_health_rankings`, derives the curated county-only historical panel `staging.chr_health_rankings_history`, validates uniqueness at `fips5 + release_year`, and writes both staging tables.
- The provider-level measure inventory, Silver inclusion decisions, and downstream architecture notes live in [`../../sources/source__chr.md`](../../sources/source__chr.md).

## Data Quality Notes
- Verify uniqueness at `fips5 + release_year`; CHR analytic staging should be one row per source geography release, including the national and state summary rows that use zero-padded pseudo-FIPS keys.
- Confirm `fips5` is always a zero-padded five-digit county FIPS key after ingest.
- Retain `county_clustered` even though it is not part of the planned Silver contract. CHR uses this flag to mark counties grouped for ranking due to small population, and it is useful context for interpretation and QA.
- Keep all `rawvalue`, `numerator`, `denominator`, `cilow`, `cihigh`, `flag`, `other_data_*`, and `race_*` fields intact in `chr_health_rankings` so we do not need to re-ingest when current-release Silver scope changes.
- `chr_health_rankings_history` is the intentional exception to the normal source-faithful staging rule for this repo. It keeps only the county-level fields we actually plan to model historically so we do not materialize ten years of unused CHR provenance columns.
- Some current CHR historical fields were introduced after `2016`, so the curated history table legitimately contains structurally null older-year columns for newer measures such as `adverse_climate_events`, `pct_access_to_parks`, and other late-added fields.

## Known Gaps / To-Dos
- `chr_health_rankings_history` is ready for the multi-year Silver extension work in Track `19.2.5`; `silver.chr_health_outcomes` still needs to switch from the current single-year wide source to the new annual panel.
- The provider changes the analytic CSV filename pattern across release years, including inconsistent suffixes such as `_0` and `_v3`. The staging script now resolves the official documentation-page link first and uses pattern-based fallbacks only as a backup.
