# Patterns in Place — Working Roadmap

*Last updated: 2026-06-18. This is the strategy memo — it describes what we're building and why, and tracks high-level state per product area. Tactical work lives in product-level roadmaps: `INTELLIGENCE_LAYER_ROADMAP.md` for the Intelligence Layer. Future roadmaps for Area Explorer, Publisher, and Metro Deep Dive follow the same pattern.*

---

## Strategic Frame

The platform has five product areas and a shared foundations layer. The mental model for how they relate:

- **Foundations** is infrastructure. Get the remaining data sources done quickly, then stop thinking about it until the Points layer becomes relevant for Deep Dive work.
- **Publisher** is the content flywheel. The Chatbot ships for feedback; the Content pipeline runs on a structured cadence. Both generate writing material about the process itself.
- **Area Explorer + exploration/** is the analytical workspace. Raw discovery happens in `exploration/` notebooks. Clean outputs become lightweight Area Explorer dashboards. This is also where Intelligence scoring models get defined — through doing, not through upfront spec.
- **Metro Deep Dive** is the destination product. Long-form, rigorous, publishable market reports. Built on what the Area Explorer discovers.
- **Stoop** is a live v1. Incremental improvements as Intelligence scoring solidifies. Not a near-term focus.

**The core flywheel:**
```
exploration/ (ad hoc discovery)
    → Area Explorer (clean outputs + Intelligence calibration)
        → intelligence_catalog.yml (scoring models formalized)
            → Metro Deep Dive (first published report)
            → Stoop v2 (Livability + Opportunity scoring at NTA grain)
            → Publisher expansion (question bank grows from discoveries)
```

**Publishing is parallel throughout.** Content pipeline posts (Substack/X, anonymous) run continuously from the existing queue and grow as discoveries surface new questions. LinkedIn posts happen opportunistically when there's something worth writing about.

---

## Current State Snapshot (2026-06-18)

### Foundations — what's real

**Data platform is solid.** Tracks 1–5 are complete and Tracks 6–14 silver scripts all exist on disk — EPA AQI, FEMA NRI, EPA SLD, ACS broadband/disability/language, CBP, BFS, HUD CHAS, USDA Food Atlas, and Opportunity Insights Social Capital all have silver ETL scripts. Gold has 17 tables covering population, housing, economy, migration, transport, health, affordability, environment, food access, social fabric, social infrastructure, policy designations, and geo dimensions.

**The semantic layer is in progress.** `metric_catalog.yml` and `intelligence_catalog.yml` are populated but Intelligence catalog entries are still moving from `status: placeholder` to `status: calibrated` as Intelligence Layer phases complete. A final semantic layer alignment pass is planned after Intelligence scoring is stable — not before.

**Remaining foundations work:** The silver scripts for Tracks 6–14 exist; the remaining work is Gold promotion and semantic layer wiring for any sources not yet flowing into Gold tables. Treat this as opportunistic — do it when a gap is felt during Intelligence or Deep Dive work, not as a proactive sprint.

**Deferred until Deep Dive work begins (Tracks 15–17):** Points layer (K–12 school points, national POI sources, per-market OSM/Overture/parcels). Jacksonville has existing POI data from the Stoop pipeline; use that as the starting point.

### Products — what's real

| Product | State | Next step |
|---|---|---|
| Stoop Explore | Live (NYC, ~75%) | Incremental; revisit after Intelligence work |
| Stoop Search | Scaffolded (~20%) | Dormant until Intelligence scoring is stable |
| Publisher — Content pipeline | Infrastructure built; zero posts published | Start running posts after Intelligence work is done |
| Publisher — Chatbot | NL→SQL built locally; not deployed | Deploy after Intelligence scoring is in a working state |
| Area Explorer | Two-file scaffold; not deployed | Build CBSA Internal (Phase 1) after Intelligence Phase 8 |
| Intelligence Layer | Phase 3 (Livability) complete; Phase 4 (Opportunity) built, review notebook pending; Phase 2 (Character) not started | See `INTELLIGENCE_LAYER_ROADMAP.md` |
| Metro Deep Dive | ROF prototype only; no generalized template | Research Tool (D1) after Phase 8; first report (D2) after Phases 6–7 |
| exploration/ | Intelligence framework notebooks active | Primary analytical workspace right now |

---

## Roadmap

### Track A — Foundations (opportunistic, not a sprint)

The data platform is in good shape. Silver scripts for all Track 6–14 sources exist. Gold promotion for remaining sources happens when a specific gap is felt during Intelligence or Deep Dive work — not proactively.

After Intelligence scoring stabilizes, do a final semantic layer alignment pass: verify `intelligence_catalog.yml` entries are calibrated, `metric_catalog.yml` reflects the final empirically-tested KPI sets, and `theme_catalog.yml` is pruned of low-variance metrics. This is a one-time tightening pass before Area Explorer Phase 2 and the Chatbot are wired to the catalog.

Points layer (Tracks 15–17): defer until the first Deep Dive market is selected.

---

### Track B — Publisher (starts after Intelligence is done)

**B1 — Content pipeline:** Zero posts published. The infrastructure is built and the question backlog has good material. Start running posts once Intelligence scoring is stable — the L/O scatter, the Southern health deficit finding, and the social capital hypothesis are all ready to publish. See `publisher/content/publisher_backlog.md`.

**B2 — Chatbot:** NL→SQL pipeline is built locally. Two things needed before shipping: (1) wire `theme_catalog.yml`, `intelligence_catalog.yml`, and `question_catalog.yml` into the query pipeline; (2) deploy to Streamlit Cloud + Groq + MotherDuck. Ship when Intelligence has working scores — not perfect, just working. Portfolio/demo piece, not commercial.

---

### Track C — Area Explorer (starts after Intelligence is done)

Area Explorer is the metric-first analytical surface for the platform. You pick a theme, subject, topic, or metric — the map, ranking table, and charts update around that selection. Three independent Streamlit apps, connected by a landing page. See `area-explorer/AREA_EXPLORER_ROADMAP.md` for the full spec.

**Two audiences, two CBSA apps:**
- `cbsa_internal` — dense analytical tool for Dan; includes Intelligence frame clusters, scores, GMM soft memberships, cosine-similarity peers, and the L/O four-quadrant Intelligence tab. Local deployment.
- `cbsa_public` — clean reader/client-facing tool; same metric-first structure but no frame scores or cluster labels until those are established in published articles. Deployed on Streamlit Cloud.

**Three apps in build order:**

**Phase 1 — CBSA Internal:** Catalog-driven metric picker (theme → subject → topic → metric), choropleth map, ranking table, profile panel with national + Census Division benchmarks, scatter / trend / distribution / Intelligence tabs. Replaces the current `app/data_explorer.py` with the new shared-component architecture. Requires Intelligence Phase 8 (Gold intelligence tables) to be complete for the Intelligence tab.

**Phase 2 — CBSA Public + Landing Page:** Public-facing CBSA app with public theme labels ("Community Profile" / "Quality of Life" / "Economic Conditions"), plain-language benchmark framing, no cluster labels or frame scores. Deployed to Streamlit Cloud. Landing page linking all three apps.

**Phase 3 — County Explorer:** Independent county-level app, state-filtered by default (national county choropleth is too slow as default). No Intelligence frames at county grain. Links back to CBSA app by state. Deployed to Streamlit Cloud.

**Phase 4 — Zone Layer:** Tract-level zone cluster view in the internal app for Deep Dive markets (Jacksonville, Richmond VA first). Follows Intelligence Phase 7 (Zone Methodology) and requires `gold.intelligence_zones` to be populated.

---

### Track D — Metro Deep Dive (destination product; follows Intelligence + Area Explorer)

Two parallel deliverables: the published long-form report, and the internal Research Tool that supports writing it.

**D1 — Deep Dive Research Tool** (`metro-deep-dive/RESEARCH_TOOL_ROADMAP.md`): A place-first Streamlit app. Pick a metro → see its full profile across all three Intelligence frames, trajectory signals, zone map, peer comparisons, and the Phase 6 candidate list. Internal only. This is the analyst's workspace for building the report. Build Steps 1–3 (metro selector, frame tabs, peers tab) are available after Intelligence Phase 8; Steps 4–6 (trajectory, zone map, candidate list) follow Phases 6 and 7.

**D2 — Deep Dive Report:** Long-form, rigorous, publishable market analysis. Structure: Overview → 3 Intelligence Frames → Zone Analysis → (optional) Parcel layer. Output is a Substack post, PDF, or interactive document.

**Prerequisites before first report:**
- Intelligence Phases 2–8 complete (all frame models, trajectory, zones, DuckDB promotion)
- Deep Dive Research Tool Steps 1–3 working (needed to select market and develop narrative)
- Market selected via the Phase 6 candidate list — Jacksonville and Richmond VA are the two Phase 7 test markets and the most likely candidates
- Points layer not needed for Phase 1 report — Places-only is sufficient for Overview + 3 Frames structure

The old ROF retail framing (`metro-deep-dive/markets/jacksonville/`) is reference material only. The first report starts fresh from the Intelligence Frame structure.

---

### Track E — Stoop (not a near-term focus)

Stoop Explore is live. No major investment until Intelligence scoring is stable.

**Stoop Search:** Dormant until Livability and Opportunity scoring are working and a decision is made to build the listing scoring UI. Zillow ingest is already at Gold.

**Stoop v2:** After the first Deep Dive establishes the per-market Points framework. Jacksonville is the natural second market.

---

## Sequencing Summary

```
Now (active):
  Intelligence Layer — Phases 2–8 in sequence
  See INTELLIGENCE_LAYER_ROADMAP.md for the full phase-by-phase sequence

After Intelligence Phases 2–5 complete (all frame models stable):
  A  — Semantic layer alignment pass: finalize intelligence_catalog.yml,
       prune metric/theme catalogs
  B1 — Start Publisher content pipeline; L/O scatter + health deficit findings
       are the first posts
  B2 — Wire catalogs into chatbot, deploy

After Intelligence Phase 8 (DuckDB Gold intelligence tables promoted):
  C1 — Build Area Explorer CBSA Internal (Phase 1) — full metric-first explorer
       with Intelligence frames; replaces data_explorer.py
  D1 — Build Deep Dive Research Tool Steps 1–3 (metro selector, frame tabs,
       peers tab) — the analyst workspace before the first report

After Area Explorer Phase 1 deployed:
  C2 — Area Explorer CBSA Public + Landing Page (Phase 2)

After Intelligence Phases 6–7 complete (trajectory + zone methodology):
  D1 — Complete Deep Dive Research Tool Steps 4–6 (trajectory, zone map,
       candidate list)
  D2 — Select first Deep Dive market from Phase 6 candidate list;
       write first report
  C3 — Area Explorer County Explorer (Phase 3)

After first Deep Dive report:
  D2 — Repeatable pipeline; second/third market
  C4 — Area Explorer Zone Layer (Phase 4, from Deep Dive zone methodology)
  E  — Stoop Search if scoring is ready
  A  — Track 15–17 (Points layer) as Deep Dive work demands it
```

---

## Open Questions (to revisit)

- First Deep Dive market: use the cross-frame overlap and trajectory candidate lists from Intelligence Phases 5–6 to decide — don't pick before that analysis is done.
- Publishing cadence: start with one post and see how long it actually takes before committing to a schedule.
- Chatbot auth: open public or shared-link only?
- Area Explorer deployment: Streamlit Cloud is the default; revisit only if it becomes limiting.
- Stoop Search priority: dormant until there's a personal use case that pulls it forward.
