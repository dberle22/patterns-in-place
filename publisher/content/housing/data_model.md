# Housing Data Model

This document records the current housing-section data model, the editorial choices we made while building it, and the Gold-layer improvements we either implemented or should queue next.

## Current Mart Surface

### Core mart

- Table: `mart_housing.core_metrics`
- Build file: [core_metrics.sql](publisher/content/housing/sql/core_metrics.sql:1)
- Grain: one row per `geo_level + geo_id + year`
- Geo levels: `division`, `state`, `cbsa`, `county`
- Current row count: `54,748`
- Key check: `54,748` distinct keys on `geo_level + geo_id + year`

### Overheating mart

- Table: `mart_housing.overheating_matrix`
- Build file: [overheating_matrix.sql](publisher/content/housing/sql/overheating_matrix.sql:1)
- Grain: one row per `geo_level + geo_id + year`
- Geo levels: `cbsa`, `county`
- Current row count: `35,410`
- Key check: `35,410` distinct keys on `geo_level + geo_id + year`
- Time coverage:
  - `cbsa`: `2016` to `2024` with `8,259` rows
  - `county`: `2016` to `2024` with `27,151` rows

### Inputs

- `gold.housing_core_wide`
- `gold.population_demographics`
- `gold.economics_income_wide`
- `gold.dim_geo`

### Temporary section flags

- `major_cbsa_100k_flag`
- `major_cbsa_250k_flag`

These are derived from `2024` CBSA population and inherited by counties through `parent_cbsa_code`.

## Snapshot-Year Rules

### Primary snapshot year

- Use `2024` for section snapshots, rankings, and most cross-sectional visuals.

### Income-growth rule

- Use `acs_income_pc_growth_1yr` and `acs_income_pc_growth_5yr` for `2024` snapshot work.
- Keep `income_pc_growth_1yr` and `income_pc_growth_5yr` as BEA-based historical context fields.
- Treat `2023` as the latest live year for BEA-backed income growth in the current warehouse.

### HUD benchmark-rent rule

- Treat `2023` as the latest live year for `fmr_2br`, `rent50_2br`, and related HUD benchmark fields.
- Do not use HUD benchmark rent fields as required inputs for `2024` snapshot rankings.

### Overheating snapshot rule

- Build the overheating mart across all available years so we can study change over time later.
- Use `2024` as the default editorial year for overheating rankings, quadrant views, and listicle-style outputs.
- Keep the composite explicitly provisional; downstream visuals can use components, percentiles, or the composite depending on the story.

## Historical KPI Coverage

The core mart has strong history for most housing KPIs. The main exceptions are BEA-backed income growth and HUD benchmark rents.

### Broadly reliable across all four geographies

- `vacancy_rate`: `2012` to `2024`
- `pct_rent_burden_30plus`: `2012` to `2024`
- `pct_rent_burden_50plus`: `2012` to `2024`
- `median_gross_rent`: `2012` to `2024`
- `annualized_median_rent`: `2012` to `2024`
- `median_home_value`: `2012` to `2024`
- `rent_to_income`: `2012` to `2024`
- `value_to_income`: `2012` to `2024`
- `pct_struct_multifam`: `2012` to `2024`
- `pop_total`: `2012` to `2024`
- `median_hh_income`: `2012` to `2024`

### Growth fields with built-in warmup windows

- `pop_growth_1yr`: first available `2013`
- `pop_growth_3yr`: first available `2015`
- `pop_growth_5yr`: first available `2017`
- `acs_income_pc_growth_1yr`: first available `2013`
- `acs_income_pc_growth_5yr`: first available `2017`

These warmup gaps are expected because they require prior-year history.

### Permit metrics with partial county sparsity

- `permits_per_1000_housing_units`: `2012` to `2024`
- `permits_per_1000_population`: `2012` to `2024`
- `permits_share_multifam_units`: `2012` to `2024`
- `permits_share_units_5_plus`: `2012` to `2024`
- `permits_avg_units_per_bldg`: `2012` to `2024`

Coverage notes for `2024`:

- `division` and `state`: effectively complete
- `cbsa`: low null rates, generally under `1%`
- `county`: visibly sparser, with about `3.8%` null for per-capita permit rates and about `11.6%` null for permit mix / average-units fields

### BEA-backed income growth

- `income_pc_growth_1yr`
  - `state`, `cbsa`, `county`: `2013` to `2023`
  - `division`: not currently available
- `income_pc_growth_5yr`
  - `state`, `cbsa`, `county`: `2017` to `2023`
  - `division`: not currently available

Interpretation:

- `2024` rows exist in `gold.economics_income_wide`, but they only carry ACS income levels today because BEA `CAINC` is not yet live for `2024`.
- Division BEA growth is missing because the current BEA Gold model is only built for `state`, `cbsa`, and `county`.

### HUD benchmark rents

- `fmr_2br`
  - `state`, `cbsa`, `county`: `2023` only
  - `division`: not currently available
- `fmr_gap_2br_vs_median_rent`
  - `state`, `cbsa`, `county`: `2023` only
  - `division`: not currently available

Interpretation:

- The live HUD FMR and rent50 warehouse surfaces currently top out at `2023`.
- Division HUD metrics are not modeled in Gold today.

## Overheating Mart Design

The overheating mart is a feature-and-score table, not just a final ranking output.

### Inputs

- `mart_housing.core_metrics`
- `gold.housing_market_wide`

### Raw KPI families in the mart

#### Momentum

- `hpi_yoy_pct`
- `hpi_5yr_pct`
- `zori_annual_avg_yoy_pct`

#### Pressure

- `acs_income_pc_growth_1yr`
- `acs_income_pc_growth_5yr`
- `pop_growth_1yr`
- `pop_growth_5yr`

#### Strain

- `rent_to_income`
- `value_to_income`
- `pct_rent_burden_30plus`

#### Tightness / supply

- `vacancy_rate`
- `permits_per_1000_housing_units`
- `permits_share_multifam_units`

### Standardization fields

The mart keeps two normalization layers for QA and downstream flexibility:

- Direction-aware percentile ranks within `geo_level + year`
- Direction-aware z-scores within `geo_level + year`

The direction logic is intentional:

- Higher is more overheating for price/rent momentum, population growth, income growth, burden, and price-to-income strain.
- Lower is more overheating for vacancy and permit-response supply metrics, so those are inverted during normalization.

### Component scores

- `momentum_component_score`
- `pressure_component_score`
- `strain_component_score`
- `tightness_component_score`

Each component score is the average of the available normalized input metrics in that component.

### Provisional composite

- `provisional_overheating_score`
- `provisional_overheating_score_pctile`
- `provisional_overheating_rank`

The composite is the average of the four component scores that are present for a row.

This is intentionally labeled provisional because:

- we have not yet tuned weights
- we have not yet pressure-tested alternative framings
- some source families, especially ZORI, remain partially missing

### Coverage and completeness

For `2024`, the component and composite score surface is complete for both `cbsa` and `county`:

- `momentum_component_score`: `0.0%` null in `2024`
- `pressure_component_score`: `0.0%` null in `2024`
- `strain_component_score`: `0.0%` null in `2024`
- `tightness_component_score`: `0.0%` null in `2024`
- `provisional_overheating_score`: `0.0%` null in `2024`

This works because the mart averages over the available metrics rather than requiring every single raw field to be populated.

### Source caveats inside the overheating mart

- FHFA coverage is strong but not perfect:
  - `2024` `hpi_yoy_pct` null rate is about `0.5%` for `cbsa`
  - `2024` `hpi_yoy_pct` null rate is about `15.5%` for `county`
- ZORI remains much sparser:
  - `2024` `zori_annual_avg_yoy_pct` null rate is about `45.4%` for `cbsa`
  - `2024` `zori_annual_avg_yoy_pct` null rate is about `71.7%` for `county`

Interpretation:

- ZORI should be treated as a useful enhancer, not a row-inclusion requirement.
- County overheating rankings are usable, but they still depend more heavily on FHFA plus the structural/context KPIs than on rent-momentum coverage.

## Rollup Guidance

If a KPI is missing at `state` or `division`, county rollup is feasible from a geography-coverage perspective:

- `100%` of states have county support in `gold.dim_geo`
- `100%` of divisions have county support in `gold.dim_geo`

That said, we should not blindly roll up every KPI the same way.

### Rollup types that are safe with explicit weighting

- Counts and totals:
  - `pop_total`
  - housing-unit or permit counts
- Rates or medians that can be recomputed from numerator / denominator fields already in the mart:
  - `vacancy_rate` from occupied and vacant counts
  - `pct_rent_burden_*` from burden counts and universes
  - permit-per-`1000` rates from permit counts plus `pop_total` or `hu_total`

### Rollup types that need care

- `fmr_2br`
  - should be population-weighted or renter-household-weighted from county values
  - should not be a simple unweighted average
- `median_gross_rent`
- `median_home_value`
- `median_hh_income`
- `acs_income_pc`

These are not additive and should only be rolled up if we define an explicit weighting rule or rebuild them upstream from a more granular source surface.

### Recommended policy

- Prefer direct Gold values when they exist.
- Use county rollups only for metrics that are missing at the requested geography and only with a documented aggregation rule.
- Do not silently mix direct state values with rolled-up division values inside the same published ranking without labeling the distinction.

## Choices We Made

### Implemented in the housing mart

- Built `mart_housing.core_metrics` as the reusable section mart.
- Restricted the section mart to `division`, `state`, `cbsa`, and `county`.
- Anchored snapshots on `2024`.
- Added `major_cbsa_100k_flag` and `major_cbsa_250k_flag`.
- Added `acs_income_pc` and `bea_income_pc` as separate columns so the income source is visible.
- Added `acs_income_pc_growth_1yr` and `acs_income_pc_growth_5yr` in the housing mart for contemporaneous `2024` snapshot use.
- Built `mart_housing.overheating_matrix` as a multi-year `cbsa` / `county` feature mart with raw inputs, percentile ranks, z-scores, component scores, and a provisional composite.

### Implemented upstream improvement

- Fixed a BEA state-key mismatch in [gold_economy_income.sql](foundations/etl/gold/gold_economy_income.sql:1) so `2023` state BEA income growth now joins and populates correctly.

## Gold-Layer Improvements To Suggest

### High priority

- Extend the BEA income ingest and Gold rebuild to include `2024` once the source is available.
- Add documented division rollups for BEA income fields if we want division-level income-growth analysis to be first-class.
- Extend HUD FMR / rent50 ingest beyond `2023`.
- Add a canonical major-market flag table in the Intelligence Layer so the housing section does not need temporary CBSA flags.

### Medium priority

- Add explicit source-vintage columns for mixed-source marts like `gold.housing_core_wide` and `gold.economics_income_wide`.
- Add coverage / null-profile QA checks for the KPI families that drive editorial rankings.
- Consider a shared rollup helper mart or reusable SQL pattern for county-to-state and county-to-division backfills.
- Consider adding a reusable normalization helper for percentile-rank and z-score feature marts if we expect to build similar scored marts in other sections.

### Low priority

- Decide whether ACS-derived income growth should eventually live in Gold proper or remain a section-layer convenience field.
- Add documentation that distinguishes “directly observed at this geography” from “derived by rollup” once any county-backfilled fields are introduced.

## Current Model Status

At this point, the housing section has both of its planned marts:

- `mart_housing.core_metrics`
- `mart_housing.overheating_matrix`

That means the workflow foundation is now in place for section-specific query writing:

- `2024` housing, population, and ACS income-growth context are available at `cbsa` and `county`
- BEA income growth is available through `2023`
- market momentum from `gold.housing_market_wide` is available for `cbsa` and `county` from `2016` through `2024` in the overheating mart
- HUD benchmark rents are optional context, not a required `2024` overheating input
- the overheating composite is ready for first-pass ranking and QA, but should still be treated as provisional while we test framing choices
