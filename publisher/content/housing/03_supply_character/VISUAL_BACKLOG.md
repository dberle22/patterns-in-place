# Supply Character Visual Backlog
**Section:** `publisher/content/housing/03_supply_character/`  
**Last updated:** 2026-07-05  
**Purpose:** Exact first-pass checklist of Supply Character visuals to produce as standalone artifacts.

---

## Build Principle

We are using the same one-visual-per-script production pattern established in
the Vacancy and Costs sections.

Each visual should have:

- one chart-specific SQL file when query reuse is helpful
- one chart-specific `.R` build file
- one deliberate exported image artifact
- one stable visual name shared across SQL, script, and PNG output

---

## Priority Order

Build these in order so the section locks in its core framing first:

1. Major-CBSA permit-intensity map
2. Major-CBSA supply-mix comparison
3. Major-CBSA supply-vs-growth scatter

---

## Visual Checklist

### 1. Major-CBSA Permit-Intensity Map

- [x] **Visual ID:** `cbsa_permit_intensity_map`
- [x] **Chart type:** Proportional symbol map
- [x] **Story role:** Opening national map of where new building is concentrated
- [x] **Question:** Which major metros were building the fastest in `2024`, measured as permits per 1,000 housing units?
- [x] **Geography:** `cbsa`
- [x] **Metric:** `permits_per_1000_housing_units`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Geometry source:** `geo.cbsas`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_permit_intensity_map.sql`, `visuals/cbsa_permit_intensity_map.R`
- [x] **Export target:** `outputs/cbsa_permit_intensity_map.png`
- [x] **Status:** First production script created and rendered

### 2. Major-CBSA Supply-Mix Comparison

- [x] **Visual ID:** `cbsa_supply_mix_top_markets`
- [x] **Chart type:** Two-panel stacked bar
- [x] **Story role:** Compare what new building looks like against the current housing stock
- [x] **Question:** In the fastest-building major metros, how does the new permit mix compare with the existing stock mix in `2024`?
- [x] **Geography:** `cbsa`
- [x] **Metrics:** `permits_share_multifam_units`, `permits_share_units_1_unit`, `pct_struct_multifam`, `pct_struct_1_unit`
- [x] **Year / window:** `2024`
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Ranking rule:** Top `15` major CBSAs by `permits_per_1000_housing_units`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_supply_mix_top_markets.sql`, `visuals/cbsa_supply_mix_top_markets.R`
- [x] **Export target:** `outputs/cbsa_supply_mix_top_markets.png`
- [x] **Status:** First production script created and rendered

### 3. Major-CBSA Supply Vs Growth

- [x] **Visual ID:** `cbsa_supply_vs_growth`
- [x] **Chart type:** Scatter
- [x] **Story role:** Show whether fast-growing metros are adding enough housing supply
- [x] **Question:** Which major metros combined strong `2019` to `2024` population growth with strong or weak `2024` permit intensity?
- [x] **Geography:** `cbsa`
- [x] **Metrics:** `permits_per_1000_housing_units`, `pop_growth_5yr`
- [x] **Year / window:** `2024` snapshot + `2019` to `2024` population growth
- [x] **Source table:** `mart_housing.core_metrics`
- [x] **Filter choices:** `major_cbsa_100k_flag = TRUE`; exclude Puerto Rico rows
- [x] **Production files to create:** `sql/cbsa_supply_vs_growth.sql`, `visuals/cbsa_supply_vs_growth.R`
- [x] **Export target:** `outputs/cbsa_supply_vs_growth.png`
- [x] **Status:** First production script created and rendered

---

## First-Pass Scope Lock

These are in scope for the first Supply Character build:

- [x] major-CBSA permit-intensity map
- [x] top-market permit vs stock mix comparison
- [x] supply-vs-growth metro scatter

These are out of scope for the first pass unless we explicitly add them:

- [ ] county permit maps
- [ ] state permit choropleths
- [ ] division-level supply mix summaries
- [ ] permit-value visuals
- [ ] historical multifamily trend charts

---

## Notes

- The current major-market proxy is `major_cbsa_100k_flag` from `mart_housing.core_metrics`.
- The current production DuckDB is `foundations/etl/data/duckdb/patterns_in_place.duckdb`.
- The current implementation uses the top `15` major CBSAs by permit intensity for the mix bars so the section keeps a readable first-pass publishable subset.
- Population growth is framed with the `pop_growth_5yr` field on the `2024` mart surface, which corresponds to a `2019` to `2024` growth window.
- Completed so far:
- `03_supply_character/` now has a production `README.md`, `VISUAL_BACKLOG.md`, `sql/`, `visuals/`, `outputs/`, and `render_all.R`.
- All three first-pass Supply Character visuals now have standalone SQL inputs, production `R` build scripts, and rendered PNG outputs.
- The supply-mix comparison was implemented as a two-panel chart so the new permit mix and the inherited stock mix can be compared using the same ranked set of fast-building metros.
