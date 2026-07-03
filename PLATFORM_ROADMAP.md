# Patterns in Place — Platform Roadmap

*Last updated: 2026-07-03. This is the milestone-level roadmap for all tracks. Strategy and rationale live in `ROADMAP.md`. Tactical task lists live in the track-level roadmaps linked from each section. This doc sits in between: meaningful milestones, track status, dependencies, and notes on how each piece fits.*

---

## Now / Next / Later

| Track | Status | Active milestone | Next unlock |
|---|---|---|---|
| A — Foundations: Places | Winding down | Remaining sources (HMDA, IPEDS, ACS expansions) | Unlocks full Intelligence inputs + Deep Dive |
| B — Foundations: Points | Starting | Points layer schema + national-once sources | Unlocks Stoop v2, Deep Dive POI layer |
| C — Foundations: Semantic Layer | Deployed, needs testing | Chatbot QA and tuning | Unlocks Chatbot prod deploy, Headless BI |
| D — Intelligence Layer | Complete | Zone methodology testing | Unlocks Deep Dive report, Area Explorer Zone Layer |
| E — Area Explorer | Phase 1 built | End-to-end verification run | Unlocks CBSA Public + Chatbot wire-up |
| F — Metro Deep Dive | Research Tool built | Zone methodology testing + POI pipes | Unlocks first published Deep Dive report |
| G — Publisher / Content | Unstarted | Write first post | Unlocks publishing cadence |
| H — Chatbot | Local, needs deploy | Prod deploy to Streamlit Cloud + Groq | Unlocks public-facing Q&A product |
| I — Stoop | Explore v1 live | V2 planning | Unlocks Search when POI layer is ready |
| J — Publishing & Distribution | Not started | Write first post | Unlocks every outreach lane; makes platform visible |

---

## Track A — Foundations: Places

**Status:** Winding down — 12 of ~14+ source tracks complete. A few remaining.

*The Places layer is the canonical warehouse of aggregate metro, county, tract, and ZCTA facts — the Gold tables that feed Intelligence scoring, Area Explorer, the Chatbot, and the Deep Dive. Getting Places solid was the prerequisite for everything downstream.*

### Done

- [2026-05] ETL Migration: monorepo unified; `patterns_in_place.duckdb` established; staging/silver/gold pattern locked
- [2026-06-02] Track 2: Shared field definitions resolved; data dictionary governance finalized
- [2026-06-03] Track 1: IRS Migration, Zillow, HUD CHAS, BLS QCEW — all promoted to Silver + Gold
- [2026-06-04] Track 3: FHFA HPI — staging, silver, gold (`housing_market_wide`)
- [2026-06-04] Track 4: CHR (County Health Rankings) — staging, silver, gold (`health_wide`)
- [2026-06-04] Track 5: Opportunity Zones + FHFA Underserved — `dim_policy_designations` live
- [2026-06-08] Track 6: EPA AQI + EJScreen — `environment_wide` with AQI and tract EJScreen columns
- [2026-06-08] Track 7: FEMA NRI — environment table extended with risk scores; tract FEMA promoted
- [2026-06-09] Track 9: EPA Smart Location Database — `transport_built_form_sld` baseline mart
- [2026-06-09] Track 12: CBP + BFS — establishment density and business formation in `economics_industry_wide`
- [2026-06-09] Track 14: Social Capital Atlas (Opportunity Insights) — `social_fabric_wide` live
- [2026-06-09] Track 11: ACS Broadband, Disability, Language — Silver + `social_infra_wide` Gold promoted
- [2026-06-25] All 14 primary source tracks at Silver and Gold; 23 Gold tables materialized

### Ahead

- [ ] **Track 10: IPEDS** — postsecondary institution density; `education_k12_wide` or `population_demographics` extension | *No hard dependency; fill when useful*
- [ ] **Track 11.6–11.8**: ACS broadband/disability/language Gold wiring and pipeline manifest updates | *Partially done; close out*
- [ ] **Track 13: HMDA** — mortgage lending equity metrics at tract/county/CBSA; `housing_lending_wide` | *Unblocked; medium effort*
- [ ] **Track 9.11**: SLD tract normalization follow-on — governed tract relationship for EPA SLD | *Low priority; do when tract-level Deep Dive work pulls it*
- [ ] **Final semantic layer alignment pass** — prune low-variance metrics from `theme_catalog.yml`; verify `metric_catalog.yml` reflects calibrated KPI sets | *Required before Area Explorer public deploy and Chatbot wire-up*

### Notes

The data platform is functionally complete for Intelligence scoring and the first Deep Dive report. HMDA and IPEDS are genuinely useful but not blocking. The remaining open work (11.6–11.8, 9.11) is housekeeping — close it out opportunistically, not as a sprint.

Data quality has not been integrated. There is no automated DQ pipeline. This is a future investment, not a current gap — the manual audit passes embedded in each Silver script are sufficient for now.

The SLD baseline is a single-vintage 2021 layer, which is intentional — it behaves like a context layer, not a recurring panel. Keep it in `transport_built_form_sld` separately rather than mixing into the time-series ACS mart.

**Unlocks when done:** Full Intelligence input coverage (already unlocked at current state). HMDA unlocks housing equity Deep Dive angles. IPEDS unlocks college-town character analysis.

---

## Track B — Foundations: Points

**Status:** Not started — schema design needed before any source ingestion.

*The Points layer is the spatial layer: individual place records (schools, hospitals, libraries, parks, transit stops, POIs) at lat/lon precision. It is the foundation for neighborhood-level Deep Dive analysis and for Stoop v2. The Stoop POI pipeline is the direct template — this is a promotion and generalization job, not greenfield design.*

### Done

- [2026-06] Stoop POI architecture validated in production (SHA256 stable IDs, `dim_public_poi`, category taxonomy, OSM Overpass adapter) — serves as the direct template

### Ahead

- [ ] **16.1 Schema + taxonomy promotion** — promote `poi_categories.yaml` from Stoop to `foundations/config/`; write `gold.dim_point_of_interest` + `point_source_mapping` schema; document stable ID strategy | *Prerequisite for all source ingestion*
- [ ] **16.2 National-once sources** — NCES CCD (K–12), HIFLD (hospitals), IMLS (libraries), USDA Farmers Markets; all have native lat/lon, ~2–3 hours each following R staging patterns | *Depends on 16.1*
- [ ] **16.3 Geo-aggregations stub** — `gold.fct_geo_aggregations`; POI counts and density by category per tract/county; adapted from `stoop/sql/gold/fct_nta_features.sql` | *Depends on 16.2*
- [ ] **17.x Per-market OSM + Overture framework** — parameterize Stoop OSM adapter; add Overture GeoParquet query pattern; per-market onboarding checklist | *Run immediately before first Deep Dive market is selected; do not pre-build*

### Notes

Track B is a genuine next investment area. The Stoop OSM adapter, category taxonomy, and SHA256 ID scheme are all proven and directly reusable — this is not a design problem, it's a translation-and-promotion problem.

The per-market OSM work (Track 17) should wait until a Deep Dive market is committed. Building it speculatively is waste. Jacksonville has existing POI data from the Stoop pipeline that can serve as the starting point.

**Unlocks when done:** Deep Dive POI layer for Zone Analysis section. Stoop v2 expansion beyond NYC. `fct_geo_aggregations` unlocks POI-density signal for Intelligence scoring and Area Explorer annotations.

---

## Track C — Foundations: Semantic Layer

**Status:** Deployed and complete for Intelligence Layer consumers. Needs end-to-end testing.

*The semantic layer (`metric_catalog.yml`, `theme_catalog.yml`, `question_catalog.yml`, `table_catalog.yml`, `intelligence_catalog.yml`) is the translation layer between the Gold tables and any consumer product — the Chatbot, Area Explorer, the Publisher, the Deep Dive Research Tool. It's what makes NL → SQL work and what drives the metric picker in Area Explorer.*

### Done

- [2026-06] `metric_catalog.yml`, `theme_catalog.yml`, `question_catalog.yml`, `table_catalog.yml` — all populated and wired
- [2026-06] `intelligence_catalog.yml` — all four frame entries at `status: calibrated`; zone methodology documented
- [2026-06] Semantic layer wired into Chatbot query pipeline (`chatbot/query/catalogs.py`)

### Ahead

- [ ] **End-to-end semantic layer test** — run representative questions through Chatbot query pipeline; confirm `theme_catalog.yml` → topic → metric → SQL path produces correct output | *Unblocked*
- [ ] **Final alignment pass** — prune low-variance metrics from `theme_catalog.yml`; ensure catalog reflects empirically-tested KPI sets from Intelligence calibration | *Required before Area Explorer Phase 2 public deploy*
- [ ] **Headless BI use case** — wire semantic layer to a BI tool (Superset, Evidence, or similar) as a proof of concept | *Exploratory; not on critical path*
- [ ] **Benchmarking article** — compare our semantic layer approach to peers; interesting technical content for Track 1 publishing | *Good article angle; run after first publish cycle*

### Notes

The semantic layer is the right abstraction and the foundation is solid. The main remaining risk is untested paths — we haven't stress-tested the full NL → intent → SQL → chart pipeline against the full catalog breadth. The Chatbot QA app is ready for exactly this.

The benchmarking angle (semantic layer vs. peers, different modeling approaches) is a genuinely interesting technical article. Stack it after publishing momentum is established.

**Unlocks when done:** Chatbot prod deploy. Area Explorer public deploy. Headless BI prototype. Technical article on semantic layer design.

---

## Track D — Intelligence Layer

**Status:** Complete — all 8 phases done; marts materialized in local DuckDB.

*The Intelligence Layer is the scoring and clustering stack: Character, Livability, and Opportunity frame models at CBSA grain, cross-frame analysis, trajectory analysis, and zone methodology at tract/ZCTA grain. All outputs are promoted to `mart_intelligence` in DuckDB.*

### Done

- [2026-06-17] Phase 0–1: Metric mapping and variable selection complete
- [2026-06-18] Phase 3: Livability Frame Model — `k=6` clustering, scoring, similarity, `livability_scores.parquet`
- [2026-06-18] Phase 4: Opportunity Frame Model — `k=6` clustering, L/O scatter, OZ overlay, `opportunity_scores.parquet`
- [2026-06-18] Phase 5: Cross-Frame Combined Model — `35`-KPI reduced set, `k=6`, overlap flags, candidate list
- [2026-06] Phase 2: Character Frame Model — `17`-KPI set, `k=7`, literature anchors, `character_scores.parquet`
- [2026-06] Phase 6: Trajectory Analysis — momentum + outlier passes, 5 pattern filters, ranked `phase6_candidate_list.csv`
- [2026-06] Phase 7: Zone Methodology — national tract model (`k=7`, 7 named zone types), ZCTA rollup with HUD weights; both promoted to `mart_intelligence`
- [2026-06-30] Phase 8: Catalog Finalization + DataMart Promotion — all 6 `mart_intelligence` tables materialized; `intelligence_calibration_notes.md` complete

### Ahead

- [ ] **Zone methodology testing** — verify zone assignments against Jacksonville and Richmond VA test markets; confirm zone labels are interpretable and defensible before publishing | *Required before Deep Dive Zone Map section*
- [ ] **MotherDuck promotion** — confirm `mart_intelligence` tables are queryable from MotherDuck and accessible to Area Explorer public deploy and Chatbot | *Required before any cloud-deployed consumer product*
- [ ] **Area Explorer + Chatbot verification** — confirm all downstream consumers read correct columns from `mart_intelligence.*` semantic aliases | *Required before Area Explorer Phase 2 and Chatbot wire-up*

### Notes

The Intelligence Layer is the analytical core of the platform and is complete at CBSA and tract grain. The four CBSA-grain frame tables plus the two zone tables are the primary data surfaces for Area Explorer, the Research Tool, and the Chatbot.

The zone methodology is architecturally complete but not yet empirically tested at the market level. The `k=7` labels need to hold up against what you see on the ground in Jacksonville and Richmond VA before they're defensible in a published piece.

The Phase 6 candidate list is the market selection surface for the first Deep Dive. Jacksonville and Richmond VA are the Phase 7 test markets and likely first subjects, but the list may surface something more compelling.

**Unlocks when done:** Area Explorer Intelligence Tab. Deep Dive Zone Map section. Chatbot Intelligence frame queries. Articles 1–9 (the finding content from each phase).

---

## Track E — Area Explorer

**Status:** Phase 1 built; needs one end-to-end verification run before calling it shipped.

*Area Explorer is the metric-first analytical surface: pick a metric → see how all places rank. Three Streamlit apps (CBSA Internal, CBSA Public, County) plus a landing page. The internal app is the analyst's tool; the public app is reader/client-facing.*

### Done

- [2026-06-19] Product spec written: `area-explorer/AREA_EXPLORER_ROADMAP.md`
- [2026-06] Shared foundation built: `shared/db.py`, `shared/catalog.py`, `shared/geo_utils.py`, `shared/benchmark.py`
- [2026-06] CBSA Internal app: catalog-driven metric picker, choropleth map, ranking table, profile panel, Scatter / Trend / Distribution / Intelligence tabs — all implemented
- [2026-06] `mart_intelligence` tables wired into Intelligence Tab (all four tables materialized in local DuckDB)
- [2026-06] Initial exploration app (`data_explorer.py`) — serves as migration-state reference

### Ahead

- [ ] **Phase 1: End-to-end verification** — run the internal CBSA app against local DuckDB; confirm all four tabs work, Intelligence tab shows correct cluster labels and peers, benchmarks compute correctly | *Unblocked; one session*
- [ ] **Phase 2: CBSA Public app** — feature-gated version (no cluster labels, no Intelligence tab, public theme labels); deploy to Streamlit Cloud; landing page | *Depends on: Phase 1 shipped + semantic layer alignment pass + MotherDuck promotion*
- [ ] **Phase 2: MotherDuck connection** — test public app reads from MotherDuck, not local path; set `MOTHERDUCK_CONNECTION` secret in Streamlit Cloud | *Part of Phase 2*
- [ ] **Phase 3: County Explorer** — state-filtered by default; state percentile benchmarks; links from CBSA app | *Depends on: Phase 1 shipped*
- [ ] **Phase 4: Zone Layer** — tract-level zone cluster view in internal app for Jacksonville + Richmond VA; feeds from `mart_intelligence.intelligence_zones` | *Depends on: Intelligence Zone methodology testing*
- [ ] **Feature expansion cadence** — add features as articles are written; don't pre-build | *Ongoing; driven by publishing*

### Notes

The internal app is the primary analytical tool for Deep Dive market development and Intelligence calibration verification. Ship it first; the public app follows.

The public app should not surface cluster labels or Intelligence frame scores until the methodology has been published (Article 2: "A New Map of American Metros"). The feature-gate config in `apps/cbsa_public/config.py` handles this.

Area Explorer is intentionally not the place-first product. If someone starts with a metro in mind, they should use the Deep Dive Research Tool. Area Explorer answers "how do all places rank on X," not "tell me everything about Jacksonville."

**Unlocks when done:** Phase 1 → Chatbot wire-up, Publisher content verification. Phase 2 → Public-facing portfolio piece, reader engagement surface. Phase 4 → Deep Dive Zone Map companion.

---

## Track F — Metro Deep Dive

**Status:** Research Tool built; zone methodology + POI pipes needed before first report.

*The Deep Dive is the destination product: long-form, rigorous, publishable market analysis reports. The Research Tool is the internal Streamlit app that supports writing them — place-first, full profile across all three Intelligence frames, trajectory signals, zone map, peer comparisons. The report is what you write when the tool surfaces something worth writing about.*

### Done

- [2026-06-30] Research Tool spec: `metro-deep-dive/RESEARCH_TOOL_ROADMAP.md`
- [2026-07] Research Tool built: metro selector, Overview tab, Livability / Opportunity / Character frame tabs, Trajectory tab, Zone Map tab (placeholder), Peers tab, Candidate List tab — all implemented
- [2026-07] Deep Dive article template: `templates/metro_deep_dive_template_guidance.md`
- [2026-06] Phase 6 candidate list available: `phase6_candidate_list.csv` — ranked market selection surface
- [2026-06] `mart_intelligence` tables available for all Research Tool frame and trajectory queries

### Ahead

- [ ] **Zone methodology testing** — validate `k=7` zone labels against Jacksonville and Richmond VA; update zone names if on-the-ground patterns don't match | *Required before Zone Map tab is functional; shared dependency with Track D*
- [ ] **POI pipes for Deep Dive market** — run Track B per-market OSM + Overture framework for selected market; produce `dim_point_of_interest` rows and `fct_geo_aggregations` for the market | *Depends on: Track B 16.1–16.3 + market selection; required for POI overlay in Zone Map*
- [ ] **Market selection** — choose first Deep Dive market from `phase6_candidate_list.csv`; Jacksonville and Richmond VA are Phase 7 test markets; candidate list may surface something more compelling | *Depends on: Zone methodology testing*
- [ ] **First Deep Dive report** — Overview → 3 Intelligence Frames → Zone Analysis → (optional) Parcel layer; output is Substack post, PDF, or interactive doc | *Depends on: market selection + zone testing + POI pipes for selected market*
- [ ] **Second market + repeatable pipeline** — after first report, formalize what was reusable | *Follows first report*

### Notes

The Research Tool is the most sophisticated internal product in the platform. It's built to support writing, not to be a product in itself — the deliverable is the report.

Zone methodology needs to be tested before the Zone Map tab is useful. Right now the tab exists but the zone assignments haven't been verified on the ground for any specific market. This is the critical remaining analytical gate before the first report.

POI pipes are needed for the Zone Analysis section only — the Overview and 3 Intelligence Frames sections can be written without them. Consider whether to write the first report without the full POI layer and add it in revision, or wait for POI to be ready.

The Deep Dive template (`metro_deep_dive_template_guidance.md`) defines the structure. Use it, but treat it as a starting point — the narrative should lead, not the template.

**Unlocks when done:** First Deep Dive report. Publisher content for Track 1 and Track 2 simultaneously. Market selection feedback loop for future reports.

---

## Track G — Publisher / Content Pipeline

**Status:** Infrastructure built; zero posts published. Ready to start.

*The Publisher is the content flywheel. Two independent tracks: technical writing (how the platform was built) and data analysis writing (what it finds). Both generate credibility and audience. The most powerful posts sit at the intersection.*

### Done

- [2026-06] Publisher migration complete: `publisher/` in monorepo; chatbot backend, batch runner, frontend, content workspace all migrated
- [2026-06] Content workspace established: `publisher/content/` with topic-driven manual workflow
- [2026-06-30] Publisher backlog written: `publisher/content/publisher_backlog.md` — question bank, workflow, two-track strategy
- [2026-06] Visual Library in place: `foundations/visual_library/` — R render scripts for all chart types
- [2026-06] Question bank in semantic layer: `question_catalog.yml`
- [2026-06] `question_queue.yaml` populated with first questions; `q001` reference artifact committed

### Ahead

- [ ] **Write first post** — start with one calibrated finding: L/O scatter, Southern health deficit, or social capital hypothesis; follow the 7-step workflow in `publisher_backlog.md` | *Unblocked; highest priority in this track*
- [ ] **Measure and set cadence** — after first post, note how long it actually took; set cadence from that, not from aspiration | *Follows first post*
- [ ] **Content pipeline skill** — make the 7-step workflow replicable as a Claude skill so future posts follow the same path reliably | *Medium effort; do after first post proves the workflow*
- [ ] **Technical Track 1 posts** — DuckDB architecture, DWH design, semantic layer approach, Intelligence scoring methodology; audience is data engineering community | *Ongoing; write as platform work surfaces good angles*
- [ ] **Analysis Track 2 posts** — metro pattern findings from Intelligence phases; audience is urban policy / housing / economic geography community | *Ongoing; triggered by findings, not schedule*
- [ ] **Chatbot benchmarking article** — compare semantic layer approaches; good technical content; run after Chatbot is deployed | *Depends on: Track H Chatbot prod deploy*

### Notes

Zero posts published is the single biggest gap in the platform right now. The findings are calibrated and publishable. The infrastructure exists. The only thing missing is starting.

The 7-step workflow (question → visual → SQL/R → execute → write → publish → notes) is the right frame. The `publisher/content/vacancy_rates/` folder is a worked example to follow.

The content pipeline skill (making this replicable as a Claude Code skill) is worth building after the first post, not before. Prove the workflow works manually before automating it.

Both publishing tracks can run in parallel. Technical posts go to LinkedIn and the data engineering community; analysis posts go to Substack and urban policy communities. The crossover piece (surprising finding + infrastructure that made it visible) is the most powerful single post type.

**Unlocks when done:** First post → publishing momentum + credibility signal. Regular cadence → audience growth. Chatbot article → technical credibility. Deep Dive report → flagship content piece.

---

## Track H — Chatbot

**Status:** Local and functional; needs prod deploy.

*The Chatbot is the NL-to-SQL product: ask a question in plain language, get a chart and answer back. It's a portfolio piece and a demo of the semantic layer. Built locally, tested against local DuckDB. Needs deployment and tuning.*

### Done

- [2026-06] NL → SQL pipeline built and working locally against local DuckDB: intent parser, LLM, SQL generator, validator, executor, chart renderer, response assembler
- [2026-06] Migration complete: `publisher/chatbot/` — all path fixes applied (`FOUNDATIONS_PATH` env var pattern)
- [2026-06] Semantic layer wired into query pipeline: `table_catalog.yml`, `metric_catalog.yml`, `join_catalog.yml`, `geography_catalog.yml`, `chart_rules.yml`, `query_templates.yml`
- [2026-06] QA app ready for local use: `publisher/frontend/` — artifact review and prompt tuning interface
- [2026-06] Phase 4.1–4.2 verification gates passed locally

### Ahead

- [ ] **Wire `theme_catalog.yml`, `intelligence_catalog.yml`, `question_catalog.yml`** into query pipeline — these are planned additions not yet loaded in `chatbot/query/catalogs.py` | *Unblocked; required before Intelligence frame queries work*
- [ ] **Prod deploy to Streamlit Cloud + Groq** — set `MOTHERDUCK_CONNECTION` and Groq API key as secrets; confirm public app reads from MotherDuck | *Depends on: MotherDuck promotion (Track D); intelligence catalog wiring*
- [ ] **Auth decision** — open public or shared-link only? | *Required before public deploy*
- [ ] **Tuning pass** — run representative questions through QA app; identify failure modes; tune prompts | *Ongoing after deploy*
- [ ] **Chart render in Streamlit UI** — Phase 4.3 frontend QA gate not yet fully verified (charts may not render in browser, only headlessly) | *Required before calling frontend functional*

### Notes

The Chatbot is primarily a portfolio/demo piece, not a commercial product. The goal is to show what a well-structured semantic layer enables — the questions it can answer are more impressive than the UI.

The intelligence catalog wiring is the most important near-term task. Questions like "which metros have the best Livability score in the South Atlantic?" require `intelligence_catalog.yml` to be loaded alongside the table/metric catalogs.

The Groq + Streamlit Cloud path is the right deployment choice: fast inference, free tier for a demo product, no infrastructure to maintain.

**Unlocks when done:** Public-facing Chatbot demo. Intelligence frame NL queries. Chatbot benchmarking article (good technical content). Evidence that the semantic layer works end-to-end.

---

## Track I — Stoop

**Status:** Explore v1 live; Search requires POI layer and listing parser.

*Stoop is the live consumer product: neighborhood search and exploration for NYC. Explore v1 is live. Search is scaffolded but dormant until the POI layer is updated and a listing parser exists. V2 planning can begin now.*

### Done

- [2026-06-05] Stoop migration complete: `stoop/` in monorepo; app, SQL, config, source library all migrated
- [2026-06-05] Stoop Explore v1 verification passed: choropleth map, curated + public POI layers, NTA character profile panel, category filters all functional
- [2026-06] Intelligence frames (Livability + Opportunity scores) at CBSA/NTA grain — complete and available from `mart_intelligence`

### Ahead

- [ ] **V2 planning** — what does Stoop Explore v2 look like after the Intelligence frames are stable? NTA-level Intelligence scoring, updated POI layer, expanded markets | *Can begin now; not a near-term sprint*
- [ ] **Update POI layer** — refresh NYC POI data from updated OSM/Overture sources; this will be easier once Track B national-once sources are done and the per-market framework (Track 17) exists | *Depends on: Track B 16.1–16.3*
- [ ] **Listing parser** — Stoop Search requires a parser for home listing data (Zillow/StreetEasy); this is a product decision, not just a data decision | *Depends on: POI layer update + product decision on Search priority*
- [ ] **Stoop Search** — full NTA scoring + listing enrichment + listing score UI | *Depends on: POI layer + listing parser; dormant until personal use case pulls it forward*
- [ ] **Second market** — Jacksonville is the natural second Stoop market after the Deep Dive establishes the per-market Points framework | *Depends on: first Deep Dive report + Track 17 per-market framework*

### Notes

Stoop Explore v1 is live and the core product works. It's not a near-term investment area — the Intelligence frames are stable, the POI layer needs a refresh, but nothing is broken.

Stoop Search is dormant by design. The gate is a product decision: is there a listing scoring UI worth building given the effort to get listing data? The listing parser is the harder technical problem. Revisit when there's a personal use case that makes it worth the investment.

The Intelligence frames (Livability and Opportunity scores) are complete and available. Wiring them into Stoop's NTA scoring layer is an incremental step once V2 planning begins — the `mart_intelligence` tables are the data source.

**Unlocks when done:** V2 planning → roadmap for expanded Stoop. POI update + listing parser → Stoop Search. Second market → product generalization beyond NYC.

---

## Track J — Publishing, Distribution & Public Presence

**Status:** Not started — infrastructure exists, nothing is live or announced.

*This is the track that makes everything else matter. The platform produces findings, tools, and a technical story. This track gets them in front of people. It covers three things in sequence: writing and publishing consistently, building a public web presence, and distributing to the right audiences. Nothing in the platform is visible until this track moves.*

### Done

- [2026-06] Two-track content strategy defined: technical writing (how it's built) + data analysis writing (what it finds)
- [2026-06] Publisher workflow documented: 7-step process, post output format, backlog written
- [2026-06] Backlog written: Track 1 and Track 2 post ideas catalogued in `publisher/content/publisher_backlog.md`
- [2026-06] Outreach strategy mapped: `OUTREACH_TRACKER.md` — five lanes, sequenced action plan, per-target lead artifacts
- [2026-06] Tech landscape mapped: `TECH_LANDSCAPE_MAP.md` — communities, contributable projects, positioning per category

### Ahead

**Writing — start here, everything else follows:**

- [ ] **First post published** — one calibrated finding from the backlog: L/O scatter ("which metros have high livability but low opportunity"), Southern health deficit, or social capital hypothesis. Follow the 7-step workflow. Measure how long it takes. | *Unblocked right now; the only gate is starting*
- [ ] **Second and third posts** — one Track 1 (technical) and one Track 2 (analysis) before setting a cadence; see which audience responds and how long each actually takes | *Follows first post*
- [ ] **Set and commit to a cadence** — pick a realistic posting frequency based on measured post time, not aspiration. One post every two weeks is defensible; one per week is optimistic. Don't commit until you have two data points. | *Follows second post*
- [ ] **Content pipeline skill** — encode the 7-step workflow as a Claude skill so future posts start from a consistent scaffold | *After first post proves the workflow; medium effort*
- [ ] **Stoop Explore launch post (S1)** — announce Stoop to BetaNYC, NYC Open Data community, r/nyc, Streamlit gallery; app is live but unannoounced | *Unblocked; one post + a few emails*
- [ ] **HIB-1: DuckDB pipeline post** — the "how I built a 23-table Gold layer on DuckDB as a solo analyst" post; writable now; unlocks Lane 2 outreach (MotherDuck, DuckDB Discord, Kyle Walker, dbt Slack) | *Unblocked; highest-ROI technical post*
- [ ] **HIB-2: Constrained NL-to-SQL post** — the Chatbot architecture post; "why I constrained the LLM to templates instead of free generation"; unlocks Show HN and Chatbot benchmarking | *Depends on: Track H Chatbot prod deploy*

**Public presence — once writing cadence is established:**

- [ ] **Substack publication** — set up public Substack for Track 2 analysis posts; clean name, short description, one-line framing that isn't "I built a platform" | *Before or alongside first Track 2 post*
- [ ] **X/Bluesky account** — build the urban-econ engagement list; reply with charts before posting original content; daily engagement from the PiP account | *Start now; no dependency*
- [ ] **Public website** — a simple landing page for Patterns in Place: what it is, who it's for, links to the Substack, Stoop, Area Explorer (when public), Chatbot (when deployed); does not need to be elaborate | *After 3+ posts are live so there's something to point to*
- [ ] **LinkedIn presence** — crosspost technical posts; LinkedIn is where the data engineering audience lives and where grad school contacts will look | *Alongside first HIB post*

**Distribution — triggered by shipped artifacts:**

- [ ] **Lane 2 activation (data engineering)** — join MotherDuck Slack, DuckDB Discord, Locally Optimistic, dbt Slack; post HIB-1 when written; pitch MotherDuck devrel at migration | *Join communities now; pitch at HIB-1*
- [ ] **Lane 3 activation (R/viz)** — create Bluesky account; post charts with ggplot2 process notes; tag Kyle Walker when HIB-1 ships | *Bluesky now; pitch at HIB-1*
- [ ] **Lane 1 activation (urban econ)** — email Joe Cortright and Jed Kolko at A1 (L/O scatter); these require the strongest artifact, not warmup posts | *After A1 is published*
- [ ] **Lane 4 activation (NYC/Stoop)** — BetaNYC event before launch; NYC Open Data tag; THE CITY email at S1 | *At S1*
- [ ] **r/dataisbeautiful** — one chart post from the strongest single-image finding (four-quadrant scatter); weekday morning, [OC] format | *After first Track 2 post*
- [ ] **Data Is Plural submission** — release the calibrated frame scores or AI exposure index as downloadable data; submit to Jeremy Singer-Vine | *When a dataset is ready to release publicly*

**Productization — later, after audience exists:**

- [ ] **Area Explorer public deploy (CBSA Public)** — Streamlit Cloud; shareable URL for embedding; the metric-first public surface | *Depends on: Track E Phase 2 + MotherDuck promotion*
- [ ] **Chatbot public deploy** — Streamlit Cloud + Groq; shared-link or open; the NL-to-SQL demo | *Depends on: Track H prod deploy*
- [ ] **Frame scores public data release** — publish the calibrated Livability/Opportunity/Character scores for all 401 CBSAs as a downloadable CSV; enables Data Is Plural submission and makes findings verifiable | *After methodology is published (post A1 + M1)*
- [ ] **posit::conf talk proposal** — "R + DuckDB + Quarto: a solo analyst's production data stack"; CFP typically opens January; a talk is the highest-credibility single artifact for the technical community | *CFP watch Jan 2027*

### Notes

The platform is analytically ~80% complete and publicly ~0% visible. This track is the one that closes that gap. Every other track in the roadmap produces something that feeds here — the findings, the tools, the technical decisions. None of it compounds until something is published.

The order matters: writing first, then presence, then distribution, then productization. Distribution without a body of work to point to doesn't stick. Productization before writing means building for an audience that doesn't exist yet.

The two-track content strategy (technical + analysis) is right because they serve different communities that don't overlap much. Write both, but don't force the crossover too early — it emerges naturally once each track has a few posts.

The outreach tracker has specific targets and sequenced moves for each lane. The key principle it establishes: every outreach contact leads with a shipped artifact, never with "I built a platform." The artifact does the work.

The website doesn't need to be built before writing starts. Three or four published posts are more credible than a polished landing page with nothing behind it.

**Unlocks when done:** First post → publishing cadence. HIB-1 → Lane 2 distribution. S1 → Lane 4 distribution. A1 → Lane 1 outreach (Cortright, Kolko). Public website + deployed products → complete public presence. Frame scores release → academic and data journalism credibility.

---

## Cross-Track Dependencies

```
Track A (Places)  ─────────────────────────────────────────────────────────┐
  Places Silver/Gold complete                                                │
         │                                                                   │
         ▼                                                                   │
Track D (Intelligence Layer) ──── complete ────────────────────────────┐   │
  mart_intelligence tables live                                         │   │
         │                                                              │   │
         ├──── Track E Phase 1 (Area Explorer Internal) ──────────────┐│   │
         │       Intelligence Tab, frame scores                        ││   │
         │                                                             ││   │
         ├──── Track F (Research Tool) ──── complete                  ││   │
         │       Frame tabs, Trajectory tab, Candidate List            ││   │
         │                                                             ││   │
         └──── Zone methodology testing ─────────────────────────┐    ││   │
                                                                  │    ││   │
Track B (Points) ──── 16.1–16.3 national-once sources ──────────┤    ││   │
         │                                                        │    ││   │
         └──── Track 17 per-market OSM/Overture ─────────────────┤    ││   │
                                                                  │    ││   │
                                             ┌────────────────────┘    ││   │
                                             ▼                         ││   │
                              First Deep Dive report ◄─────────────────┘│   │
                              (Zone Map + POI overlay)                   │   │
                                             │                           │   │
                                             ▼                           │   │
                              Second Deep Dive + pipeline                │   │
                                                                         │   │
Track C (Semantic Layer) ──── alignment pass ────────────────────────────┘   │
         │                                                                    │
         ├──── Track E Phase 2 (CBSA Public) ◄───── MotherDuck promotion ◄──┘
         │                                           (Track D)
         └──── Track H (Chatbot prod deploy)

Track J (Publishing & Distribution)
  │
  ├── First post (unblocked) ──────────────────────────── publishing cadence
  │
  ├── HIB-1 (DuckDB pipeline post) ──── Lane 2 activation (MotherDuck, DuckDB Discord, dbt Slack)
  │
  ├── S1 (Stoop launch post) ──────── Lane 4 activation (BetaNYC, NYC Open Data, r/nyc)
  │
  ├── A1 (L/O scatter post) ──────── Lane 1 activation (Cortright, Kolko)
  │
  ├── HIB-2 ◄── Track H (Chatbot deploy) ──── Show HN + benchmarking article
  │
  ├── Area Explorer public ◄── Track E Phase 2 ──── public metric surface
  │
  └── Frame scores release ──── Data Is Plural + academic credibility
```

---

## Appendix: Naming Conventions

For reference when reading track-level roadmap files:

| Term | Meaning |
|---|---|
| `mart_intelligence.*` | Intelligence DataMart in DuckDB — scored outputs, zone assignments |
| `gold.*` | Source-of-record fact tables; Places layer |
| `silver.*` | Standardized intermediate layer; per-source grain |
| `staging.*` | Source-faithful raw layer; never edited downstream |
| CBSA | Core Based Statistical Area — metro-level geography (401 CBSAs ≥ 100K population) |
| NTA | Neighborhood Tabulation Area — NYC-specific sub-borough unit (Stoop only) |
| Zone | Tract-level cluster label from Intelligence Phase 7 (`k=7` zone types) |
| Frame | One of the three Intelligence scoring models: Character, Livability, Opportunity |
| Phase 6 candidate list | Ranked list of 401 CBSAs by trajectory interest; primary market selection surface |
