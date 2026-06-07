# Patterns in Place — Working Roadmap

*Last updated: 2026-06-06. Post-migration (all repos consolidated). This document supersedes the phased roadmap in `notes/patterns_in_place_notes/Roadmap.md` and should be the working reference going forward.*

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

## Current State Snapshot (2026-06-06)

### Foundations — what's real
The PLATFORM_COMPLETION_PLAN.md is the authoritative source. Summary:

**Done (Tracks 1–5 complete):**
- Staging: 19 scripts (ACS, BEA, BLS, HUD, BPS, IRS, Zillow, TIGER, TEA, QCEW, CHR, FHFA, OZ)
- Silver: 22+ scripts — IRS Migration, Zillow, HUD CHAS, BLS QCEW, CHR, FHFA HPI, FHFA Underserved, Opportunity Zones all complete as of 2026-06-03/04
- Gold: 14 tables — population, housing core, housing market (Zillow + FHFA), economy (GDP, income, labor, industry), migration, transport, health, affordability, policy designations, geo dim
- Data dictionary: shared field definitions resolved; all Track 1–5 sources documented
- Semantic layer: table_catalog, metric_catalog, join_catalog, geography_catalog, chart_rules, query_templates, theme_catalog, intelligence_catalog, question_catalog — all written (stubs for the last three)

**Remaining foundations work (Tracks 6–14, medium priority):**
- Track 6: EPA EJScreen + AQI (environment topic) — not started
- Track 7: FEMA NRI (climate risk) — not started
- Track 9: EPA Smart Location Database (walkability, transit built environment) — not started
- Track 10: IPEDS (postsecondary education) — not started
- Track 11: ACS broadband / disability / language expansions — not started
- Track 12: CBP + BFS (business formation) — not started
- Track 13: HMDA (mortgage lending) — not started
- Track 14: JEC Social Capital Index — not started

**Deferred until Deep Dive work begins (Tracks 15–17):**
- Track 15: NCES CCD (K–12 school points)
- Track 16: Points layer schema + national-once sources (HIFLD, IMLS, USDA farmers markets)
- Track 17: Per-market Points framework (Overture, OSM, Transitland, parcels, neighborhood boundaries)

**Decision on Track 6–14:** These are medium-priority additions that enrich the Livability and Opportunity frames. They do not block Area Explorer Phase 1 or the first Metro Deep Dive. Add them opportunistically — either as a batch foundations sprint before Deep Dive work, or one at a time as a specific data gap becomes felt in actual analysis.

### Products — what's real

| Product | State | Next step |
|---|---|---|
| Stoop Explore | Live (NYC, ~75%) | Incremental; revisit after Intelligence work |
| Stoop Search | Scaffolded (~20%) | Dormant until Intelligence scoring + Zillow ingest |
| Publisher — Content pipeline | Pipeline live; 1 post run | Run q002–q015; establish cadence |
| Publisher — Chatbot | NL→SQL built locally; not deployed | Deploy after Intelligence is working |
| Area Explorer | Bare MVP exists; not deployed | Primary near-term build focus |
| Metro Deep Dive | ROF prototype only; no generalized template | Destination product; build after Area Explorer discovery |
| exploration/ | Ad hoc notebooks; migrated | The analytical sandbox going forward |

---

## Roadmap

### Track A — Foundations (finish quickly, don't overthink)

The remaining Track 6–14 work is all well-defined. Execute it when bandwidth allows; it doesn't gate anything immediately.

**Priority order for Track 6–14 if batching:**
1. FEMA NRI + EPA AQI (Track 6–7) — climate/environment is a strong editorial angle; both feed `gold.environment_wide`
2. EPA Smart Location Database (Track 9) — walkability/transit built environment; Livability scoring input
3. ACS broadband/disability/language (Track 11) — extends existing ACS silver scripts; low effort
4. CBP + BFS (Track 12) — business formation is an Opportunity scoring input
5. IPEDS (Track 10) — postsecondary education for Character scoring
6. HMDA (Track 13) — mortgage lending equity; strong editorial angle for a later post
7. JEC Social Capital (Track 14) — lowest priority; interesting but not blocking

Points layer (Tracks 15–17): defer until the first Metro Deep Dive market is selected and Deep Dive work begins. Jacksonville already has POI data from the Stoop/rental_area_search pipeline; use that as the starting point.

**Themes/zones datamarts and benchmarks datamart:** Build these during Area Explorer work, not before. They are outputs of the discovery process.

**Writing angle for foundations work:** "Building a data platform for urban intelligence" — technical/methodological posts are good LinkedIn/personal brand content. Write about the pipeline architecture, the medallion design, the semantic layer approach when something interesting surfaces. Opportunistic, not scheduled.

---

### Track B — Publisher (content flywheel, ship chatbot)

**B1 — Content pipeline: run the queue and establish cadence**

The infrastructure is built. This is execution.

- Run q002–q015 through the publisher pipeline
- Publish 5 posts on Substack/X; establish bi-weekly cadence
- Expand question queue to 25+ as Area Explorer discovery surfaces new questions
- Document the Writing Bank (tone, citation style, post length rules)
- Posts are anonymous/brand-level on Substack/X; not tied to personal LinkedIn

**B2 — Chatbot: deploy once Intelligence has a working version**

The NL→SQL pipeline is fully built and tested. Two things needed before shipping:
1. Wire the existing theme_catalog, intelligence_catalog, question_catalog YAMLs into the query pipeline so the chatbot can handle theme-level queries at launch
2. Deploy: Streamlit Cloud + Groq + MotherDuck

Ship when Intelligence scoring is in a working (not perfect) state. The chatbot is a portfolio/demo piece — publicly accessible, shareable with friends and colleagues. Not commercial.

**Writing angle:** "How we built an NL-to-SQL chatbot on our own data platform" — strong LinkedIn post once deployed.

---

### Track C — Area Explorer + exploration/ (the analytical workspace)

This is the near-term primary build focus. Two parallel modes:

**C1 — exploration/ as the raw workspace**

`exploration/` is where ad hoc discovery happens: notebooks, quick analyses, experiments. The output of a good exploration session is one or more of:
- A validated finding → Insights Generator queue candidate
- A scoring calibration decision → updates to intelligence_catalog.yml
- A publishable pattern → Area Explorer dashboard or Deep Dive section

The TX school districts work and national analysis notebooks already live here. This is the model.

**C2 — Area Explorer as the lightweight product surface**

Area Explorer turns the best exploration outputs into deployable, shareable dashboards. Each dashboard is a clean, limited-scope Streamlit app: one question, well-executed. Not an all-in-one tool. Easy to build, easy to share.

Phase 1 — CBSA metric explorer (can start now):
- CBSA choropleth + metric picker
- Ranking table (top/bottom N)
- Benchmark comparison (one CBSA vs. national/regional)
- Scatter (two metrics, CBSA points)
- Deploy to Streamlit Cloud

Phase 2 — Intelligence Frames (after scoring models are in working state):
- Character, Livability, Opportunity frame views
- Requires: themes datamart, working intelligence_catalog entries

Phase 3 — Zone layer (after Deep Dive methodology is defined):
- Tract-level cluster zones
- Requires: zones datamart, clustering methodology defined from Deep Dive work

**Intelligence scoring — defined through this work, not before:**

The three frames (Character, Livability, Opportunity) get fleshed out by running the discovery analyses in `exploration/` and calibrating against what the data actually shows. The intelligence_catalog.yml stubs are the starting scaffolding; they get filled in as decisions are made. There is no formal "Intelligence milestone" that gates everything — it's a living document that evolves with the work.

---

### Track D — Metro Deep Dive (destination product)

The most intellectually interesting work and the long-term destination. Built on what Area Explorer discovery produces.

**What it is:** Long-form, rigorous, publishable market reports. Structure: Overview → 3 Intelligence Frames → Zone Analysis → (optional) Parcel layer. The output is a document — Substack, PDF, or interactive — not a real-time app.

**Starting point:** Jacksonville has the most existing work (ROF notebook sequence). Use it as reference material. The first actual published report starts fresh with the Intelligence Frame structure — not constrained to retail/commercial framing.

**First market selection:** TBD — see the exploration doc for criteria and candidate markets.

**ROF track:** Absorbed into Metro Deep Dive. Not a separate product. Jacksonville notebooks live in `metro-deep-dive/markets/jacksonville/` as reference.

**What needs to be true before the first report:**
- Area Explorer Phase 1 has been run and interesting patterns identified
- Intelligence scoring models have working definitions (not perfect — calibrated enough to produce meaningful frame views)
- A market has been selected and the data coverage confirmed
- Points layer not needed for Phase 1 — Places-only report is sufficient for the Overview + 3 Frames structure; add Parcels in Phase 2

**Publishing angle:** "A data-driven deep dive on [City]" — Substack/LinkedIn. The methodology post ("how we analyze a market") is also strong content.

---

### Track E — Stoop (incremental improvement, not a focus)

Stoop Explore is live and solid. No major investment until Intelligence scoring solidifies through Track C work.

**Incremental improvements that can happen anytime:**
- Formalize the Character score into intelligence_catalog.yml (small lift once the catalog patterns are established)
- Any UX improvements that surface from actual use

**Stoop Search:** Dormant until:
- Livability and Opportunity scoring are in working state (Track C)
- Zillow ingest is complete (already done at Silver level — Gold promotion complete)
- A decision is made to invest in the listing scoring UI

**Stoop v2 (second city):** After Deep Dive work establishes the per-market Points framework. Jacksonville is the natural second market given existing POI work.

---

## Sequencing Summary

```
Now (no blockers):
  B1 — Run publisher queue, establish Substack/X cadence
  C1 — Start exploration/ discovery work
  C2 — Build Area Explorer Phase 1 MVP

After Area Explorer Phase 1 is running:
  Intelligence scoring starts filling in (living doc)
  B2 — Wire catalogs into chatbot, deploy
  A  — Batch foundations Track 6–9 if data gaps are felt

After Intelligence has working definitions:
  D  — Select first Deep Dive market, run report
  C2 — Area Explorer Phase 2 (Intelligence Frames)
  E  — Stoop v2 scoping

After first Deep Dive:
  D  — Repeatable pipeline; second/third market
  C2 — Area Explorer Phase 3 (zones, from Deep Dive methodology)
  E  — Stoop Search if Zillow + scoring are ready
  A  — Track 15–17 (Points layer) as market Deep Dive begins
```

---

## Open Questions (to revisit)

- First Deep Dive market: what criteria matter? See `DEEP_DIVE_EXPLORATION.md`.
- Publishing cadence for Content pipeline: weekly or bi-weekly? Quality vs. volume tradeoff.
- Chatbot auth: who is the intended audience? Open public or shared link only?
- Area Explorer deployment: Streamlit Cloud for all apps, or something else?
- Stoop Search priority: is there a personal use case that would pull this forward?
