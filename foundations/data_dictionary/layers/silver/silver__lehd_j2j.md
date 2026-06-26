# Data Dictionary: silver.lehd_j2j

## Overview
- **Table**: `silver.lehd_j2j`
- **Purpose**: Silver-layer labor-mobility table that standardizes staged LEHD J2J annual rows into a canonical state / CBSA contract and derives the compact mobility-rate surface we can use downstream without carrying the full raw LEHD naming complexity.
- **Status**: materialized from the current annualized state + metro J2J staging implementation.
- **Row count**: `457,889`

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year + demo_code + industry_code`
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`, `demo_code`, `industry_code`)
- **Current geography coverage**: `state` and `cbsa`
- **Current demographic coverage**: age-family only
- **Current time coverage**: per-source rolling completed-year windows; current observed min=`2011`, max=`2024`

## Live Profile
- **State coverage**: `48,138` rows across `51` state geographies
- **CBSA coverage**: `409,751` rows across `435` metro geographies
- **Complete-year rows**: `456,022`
- **Incomplete-year rows**: `1,867`
- **Legacy metro fallback**:
  - `48` distinct source metro codes do not match the current CBSA naming crosswalk
  - these rows remain in Silver with `has_current_cbsa_match = FALSE`
  - current unmatched volume is `45,309` rows

## Contract Summary
- Input: `staging.lehd_j2j`
- Geography policy:
  - keep staged state rows directly as canonical `state`
  - keep staged metro rows directly as canonical `cbsa`
  - do not derive county, division, or U.S. rows from this table in the current first pass
- Analytical surface:
  - preserve core annual mobility counts
  - preserve annual average persistence / job-stayer reference counts
  - preserve annual average earnings fields
  - derive compact mobility-share metrics only for complete four-quarter annual rows
- Deferred from the first canonical Silver contract:
  - `J2JR` published-rate parity
  - `J2JOD` origin-destination industry-switching pairs
  - earnings-change distributions such as gaining / losing / stable shares, which require the deferred O-D or more detailed transition surface

## Recommended Canonical Columns
- Geography: `geo_level`, `geo_id`, `geo_name`
- Scope provenance: `source_scope_type`, `source_scope_id`, `has_current_cbsa_match`
- Time: `year`
- Demographic identifiers: `demo_family`, `demo_code`, `demo_label`
- Industry identifiers: `ind_level`, `industry_code`, `industry_label`, `industry_rollup_family`, `industry_rollup_level`
- Provenance and QA: `periodicity`, `source_periodicity`, `quarters_observed`, `is_complete_year`, `release_id`, `schema_version`, `keep_start_year`, `keep_end_year`, `latest_source_year`

## Recommended Canonical Measures
- Mobility counts:
  - `hires_total`
  - `separations_total`
  - `job_starts_total`
  - `job_ends_total`
  - `hires_from_employment`
  - `separations_to_employment`
  - `hires_from_adjacent_quarter_nonemployment`
  - `separations_to_adjacent_quarter_nonemployment`
  - `j2j_hires`
  - `j2j_separations`
  - `hires_from_nonemployment`
  - `separations_to_nonemployment`
- Reference counts:
  - `avg_nonemployment_persistence`
  - `avg_employment_persistence_after_nonemployment`
  - `avg_full_quarter_nonemployment`
  - `avg_full_quarter_employment_after_nonemployment`
  - `avg_job_stayers_count`
- Earnings:
  - `avg_ee_hire_earnings_dest`
  - `avg_ee_sep_earnings_orig`
  - `avg_jobstayer_earnings_dest`
  - `avg_jobstayer_earnings_orig`
  - `avg_ee_earnings_delta`

## Source Mappings
- `hires_total` <- `annual_mhire`
- `separations_total` <- `annual_msep`
- `job_starts_total` <- `annual_mjobstart`
- `job_ends_total` <- `annual_mjobend`
- `hires_from_employment` <- `annual_eehire`
- `separations_to_employment` <- `annual_eesep`
- `j2j_hires` <- `annual_j2jhire`
- `j2j_separations` <- `annual_j2jsep`
- `hires_from_nonemployment` <- `annual_nehire`
- `separations_to_nonemployment` <- `annual_ensep`
- `avg_ee_hire_earnings_dest` <- `annual_avg_eehiresearn_dest`
- `avg_ee_sep_earnings_orig` <- `annual_avg_eesepsearn_orig`

## Recommended Derived Measures
- `j2j_hire_share` = `j2j_hires / hires_total`
- `j2j_sep_share` = `j2j_separations / separations_total`
- `ee_hire_share` = `hires_from_employment / hires_total`
- `ne_hire_share` = `hires_from_nonemployment / hires_total`
- `ee_sep_share` = `separations_to_employment / separations_total`
- `en_sep_share` = `separations_to_nonemployment / separations_total`
- `avg_ee_earnings_delta` = `avg_ee_hire_earnings_dest - avg_ee_sep_earnings_orig`

## Standardization Rules
- Convert staged `source_scope_type = 'state'` rows to canonical `geo_level = 'state'`.
- Convert staged `source_scope_type = 'metro'` rows to canonical `geo_level = 'cbsa'`.
- Use the state geography backbone to name state rows.
- Use `silver.xwalk_cbsa_county` distinct CBSA names for metro rows when available.
- Keep legacy / unmatched metro codes instead of dropping them:
  - set `geo_name = 'Legacy metro code {geo_id}'` when no current CBSA name exists
  - flag them with `has_current_cbsa_match = FALSE`
- Preserve both `ind_level = 'A'` total-industry rows and `ind_level = 'S'` sector rows.
- Preserve both `A00` all-ages rows and age-slice rows so Silver supports headline and age-specific downstream use from one table.

## Rate Rules
- Derive rate/share fields only when:
  - `quarters_observed = 4`
  - the relevant denominator is positive
- Leave derived rates null for incomplete annual rows instead of inferring partial-year rates.
- Keep raw annual counts even when the year is incomplete so users can inspect partial or older-provider coverage explicitly.

## Data Quality Notes
- Validate uniqueness at `geo_level + geo_id + year + demo_code + industry_code`.
- Confirm `demo_family = 'age'` for all rows in the current Silver contract.
- Confirm `periodicity = 'A'` and `source_periodicity = 'Q'`.
- Confirmed the live Silver key is unique with `0` duplicate rows at the declared grain.
- Current live Silver is expected to include legacy metro codes that are not present in the current CBSA crosswalk; these should remain queryable but flagged.
- Because staging keeps a per-source rolling completed-year window, Silver also has uneven history by geography and should not be treated as a balanced panel without filtering.

## Gold Handoff
- Likely Gold home: dedicated `gold.labor_j2j_wide` rather than extending the existing QWI workforce-composition table.
- Intended Gold use:
  - annual labor-fluidity signals by state and CBSA
  - headline transition shares and earnings-change direction
  - Opportunity-frame labor-mobility comparisons across metros

## Lineage
1. [`foundations/etl/staging/get_lehd_j2j.R`](../../../etl/staging/get_lehd_j2j.R) materializes the annualized state + metro staging table.
2. [`foundations/etl/silver/lehd_j2j_silver.R`](../../../etl/silver/lehd_j2j_silver.R) standardizes geography, enriches labels, derives canonical rates, and writes `silver.lehd_j2j`.

## Known Gaps / To-Dos
- If published-rate parity becomes important, add a QA routine against `J2JR` rather than widening the core Silver contract immediately.
- If Deep Dive labor-flow work needs industry-switching pairs, that should land through a separate `J2JOD` path rather than by widening this table.
