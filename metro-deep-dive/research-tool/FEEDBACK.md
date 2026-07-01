# Deep Dive Research Tool — Feedback Log

*Capture bugs, unclear displays, missing context, or anything that feels off. Include metro and tab.*

---

## Bugs

- [x] **Candidate List** — `IndexError: single positional indexer is out-of-bounds` on highlighted row. Fixed 2026-07-01.
- [ ] **Trajectory — KPI Movement** — heatmap is empty for all metros. The `phase6_kpi_trajectory_long.csv` uses `int64` CBSA codes; the app queries with a string. Fix: cast cbsa_code to int before filtering.
    - The current Trajectory visual is too dense. We should include line charts where we can select one or multiple KPIs to compare.
    - We should also find a way to compare to the national average for that KPI as well.
- [x] **Overview — gauge titles** — Livability / Opportunity / Character labels are clipped inside the gauge charts. Fix: increase top margin or shorten text.
- [x] **Livability / Opportunity — cluster name cutoff** — cluster label is truncated in the header metric widget. Fix: use `st.markdown` instead of `st.metric` for long strings.
- [ ] **Market Coverage** - we currently only have the three sample markets, JAX, Richmond, and NYC. We will need to resolve this at the end.

---

## Unclear / Confusing Displays

- [x] **Overview — Key Stats strip** — population rounds to millions (too coarse), Cross-Frame Type duplicates the header badge, Half-Alignment is blank for most metros. Replace with core human-readable KPIs: Population (exact), Median Age, 5yr Pop Growth, Median HH Income, Home Value-to-Income. All available in `mart_area_explorer.cbsa_profile_year`.
- [x] **Overview — Trajectory Summary** — "Diverging-Declining" and other direction labels need a tooltip or glossary link so the meaning is clear on first read.
- [x] **Livability / Opportunity — Topic Scores vs KPIs** — topics and their constituent KPIs are shown in separate tables with no visible connection. Should group KPIs under their parent topic so it's clear what rolls up to what. Topics come from our Intelligence frame design (defined in `intelligence_catalog.yml`) and are aligned with the semantic layer.
- [x] **Livability — KPI scaling unclear** — e.g. Premature Death Rate of 10,033.7 has no units or benchmark. Need either inline units (from `metric_catalog.yml`) or a national median comparator column.
    - Some of the units and rates are clearer now, still some aren't so clear like the Raw Values in Share Walk to Work, I'm assuming this should be a percentage. 
    - Let's confirm that the Scores are the z-scores.
- [x] **Character — GMM soft membership only appears for some metros** — this is correct behavior (all metros have it), but the cluster labels currently show "Cluster 1" through "Cluster 7" instead of the named cluster labels. Fix: look up cluster name from `character_cluster_name` map.
    - Should soft membership GMM show up for Livability and Opportunity and they are just missing since our samples don't have soft membership. Confirm this behavior.
- [x] **Trajectory — Pattern Flags empty for most metros** — correct: only top-decile metros get flags. Add a caption explaining the threshold so it doesn't look broken.
    - I see these values for NYC, but it's not clear what the Pattern Flags really mean. We need a better explanation of what to expect here and the methodology.
- [ ] **Trajectory — Candidate Score on this tab** — the analytical value here is showing *why* this metro surfaced, which is useful context alongside trajectory signals. But needs a brief label explaining the score is a composite of cross-frame divergence + trajectory strength.
    - Still not fully clear, what is the methodology and how is it useful outside of picking places to deep dive?
- [ ] **Candidate List tab** — feels out of place inside a metro profile. Consider moving it to the landing page as the primary market selection surface, and removing it as a tab (or keeping it as a secondary reference tab).

---

## Missing Content

- [x] **Overview — CBSA boundary map** — show the CBSA boundary with counties overlaid as a geographic orientation. CBSA + county GeoJSON already exists in `area-explorer/data/`. No KPIs required for v1; county-level KPI overlay is a nice-to-have.
- [x] **Opportunity — Top Industries & Occupations** — add a section showing employment share by industry and occupation category vs. national/division average. Data available in `gold.economics_industry_wide` and `gold.economics_occupation_wide` (LQ columns are especially useful for comparison).
    - We've added Industry and Occupation categories, before we close it out can you explain what exactly LQ means and how we can understand it? And why do we have a national comparison for Industry Employment and LQ for occuption mix? Can we have both metrics for both sets?
- [ ] **Zone Map — tract geometry** — the DuckDB spatial extension isn't loading, so the choropleth falls back to a table. Need to either: (a) pre-export per-CBSA GeoJSON files to disk, or (b) confirm `LOAD spatial` works in this Python environment and fix the extension path. Not worth loading all 78k tracts at startup — load per CBSA on tab open.
    - How do we resolve this? Can we try for a single market first.
- [x] **Zone Map — single unified tract table** — show all tract cluster types in one table so clusters can be compared across zone types without toggling the selector.
    - This is still not complete.
- [x] **Peers — comparison table KPIs** — the H2H and diverging peer tables only show percentiles and cluster labels. Add 4–5 core KPIs (population, median income, pop growth, home value-to-income) so the comparison is substantive. Same data source as the Key Stats fix above.

---

## Nice to Have

- [ ] **Landing page** — make Suggested Market buttons smaller/denser so more fit without scrolling. Add a brief description of what the tool is and what the Intelligence frames mean (1–2 sentences each).
- [ ] **Glossary / Key Terms** — a lightweight modal or sidebar expander defining: frame scores and their scale, trajectory direction labels (diverging vs. converging, improving vs. declining), cluster types, candidate score methodology. Could be a static markdown block in a `?` expander on each tab.
    - This is in progress across the app.
- [ ] **Peers — full market head-to-head** — allowing any two CBSAs (not just peers) to be compared would be useful. Probably too heavy to pre-load all 401×401 combinations; a two-selector UI pulling on demand is feasible.
    - We can continue to defer.
- [ ] **KPI units and benchmarks** — add national median as a comparator column in all KPI tables. Units for each KPI should come from `metric_catalog.yml` (`unit_format` field) once the mart KPIs are mapped there.

---

## Semantic Layer Gaps

- [ ] Individual KPI mart columns (e.g. `value_to_income`, `premature_death_rate`) have no `display_name` in `metric_catalog.yml`. Currently using a hand-coded dict in `config.py`. Should be unified.
- [ ] `metric_catalog.yml` has `unit_format` for gold-layer metrics but not for the Intelligence mart's scored/raw columns. Needed for the KPI scaling clarity issue above.

---

## Notes

- Topics in the Intelligence frame tabs (Livability, Opportunity, Character) come from our Intelligence frame design in `intelligence_catalog.yml`, not from PCA groupings. The semantic layer and Intelligence design are aligned — topics were defined first, then KPIs were assigned to them. The PCA was used to validate that groupings made sense, not to define them.
