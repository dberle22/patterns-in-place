# Overheating Visual Backlog
**Section:** `publisher/content/housing/04_overheating/`  
**Last updated:** 2026-07-05  
**Purpose:** Exact first-pass checklist of Overheating visuals to produce as standalone artifacts.

---

## Build Principle

We are using the same one-visual-per-script production pattern established in
the earlier housing sections.

Each visual should have:

- one chart-specific SQL file when query reuse is helpful
- one chart-specific `.R` build file
- one deliberate exported image artifact
- one stable visual name shared across SQL, script, and PNG output

---

## Priority Order

Build these in order so the section locks in its core framing first:

1. Hottest major CBSAs
2. Still-affordable shortlist
3. Momentum vs strain scatter
4. Momentum vs strain bivariate map
5. Component heatmap table

---

## Visual Checklist

### 1. Hottest Major CBSAs

- [x] **Visual ID:** `cbsa_overheating_hottest`
- [x] **Chart type:** Ranked horizontal bar
- [x] **Story role:** Name the markets that rise to the top under the provisional composite
- [x] **Question:** Which major metros look most overheated in `2024` under the current composite?
- [x] **Geography:** `cbsa`
- [x] **Metric:** `provisional_overheating_score`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.overheating_matrix`
- [x] **Ranking rule:** Top `10` by provisional overheating score
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_overheating_rankings.sql`, `visuals/cbsa_overheating_hottest.R`
- [x] **Export target:** `outputs/cbsa_overheating_hottest.png`
- [x] **Status:** First production script created and rendered

### 2. Still-Affordable Shortlist

- [x] **Visual ID:** `cbsa_overheating_still_affordable`
- [x] **Chart type:** Ranked horizontal bar
- [x] **Story role:** Surface markets that still look relatively affordable and less overheated by the current heuristic
- [x] **Question:** Which major metros still look comparatively affordable once we require below-median rent and value strain?
- [x] **Geography:** `cbsa`
- [x] **Metric:** custom shortlist score built from lower strain and lower momentum inside a below-median affordability universe
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.overheating_matrix`
- [x] **Ranking rule:** Top `10` by still-affordable shortlist score
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows; require below-median `rent_to_income` and `value_to_income`
- [x] **Production files to create:** `sql/cbsa_overheating_rankings.sql`, `visuals/cbsa_overheating_still_affordable.R`
- [x] **Export target:** `outputs/cbsa_overheating_still_affordable.png`
- [x] **Status:** First production script created and rendered

### 3. Momentum Vs Strain Scatter

- [x] **Visual ID:** `cbsa_overheating_scatter`
- [x] **Chart type:** Scatter
- [x] **Story role:** Show how fast price momentum and affordability strain interact across major metros
- [x] **Question:** Which major metros combine high momentum with high strain, and which remain calmer on both dimensions?
- [x] **Geography:** `cbsa`
- [x] **Metrics:** `momentum_component_score`, `strain_component_score`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.overheating_matrix`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_overheating_scatter.sql`, `visuals/cbsa_overheating_scatter.R`
- [x] **Export target:** `outputs/cbsa_overheating_scatter.png`
- [x] **Status:** First production script created and rendered

### 4. Momentum Vs Strain Bivariate Map

- [x] **Visual ID:** `cbsa_overheating_bivariate_map`
- [x] **Chart type:** Bivariate choropleth
- [x] **Story role:** Map where affordability strain and housing-market momentum overlap
- [x] **Question:** Which major metros combine high momentum and high strain on the national map?
- [x] **Geography:** `cbsa`
- [x] **Metrics:** `momentum_component_score`, `strain_component_score`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.overheating_matrix`
- [x] **Geometry source:** `geo.cbsas`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_overheating_bivariate_map.sql`, `visuals/cbsa_overheating_bivariate_map.R`
- [x] **Export target:** `outputs/cbsa_overheating_bivariate_map.png`
- [x] **Status:** First production script created and rendered

### 5. Top-Metro Component Heatmap

- [x] **Visual ID:** `cbsa_overheating_component_heatmap`
- [x] **Chart type:** Heatmap table
- [x] **Story role:** Show the component profile behind the hottest metros rather than leaving the composite unexplained
- [x] **Question:** Which component scores are driving the top overheating markets in `2024`?
- [x] **Geography:** `cbsa`
- [x] **Metrics:** momentum, pressure, strain, tightness, and composite percentile
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.overheating_matrix`
- [x] **Ranking rule:** Top `10` by provisional overheating score
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_overheating_component_heatmap.sql`, `visuals/cbsa_overheating_component_heatmap.R`
- [x] **Export target:** `outputs/cbsa_overheating_component_heatmap.png`
- [x] **Status:** First production script created and rendered

---

## First-Pass Scope Lock

These are in scope for the first Overheating build:

- [x] hottest major-CBSA composite ranking
- [x] still-affordable shortlist
- [x] momentum-vs-strain scatter
- [x] CBSA bivariate map
- [x] top-metro component heatmap

These are out of scope for the first pass unless we explicitly add them:

- [ ] county overheating visuals
- [ ] state overheating rollups
- [ ] alternative composite-weight scenarios
- [ ] rent-momentum-only maps
- [ ] multi-year overheating trend lines

---

## Notes

- The current major-market proxy is `major_cbsa_100k_flag` from `mart_housing.overheating_matrix`.
- The current production DuckDB is `foundations/etl/data/duckdb/patterns_in_place.duckdb`.
- The current implementation uses the provisional composite for rankings, but pairs it with component views so we do not overstate the stability of one locked heuristic.
- The “still affordable” shortlist is intentionally stricter than “least overheating”: it first requires below-median `rent_to_income` and `value_to_income`, then prefers lower strain and lower momentum.
- Completed so far:
- `04_overheating/` now has a production `README.md`, `VISUAL_BACKLOG.md`, `sql/`, `visuals/`, `outputs/`, and `render_all.R`.
- All five first-pass Overheating visuals now have standalone SQL inputs, production `R` build scripts, and rendered PNG outputs.
- The section uses the provisional composite for rankings, but the scatter, map, and heatmap keep the methodology legible by surfacing the underlying component structure.
