# Data Dictionary: silver.bls_oews

## Overview
- **Table**: `silver.bls_oews`
- **Purpose**: Silver-layer occupational employment and wage table that standardizes staged OEWS state and metro rows into canonical Foundations geography keys while preserving the occupation and wage-distribution surface needed for archetype and opportunity analysis.
- **Status**: materialized from the current `May 2025` state-plus-metro staging implementation.
- **Row count**: `186,419`
- **KPI applicability**: not explicitly a KPI table.

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year + soc_code`
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`, `soc_code`)
- **Current geography coverage**: `state` and `cbsa`
- **Current time coverage**: `2025`

## Contract Summary
- Input staging tables:
  - `staging.bls_oews_state`
  - `staging.bls_oews_metro_nonmetro`
- Base geography inputs:
  - state rows from `source_area_scope = 'state'`
  - metro rows from `source_area_scope = 'metro'`
- Deferred geography inputs:
  - nonmetro rows remain staged only in the first pass
  - territorial state-workbook rows remain staged only unless we explicitly decide to widen the geography policy
- Scope rule:
  - keep cross-industry state rows
  - keep cross-industry metro rows
  - drop nonmetro and territory rows from the first modeled Silver table
  - keep one row per `geo_level + geo_id + year + soc_code`

Live profile after materialization:
- `state` rows: `36,396`
- `cbsa` rows: `150,023`
- distinct `state` geographies: `51`
- distinct `cbsa` geographies: `393`
- distinct `soc_code` values: `852`

## Curated Keep / Drop Rule

This table is intentionally narrower than staging.

### Keep from staging
- Geography and source keys:
  - `area`
  - `area_title`
  - `area_type`
  - `prim_state`
  - `source_area_scope`
  - `release_year`
- Occupation keys:
  - `occ_code`
  - `occ_title`
  - `o_group`
- Core analytical metrics:
  - `tot_emp`
  - `jobs_1000`
  - `loc_quotient`
  - `h_mean`
  - `a_mean`
  - `h_pct10`
  - `h_pct25`
  - `h_median`
  - `h_pct75`
  - `h_pct90`
  - `a_pct10`
  - `a_pct25`
  - `a_median`
  - `a_pct75`
  - `a_pct90`
- Reliability and note fields:
  - `emp_prse`
  - `mean_prse`
  - `annual`
  - `hourly`
- Minimal provenance:
  - `source_workbook`

### Keep in staging but drop from first-pass Silver
- `naics`
- `naics_title`
- `i_group`
- `own_code`
- `pct_total`
- `pct_rpt`
- `source_geo_family`

Why this rule exists:
- the current staged workbooks are cross-industry files, so `naics`, `naics_title`, and `i_group` are largely constant in the first pass
- `pct_total` is only materially useful if we later widen to industry-specific OEWS or use industry context directly
- `pct_rpt` is useful QA context but not a core first-pass analytical measure
- `source_geo_family` is staging lineage rather than a decision-useful Silver dimension

## Recommended Canonical Dimensions
- Geography:
  - `geo_level`
  - `geo_id`
  - `geo_name`
  - `state_fips`
  - `state_abbr`
- Time:
  - `year`
- Occupation:
  - `soc_code`
  - `soc_title`
  - `soc_major_group`
  - `soc_major_group_title`
  - `o_group`
  - `occupation_bucket`
  - `is_stem`
- Provenance and QA:
  - `source_area_code`
  - `source_area_title`
  - `source_workbook`
  - `state_name`

## Recommended Canonical Measures
- `employment`
- `employment_prse_pct`
- `jobs_per_1000`
- `location_quotient`
- `hourly_mean_wage`
- `annual_mean_wage`
- `mean_wage_prse_pct`
- `hourly_p10_wage`
- `hourly_p25_wage`
- `hourly_median_wage`
- `hourly_p75_wage`
- `hourly_p90_wage`
- `annual_p10_wage`
- `annual_p25_wage`
- `annual_median_wage`
- `annual_p75_wage`
- `annual_p90_wage`
- `annual_note`
- `hourly_note`

## Source Mappings
- `year` <- `release_year`
- `soc_code` <- `occ_code`
- `soc_title` <- `occ_title`
- `employment` <- `tot_emp`
- `employment_prse_pct` <- `emp_prse`
- `jobs_per_1000` <- `jobs_1000`
- `location_quotient` <- `loc_quotient`
- `hourly_mean_wage` <- `h_mean`
- `annual_mean_wage` <- `a_mean`
- `mean_wage_prse_pct` <- `mean_prse`
- `hourly_p10_wage` <- `h_pct10`
- `hourly_p25_wage` <- `h_pct25`
- `hourly_median_wage` <- `h_median`
- `hourly_p75_wage` <- `h_pct75`
- `hourly_p90_wage` <- `h_pct90`
- `annual_p10_wage` <- `a_pct10`
- `annual_p25_wage` <- `a_pct25`
- `annual_median_wage` <- `a_median`
- `annual_p75_wage` <- `a_pct75`
- `annual_p90_wage` <- `a_pct90`
- `annual_note` <- `annual`
- `hourly_note` <- `hourly`

## Standardization Rules
- Geography mapping:
  - state rows: map staged `area` directly to canonical 2-digit `state_fips`
  - metro rows: map staged `area` directly to canonical 5-digit `cbsa_code`
  - set `geo_level = 'state'` for state rows and `geo_level = 'cbsa'` for metro rows
  - carry `source_area_code` and `source_area_title` so the original OEWS identifiers remain inspectable
- Occupation mapping:
  - rename `occ_code` to `soc_code`
  - rename `occ_title` to `soc_title`
  - derive `soc_major_group` from the first two digits of detailed SOC rows
  - assign `soc_major_group_title` from the official 2018 SOC major-group definitions
  - assign `occupation_bucket` from the repo-defined archetype mapping
  - assign `is_stem` from the OEWS STEM auxiliary definition rather than a custom heuristic
- Type handling:
  - coerce numeric-looking estimate fields to numeric
  - preserve note-marked values through explicit parsing rules rather than naive `as.numeric()`

## Recommended Coercion Policy
- Treat plain numeric strings as numeric values.
- Treat `*` as unavailable wage estimate and store the numeric field as `NULL` while preserving the note through `annual_note` or `hourly_note`.
- Treat `**` as unavailable employment estimate and store the numeric employment field as `NULL`.
- Treat `#` top-coded wages as `NULL` in the numeric wage field unless we also add a separate top-coded numeric convention; the note must survive either way.
- Treat `~` as a note on `pct_rpt`, which is dropped from first-pass Silver.

## Derived Columns
- `soc_major_group`
- `soc_major_group_title`
- `occupation_bucket`
- `is_stem`
- `is_major_group`
- `is_total_occupation`
- `employment_not_released`
- `any_wage_not_available`
- `any_wage_topcoded`

## Gold Handoff
- Primary Gold home: `gold.economics_occupation_wide`
- Intended Gold use:
  - occupation-bucket employment shares for archetype classification
  - wage percentile benchmarks by state and CBSA
  - occupation concentration benchmarking through `location_quotient`

## Data Quality Notes
- Validate uniqueness at `geo_level + geo_id + year + soc_code`.
- Confirm all first-pass Silver rows come only from `source_area_scope in ('state', 'metro')`.
- Confirm `naics = '000000'` and `naics_title = 'Cross-industry'` for all retained first-pass rows.
- Keep note-aware parsing explicit so suppressed or top-coded estimates are not silently turned into zeros.
- Confirm state rows exclude the territorial state-workbook members unless the geography policy changes.
- Live validation checks:
  - duplicate key count at `geo_level + geo_id + year + soc_code`: `0`
  - `is_stem = TRUE` rows: `19,538`
  - `is_total_occupation = TRUE` rows: `444`
  - `is_major_group = TRUE` rows: `9,737`
  - `employment_not_released = TRUE` rows: `4,220`
  - `any_wage_not_available = TRUE` rows: `12,574`
  - `any_wage_topcoded = TRUE` rows: `310`

## Lineage
1. [`foundations/etl/staging/get_bls_oews.R`](../../../etl/staging/get_bls_oews.R) lands the source-faithful OEWS state and metro/nonmetro tables.
2. [`foundations/etl/silver/bls_oews_silver.R`](../../../etl/silver/bls_oews_silver.R) filters the staged rows to the approved first-pass subset, normalizes geography and occupation metadata, downloads the official `May 2025` OEWS STEM occupation list, coerces the estimate fields, and writes `silver.bls_oews`.

## Known Gaps / To-Dos
- The current first pass converts top-coded `#` wage cells to `NULL` in the numeric wage fields and preserves their existence through `any_wage_topcoded`. Revisit if downstream Gold wants explicit capped-threshold values.
- The current STEM flag is pinned to the official `May 2025` `STEM occupations list` sheet. If we backfill earlier years, keep the year-specific BLS STEM definitions aligned to each release.
- The current first pass keeps total, major-group, and detailed occupation rows together. Gold should decide how much of that hierarchy to expose directly.
