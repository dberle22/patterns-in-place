# Data Dictionary: gold.economics_occupation_wide

## Overview
- **Table**: `gold.economics_occupation_wide`
- **Purpose**: Gold-layer OEWS occupation-structure mart that summarizes the 2025 occupational mix of each state and CBSA on one wide `geo_level + geo_id + year` surface for archetype classification, specialization benchmarking, and wage-structure analysis.
- **Status**: materialized first-pass OEWS Gold output.
- **KPI applicability**: yes, this table is intended to expose decision-ready occupation-mix and wage benchmarks.

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year`
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current geography coverage**: `state` and `cbsa`
- **Current time coverage**: `2025`

## Contract Summary
- Input: `silver.bls_oews`
- Base geography: OEWS total rows where `geo_level in ('state', 'cbsa')`
- Rollup rule:
  - use the OEWS `total` row only as the denominator
  - use `detailed` SOC rows only for bucket employment and wage rollups
  - do not sum `major` rows into Gold family totals
- Surface design:
  - one wide row per geography-year
  - keep the five primary occupation families needed for archetype work
  - keep employment shares, family location quotients, employment-weighted mean wages, and compact quality counts
- Deferred from Gold:
  - full detailed SOC-level long surface
  - family percentile wage rollups
  - nonmetro and territory rows

## Live Profile
- **Row count**: `444`
- **Key check**: `444` rows and `444` distinct `geo_level + geo_id + year` combinations
- **Geo coverage**:
  - `51` state rows
  - `393` CBSA rows

## Why This Is A Dedicated Gold Table
- OEWS is an occupation-structure mart, not a labor-force status mart.
- `gold.economics_labor_wide` already owns LAUS and QWI labor-force / churn / worker-composition headlines at geography-year grain.
- `gold.economics_industry_wide` already owns industry employment and wage structure.
- OEWS answers a different question: what kinds of jobs a market has, how concentrated those occupational families are, and what those occupational families tend to earn.

That makes `gold.economics_occupation_wide` the right peer mart rather than a wide append onto an existing labor or industry table.

## Occupation Family Design
- `STEM` is an overlay, not a mutually exclusive family.
- The mutually exclusive families come from the curated `occupation_bucket` field in `silver.bls_oews`:
  - `management_professional`
  - `service`
  - `production_transportation`
  - `other`
- Gold recomputes family specialization from these family totals rather than averaging detailed occupation-level `location_quotient` values.

## Column Families

| Family | Columns | Definition |
| --- | --- | --- |
| Geography keys | `geo_level`, `geo_id`, `geo_name`, `year` | Canonical geography-year identifiers carried from `silver.bls_oews`. |
| OEWS denominator | `oews_emp_total` | Published all-occupation employment used as the denominator for Gold share and location-quotient metrics. |
| Occupation-family employment levels | `oews_emp_*` | Detailed-SOC employment rolled up to the approved occupation families plus the STEM overlay. |
| Occupation-family employment shares | `oews_pct_emp_*` | Family employment divided by `oews_emp_total`. |
| Occupation-family location quotients | `oews_lq_*` | Family employment share divided by the same-year national family share reconstructed from the published `state` slice. |
| Employment-weighted annual wages | `oews_mean_annual_wage_*` | Weighted mean annual wage across detailed occupations with non-null annual wage values inside each family. |
| Employment-weighted hourly wages | `oews_mean_hourly_wage_*` | Weighted mean hourly wage across detailed occupations with non-null hourly wage values inside each family. |
| Coverage diagnostics | `oews_unreleased_emp_soc_count`, `oews_missing_wage_soc_count`, `oews_topcoded_wage_soc_count` | Geography-year counts of detailed SOC rows with unreleased employment, unavailable wages, or top-coded wages. |

## Alignment Notes
- This table is aligned with the other economics-wide marts in one important way: it stays wide at `geo_level + geo_id + year` grain and is built as a dedicated peer mart.
- It intentionally does **not** reuse the ACS population spine because the live OEWS first-pass release is `2025` while `silver.age_kpi` currently ends in `2024`.
- The managed occupation families are not the same as the industry families in `gold.economics_industry_wide`; they come from curated SOC-based occupation buckets rather than NAICS-based industry rollups.

## Data Quality Notes
- National family shares used for Gold location quotients are derived from the `state` slice, not the `cbsa` slice, because CBSAs exclude nonmetro counties.
- The first pass will undercount family employment where detailed occupation employment is unreleased; the quality-count columns should be used to interpret those rows.
- The first pass intentionally excludes territory and nonmetro rows even though they are available upstream and in staging.
- `STEM` employment is not additive with the mutually exclusive occupation buckets because it is an overlay based on the official BLS STEM occupation list.

## Lineage
1. [`foundations/etl/staging/get_bls_oews.R`](../../../etl/staging/get_bls_oews.R) lands the OEWS state and metro/nonmetro workbook rows.
2. [`foundations/etl/silver/bls_oews_silver.R`](../../../etl/silver/bls_oews_silver.R) standardizes the state and CBSA rows into `silver.bls_oews`.
3. [`foundations/etl/gold/gold_economics_occupation_wide.sql`](../../../etl/gold/gold_economics_occupation_wide.sql) pivots the detailed occupation surface into the Gold geography-year occupation-family mart described here.

## Known Gaps / To-Dos
- If products later need a small number of flagship detailed occupations, add them intentionally as a second Gold surface or a narrow extension table instead of bloating this mart.
- If we later backfill `2021–2024`, revisit cross-year comparability notes and whether the BLS STEM overlay should be pinned year-by-year.
- If ACS `2025` geography-year base rows are added later and we want population-denominated occupation metrics, we can layer those on in a later revision without changing the OEWS core columns.
