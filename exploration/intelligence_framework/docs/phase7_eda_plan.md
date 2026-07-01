# Phase 7 EDA Plan

*Last updated: 2026-07-01*

---

## What we are building

A Streamlit app (`phase_7_zone_methodology/app/app.py`) that lets us interactively explore the Phase 7 tract KPI input set before committing to a clustering approach. The goal is to make the Sprint 1.2 (KPI finalization) and Sprint 2.2 (imputation and standardization) decisions with actual data in front of us rather than on assumption.

The app reads directly from our DuckDB Gold layer via `gold.intelligence_zone_inputs`. It loads once, caches, and lets us slice by CBSA.

---

## The input data

**31 KPIs across three themes, one row per census tract.**

The tract frame is built by joining the Gold tables below on `geo_id` at `geo_level = 'tract'` across the full current tract base carried by `gold.intelligence_zone_inputs`. In the current live build, that surface spans about `78k` tracts across `925` CBSAs because it inherits the broader `silver.xwalk_cbsa_county` crosswalk rather than a narrowed 396-CBSA modeling subset.

| Theme | KPI | Gold table | Column |
|---|---|---|---|
| Character | Diversity Index | `population_demographics` | `diversity_index` |
| Character | % Hispanic | `population_demographics` | `pct_hispanic` |
| Character | % Black (non-Hispanic) | `population_demographics` | `pct_black_nh` |
| Character | % Asian (non-Hispanic) | `population_demographics` | `pct_asian_nh` |
| Character | % Age 65+ | `population_demographics` | `pct_age_over_64` |
| Character | % BA+ | `population_demographics` | `pct_ba_plus` |
| Character | % BA+ Change (3yr) | `population_demographics` | `pct_ba_plus_change_3yr` |
| Character | % Foreign Born | `migration_wide` | `pct_foreign_born` |
| Character | % Same House (Stability) | `migration_wide` | `pct_same_house` |
| Character | Owner Occupancy Rate | `housing_core_wide` | `owner_occ_rate` |
| Character | % Multifamily Structures | `housing_core_wide` | `pct_struct_multifam` |
| Character | Pop-Weighted Density | `transport_built_form_wide` | `pop_weighted_density_sqmi` |
| Livability | % Rent Burdened (30%+) | `housing_core_wide` | `pct_rent_burden_30plus` |
| Livability | Median Gross Rent | `housing_core_wide` | `median_gross_rent` |
| Livability | Median Home Value | `housing_core_wide` | `median_home_value` |
| Livability | Vacancy Rate | `housing_core_wide` | `vacancy_rate` |
| Livability | % No Internet Access | `social_infra_wide` | `pct_no_internet_access` |
| Livability | % HH Zero Vehicles | `transport_built_form_wide` | `pct_hh_0_vehicles` |
| Livability | % Commute by Walk | `transport_built_form_wide` | `pct_commute_walk` |
| Livability | % Commute by Transit | `transport_built_form_wide` | `pct_commute_transit` |
| Livability | Walkability Index | `transport_built_form_sld` | `walkability_index` |
| Livability | Jobs Access within 45 Min Transit | `transport_built_form_sld` | `jobs_access_45min_transit` |
| Livability | EJScreen PM2.5 | `environment_wide` | `ejs_pm25` |
| Livability | FEMA Risk Score | `environment_wide` | `fema_risk_score` |
| Opportunity | Median HH Income | `economics_income_wide` | `median_hh_income` |
| Opportunity | Poverty Rate | `economics_income_wide` | `pov_rate` |
| Opportunity | Poverty Rate Change (3yr) | `economics_income_wide` | `pov_rate_change_3yr` |
| Opportunity | Unemployment Rate | `economics_labor_wide` | `pct_unemployment_rate` |
| Opportunity | Jobs-to-Workers Ratio | `economics_lodes_wide` | `jobs_to_workers_ratio` |
| Opportunity | % Jobs High Wage | `economics_lodes_wide` | `pct_jobs_earnings_high` |
| Opportunity | % Jobs Professional Services | `economics_lodes_wide` | `pct_jobs_ind_professional_scientific_technical` |

**Known coverage gaps to investigate:**
- `economics_labor_wide` — tract and ZCTA unemployment now come from ACS labor metrics, while county / CBSA / state rows still use the LAUS + QWI surface
- `transport_built_form_sld` — one-time `2021` tract baseline; live Phase 7 join coverage is high nationally but the remaining misses are heavily concentrated in Connecticut
- `environment_wide` — tract rows now exist for EJScreen and FEMA, but coverage is still partial, source-specific, and mixed-vintage relative to the ACS-backed marts
- `economics_lodes_wide` — 84k tract rows; LODES does not cover all states (federal workers, some states opt out)

---

## App architecture

### How the data loads

On first load the app reads the prebuilt `gold.intelligence_zone_inputs` table from DuckDB. That Gold table already joins the tract KPI inputs at `geo_level = 'tract'` on the current tract backbone, so Streamlit no longer reconstructs the wide frame itself. The current live table is about `78k` rows and reflects the full crosswalk-backed tract surface now in Gold, not the older 396-CBSA-only framing from the methodology drafts. The result is held in Streamlit's `@st.cache_data` for one hour. All five tabs operate on this cached frame in memory; there are no further database queries after initial load.

### Sidebar

- **Scope** — toggle between national (all ~78k tracts) and one or more specific CBSAs. Filtering to CBSAs slices the in-memory frame, not the database, so it's instant. Useful for iterating on distributions and within-CBSA plots without waiting on the full universe.
- **Theme filter** — restrict the KPI selector to Character, Livability, or Opportunity. Drives the default KPI shown in tabs 2, 4, and 5.
- **Selected KPI** — the single KPI driving the Distribution, Scatter default axis, and Within-CBSA Variance tabs.

### File layout

```
phase_7_zone_methodology/app/
  app.py        — Streamlit entry point; all tab rendering logic
  config.py     — KPI list, theme assignments, polarity flags, Gold source mappings
  db.py         — DuckDB connection, tract frame query, coverage computation
  README.md     — run instructions
```

`config.py` is the single source of truth for the KPI set. Adding or removing a KPI means one edit there — the SQL, coverage table, correlation matrix, and all charts update automatically.

---

## What the app shows

### Tab 1 — Coverage
**Question: which KPIs are actually usable at tract grain?**

A bar chart of missingness percentage for every KPI, sorted worst-to-best, colored by theme. A threshold slider (default 20%) draws a reference line and flags KPIs above it with a warning banner. Below the chart, a full table shows raw counts (n present, n missing, % each).

This is the first thing to check on any new data pull. Known coverage patterns that will appear here: `economics_labor_wide` mixes ACS tract/ZCTA labor metrics with LAUS-backed county / CBSA / state rows; EJScreen and FEMA risk cover a narrower tract surface than the ACS-backed marts; LODES covers ~84k tracts. The coverage tab makes the severity of each gap visible so we can decide whether to impute, drop, or source-switch before the model runs.

### Tab 2 — Distribution
**Question: what does this KPI look like across tracts, and does it need a log transform?**

Histogram for the selected KPI with controls for bin count and a log-transform toggle. Five inline stats: median, P10, P90, skewness, and excess kurtosis. When skewness exceeds 1.5 and log transform is off, an info banner prompts enabling it — `pop_weighted_density_sqmi`, `median_home_value`, and `jobs_to_workers_ratio` will almost certainly trigger this.

An optional CBSA overlay plots one market's tract distribution on top of the national histogram, using a contrasting color. This is useful for checking whether a market like Jacksonville is representative of the national spread or an outlier on a given KPI before we use it as a stress-test market.

### Tab 3 — Correlations
**Question: which KPIs are collinear and candidates for collapsing?**

A full 31×31 Pearson or Spearman correlation heatmap (toggle between the two). Color scale runs from −1 (blue) to +1 (red) with white at zero. Below the heatmap, a filterable table lists all pairs exceeding a user-set |r| threshold, sorted by |r| descending.

This tab does the same job the CBSA-level variable selection notebooks did, but at tract grain. We expect `pov_rate` / `median_hh_income` / `pct_rent_burden_30plus` to be tightly correlated; `pct_commute_walk` / `pct_commute_transit` to overlap; and the racial composition KPIs to be more independent than at CBSA grain. Where tract-grain correlations diverge from what we saw at CBSA grain, that's a signal to revisit the KPI's role in the clustering vector.

The |r| = 0.75 threshold from the CBSA work is a reasonable starting point, but it may need tightening at tract grain given the larger sample size (statistical significance is easier to achieve at 78k rows than at 396).

### Tab 4 — Bivariate Scatter
**Question: do theoretically expected relationships hold at tract grain?**

X and Y axis selectors for any two KPIs, with optional log transforms on each axis. Because 78k points at full opacity would produce an illegible blob, the plot samples to 15k tracts (random, seeded for reproducibility) and renders at 50% opacity with small markers. The full-sample Pearson r and Spearman ρ are computed on the unsampled data and displayed below the chart.

Key diagnostic pairs to run:
- `pct_ba_plus` vs `median_hh_income` — should be strongly positive; the Knowledge Corridor hypothesis depends on this
- `pov_rate` vs `vacancy_rate` — should be positive; if not, the Distressed type centroid will be hard to name
- `jobs_to_workers_ratio` vs `pct_commute_walk` — should be positive (dense jobs centers have more walkers)
- `walkability_index` vs `pct_commute_walk` — should be positive (more walkable tracts should support more walking trips)
- `jobs_access_45min_transit` vs `pct_commute_transit` — should be positive, though likely noisy outside stronger transit networks
- `ejs_pm25` vs `median_home_value` — should be negative (environmental burden concentrated in lower-value areas)
- `pct_ba_plus_change_3yr` vs `median_gross_rent` — should be positive (human capital inflow drives rent up)

If these relationships are weak or reversed, something may be wrong upstream in the ETL or the polarity assumption for that KPI needs revisiting before z-scoring.

### Tab 5 — Within-CBSA Variance
**Question: does this KPI actually differentiate neighborhoods within a metro?**

This is the most analytically important tab and has no equivalent in the prior CBSA-level work. It shows box plots of the selected KPI's tract distribution within each CBSA — how spread out are tracts inside a single market on this measure?

Controls let you set a minimum tract count per CBSA (default 20), cap the number of CBSAs shown (default 30), and sort either by median value or by IQR (spread). Sorting by IQR highlights which markets have the most internal heterogeneity on a given KPI.

Three summary metrics appear below the chart:
- **National IQR** — the overall P25–P75 range across all tracts
- **Average within-CBSA IQR** — the mean P25–P75 range computed inside each CBSA separately
- **Within/National ratio** — the key diagnostic number

A ratio near 1 means the KPI varies as much inside metros as it does nationally — high zone-clustering value, the KPI will help the model separate neighborhoods. A ratio near 0 means the KPI mostly distinguishes CBSAs from each other but adds little signal within them. KPIs with low within-CBSA variance are candidates for dropping from the clustering vector even if they performed well at CBSA grain.

---

## Decisions the EDA will inform

| Decision | Relevant tab | Sprint |
|---|---|---|
| Which KPIs to drop due to coverage gaps | Coverage | Sprint 1.2 |
| Which KPIs need log transform before z-scoring | Distribution | Sprint 2.2 |
| Which KPI pairs to collapse due to collinearity | Correlations | Sprint 1.2 |
| Whether polarity assumptions hold at tract grain | Scatter | Sprint 1.2 |
| Which KPIs have zone-level discriminating power | Within-CBSA Variance | Sprint 1.2 |

---

## Running the app

```bash
PYTHONPATH=exploration/intelligence_framework/phase_7_zone_methodology/app \
  area-explorer/.venv/bin/streamlit run \
  exploration/intelligence_framework/phase_7_zone_methodology/app/app.py
```

For iterating, filter to a small set of CBSAs in the sidebar — the national frame (~78k tracts) loads in a few seconds but within-CBSA variance plots render faster on a subset.
