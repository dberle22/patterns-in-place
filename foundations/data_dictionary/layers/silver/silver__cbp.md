# Data Dictionary: silver.cbp

## Overview
- **Table**: `silver.cbp`
- **Purpose**: Curated annual CBP analytical table for county business structure, with derived CBSA and state rollups built from the county history.
- **Row count**: `1,053,398`
- **Time coverage**: `2010` to `2023`

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + period + industry_code`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `industry_code`)
- **Observed geo coverage**:
  - `county`: `789,399` rows across `3,209` county GEOIDs
  - `cbsa`: `249,733` rows across `925` CBSA GEOIDs
  - `state`: `14,266` rows across `51` state GEOIDs
- **Industry coverage**: `20` curated CBP industry codes spanning the all-sectors row plus broad sector rows
- **Key QA**: live duplicate check on `geo_level + geo_id + period + industry_code` returned zero duplicates.

## Curated Subset Rule

This table is intentionally much narrower than staging.

- Keep the all-sectors row: `industry_code = '------'`
- Keep the published broad sector rows only:
  - `11----`, `21----`, `22----`, `23----`, `31----`, `42----`, `44----`, `48----`
  - `51----`, `52----`, `53----`, `54----`, `55----`, `56----`
  - `61----`, `62----`, `71----`, `72----`, `81----`
- Filter the county history to that curated subset first
- Derive `cbsa` and `state` rows from the filtered county subset after the county analytical surface is defined

Why this rule exists:
- the staged county history contains `2,249` distinct published NAICS-style codes and is too wide for the first analytical contract
- we want CBP to align with the same broad industry families already used elsewhere in the economics layer
- county remains the canonical base geography, so CBSA and state are governed rollups rather than parallel source feeds

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `period`, `industry_code`, `industry_title`
- **Geography helpers**: `state_fips`, `state_abbr`
- **Industry grouping helpers**: `silver_rollup_family`, `is_total_row`
- **Core business metrics**: `establishments`, `employment_march12`, `first_quarter_payroll_k`, `annual_payroll_k`
- **Establishment size buckets**: `est_n_lt_5`, `est_n_5_9`, `est_n_10_19`, `est_n_20_49`, `est_n_50_99`, `est_n_100_249`, `est_n_250_499`, `est_n_500_999`, `est_n_1000_plus`, `est_n_1000_1499`, `est_n_1500_2499`, `est_n_2500_4999`, `est_n_5000_plus`
- **Disclosure helpers**: `has_emp_flag`, `has_qp1_flag`, `has_ap_flag`
- **Derived payroll ratios**: `annual_payroll_per_employee`, `first_quarter_payroll_per_employee`
- **Metadata**: `source`

## Data Quality Notes
- County rows come directly from the staged county history after the curated industry filter is applied.
- CBSA rows are derived from county rows via `silver.xwalk_cbsa_county`.
- State rows are derived from county rows and use the USPS state abbreviation as the first-pass `geo_name`.
- Establishment, employment, and payroll metrics are summed for rollups.
- `annual_payroll_per_employee` and `first_quarter_payroll_per_employee` are recomputed from the rolled-up totals rather than averaged from county rate rows.
- The `has_*_flag` fields deliberately collapse the raw Census disclosure/noise flags to booleans in Silver.
  - County rows indicate whether the raw flag was present for that row.
  - CBSA and state rows indicate whether any contributing county row carried a flag.
- Public Administration is not included in this first-pass CBP Silver table because the county file does not expose a clean broad `92----` row comparable to the QCEW contract.
- Live profile after materialization:
  - `20` curated industry codes
  - `13` `silver_rollup_family` values
  - `58,251` total-sector rows
  - null `geo_name`: `0`

## Lineage
1. `foundations/etl/staging/get_cbp.R` lands the source-faithful county annual history in `staging.cbp_county`.
2. `foundations/etl/silver/cbp_silver.R` filters that history to the approved broad-sector analytical subset, standardizes county rows, derives CBSA and state rollups, recomputes payroll-per-employee metrics for the rolled-up geographies, and writes `silver.cbp`.

## Known Gaps / To-Dos
- This table is county-first by design; it does not attempt to preserve the deeper NAICS detail from staging.
- ZIP detail is intentionally separate and should become its own latest-year Silver surface later rather than widening this historical county table.
- If we later want a more detailed NAICS analytical table, that should be a companion Silver table rather than an expansion of this first-pass broad-sector contract.
