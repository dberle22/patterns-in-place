# Data Dictionary: silver.hud_chas_burden

## Overview
- **Table**: `silver.hud_chas_burden`
- **Purpose**: Standardized HUD CHAS housing-cost-burden table for county, place, and derived CBSA geographies, preserving tenure and income-band detail.
- **Row count**: 649,026
- **Time coverage**: 2021

## What CHAS Means Here
- This Silver contract documents CHAS as a segmented burden table, not just a single rolled-up rate.
- The table keeps direct `county` and `place` rows from staging, then derives `cbsa` rows by rolling county CHAS counts through the county-to-CBSA crosswalk.
- HUD only ships direct `All` subtotals for the all-income rows, so Silver reconstructs the segmented denominators by summing the detailed `household_type` rows and then drops `household_type` from the final contract.
- The table preserves every staged income band, including `gt_100_hamfi`, because that detail is already present upstream and is useful for affordability comparisons.
- Gold will later pull a smaller set of rolled-up burden rates from this Silver contract rather than rebuilding them directly from staging.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year + tenure + income_band`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`, `tenure`, `income_band`)
- **Observed geo coverage**: `cbsa`, `county`, and `place`
- **Key QA**: the Silver script stops if duplicate `geo_level + geo_id + year + tenure + income_band` rows appear after the pivot.

## Columns

| Column | Type | Definition |
|---|---|---|
| `source` | `VARCHAR` | Upstream source or ETL-assigned provenance label for the row. |
| `geo_level` | `VARCHAR` | Canonical geography grain label for the row. |
| `geo_id` | `VARCHAR` | Canonical geographic identifier for the row. |
| `geo_name` | `VARCHAR` | Display name for the geography identified by `geo_id`. |
| `state_fips` | `VARCHAR` | Two-digit state FIPS code for county and place rows. Null for CBSA rows because metros can span multiple states. |
| `state_abbr` | `VARCHAR` | USPS state abbreviation for county and place rows. Null for CBSA rows because metros can span multiple states. |
| `chas_period` | `VARCHAR` | Source CHAS tabulation period label carried through from staging. |
| `year` | `INTEGER` | Calendar end year used as the canonical analysis year for the CHAS tabulation period. |
| `tenure` | `VARCHAR` | Tenure segment for the CHAS row: `all`, `owner`, or `renter`. |
| `income_band` | `VARCHAR` | Income band segment for the CHAS row: `all`, `le_30_hamfi`, `gt_30_to_50_hamfi`, `gt_50_to_80_hamfi`, `gt_80_to_100_hamfi`, or `gt_100_hamfi`. |
| `total_households` | `DOUBLE` | Total households in the geography-tenure-income segment from HUD CHAS Table 7. |
| `households_cost_burden_le_30` | `DOUBLE` | Households in the segment spending 30 percent or less of income on housing. |
| `households_cost_burden_30_50` | `DOUBLE` | Households in the segment spending more than 30 percent and up to 50 percent of income on housing. |
| `households_cost_burden_50plus` | `DOUBLE` | Households in the segment spending more than 50 percent of income on housing. |
| `households_cost_burdened` | `DOUBLE` | Households in the segment spending more than 30 percent of income on housing. |
| `households_severely_cost_burdened` | `DOUBLE` | Households in the segment spending more than 50 percent of income on housing. |
| `pct_cost_burdened` | `DOUBLE` | Share of the segment spending more than 30 percent of income on housing. |
| `pct_severely_cost_burdened` | `DOUBLE` | Share of the segment spending more than 50 percent of income on housing. |

## Data Quality Notes
- The documented Silver contract now includes direct `county` and `place` rows plus derived `cbsa` rows built by summing county CHAS household counts and recomputing burden rates from those summed counts.
- `household_type` detail is used during the transform to reconstruct segmented totals, then aggregated away so the final Silver table stays focused on geography, tenure, and income band.
- `households_cost_burdened` is derived as `households_cost_burden_30_50 + households_cost_burden_50plus`.
- `households_severely_cost_burdened` is the `>50%` bucket directly from CHAS.
- The rate columns use `total_households` as the denominator and return `NULL` when the denominator is zero; 90,604 rows (13.96%) currently have null burden rates for that reason.

## Lineage
1. `foundations/etl/staging/get_hud_chas.R` reads HUD CHAS Table 7 source files and writes staged county and place long tables.
2. `foundations/etl/silver/hud_chas_silver.R` standardizes county and place rows, preserves tenure and staged income bands, reconstructs segment totals from household-type detail where needed, rebases county CHAS counts to CBSA using `silver.xwalk_cbsa_county`, pivots burden buckets, derives burden counts and rates, and writes `silver.hud_chas_burden`.

## Known Gaps / To-Dos
- State and tract CHAS staging tables remain outside the documented Silver contract for now.
- Provider-level HUD documentation still needs a follow-up sync so every section reflects that CHAS is now modeled beyond staging.
