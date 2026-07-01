# Phase 7 Tract KPI EDA App

Interactive Streamlit explorer for the Phase 7 tract KPI clustering input set.

## Run

From the repo root, using the area-explorer venv (all dependencies are already installed):

```bash
PYTHONPATH=exploration/intelligence_framework/phase_7_zone_methodology/app \
  area-explorer/.venv/bin/streamlit run \
  exploration/intelligence_framework/phase_7_zone_methodology/app/app.py
```

Or from inside the app directory:

```bash
cd exploration/intelligence_framework/phase_7_zone_methodology/app
../../../../area-explorer/.venv/bin/streamlit run app.py
```

## Tabs

| Tab | What it answers |
|---|---|
| **Coverage** | Which KPIs are missing data, and how much? Flags KPIs >20% missing. |
| **Distribution** | Shape, skewness, log-transform toggle. CBSA overlay for comparison. |
| **Correlations** | KPI × KPI Pearson/Spearman heatmap. Filterable by |r| threshold. |
| **Scatter** | Any two KPIs. Sampled to 15k tracts for browser performance. |
| **Within-CBSA Variance** | Does this KPI vary within metros (zone value) or only between them? |

## Sidebar

- **Scope:** national or specific CBSAs. Filtering a few CBSAs is much faster for iteration.
- **Theme filter:** restrict the KPI selector to Character / Livability / Opportunity.
- **Selected KPI:** drives Distribution, Scatter default, and Within-CBSA Variance tabs.

## Notes

- The app reads from `gold.intelligence_zone_inputs`, the governed Gold table materialized for Phase 7. It no longer rebuilds the tract frame inside Streamlit.
- The full frame (~70k tracts × KPI columns) loads once and is cached for 1 hour. Subsequent tab switches are fast.
- Map views are intentionally excluded — rendering 70k tract polygons in Plotly is prohibitively slow. Use CBSA-filtered scope for spatial intuition.
- LODES KPIs (`jobs_per_resident`, `pct_jobs_high_wage`, `pct_jobs_professional_services`) are already carried into `gold.intelligence_zone_inputs` from `gold.economics_lodes_wide`. Coverage tab will show if tract rows are missing for any state.
