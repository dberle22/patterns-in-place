# Data Dictionary: gold.labor_j2j_wide

## Overview
- **Table**: `gold.labor_j2j_wide`
- **Purpose**: Gold labor-fluidity mart that summarizes annual headline LEHD J2J transition behavior for each state and CBSA on one wide `geo_level + geo_id + year` surface.
- **Status**: materialized from `silver.lehd_j2j`.
- **Row count**: `2,430`
- **KPI applicability**: yes, this table is intended to expose decision-ready labor-mobility metrics for benchmarking and downstream intelligence work.

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year`
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current geography coverage**: `state` and `cbsa`
- **Current time coverage**: complete annual rows only; current observed min=`2011`, max=`2024`

## Live Profile
- **State coverage**: `255` rows across `51` state geographies
- **CBSA coverage**: `2,175` rows across `435` metro geographies
- **Legacy metro fallback**:
  - `48` distinct metro codes remain unmatched to the current CBSA crosswalk
  - those unmatched codes account for `240` Gold rows
- **Earnings delta completeness**: `0` rows currently have null `j2j_avg_ee_earnings_delta`
- **Annual row distribution**:
  - `2011-2015`: `4` rows each year
  - `2016-2018`: `23` rows each year
  - `2019`: `66` rows
  - `2020`: `482` rows
  - `2021-2023`: `459` rows each year
  - `2024`: `416` rows

## Contract Summary
- Input: `silver.lehd_j2j`
- Base geography: Silver rows where `geo_level in ('state', 'cbsa')`
- Base slice:
  - `demo_code = 'A00'` all ages
  - `industry_code = '00'` all industries
  - `is_complete_year = TRUE`
- Surface design:
  - one wide row per geography-year
  - keep only the compact headline mobility counts, shares, and earnings-delta signals
  - preserve a small set of QA and provenance fields so downstream products can recognize legacy metro-code rows and uneven history
- Deferred from Gold:
  - age-specific wide columns
  - industry-specific mobility columns
  - `J2JOD` origin-destination and industry-switching pair metrics
  - `J2JR` parity checks, which remain a QA concern rather than a Gold surface requirement

## Recommended Canonical Columns
- Dimensions:
  - `geo_level`
  - `geo_id`
  - `geo_name`
  - `year`
- Provenance and QA:
  - `j2j_quarters_observed`
  - `j2j_has_current_cbsa_match`
  - `j2j_release_id`
  - `j2j_keep_start_year`
  - `j2j_keep_end_year`
- Headline mobility counts:
  - `j2j_hires_total`
  - `j2j_separations_total`
  - `j2j_job_starts_total`
  - `j2j_job_ends_total`
  - `j2j_hires_from_employment`
  - `j2j_hires_from_nonemployment`
  - `j2j_separations_to_employment`
  - `j2j_separations_to_nonemployment`
  - `j2j_direct_hires`
  - `j2j_direct_separations`
- Headline mobility shares:
  - `j2j_direct_hire_share`
  - `j2j_direct_sep_share`
  - `j2j_ee_hire_share`
  - `j2j_ne_hire_share`
  - `j2j_ee_sep_share`
  - `j2j_en_sep_share`
- Earnings context:
  - `j2j_avg_ee_hire_earnings_dest`
  - `j2j_avg_ee_sep_earnings_orig`
  - `j2j_avg_ee_earnings_delta`
- Supporting reference counts:
  - `j2j_avg_job_stayers_count`
  - `j2j_avg_main_job_beginning_count`
  - `j2j_avg_main_job_ending_count`

## Gold Rules
- Keep Gold wide at `geo_level + geo_id + year`; do not widen by age group or industry code in the first pass.
- Filter to `A00` all-ages and `00` all-industry rows so this mart stays headline-friendly and one row per geography-year.
- Keep only `is_complete_year = TRUE` rows in Gold. Incomplete annual rows remain useful in Silver but should not drive published Gold KPIs.
- Carry state and CBSA rows only. Do not derive county, division, or U.S. rows from the current J2J Silver contract.
- Retain legacy metro fallback rows rather than dropping them, but surface the `j2j_has_current_cbsa_match` flag so downstream consumers can exclude them when strict current-CBSA alignment is required.
- Reuse the precomputed Silver share fields rather than recomputing them in Gold.

## KPI And Metric Recommendations

### Keep as primary Gold KPIs
- `j2j_direct_hire_share`
- `j2j_direct_sep_share`
- `j2j_avg_ee_earnings_delta`
- `j2j_ee_hire_share`
- `j2j_ne_hire_share`
- `j2j_ee_sep_share`
- `j2j_en_sep_share`

These are the strongest first-pass metrics for:
- labor-market fluidity benchmarking
- worker ladder-climbing / earnings-upside framing
- distinguishing employment-to-employment churn from nonemployment re-entry dynamics

### Keep as supporting metrics
- headline mobility counts
- earnings-level fields
- `j2j_avg_job_stayers_count`
- `j2j_avg_main_job_beginning_count`
- `j2j_avg_main_job_ending_count`
- `j2j_has_current_cbsa_match`

These add scale, interpretability, and QA context without widening the mart into a detailed transition lattice.

## Why This Is A New Gold Table
- J2J is a labor-fluidity mart, not a general labor-force status mart.
- [`gold.economics_labor_wide`](gold__economics_labor_wide.md) already owns ACS/LAUS/QWI labor-force, employment, unemployment, and workforce-composition headlines.
- J2J answers a different question: how fluid is the labor market, and do direct employer-to-employer moves appear to improve earnings?
- Keeping J2J separate prevents `gold.economics_labor_wide` from turning into a catch-all labor table with mixed concepts and uneven geography history.

That makes `gold.labor_j2j_wide` the cleaner home than widening the existing labor mart.

## Data Quality Notes
- Because upstream retention is a per-source rolling completed-year window, this Gold table will not be a perfectly balanced panel across all geographies.
- Metro rows with `j2j_has_current_cbsa_match = FALSE` represent legacy source metro codes that do not align cleanly to the current CBSA crosswalk.
- The first pass intentionally keeps only complete-year rows so Gold metrics are not driven by partial-year annualizations.
- J2J counts are not employment stocks; users should not interpret them as workforce size. They describe transition activity over the year.

## Lineage
1. [`foundations/etl/staging/get_lehd_j2j.R`](../../../etl/staging/get_lehd_j2j.R) lands the annualized state + metro J2J staging table.
2. [`foundations/etl/silver/lehd_j2j_silver.R`](../../../etl/silver/lehd_j2j_silver.R) standardizes those rows into the canonical `silver.lehd_j2j` surface.
3. [`foundations/etl/gold/gold_labor_j2j_wide.sql`](../../../etl/gold/gold_labor_j2j_wide.sql) filters the all-age / all-industry / complete-year Silver slice and writes one wide labor-fluidity mart at geography-year grain.

## Known Gaps / To-Dos
- If products later need age-specific mobility KPIs, add them intentionally as a second Gold surface or a narrow extension table instead of exploding this mart.
- If Deep Dive work later requires industry-switching or labor import/export logic, build that from `J2JOD` as a separate mart rather than widening this table.
- Decide later whether a small trend block such as `j2j_direct_hire_share_change_1yr` belongs here or should be derived downstream.
