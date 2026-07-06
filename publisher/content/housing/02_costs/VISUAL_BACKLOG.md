# Costs Visual Backlog
**Section:** `publisher/content/housing/02_costs/`  
**Last updated:** 2026-07-05  
**Purpose:** Exact first-pass checklist of Costs visuals to produce as standalone artifacts.

---

## Build Principle

We are using the same one-visual-per-script production pattern established in
the Vacancy section.

Each visual should have:

- one chart-specific SQL file when query reuse is helpful
- one chart-specific `.R` build file
- one deliberate exported image artifact
- one stable visual name shared across SQL, script, and PNG output

---

## Priority Order

Build these in order so the section locks in its core framing first:

1. State rent-to-income map
2. Indexed cost comovement line chart
3. Major-CBSA vacancy change vs cost change scatter
4. Major-CBSA cost correlation heatmap

---

## Visual Checklist

### 1. State Rent-To-Income Map

- [x] **Visual ID:** `state_rent_to_income_map`
- [x] **Chart type:** Choropleth
- [x] **Story role:** Opening affordability framing visual
- [x] **Question:** Which states had the highest rent-to-income ratios in `2024`?
- [x] **Geography:** `state`
- [x] **Metric:** `rent_to_income`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Geometry source:** `geo.states`
- [x] **Filter choices:** Lower 48 states plus DC only; exclude `AK`, `HI`, `PR`
- [x] **Production files to create:** `sql/state_rent_to_income_map.sql`, `visuals/state_rent_to_income_map.R`
- [x] **Export target:** `outputs/state_rent_to_income_map.png`
- [x] **Status:** First production script created and rendered

### 2. Indexed Cost Comovement

- [x] **Visual ID:** `cost_index_trends`
- [x] **Chart type:** Indexed line
- [x] **Story role:** Show how rents and home values moved together over the `2019` to `2024` run-up
- [x] **Question:** How closely did rents and home values rise from `2019` to `2024` nationally and across the major-metro average?
- [x] **Geography:** mixed comparison series
- [x] **Metrics:** `annualized_median_rent`, `median_home_value`
- [x] **Year / window:** `2019` to `2024`
- [x] **Source tables:** `gold.housing_core_wide`, `mart_housing.core_metrics`
- [x] **Series required:** `United States` and `Major CBSA average`, each with indexed rent and home-value series
- [x] **Weighting rule:** housing-unit-weighted averages for major-CBSA series
- [x] **Production files to create:** `sql/cost_index_trends.sql`, `visuals/cost_index_trends.R`
- [x] **Export target:** `outputs/cost_index_trends.png`
- [x] **Status:** First production script created and rendered

### 3. Major-CBSA Vacancy Change Vs Cost Change

- [x] **Visual ID:** `cbsa_vacancy_vs_cost_changes`
- [x] **Chart type:** Faceted scatter
- [x] **Story role:** Show where tighter markets still saw rising housing costs and where the story looks contradictory
- [x] **Question:** Which major metros saw vacancy fall while rents or home values still rose from `2019` to `2024`?
- [x] **Geography:** `cbsa`
- [x] **Metrics:** `vacancy_rate` change, `annualized_median_rent` growth, `median_home_value` growth
- [x] **Year / window:** `2019` to `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_vacancy_vs_cost_changes.sql`, `visuals/cbsa_vacancy_vs_cost_changes.R`
- [x] **Export target:** `outputs/cbsa_vacancy_vs_cost_changes.png`
- [x] **Status:** First production script created and rendered

### 4. Major-CBSA Cost Correlation Heatmap

- [x] **Visual ID:** `cbsa_cost_correlation_heatmap`
- [x] **Chart type:** Correlation heatmap
- [x] **Story role:** Show which cost-growth measures tend to move together across major metros
- [x] **Question:** How tightly are `2019` to `2024` home-value and rent growth linked to affordability, vacancy, and growth pressure across major CBSAs?
- [x] **Geography:** `cbsa`
- [x] **Metrics:** home-value growth, rent growth, vacancy change, affordability, and growth-pressure fields
- [x] **Year / window:** mixed `2019` to `2024` growth + `2024` snapshot context
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_cost_correlation_heatmap.sql`, `visuals/cbsa_cost_correlation_heatmap.R`
- [x] **Export target:** `outputs/cbsa_cost_correlation_heatmap.png`
- [x] **Status:** First production script created and rendered

---

## First-Pass Scope Lock

These are in scope for the first Costs build:

- [x] `2024` rent-to-income state map
- [x] `2019` to `2024` indexed rent vs home-value chart
- [x] `2019` to `2024` vacancy-vs-cost faceted metro scatter
- [x] major-metro cost correlation heatmap

These are out of scope for the first pass unless we explicitly add them:

- [ ] county cost visuals
- [ ] small-multiple state trend panels
- [ ] HUD benchmark rent comparisons
- [ ] bivariate affordability maps
- [ ] published tables of most-expensive metros

---

## Notes

- The current major-market proxy is `major_cbsa_100k_flag` from `mart_housing.core_metrics`.
- The current production DuckDB is `foundations/etl/data/duckdb/patterns_in_place.duckdb`.
- `2019` to `2024` is the first-pass change window for cost-growth visuals in this section.
- The current interpretation of “correlation heatmap” is a major-CBSA metric-correlation matrix centered on home-value and rent growth, with affordability and pressure context fields added so the pattern is editorially useful.
- Completed so far:
- `02_costs/` now has a production `README.md`, `VISUAL_BACKLOG.md`, `sql/`, `visuals/`, `outputs/`, and `render_all.R`.
- All four first-pass Costs visuals now have standalone SQL inputs, production `R` build scripts, and rendered PNG outputs.
- The vacancy-vs-cost chart was implemented as a two-panel scatter so rent growth and home-value growth can both appear without collapsing them into a composite.
