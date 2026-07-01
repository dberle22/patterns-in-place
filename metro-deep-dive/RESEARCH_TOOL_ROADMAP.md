# Deep Dive Research Tool — Roadmap & Spec

*Last updated: 2026-06-30. This document scopes the place-first research tool that is the primary internal product of the Metro Deep Dive track. It is a separate product from Area Explorer (which is metric-first). Deep Dive reports are what you write when you find something interesting using this tool.*

---

## What this product is

The Deep Dive Research Tool is a **place-first** Streamlit app. You start by selecting a metro (CBSA), and the tool assembles that metro's full profile across all three Intelligence frames, its zone map, its peer comparisons, and its trajectory signals.

**The Research Tool is the product. The Deep Dive reports are the output.** The tool is not a pre-publication checklist — it's the analytical environment you use to explore metros and develop theses. You write a Deep Dive when you find something worth writing about, not on a fixed cadence.

This is distinct from the two other interactive products:

| Product | Entry point | Audience | Purpose |
|---|---|---|---|
| Area Explorer (CBSA Internal) | Metric → places | Dan (analytical) | "How do all metros rank on X?" |
| Area Explorer (CBSA Public) | Metric → places | Readers / clients | "Here's how metros compare on X" |
| **Deep Dive Research Tool** | **Place → full profile** | **Dan (analytical)** | "Give me everything on this metro" |
| Deep Dive Report | — | Readers / clients | Published long-form market analysis |

---

## Prerequisites by build step

Steps 1–3 are available now. Steps 4–6 follow Phase 7.

- Intelligence Phases 2–5 complete ✓ (all three frame models + cross-frame)
- Intelligence Phase 6 complete ✓ (trajectory analysis)
- Intelligence Phase 8 complete ✓ (`mart_intelligence` tables materialized in local DuckDB)
- `phase6_candidate_list.csv` available ✓ (candidate selection surface)
- Intelligence Phase 7 in progress — needed for Zone Map tab (Step 5) only

**Build Steps 1–3 now.** Steps 4–6 wait for Phase 7.

---

## Repository location

```
metro-deep-dive/
  RESEARCH_TOOL_ROADMAP.md          ← this file
  research-tool/
    app.py                          ← Streamlit entry point
    config.py                       ← feature flags, constants
    components/
      metro_selector.py             ← CBSA search/select (entry point)
      overview_tab.py               ← top-level frame snapshot
      livability_tab.py             ← full Livability frame profile
      opportunity_tab.py            ← full Opportunity frame profile
      character_tab.py              ← full Character frame profile
      trajectory_tab.py             ← Phase 6 trajectory signals
      zone_map_tab.py               ← tract-level zone cluster map
      peers_tab.py                  ← cosine similarity peers + cross-frame comparison
      candidate_tab.py              ← candidate list review (market selection surface)
    shared/                         ← symlink or copy of area-explorer/shared/
    data/
      cbsa_boundaries.geojson       ← shared with area-explorer
      tract_boundaries/             ← per-market tract GeoJSON (Jacksonville, Richmond VA first)
```

The `shared/` library (db.py, catalog.py, geo_utils.py, benchmark.py) is shared with the Area Explorer. Either symlink it or factor it into a top-level `foundations/python/` package that both products import.

---

## Entry point and metro selector

The landing state of the app is a metro search box. No default selection — the user must pick a metro to see anything.

**Metro selector:**
- Searchable typeahead (Streamlit `selectbox` with a searchable list of all 401 CBSAs)
- Recently viewed CBSAs stored in session state (last 5)
- "Suggested markets" panel below the search — top 20 CBSAs from `phase6_candidate_list.csv`, ranked by cross-frame divergence and trajectory interest score. This is the primary market selection surface.

Once a metro is selected, the full app loads with that metro's data across all tabs. Changing the metro selector refreshes everything.

---

## Layout

After metro selection, the app renders a fixed header with the metro name and its three cluster labels (one badge per frame), then a tabbed body:

```
┌──────────────────────────────────────────────────────────────────┐
│  [Metro name]  [Character cluster]  [Livability cluster]         │
│                [Opportunity cluster]    [Cross-frame type]       │
├──────────────────────────────────────────────────────────────────┤
│  [Overview]  [Livability]  [Opportunity]  [Character]            │
│  [Trajectory]  [Zone Map]  [Peers]  [Candidate List]             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Tab specifications

### Overview tab

A one-page snapshot of the selected metro across all three frames. Purpose: give the analyst the "so what" before drilling into individual frames.

**Content:**
- Three-frame score card: Livability percentile / Opportunity percentile / Character percentile (national rank, Census Division rank, and cluster label for each)
- L/O four-quadrant scatter with the selected metro highlighted and labeled
- Cross-frame divergence flag: "This metro ranks in the top X% of [frame] but bottom Y% of [frame]" — surfaced from `cross_frame_phase5_overlap_flags.csv`
- Key statistics strip: population, median household income, Census Division, metro type (from Character cluster)
- Trajectory summary: one-line direction signal per frame from Phase 6 (e.g., "Livability: improving / Opportunity: diverging outward")

### Livability tab

Full Livability frame profile.

**Content:**
- Subject score bars: Affordability / Health & Safety / Access & Infrastructure / Physical Environment (each scored 0–100 percentile, with division comparator)
- Topic score table: all topics within each subject, with national and division percentile
- Key KPI table: the 26 Livability KPIs with values, national rank, division rank, polarity indicator
- "This metro's Livability peers" — top 5 cosine-similarity peers on the Livability frame (from `livability_phase3_similarity_top10.csv`), shown as a mini comparison table
- Cluster context: the metro's Livability cluster label, the cluster's defining characteristics (from cluster centroids), and which other well-known metros share the cluster

### Opportunity tab

Full Opportunity frame profile. Same structure as Livability tab.

**Content:**
- Subject score bars: Resident Opportunity / Market / Investor Opportunity / Business & Industry Opportunity
- Topic score table
- Key KPI table (22 Opportunity KPIs)
- OZ context: `pct_oz_tracts` and `pct_population_in_oz` from `gold.dim_policy_designations` — highlighted if metro has significant OZ exposure
- "This metro's Opportunity peers" — top 5 cosine-similarity peers
- Cluster context with defining characteristics and peer metros

### Character tab

Full Character frame profile. Same structure as Livability and Opportunity tabs.

**Content:**
- Subject score bars: Demographics / Built Form / Civic Identity
- Topic score table
- Key KPI table (17 Character KPIs)
- GMM soft memberships: the metro's probability vector across all 7 Character clusters, shown as a small bar chart — "this metro is 58% Creative Class / Knowledge Hub, 34% Sun Belt Growth"
- "This metro's Character peers" — top 5 cosine-similarity peers
- Cluster context with defining characteristics

### Trajectory tab

Phase 6 trajectory signals for the selected metro.

**Content:**
- Per-frame trajectory direction badge: Diverging-Improving / Diverging-Declining / Converging-Improving / Converging-Declining (from `trajectory_scores.parquet`)
- Opportunity turn signal flag: if the metro's 1yr direction contradicts its 5yr trend (from `phase6_opp_turn_signals.csv`)
- KPI trajectory chart: a heatmap or small-multiples view of KPI z-score movement over time for the selected metro — which KPIs are moving fastest in which direction
- Pattern flags: which of the five Phase 6 patterns apply to this metro (Bounce-Back / Hidden Livability Winner / Diverging From Themselves / Fast Demographic Changer / Environmental Risk Outlier)
- Candidate score: the metro's rank on `phase6_candidate_list.csv` and the primary pattern driving its score

### Zone Map tab

Tract-level zone cluster map for the selected metro. Only available for markets where tract GeoJSON and zone assignments are ready.

**Content:**
- Choropleth map of tract-level zone clusters within the CBSA boundary
- Zone legend: cluster label, color, and one-line definition for each zone type
- Sidebar: toggle between Character zones / Opportunity zones / Cross-theme zones (the three cluster models from Phase 7)
- Click a tract → profile card: zone label, key KPI values, OZ flag from `gold.dim_policy_designations`
- Coverage note: for markets without tract data, show a placeholder with an expected availability date

**Initial markets:** Jacksonville, FL and Richmond, VA (the two Phase 7 test markets).

### Peers tab

Cross-frame peer analysis for the selected metro.

**Content:**
- Frame-by-frame peer table: top 10 similar CBSAs on each frame independently (Livability peers / Opportunity peers / Character peers) — three columns side by side
- Combined peers: top 10 from the cross-frame cosine similarity matrix (from `cross_frame_phase5_similarity_top10.csv`)
- "Diverging peers": metros that are similar on one frame but diverge on another — surfaces the most analytically interesting comparisons
- Mini scatter for any two selected peers: pick two metros from the peer lists and compare their full KPI profiles head to head

### Candidate List tab

The Phase 6 ranked Deep Dive candidate list. This is the market selection surface — not a profile of the selected metro, but a tool for choosing which metro to analyze next.

**Content:**
- Ranked table of all 401 CBSAs from `phase6_candidate_list.csv`, with columns: candidate score, pattern flags, Phase 5 overlap rank, trajectory direction per frame
- Filter by: pattern flag, Census Division, population range, state
- Selected CBSA highlighted in the table (pre-selects to the currently viewed metro)
- "Open this metro" button on each row — switches the active metro to that selection
- Export: download the filtered candidate list as CSV

---

## Technical notes

**Shared infrastructure:** The Research Tool reuses `shared/db.py`, `shared/catalog.py`, `shared/geo_utils.py`, and `shared/benchmark.py` from the Area Explorer. Do not duplicate query logic.

**Data sources unique to the Research Tool:**
- Phase 6 outputs: `trajectory_scores.parquet`, `phase6_candidate_list.csv`, `phase6_opp_turn_signals.csv`, `phase6_kpi_trajectory_long.csv`
- Phase 5 outputs: `cross_frame_scores.parquet`, `cross_frame_phase5_overlap_flags.csv`, `cross_frame_phase5_similarity_top10.csv`
- Phase 7 outputs: `gold.intelligence_zones` (once available), per-market tract GeoJSON

**Deployment:** Local only for now. This is an internal research tool. Deploy to Streamlit Cloud only if a client-facing use case emerges (e.g., a commissioned Deep Dive where the client wants to explore the data themselves).

**Performance:** Zone map tab with tract-level GeoJSON for a single metro (~1,000–2,000 tracts) should render in under 3 seconds. Load tract GeoJSON per-market on tab open, not at app startup.

---

## Build sequence

**Step 1 — Metro selector + Overview tab**
The minimum viable Research Tool. Metro search, header badges, Overview tab with the three-frame scorecard and L/O scatter. Does not require Phase 6 or Phase 7 — runs on the Phase 2–5 Intelligence outputs.

**Step 2 — Frame tabs (Livability, Opportunity, Character)**
Full KPI tables, subject/topic score bars, cluster context, and peer panels. Requires `gold.intelligence_livability/opportunity/character` to be populated.

**Step 3 — Peers tab**
Cross-frame similarity comparison. Requires Phase 5 cross-frame similarity outputs.

**Step 4 — Trajectory tab**
Phase 6 signals. Requires Phase 6 complete.

**Step 5 — Zone Map tab**
Tract-level zones. Requires Phase 7 complete and per-market tract GeoJSON.

**Step 6 — Candidate List tab**
Market selection surface. Requires Phase 6 `phase6_candidate_list.csv`.

Steps 1–3 can be built immediately after Intelligence Phase 8 (catalog finalization + DuckDB promotion). Steps 4–6 follow the Intelligence Layer phases they depend on.

---

## Relationship to the Deep Dive Report

The Research Tool is the analyst's workspace. The Deep Dive Report is what you publish when you find something worth writing about.

**How a report gets written:**
1. Browse the Candidate List tab — which metros are most analytically interesting by divergence and trajectory?
2. Select a metro. Work through the Overview, Frame, and Peers tabs to understand what makes it unusual.
3. Use the Trajectory tab to understand direction — is it improving, diverging, turning?
4. Use the Zone Map tab (after Phase 7) to see the sub-metro spatial structure — where are the Knowledge Corridors, the distressed tracts, the growth periphery?
5. When you have a thesis — something that would surprise a reader who thinks they know the city — start writing.

The tool exports charts as PNG for publication. The report text is a writing task, not a software task.

**There is no fixed cadence for Deep Dives.** You write one when the tool surfaces something interesting. Jacksonville and Richmond VA are the Phase 7 test markets and the most likely first subjects — but the Candidate List may surface something more compelling.
