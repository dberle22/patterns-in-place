# Patterns in Place — Working Roadmap

*Last updated: 2026-06-30. This is the strategy memo — it describes what we're building and why, and tracks high-level state per product area. Tactical work lives in product-level roadmaps: `INTELLIGENCE_LAYER_ROADMAP.md` for the Intelligence Layer. Future roadmaps for Area Explorer, Publisher, and Metro Deep Dive follow the same pattern.*

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

## Current State Snapshot (2026-06-30)

### Foundations — what's real

**Data platform is solid.** All 14 source tracks are complete at Silver and Gold. Gold has 23 tables covering population, housing, economy, migration, transport, health, affordability, environment, food access, social fabric, social infrastructure, policy designations, and geo dimensions.

**The semantic layer is complete for the Intelligence Layer.** All four `intelligence_catalog.yml` frame entries are at `status: calibrated`. `metric_catalog.yml`, `theme_catalog.yml`, `question_catalog.yml`, and `table_catalog.yml` are all populated and wired. A final alignment pass (pruning low-variance metrics, ensuring catalog reflects empirically-tested KPI sets) is the only remaining semantic layer task — do it before Area Explorer Phase 2 and the Chatbot deploy, not now.

**Remaining foundations work:** Opportunistic. Do Gold promotion and semantic layer wiring for remaining sources only when a gap is felt during Intelligence or Deep Dive work.

**Deferred until Deep Dive work begins (Tracks 15–17):** Points layer (K–12 school points, national POI sources, per-market OSM/Overture/parcels). Jacksonville has existing POI data from the Stoop pipeline; use that as the starting point.

### Products — what's real

| Product | State | Next step |
|---|---|---|
| Stoop Explore | Live (NYC, ~75%) | Incremental; revisit after Intelligence work |
| Stoop Search | Scaffolded (~20%) | Dormant until Intelligence scoring is stable |
| Publisher — Content pipeline | Infrastructure built; zero posts published | Ready to start; see Track B |
| Publisher — Chatbot | NL→SQL built locally; not deployed | Wire catalogs + deploy; see Track B |
| Area Explorer — CBSA Internal | Fully built; not yet end-to-end verified | Verify + ship; see Track C |
| Area Explorer — CBSA Public, County, Zone | Not started | Follow Phase 1 ship |
| Intelligence Layer | Phases 0–7 complete, including tract and ZCTA zone marts | Verify Area Explorer and Deep Dive consumers against the final zone surfaces |
| Metro Deep Dive | No Research Tool yet; old ROF work is reference only | Build Research Tool after Phase 7 |
| exploration/ | Phase 7 zone methodology active | Primary analytical workspace right now |

---

## Roadmap

### Track A — Foundations (opportunistic, not a sprint)

The data platform is complete. Gold promotion and semantic layer wiring for any remaining sources happens when a specific gap is felt during Intelligence or Deep Dive work — not proactively.

One remaining task: a final semantic layer alignment pass before Area Explorer Phase 2 and the Chatbot deploy — verify `metric_catalog.yml` reflects the empirically-tested KPI sets, prune `theme_catalog.yml` of low-variance metrics. One-time tightening, not a sprint.

Points layer (Tracks 15–17): defer until the first Deep Dive market is selected.

---

### Track B — Publisher (ready to start)

Intelligence Phases 2–6 are complete. The gate has passed. Both B1 and B2 can begin now.

**B1 — Content pipeline:** Zero posts published, but the findings are ready. The L/O scatter, the Southern health deficit, and the social capital hypothesis are all calibrated and publishable now. Infrastructure and question backlog exist at `publisher/content/publisher_backlog.md`. Start with one post, measure how long it takes, then set cadence. Don't pre-commit to a schedule.

**B2 — Chatbot:** NL→SQL pipeline is built and working locally against local DuckDB. Two remaining tasks: (1) wire `theme_catalog.yml`, `intelligence_catalog.yml`, and `question_catalog.yml` into the query pipeline; (2) deploy to Streamlit Cloud + Groq. MotherDuck connection deferred until live apps require it. Portfolio/demo piece, not commercial. Ship it when Intelligence tab in Area Explorer is verified — both are wired to the same data.

---

### Track C — Area Explorer (Phase 1 ready to ship)

Area Explorer is the metric-first analytical surface for the platform. You pick a theme, subject, topic, or metric — the map, ranking table, and charts update around that selection. Three independent Streamlit apps, connected by a landing page. See `area-explorer/AREA_EXPLORER_ROADMAP.md` for the full spec.

**Two audiences, two CBSA apps:**
- `cbsa_internal` — dense analytical tool for Dan; includes Intelligence frame clusters, scores, GMM soft memberships, cosine-similarity peers, and the L/O four-quadrant Intelligence tab. Local deployment.
- `cbsa_public` — clean reader/client-facing tool; same metric-first structure but no frame scores or cluster labels until those are established in published articles. Deployed on Streamlit Cloud.

**Four phases in build order:**

**Phase 1 — CBSA Internal:** ✓ Built. All components implemented: catalog-driven metric picker, choropleth map, ranking table, profile panel with national + Census Division benchmarks, scatter / trend / distribution / Intelligence tabs. Intelligence tab wired to `mart_intelligence` tables (all four tables are materialized in local DuckDB). Needs one end-to-end verification run before calling it shipped.

**Phase 2 — CBSA Public + Landing Page:** Public-facing CBSA app with plain-language theme labels, benchmark framing, no cluster labels or frame scores. Deployed to Streamlit Cloud. Landing page linking all three apps. Requires: Phase 1 shipped + semantic layer alignment pass.

**Phase 3 — County Explorer:** Independent county-level app, state-filtered by default (national county choropleth is too slow). No Intelligence frames at county grain. Links back to CBSA app by state. Deployed to Streamlit Cloud.

**Phase 4 — Zone Layer:** Tract-level zone cluster view in the internal app for Deep Dive markets (Jacksonville, Richmond VA first). Follows Intelligence Phase 7 completion and requires `mart_intelligence.intelligence_zones` to be populated.

---

### Track D — Metro Deep Dive (destination product; follows Phase 7)

Two parallel deliverables: the published long-form report, and the internal Research Tool that supports writing it.

**D1 — Deep Dive Research Tool** (`metro-deep-dive/RESEARCH_TOOL_ROADMAP.md`): A place-first Streamlit app. Pick a metro → see its full profile across all three Intelligence frames, trajectory signals, zone map, peer comparisons, and the Phase 6 candidate list. Internal only. This is the analyst's workspace for building the report.

- Steps 1–3 (metro selector, frame tabs, peers tab): unblocked now — `mart_intelligence` tables exist, Phase 6 trajectory is complete, candidate list is ready. Can build in parallel with Phase 7.
- Steps 4–6 (trajectory tab, zone map, candidate list view): follow Phase 7 completion.

**D2 — Deep Dive Report:** Long-form, rigorous, publishable market analysis. Structure: Overview → 3 Intelligence Frames → Zone Analysis → (optional) Parcel layer. Output is a Substack post, PDF, or interactive document.

**Prerequisites before first report:**
- Intelligence Phase 7 complete (zone methodology; the last missing analytical layer)
- Research Tool Steps 1–3 working (needed to select market and develop narrative)
- Market selected from Phase 6 candidate list — Jacksonville and Richmond VA are the two Phase 7 test markets and most likely candidates
- Points layer not needed for first report — Places-only is sufficient for Overview + 3 Frames structure

The old ROF retail framing (`metro-deep-dive/markets/jacksonville/`) is reference material only. The first report starts fresh from the Intelligence Frame structure.

---

### Track E — Stoop (not a near-term focus)

Stoop Explore is live. Intelligence scoring is now stable; Stoop gets attention when there's a personal use case that pulls it forward.

**Stoop Search:** Dormant. Livability and Opportunity scoring are complete and available. The gate is now a product decision — is there a listing scoring UI worth building?

**Stoop v2:** After the first Deep Dive establishes the per-market Points framework. Jacksonville is the natural second market.

---

## Sequencing Summary

```
NOW (active work):
  Intelligence Layer — Phase 7 (Zone Methodology) complete
    Tract model and ZCTA rollup are both promoted into mart_intelligence

  In parallel (unblocked, can run after Phase 7):
  C1 — Verify + ship Area Explorer CBSA Internal (Phase 1)
         All components built; mart_intelligence tables materialized in local DuckDB
         One end-to-end verification run is the only remaining task
  B1 — Start Publisher content pipeline; first post from calibrated findings
         (L/O scatter, Southern health deficit, or social capital hypothesis)
  D1 — Begin Deep Dive Research Tool Steps 1–3 (metro selector, frame tabs,
         peers tab) — all data is available now

AFTER PHASE 7 COMPLETES (tract + ZCTA zone marts live):
  D1 — Complete Research Tool Steps 4–6 (zone map, trajectory tab, candidate list)
  C4 — Area Explorer Zone Layer (Phase 4) — zone view in internal app
  D2 — Select first Deep Dive market from Phase 6 candidate list;
         write first report (Jacksonville or Richmond VA)
  A  — Final semantic layer alignment pass before public deploy

AFTER AREA EXPLORER PHASE 1 SHIPPED + SEMANTIC LAYER PASS:
  C2 — Area Explorer CBSA Public + Landing Page (Phase 2) — Streamlit Cloud deploy
  B2 — Wire catalogs into chatbot; deploy to Streamlit Cloud + Groq

AFTER FIRST DEEP DIVE REPORT:
  C3 — Area Explorer County Explorer (Phase 3)
  D2 — Repeatable pipeline; second/third market
  E  — Stoop Search if there's a personal use case
  A  — Track 15–17 (Points layer) as Deep Dive work demands it
```

---

## Open Questions (to revisit)

- First Deep Dive market: Phase 6 candidate list is ready. Jacksonville and Richmond VA are both natural starting points. Use the now-materialized tract and ZCTA zone surfaces as the base layer, and run optional corridor detection only if a specific market needs the extra spatial segmentation.
- Publishing cadence: start with one post and measure how long it actually takes before committing to a schedule.
- Chatbot auth: open public or shared-link only?
- Area Explorer deployment: Streamlit Cloud is the default; revisit only if it becomes limiting.
- Stoop Search priority: dormant until there's a personal use case that pulls it forward.
