# Vacancy Visual Backlog
**Section:** `publisher/content/housing/01_vacancy/`  
**Last updated:** 2026-07-05  
**Purpose:** Exact first-pass checklist of Vacancy visuals to produce as standalone artifacts.

---

## Build Principle

We are moving toward one production visual per `.R` file.

Each visual should eventually have:

- one chart-specific SQL file when query reuse is helpful
- one chart-specific `.R` build file
- one deliberate exported image artifact
- one short interpretation / QA note if needed

Suggested pattern:

- `sql/<visual_name>.sql`
- `visuals/<visual_name>.R`
- `outputs/<visual_name>.png`

---

## Priority Order

Build these in order so we lock the core section story first:

1. State vacancy map
2. Major-CBSA vacancy boxplot by region
3. Major-CBSA vacancy boxplot by division
4. Tightest major CBSAs bar chart
5. Loosest major CBSAs bar chart
6. Vacancy trend line: US + major-CBSA weighted average + regions
7. Vacancy trend line: US + major-CBSA weighted average + divisions

---

## Visual Checklist

### 1. State Vacancy Map

- [x] **Visual ID:** `state_vacancy_map`
- [x] **Chart type:** Choropleth
- [x] **Story role:** Opening national framing visual
- [x] **Question:** Which states have the highest and lowest housing vacancy rates in `2024`?
- [x] **Geography:** `state`
- [x] **Metric:** `vacancy_rate`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Geometry source:** `geo.states`
- [x] **Filter choices:** Exclude `AK`, `HI`, `PR` for contiguous-US framing
- [x] **Production files to create:** `sql/state_vacancy_map.sql`, `visuals/state_vacancy_map.R`
- [x] **Export target:** `outputs/state_vacancy_map.png`
- [x] **Status:** First production script created

### 2. Major-CBSA Vacancy Distribution By Region

- [x] **Visual ID:** `cbsa_vacancy_boxplot_region`
- [x] **Chart type:** Boxplot
- [x] **Story role:** Show broad regional spread across major metros
- [x] **Question:** How do major-metro vacancy rates differ across Census regions in `2024`?
- [x] **Geography:** `cbsa`
- [x] **Metric:** `vacancy_rate`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Grouping field:** `region_name`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_vacancy_distributions.sql`, `visuals/cbsa_vacancy_boxplot_region.R`
- [x] **Export target:** `outputs/cbsa_vacancy_boxplot_region.png`
- [x] **Status:** First production script created

### 3. Major-CBSA Vacancy Distribution By Division

- [x] **Visual ID:** `cbsa_vacancy_boxplot_division`
- [x] **Chart type:** Boxplot
- [x] **Story role:** Show the more detailed subregional spread behind region patterns
- [x] **Question:** How do major-metro vacancy rates differ across Census divisions in `2024`?
- [x] **Geography:** `cbsa`
- [x] **Metric:** `vacancy_rate`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Grouping field:** `division_name`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_vacancy_distributions.sql`, `visuals/cbsa_vacancy_boxplot_division.R`
- [x] **Export target:** `outputs/cbsa_vacancy_boxplot_division.png`
- [x] **Status:** First production script created

### 4. Tightest Major CBSAs

- [x] **Visual ID:** `cbsa_vacancy_tightest`
- [x] **Chart type:** Ranked horizontal bar
- [x] **Story role:** Name the metros where housing looks hardest to come by
- [x] **Question:** Which major CBSAs have the lowest vacancy rates in `2024`?
- [x] **Geography:** `cbsa`
- [x] **Metric:** `vacancy_rate`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Ranking rule:** Bottom `10` by vacancy rate
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_vacancy_extremes.sql`, `visuals/cbsa_vacancy_tightest.R`
- [x] **Export target:** `outputs/cbsa_vacancy_tightest.png`
- [x] **Status:** First production script created

### 5. Loosest Major CBSAs

- [x] **Visual ID:** `cbsa_vacancy_loosest`
- [x] **Chart type:** Ranked horizontal bar
- [x] **Story role:** Name the metros with the most open housing stock
- [x] **Question:** Which major CBSAs have the highest vacancy rates in `2024`?
- [x] **Geography:** `cbsa`
- [x] **Metric:** `vacancy_rate`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Ranking rule:** Top `10` by vacancy rate
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_vacancy_extremes.sql`, `visuals/cbsa_vacancy_loosest.R`
- [x] **Export target:** `outputs/cbsa_vacancy_loosest.png`
- [x] **Status:** First production script created

### 6. Vacancy Trend By Region

- [x] **Visual ID:** `vacancy_trend_regions`
- [x] **Chart type:** Multi-line
- [x] **Story role:** Show how vacancy changed nationally and across broad regions
- [x] **Question:** How has vacancy changed since `2012` across the US, major metros, and Census regions?
- [x] **Geography:** mixed comparison series
- [x] **Metric:** `vacancy_rate`
- [x] **Year / window:** `2012` to `2024`
- [x] **Source tables:** `gold.housing_core_wide`, `mart_housing.core_metrics`
- [x] **Series required:** `United States`, `Major CBSA average`, `Northeast`, `Midwest`, `South`, `West`
- [x] **Weighting rule:** housing-unit-weighted averages for non-US rollups
- [x] **Production files to create:** `sql/vacancy_trends.sql`, `visuals/vacancy_trend_regions.R`
- [x] **Export target:** `outputs/vacancy_trend_regions.png`
- [x] **Status:** First production script created

### 7. Vacancy Trend By Division

- [x] **Visual ID:** `vacancy_trend_divisions`
- [x] **Chart type:** Multi-line
- [x] **Story role:** Show the finer-grained geography behind region-level trend differences
- [x] **Question:** How has vacancy changed since `2012` across the US, major metros, and Census divisions?
- [x] **Geography:** mixed comparison series
- [x] **Metric:** `vacancy_rate`
- [x] **Year / window:** `2012` to `2024`
- [x] **Source tables:** `gold.housing_core_wide`, `mart_housing.core_metrics`
- [x] **Series required:** `United States`, `Major CBSA average`, all Census divisions
- [x] **Weighting rule:** housing-unit-weighted averages for non-US rollups
- [x] **Production files to create:** `sql/vacancy_trends.sql`, `visuals/vacancy_trend_divisions.R`
- [x] **Export target:** `outputs/vacancy_trend_divisions.png`
- [x] **Status:** First production script created

---

## First-Pass Scope Lock

These are in scope for the first Vacancy build:

- [x] current state snapshot map
- [x] region distribution
- [x] division distribution
- [x] tightest major metros
- [x] loosest major metros
- [x] region trend line
- [x] division trend line

These are out of scope for the first pass unless we explicitly add them:

- [ ] state change map from `2019` to `2024`
- [ ] county vacancy visuals
- [ ] small multiples by region
- [ ] annotated market callouts
- [ ] combined “tightest vs loosest” two-panel publishing layout

---

## Notes

- The current major-market proxy is `major_cbsa_100k_flag` from `mart_housing.core_metrics`.
- The current production DuckDB is `foundations/etl/data/duckdb/patterns_in_place.duckdb`.
- We should treat this file as the source-of-truth checklist and tick items off as each visual is rebuilt into its standalone `.R` workflow.
- Completed so far:
- `state_vacancy_map` now has a standalone SQL input, production `R` build script, and exported PNG path under `outputs/`.
- All seven first-pass Vacancy visuals now have standalone production `R` build scripts under `visuals/`.
- `render_all.R` now provides a simple batch rerun path for the full first-pass section.
