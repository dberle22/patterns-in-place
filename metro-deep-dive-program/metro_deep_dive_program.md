# Metro Deep Dive — Program

**Status:** Program structure locked; Position implementation and engine review in progress
**Drafted:** 2026-08-22
**Updated:** 2026-09-08
**Sits above:** `metro_deep_dive_build_approach.md`, `metro_deep_dive_template_guidance.md`, `analysis_program.md`, `deep_dive_question_bank.md`, `RESEARCH_TOOL_ROADMAP.md`, `zone_methodology_notes.md`
**Does not replace:** any of the above. This document says how they relate and what gets built in what order.

---

## 1. Why this document exists

Over the last two months the project accumulated seven overlapping efforts — the Intelligence Framework, Area Explorer, the Research Tool, the Industry Explorer, Place Intelligence, the Analysis Program, and the Deep Dive template — each partly answering "show me a metro." They were listed as peers. They are not. This document sorts them into three layers, places every analysis idea we have raised into one of them, states the routing rule that connects them, and proposes the first market arc.

The organizing decision: **the Intelligence Framework is the router.** It tells us what is interesting about a metro, and therefore which analyses to run and which act to lead with. It is not a stat-box lookup. Acts are assembled in the issue from whatever the router selected; nothing is pre-built toward an act.

## 1.1 Act shorthand

The acts are best understood as output lenses:

- `Act 1` = who this market is
- `Act 2` = what this market is and how it works
- `Act 3` = how this market is changing
- `Act 4` = where inside the market the structure and opportunity are

In practical terms:

- `Act 1` gives identity
- `Act 2` gives explanation
- `Act 3` gives change over time
- `Act 4` gives internal geographic targeting

Another useful shorthand:

- `Act 1` = what kind of place is this?
- `Act 2` = why does it work this way?
- `Act 3` = how is it moving?
- `Act 4` = where exactly is the action inside it?

Important nuance:

- `Act 1` is the identity layer: fingerprint, cluster labels, peer set, and light framework interpretation
- `Act 2` can include regional framing, but it is not primarily a time/trend act
- `Act 3` is where explicit dynamics and trend interpretation belong
- `Act 4` is the intra-CBSA narrowing layer: zone types, corridors, districts,
  and sometimes parcels
- `Act 4` should still be legible through the three Intelligence frames, not just through an opportunity lens

The acts are not rigid containers for questions. The questions, themes,
datasets, and methods can cut across multiple acts. That is a feature, not a
bug. The act structure tells us what kind of output we are producing; the
analysis families tell us what tools we have available to produce it.

One more practical reading rule:

- start from the `issue` output we want
- trace back to the `analysis` that answers it
- then identify the `engine`, `shared method`, `shared dataset / mart`, and `supporting infrastructure` needed underneath

That is the main planning loop for Metro Deep Dive. It keeps us working
backward from outputs while still standardizing the reusable systems that power
them.

---

## 2. The three layers

| Layer | What it is | Unit of work | Rule |
|---|---|---|---|
| **Engines** (`engines/`) | Reusable computation: scoring, similarity, POI ingest and taxonomy, infrastructure, benchmarking, time series, geography | A component folder with a notebook, a `NOTES.md`, and a contract | Built only when an analysis calls it. Promoted to `foundations/` when two consumers use it unchanged. |
| **Analyses** (`analyses/`) | Parameterized notebooks that run one question nationally or for one market so we can look | One notebook per question | Exploratory. Reusable queries and QA outputs are welcome; final issue outputs and presentation locks do not live here. |
| **Issues** (`issues/`) | Where the compelling parts of an analysis are selected, rendered to publisher spec, and written up | One folder per published piece | Owns every lock-once decision. Assembles acts from routed analyses. |

Analyses are where new things get found. Issues are where the series stays
comparable. Build order and publication order are separate: the former follows
dependencies, while the latter follows the strongest completed story.

*Naming note: "engine," "analysis," and "issue" already carry these meanings in the existing docs — the build approach calls the shared components engines, `analysis_program.md` calls its entries analyses, and the template calls a published market an issue. The folders adopt that vocabulary rather than inventing a parallel one. Where "Analysis Program" appears below it means the specific banked list, not the layer.*

## 2.1 Reusable component view

The three layers are the program structure. A second view is useful for build
planning: the reusable component view. This helps us distinguish what should be
built once and reused across acts, questions, and themes.

| Component type | What it is | Example shape |
|---|---|---|
| `engine` | A reusable computational system that produces a class of derived outputs | Intelligence Framework outputs, zone model outputs, theme engine interface |
| `shared method` | Reusable analytical logic applied across multiple questions or themes | comparison/benchmarking, regional role, job-proximity logic |
| `shared dataset / mart` | A queryable output layer storing prepared inputs or derived results for downstream notebook work | trajectory mart, geo mart, benchmark datasets |
| `supporting infrastructure` | Enabling inputs or platform pieces that make methods and marts possible without being the main analytical product | source extract caches, source registries, market config |

This view matters because the acts are output lenses, while the reusable
components underneath can cut across multiple acts. The practical build goal is
to standardize the reusable part:

- datasets and marts
- methods
- notebook workflows
- shared visual/output patterns

The market-specific part is usually which questions or themes get chosen, not
the build method used to answer them.

## 2.2 Scaffold rule for the new build tree

The new build tree should be scaffolded by `engines`, `analyses`, and
`issues`, not by acts.

Why:

- the `acts` are reader-facing output lenses
- the reusable work happens underneath them
- if we scaffold by acts too early, we risk duplicating logic that should stay shared

The intended folder logic is:

- `engines/` = reusable systems, methods, marts, and supporting infrastructure
- `analyses/` = reusable question notebooks, theme notebooks, and reusable act-level issue builders
- `issues/` = market-specific assembly, selections, lock-once decisions, and final output planning

One important consequence:

- reusable `Act 1`, `Act 2`, `Act 3`, or `Act 4` builders should usually live under `analyses/`, not under `issues/`
- `issues/` can still have a `_shared/` area for conventions, specs, and shared issue-facing guidance
- market folders under `issues/` should stay focused on market-specific assembly rather than becoming a second reusable notebook layer

This new structure should be developed first inside `metro-deep-dive-program/`
as a clean sandbox alongside the legacy `metro-deep-dive/` tree. If it proves
itself, we can later decide how to merge or migrate it.

---

## 3. Analysis families

Analyses are organized by **where the question comes from**, not by where the answer gets published.

### 3.1 Position — what the framework says (CBSA grain, every market, same every time)

This is the Research Tool's content, rebuilt as notebooks. Runs first; its output routes everything else.

| Analysis | Contents | Current implementation state |
|---|---|---|
| **Profile** | Identity labels; frame percentiles; topic and subject scores; raw KPI candidates and vintages; governed benchmark context | Marimo notebook and four reusable SQL surfaces implemented. Interactive review and headless-QA reconciliation remain. |
| **Peers** | Promoted cross-frame and frame-specific top-10 peers; transparent overlap; target/top-five position; featured-peer governed KPI comparison | Marimo notebook and reusable peer query surfaces implemented. Interactive review and headless-QA reconciliation remain. Diverging peers, slopes, and forward analogs are not part of this level-based surface. |
| **Trajectory** | Stored frame position and momentum; metric and annual evidence; national context; persisted turn signals and threshold sensitivity | Marimo notebook, six reusable SQL surfaces, and the 50-metric direct recurring Time-Series panel implemented. Interactive review and contract freeze remain. |
| **Internal structure** | Part 1: market geography and zone structure across counties, Census Places, tracts, ZCTAs, Phase 7 types, and sourced local neighborhoods when available. Part 2: POI/activity patterns, employment centers, Infrastructure, and optional corridor exploration. | Planned as a two-part Marimo market-anatomy analysis. The base can proceed from existing engines; local-neighborhood mapping is the next geography priority, while corridor work is analysis-local. |
| **Candidate scan** | Filterable all-market selection surface using cross-frame divergence and current trajectory evidence, with visible rank contributions | Planned as a Marimo-only port and update of the frozen Research Tool Candidate List. |

`Similarity neighborhood` is retired as a Position analysis because it mixed
three distinct objects. CBSA similarity stays in `Peers` and the standalone
similarity-method study; national tract and ZCTA classifications stay in the
Intelligence Framework; local-neighborhood mapping belongs in Geography; and
within-market corridor questions belong in `Internal structure` analysis.

Internal Structure is broader than the structural-candidate pool. Its primary
job is to show how the metro is assembled across formal Places, sourced local
neighborhoods, small-area zone types, activity anchors, employment centers,
and physical networks. Corridor exploration is optional within that review.

**Issue caveat:** Position analyses are internal until the Intelligence Framework review (`intelligence_framework_review_question_bank.md`) is answered — specifically Section B (similarity validation) and A1 (universe: 396 / 401 / 925). Until then, only the cross-frame cluster label and the peer list go in print, with a methods caveat. Frame composite scores do not.

**Position completion boundary:** the implementation work for Profile, Peers,
and Trajectory is complete enough for exploratory use. This is not a claim that
their values, labels, or visuals are publication-ready. Remaining work is
interactive multi-market review, reconciliation with the separate headless QA
runners, and the applicable Intelligence/Trajectory contract reviews.

### 3.2 Explanation — why it sits there (sub-CBSA grain, routed per market)

The deep dive question bank. National methods say where a market sits; these say why.

| Analysis | Question | Inputs | Status |
|---|---|---|---|
| **Q6 One metro?** | Are outlying counties functionally part of it | LODES WAC/RAC integration, county industry mix | Not built; integration threshold must be stated |
| **Q1 Supply or demand** | Is cheap housing abundant supply or absent demand, by submarket | Stock composition, vacancy, permits, HPI | Not built |
| **Q2 Job-proximity gradient** | Price gradient from employment centers | Industry D3 job centers + tract prices; validated Infrastructure candidate when a named physical-context experiment needs it | Job centers built; gradient not. Straight-line proximity can start now; routing remains out of scope until the method demonstrates a need. |
| **Q3 Where growth lands** | Greenfield vs. infill vs. nowhere | Tract housing-unit and pop change | Not built; tract vintage handling is the hazard |
| **Q4 Daily-needs access** | Per-tract amenity access | Overture POIs, POI taxonomy; validated Infrastructure candidate only if the method names a physical-context need | POI Engine ready for Richmond analysis; daily-needs basket and access metric are the next build. Infrastructure is available but does not define access or barriers. |
| **Q5 Afford to live near jobs** | Residence income vs. workplace wages | LODES RAC/WAC, tract income, OEWS | Not built; OEWS ingestion needed |
| **Regional role** | Inflow/outflow, commute shed, migration origins | LODES OD (not ingested), IRS flows | Partial from WAC/RAC; OD deferred |
| **Corridor exploration** | Where does a named or observed corridor pattern warrant deeper analysis, and why | Internal Structure + routed Q2/Q4/Trajectory evidence where relevant | Analysis-local and conditional; it does not rely on an engine-produced candidate boundary. |
| **Parcel watch** | Underutilized parcels in the selected corridor or district | Regrid / county parcels | Conditional; Jacksonville path exists |
| **Catchment** | Point-centered tract apportionment, daytime population, barriers | Place Intelligence D1–D3 | Built for Jacksonville as a site product; methods promote, app does not |

POIs are not an analysis. They are an input to Q4, Internal Structure's
Place/Zone/neighborhood activity review, and any later corridor exploration.

**Cross-act note:** Explanation questions are not owned by one act. Many of
them feed multiple acts:

- `Act 2` as the main explanatory workbench
- `Act 3` when the same question gains a time-series or comparative dynamic read
- `Act 4` when the same question becomes spatially targeted within the market

The most reusable early explanation questions currently look like:

- Regional role
- Q1 Supply or demand
- Q2 Job-proximity gradient
- Q6 One metro?
- Q3 Where growth lands

This is also why `Act 2` matters so much. It is increasingly the main
explanatory workbench of the program. A large share of what later appears in
`Act 3` and `Act 4` will be assembled first here, then reused in change-over-
time or intra-market form.

### 3.3 Thematic — the Analysis Program (national grain, transposable)

Each entry produces a **theme engine** that runs in two modes: `market: all`
yields the national analytical build; `market: <cbsa>` yields that market's
section. Same notebook, one parameter. The canonical order is national first,
then market mode. Industry is the first instance of the interface; Housing and
Migration follow its shape.

Thematic work starts in `market: all` mode to understand the distribution,
test the claim, and stabilize the shared method. It then runs in
`market: <cbsa>` mode so the issue can select the locally relevant findings.
The reusable part is the build method and theme-engine interface, not the
choice of which theme a given market gets.

| Entry | Themes crossed | Engine | Status |
|---|---|---|---|
| **A1 AI inversion** | Industry × People | Industry engine + NAICS→AIOE crosswalk | Active; Marimo |
| A2 Building lowers prices? | Housing × People | Housing engine | Banked |
| A3 Moving toward harm? | Environment × People × Housing | Hazard × growth | Banked |
| A4 Remote work rewired? | Work Geography × Housing × Industry | WFH series + LODES | Banked |
| A5 How many downtowns? | Work Geography × Housing | Polycentricity from WAC | Banked |
| A6 Specialization predicts growth? | Industry × People | LQ lagged panel | Banked |
| A7 Who is squeezed? | Housing × Industry | Price level vs. burden | Banked |
| A8 Geography of life expectancy | Health × Housing × Social Fabric | `health_wide` | Banked |
| A9 Converging or diverging? | People × Industry × Housing | Long-panel dispersion | Banked |
| A10 Polarization | Industry × People | Sector wage distribution | Banked |
| Housing satellite | Vacancy, costs, supply character, overheating heuristic | Housing engine | Satellite to Richmond acts; feeds A2, A7, Q1 |
| CBSA similarity study | The cosine method itself | — | Standalone article; depends on the methods memo |

"Also raised, not yet entries" stays as listed in `analysis_program.md`.

---

## 4. Routing

Position runs first and is cheap. Its outputs select the Explanation and Thematic analyses a market gets. Theme choice is therefore discovered per market, as `metro_deep_dive_build_approach.md` already requires — this is the mechanism.

| Position signal | Routes to |
|---|---|
| Divergence flag on a frame | Explanation questions in that frame — Livability → Q1, Q4; Opportunity → Q5; Character → Q6 |
| Pattern flag | The Thematic entry that tests it — Fast Demographic Changer → A9; Environmental Risk Outlier → A3; Hidden Livability Winner → A7; Diverging From Themselves → the frame pair's questions |
| Diverging peer | A paired comparison; candidate for the featured peer in print |
| Zone composition outlier | Internal Structure Place/Zone and activity review; inspect corridors only where they add explanatory value |
| Opportunity turn signal | Trajectory leads Act 3 |
| No strong signal | Run the default set (Section 7) and let the Data Take scan find the hook |

Routing is a proposal the analyst reviews, not an automated pipeline. The router's job is to make the first look efficient, not to replace judgment.

In practice the routing path is:

`Act / issue need`
-> `analysis family`
-> `specific question or theme`
-> `reusable components required underneath`

That means routing is not only about editorial sequencing. It is also how we
discover what should become a shared build asset.

---

## 5. Engines

Built only on call. Each gets a folder under `engines/` with a notebook, `NOTES.md` (audit of what exists, done when the folder opens), and a contract.

| Engine | First called by | Exists where (verify) |
|---|---|---|
| **Registries** — `market.yaml`; lock-once constants as data | Every analysis | Not built |
| **Benchmarking** — one function: metric at grain → national / division / state / peer-set percentile and rank | Profile, Fingerprint, theme engines | Implemented in `engines/benchmarking/`, `mart_benchmarking`, and `foundations/benchmarking_py`; current national/geographic/peer-set comparisons are available. |
| **Intelligence Framework** — scores, clusters, similarity, trajectory, zones | All Position analyses; later Corridor Intelligence | Implemented promoted marts and canonical contract in `engines/intelligence_framework/`; similarity/universe review remains an issue-publication gate. |
| **Theme engine interface** — inputs, outputs, two run modes, one lock-once asset per theme | A1 / Industry | Industry D1/D3/D6 + A1 notebook |
| **POI** — point-source ingest, identity and provenance, explicit taxonomy mappings, geographic assignment, and QA | Q4, Corridor Intelligence, Internal Structure activity review, and later access analyses | Implemented through Epic 5 in `engines/poi/`; Richmond Overture is acquired, normalized, classified, and assigned to tract/county. Postal ZIP is source-address evidence; ZCTA geometry remains a Geography dependency. |
| **Infrastructure** — governed roads, rail, and river/canal geometry with raw OSM evidence and QA | Corridor Intelligence, Q4 where needed, Q2, and Internal Structure's physical skeleton | Implemented through Epic 5 in `engines/infrastructure/` for Richmond and Jacksonville: reproducible source runs, narrow mappings, geometry QA, and a verified read-only consumer handoff. Promotion is gated on analytical CBSA geometry and two unchanged consumer uses. |
| **Corridor Intelligence** — prototype within-market structural grouping | Optional Internal Structure corridor exploration | Paused after Jacksonville/Richmond calibration. Preserve artifacts for method reference; do not publish, promote, or make it a consumer dependency. |
| **Time series** — metric-aware trends, start/end percentile paths, national momentum and salience, tiered trajectory labels, turn signals | Position / Trajectory, Act 3, Data Takes, forward-analog slopes, Candidate Scan | Implemented in `engines/time_series/` and materialized in `mart_intelligence`. Current panel has 50 direct recurring KPIs; derived-change review and contract freeze remain. |
| **Geography** — governed identities, exact rollups, tract→Place/ZCTA allocation edges, vintage handling, on-demand display geometry, and future sourced local-neighborhood mappings | Q3, Internal Structure, and maps | Implemented in `engines/geography/` and `mart_geography`; local-neighborhood source discovery and mapping are next. |
| **Data foundation gaps** — vertical benchmark rows, vintage per metric, OEWS, LODES OD | Benchmarking, Q5, Regional role | Logged |

**Promotion rule:** a component moves to `foundations/` when two different consumers call it without modification. One consumer is a notebook; two is a library.

**Infrastructure next step:** Q4 can now define and run its daily-needs method
using the POI handoff, adding infrastructure only if that method explicitly
needs it. Q2 can begin a straight-line job-proximity experiment from existing
job centers and prices. In parallel, Geography needs to provide analytical
CBSA geometry so the Infrastructure candidates can become authoritative
consumer layers. These are integrations, not a reason to add routing, barrier,
or corridor logic prematurely.

**Naming rule for internal geography:** *zone types* = Phase 7 national tract
labels; *corridors* = linear or branched structural candidates organized around
a spine; *districts* = compact structural candidates without one dominant
spine; *catchments* = point-centered tract weights. Distinct objects keep
national classification, market form, and site reach from being conflated.

**Structural-candidate membership rule:** every candidate stays within one CBSA
and has one primary Phase 7 `zone_type`. Same-type tracts form its core; a small
number of different-type tracts may join as explicit bridge members when they
connect core sections and pass structural and Infrastructure checks. Governed
Infrastructure evidence can strengthen, weaken, or block tract relationships;
aggregate POI composition can refine borderline relationships but cannot form
a candidate or justify a bridge alone. County lines do not split a qualifying
candidate. One shared, versioned method is applied market by market, with no
manual tract edits.

**Spatial ownership rule:** `spatial` is a cross-cutting capability, not one
catch-all engine. Geography owns boundaries and crosswalks; POI owns place
points; Infrastructure owns physical line and polygon features. Catchment,
broad access/barrier handling, and corridor exploration remain analytical
methods. Geography, POI, and Infrastructure remain the source authorities;
analyses do not rewrite their classifications.

**Act 2 workbench note:** `Act 2` is increasingly the main explanatory
workbench of the program. `Act 3` and `Act 4` should be expected to reuse work
first assembled there. That means the engine list above should be read less as
"components for one section" and more as reusable building blocks that support
multiple acts.

The same logic should shape the initial scaffold:

- do not create `act_1/`, `act_2/`, `act_3/`, `act_4/` as top-level build folders
- keep reusable act builders inside `analyses/`
- keep market issue assembly inside `issues/`

---

## 6. Issues

The template (`metro_deep_dive_template_guidance.md`) remains the delivery shape. Acts are assembled from routed analyses:

| Act | Draws from |
|---|---|
| Verdict | Written last from all acts |
| 1 Identity | Position: Profile, Peers |
| 2 Engine & Fabric | Thematic instantiated for this market; Explanation Q6, Q4, Regional role |
| 3 Dynamics | Position: Trajectory; Time series engine on reader-facing KPIs |
| 4 Opportunity Funnel | Position: Internal structure; Explanation: conditional corridor opportunity read, Q2, Q5, Parcel watch |

**Issue types:** market act (one frame-sized Substack post; the unit of the arc), market synthesis, national theme piece (with its methods note), Data Take (boxed, one chart, ~100 words, inside an act), methods piece.

**Lock-once decisions live here.** Each is made the first time an issue needs it, recorded in `decisions.md` with a date, and inherited by every subsequent issue:

- Fingerprint radar KPI slots and axis order
- Top-line stat box fields
- NAICS→exposure crosswalk version and citation
- Archetype (zone type) names
- Structural-candidate stat block format and Investment Score threshold
- Peer count shown and the similarity caveat language

Analyses never own locks. They show the full set; the issue picks the locked subset.

**Editorial-only elements** (no analysis behind them): Market Verdict, History Box, cultural fabric narrative, corridor and district names. Methods pieces currently identified: apportionment ("why the circle around your property is lying to you"), the fastest-growing-tract redistricting artifact, the similarity study, the contract-driven data development series.

One more practical distinction:

- the `issue` decides what gets shown and in what form
- the `analysis` decides how the question is answered
- the `reusable component` view tells us what should be built once and reused underneath both

---

## 7. Richmond — initial proposal

Richmond, VA (CBSA 40060) is market #1. Jacksonville is market #2 and is where Act 4 debuts, because zone types, Place Intelligence, and the ROF parcel path already exist there.

What we know going in: the Act 2 pilot is underway; Gold industry profile
shows professional services, transportation/utilities, and construction as
stronger leads than information or manufacturing; A1 is active in Marimo;
~77k Overture POIs and `osmextract` infrastructure layers are ingested and
reviewed; Richmond Profile and Peers analysis surfaces and QA bundles now
exist, and the 50-metric Trajectory panel is materialized with its Marimo
review surface. The open Position step is now interactive review and routing.

### Step 0 — Review Position

Run Profile, Peers, and Trajectory for Richmond and at least one contrasting
metro. This is the routing checkpoint. Record the labels, peer lenses,
coverage limitations, and ordinary/no-signal results before choosing anything
else. Reconcile stable row counts and ordering with the headless QA runners;
do not add market-specific logic to the Position notebooks during review.

### Step 1 — Default routed set (pending Step 0)

Proposed on current evidence, to be confirmed or replaced by the Position
routing brief:

| Analysis | Why now |
|---|---|
| **A1 / Industry engine, all-market then Richmond mode** | Already active; sets the theme engine interface; produces §4 |
| **Q4 Daily-needs access** | Richmond POIs are ready and Infrastructure has a verified candidate handoff; define the narrow basket and access method, using physical context only if needed. |
| **Q6 One metro?** | Character opener; WAC/RAC exist; differentiates the first post a reader sees |
| **Regional role (partial)** | WAC/RAC only; OD stays deferred |
| **Housing satellite → Q1** | Only if Position flags Livability divergence |

### Step 2 — Build routed analyses

For themes, build and inspect the national notebook first, then run the same
analysis in Richmond mode. For Explanation questions, build the reusable
question notebook and inspect its Richmond outputs. Open or widen an Engine
component only when the analysis actually requires it.

### Step 3 — Issue arc

Publication order is separate from build order. The initial reader arc is:

1. **Act 2 post — Industry makeup and exposure.** From A1 market mode. First lock: the exposure crosswalk.
2. **Act 1 post — Identity.** From Profile and Peers. Locks: radar slots, axis order, stat boxes. Cluster label and peer list only; frame scores held back.
3. **Act 2 post — Fabric.** From Q4 and Q6. Lock: daily-needs POI definition.
4. **Act 3 post — Dynamics.** From Trajectory plus routed Act 2 context.
5. **Synthesis + Verdict.**

Act 4 is not in the Richmond arc. Overview + Acts 1–3 is a valid first issue per the build approach.

### Parallel, not blocking

- Run the Intelligence Framework review question bank as the `engines/intelligence_framework/NOTES.md` audit. Section B first.
- Freeze the Research Tool at its current state. Keep the Candidate List for choosing market #3.
- Area Explorer marts (`cbsa_profile_year`, `cbsa_metric_long`) stay maintained as the read layer; the public app is not on the critical path.

---

## 8. What locking each layer means

- **Engines locked:** the named component boundaries, each with a one-paragraph contract on open; built only on call; promoted on second use.
- **Analyses locked:** three families, the membership in Section 3, the routing rule in Section 4. New ideas get placed into a family or rejected. There is no fourth family.
- **Issues locked:** the template as delivery shape; the lock-once list in Section 6 owned here; acts assembled from routed analyses.

## 9. Open before build

- Confirm Richmond as market #1 and Jacksonville as #2 (build approach still lists this open).
- Reconfirm `mart_area_explorer` and `mart_intelligence` consistency when a
  new engine build changes their shared inputs (universe, CBSA code types).
- Confirm what A1 currently reads from — marts, Gold, or the Industry Explorer prep layer.
- Decide `market.yaml` shape when the first analysis opens, not before.

## 10. Weekly question

Did an analysis run, did an issue move, and did at least one chart go out?
