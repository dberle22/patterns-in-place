---
section: site_brief
status: draft
spotlight_site: jacksonville_fl (CBSA 27260)
timebox: 1 week
last_updated: 2026-07-31
---

# Site Context Brief — Spec

Analytical content and output requirements for the Site Context Brief, in one document. This is the spec of record — `site_prep.py` and `app.py` are built to satisfy it.

"Property Analyzer" is the eventual product name. This spec covers **v0 only**: a single-site Streamlit app, built on the Metro Deep Dive Industry section pattern (`data_prep.py` + `app.py`, single page, section-ordered containers, each deliverable independently hideable while the build is in progress).

**Note on the artifact:** the original ask was something forwardable to investors. A Streamlit app is explorable but not forwardable, and the two are different products. v0 optimizes for build speed on a proven pattern; a static export is a v1 concern, not a v0 blocker. Keep the prep layer render-agnostic so a static path can be added later without a rewrite.

## Purpose

Take one property address and produce a written, chart-backed brief describing the trade area around it: who lives there, who works there, what's already built there, how people get to it, and how all of that compares to the rest of the metro and the country.

Built site-agnostic. A **site** is:

```yaml
site_id: str
address: str          # human-readable, canonical — the primary identifier
lat: float            # geocoded from address; may be overridden manually
lon: float
geocode_source: str   # provenance + match quality
market_id: str        # CBSA GEOID, e.g. 27260
asset_type: enum      # retail | residential | mixed  (v0 ships retail only)
rings_mi: [1, 3, 5]
primary_ring_mi: 3
```

**Address is the primary identifier.** It is what a human recognizes, what gets pasted into Google Maps, and what makes a figure traceable back through the pipeline. Coordinates are derived, not authored. Geocode via the free Census Geocoder (which also returns the containing tract GEOID, saving a spatial join), store the returned match type and quality, and always allow a manual lat/lon override — commercial outparcels and new construction geocode badly, and a rooftop-vs-street-interpolated difference of 200 feet can move a 1-mile ring across a corridor.

**Ring convention:** 3 miles is the primary ring — it carries the headline numbers, the benchmark comparisons, and the percentile positions. 1 and 5 exist to produce the gradient, which is where the actual analysis lives: a site where income rises from 1 to 5 miles is a different deal from one where it falls, even when the 3-mile figure is identical.

Rationale for 3 over 1: Florida is car-first, and a 5-mile trip is a ~10-minute drive, so a 1-mile ring badly understates a realistic catchment. Rationale for 3 over 5: realized trade areas are smaller than drivable ones — people do not pass one grocery store to reach an identical one four miles on — and a 5-mile straight-line circle in Jacksonville is far more likely to be distorted by river and highway barriers (see D3). `primary_ring_mi` is config, not a constant: a home-improvement big box genuinely pulls 5–10 miles while a QSR outparcel pulls under 1.5, so format should set it.

Every deliverable below must accept that config as input. Jacksonville is the first site run through it, not a hardcoded target.

## Scope discipline

One week. One site. One app.

**Repo access for the build agent.** The agent may read and write across `foundations/`, `metro-deep-dive/`, `publisher/`, and `intelligence/`. Cross-folder reading is not just permitted, it is expected: a standing task of this build is to **identify modules that already exist in one folder, are about to be needed in a second, and therefore belong in `foundations/`**. Where the agent finds one, it should surface the candidate with a short rationale rather than silently copying, duplicating, or refactoring it. Promotions get proposed, reviewed, and then executed — not executed and then reported.

**Hard stop at the end of D3.** D3 concentrates the methodological content of this build (POI classification, density and clustering analysis, dasymetric apportionment, barrier heuristics). The agent finishes D1–D3, writes up what it did and what it chose, and **stops for review before starting Phase 2 or Phase 3.** This gate exists so the methods can be taught and interrogated rather than inherited.

If a deliverable is not done by day 5, it gets cut rather than extending the timebox. Phase 2 items are the designated cut candidates.

## Data sources

| Source | Table | Grain | Notes |
|---|---|---|---|
| Population, age, race, education | `gold.population_demographics` | geo_level/geo_id/year | Tract grain available. Primary catchment demographic input. |
| Income and earnings | `gold.economics_income_wide` | geo_level/geo_id/year | Median HH income, per-capita income, poverty rate, RPP at CBSA. Tract coverage needs a confirm pass. |
| Housing stock and cost | `gold.housing_core_wide` | geo_level/geo_id/year | Tenure, vacancy, median value, median rent, structure type. Tract grain. |
| Housing market trend | `gold.housing_market_wide` | geo_level/geo_id/year | ZHVI, ZORI, FHFA HPI. CBSA/county grain — **not tract**. Used as market context, not catchment context. ZHVI is published at ZIP and FHFA has a ZIP-level annual series; a ZIP overlay would be a meaningfully better catchment read than county. **Deferred to v2** — everything else is tract-grain and mixing in a third geography for one metric family is not worth the timebox. Do not spend build time investigating this. |
| Affordability | `gold.affordability_wide` | geo_level/geo_id/year | Rent-to-income, value-to-income, burden. |
| Commute and vehicle access | `gold.transport_built_form_wide` | geo_level/geo_id/year | Drive-alone share, mean travel time, zero-vehicle share, WFH share. WFH matters for daytime population read. |
| Workplace jobs (daytime population) | `silver.lehd_lodes_wac` | tract | `jobs_ind_*` at tract. The daytime-population input. |
| Resident workers | `silver.lehd_lodes_rac` | tract | `workers_ind_*` at tract. Pairs with WAC for the day/night divergence read. |
| Industry mix and specialization | `gold.economics_industry_wide` | geo_level/geo_id/year | CBSA/county grain. Market-level context panel only. |
| Composite hazard risk | FEMA NRI | county + tract | **Reported as already available — agent must confirm the table name and grain before relying on it.** If tract-grain NRI is present it apportions through D1 like any other tract metric and the risk section needs no new ingest. |
| POIs / competition / co-tenancy | `outputs/<market_id>/overture_pois.parquet` | point | Overture slice. Proven on Richmond (76,913 rows). Needs a Jacksonville run. |
| Building footprints | Overture buildings theme | polygon | Not currently extracted. Candidate density surface for dasymetric apportionment — see D1. Cheap if the existing Overture path already supports a second theme; skip if it does not. |
| Road network and corridors | `outputs/<market_id>/osm_infrastructure_lines.parquet` | line | OSM via `osmextract`/`pyrosm`. Road hierarchy, water features, and crossings for the D3 barrier read. |
| Tract geometry | `geo.tracts_all_us` | tract | Required for ring intersection. |
| Flood zone | **Not ingested** | polygon | FEMA NFHL. Point-in-polygon query against a published REST service — likely an hour, not a day. See D5. |
| Traffic counts (AADT) | **Not ingested** | segment / count station | FDOT statewide AADT layer. Highest analytical value of anything not yet held, but also the highest format risk. See D4. |

Phase 1 requires no new ingestion. Phase 2 is explicitly conditional: **anything that is not light ships in v2 rather than holding up v0.**

---

# Phase 1 — Prep existing data into catchment format

### D1 — Catchment geometry and tract apportionment

**This is the deliverable the whole spec rests on.** Every other number in the brief is downstream of getting this right, and it is the only genuinely novel methodological work in the build.

**The problem:** Gold demographics are tract-grain. Rings are circles. Tracts do not align with circles. Jacksonville tracts are large and car-oriented — a 1-mile ring around a suburban retail site may contain **zero** tract centroids while overlapping four tracts. Centroid-in-ring inclusion, which is the naive default, will silently produce either an empty catchment or a wildly overstated one.

**What it produces:**
- Ring geometries at 1 / 3 / 5 miles around the site point, projected to an appropriate equal-area or local CRS before buffering (not buffered in WGS84 degrees)
- A tract-to-ring **weight table** — one row per tract per ring, the atomic output of this deliverable:

```
site_id        str      site identifier
ring_mi        int      which ring
tract_geoid    str      11-digit tract
weight         float    share of the tract assigned to this ring, 0–1
weight_method  str      areal | dasymetric
intersect_area float    projected area of the tract ∩ ring
tract_area     float    projected area of the full tract
containment    enum     full | fragment
centroid_in    bool     diagnostic only — does the tract centroid fall inside the ring
```

- A reusable `apportion(metric_series, weight_table, method)` function that correctly distinguishes:
  - **extensive** metrics (counts — population, households, jobs): summed with weights
  - **intensive** metrics (rates, medians, ratios): weighted average for rates; medians must be flagged as approximate or recomputed from distributions, never naively averaged
- A coverage diagnostic: how many tracts intersect each ring, total weight captured, and a warning flag when a ring is dominated by a single partially-captured tract

**Selection rule — one clarification worth making explicit.** "Include tracts whose centroid falls in the ring **and** tracts that overlap the ring" reduces to just "tracts that overlap the ring," because any tract with its centroid inside a ring necessarily overlaps that ring. Overlap is a strict superset. So the selection rule is simply **intersects**, and `centroid_in` is retained as a diagnostic column rather than a filter.

The instinct behind the note is right and lands one step further downstream: the problem is not *which* tracts to include, it is *how much* of each to count. Areal weighting selects correctly but still assumes population is spread evenly across the tract's area — the same "geographic center is not the population center" objection, just relocated from selection to weighting.

**Method for v0:** areal-weighted interpolation — weight = intersected area / total tract area. Document the uniform-density assumption explicitly in the methods note.

**Optional upgrade, if cheap: dasymetric weighting.** The uniform-density assumption is exactly what "the geographic center is not the population center" objects to, and there is a nearly-free fix available because the Overture extract is already being run. Instead of weighting by land area, weight by the share of the tract's **building footprint area** that falls inside the ring — filtered to residential subtypes where the attribute is populated, all buildings otherwise. A tract that is half conservation land and half subdivision then contributes correctly rather than being split down the middle.

This is a real improvement in a place like Jacksonville, where tracts routinely contain large undeveloped, industrial, or water areas. Conditions: only do it if the existing Overture path supports pulling a second theme without new plumbing, and only as a *swap of the weight column* — `weight_method` already carries the provenance, and nothing downstream should need to know which method produced the number. If it takes more than half a day, ship areal and leave dasymetric as the documented v1 upgrade.

Note the honest limitation: building footprint area is a proxy for floor area, which is a proxy for households, which is a proxy for population. It is better than land area, not correct.

**Risk profile by ring:** the 3-mile primary ring is ~28 sq mi and will contain a healthy number of whole tracts, so areal weighting is defensible there and the block-group question is no longer urgent. The 5-mile ring is safer still. The **1-mile ring is where this method is weakest** — it may be mostly or entirely composed of tract fragments. Treat the 1-mile figures as directional gradient input, not as reportable standalone numbers, and let the coverage diagnostic say so per ring rather than as a blanket caveat.

**Acceptance criteria:**
- [ ] Ring buffers are generated in a projected CRS; a sanity check confirms the 1-mile ring area is within 1% of π square miles
- [ ] Weight table sums to ≤ 1.0 per tract across all rings and exactly 1.0 for any tract fully contained in the largest ring
- [ ] `apportion()` refuses to run on a median-type metric without an explicit `method="approximate"` flag being passed
- [ ] A 1-mile ring containing no tract centroids still returns a populated catchment
- [ ] Coverage diagnostic renders in the brief appendix, not hidden in logs
- [ ] Coverage diagnostic emits a per-ring reliability flag (whole-tract count, share of catchment coming from fragments) so the 1-mile ring's weaker footing is visible rather than assumed
- [ ] Function accepts any lat/lon + ring list, with no Jacksonville-specific logic

---

### D2 — Catchment profile and benchmark stack

**What it produces:**
- A long-format catchment table: `(site_id, ring_mi, metric, value)` covering:
  - Population, households, household size, median age, age distribution
  - Race/ethnicity shares, foreign-born share
  - Educational attainment (BA+ share)
  - Median household income, per-capita income, poverty rate
  - Housing: owner/renter split, vacancy, median value, median rent, structure type mix
  - Commute: drive-alone share, mean travel time, zero-vehicle share, WFH share
- A parallel benchmark table at four levels: **CBSA, county, state, national**, for every metric above
- A percentile position for each metric against the CBSA tract distribution — "this ring is at the 78th percentile of Jacksonville tracts for median income"
- 5-year change for every metric where a comparable prior vintage exists

**Benchmark rule:** the brief always shows raw value + CBSA percentile, computed against the **primary ring**. Secondary rings appear in the gradient view, not in the benchmark stack — benchmarking three rings against four geography levels produces twelve numbers per metric and no insight. State and national are secondary to CBSA. No composite score, no single number — consistent with the frames-are-lenses principle.

**Acceptance criteria:**
- [ ] Every metric renders at all three ring distances or is explicitly marked unavailable
- [ ] Every metric carries its source vintage year; panels do not imply a common year across sources
- [ ] Benchmark rows derive from the same Gold query path as the catchment rows, not a separate hand-built lookup
- [ ] Percentile is computed against tracts within the market CBSA, and the denominator count is stated
- [ ] A metric missing from Gold at tract grain is dropped with a logged reason, not silently imputed

---

### D3 — Daytime population and built-environment context

**What it produces:**
- Workplace jobs and resident workers apportioned to each ring from tract WAC/RAC, with the jobs-to-resident-workers ratio per ring
- Workplace jobs by industry within the ring — specifically retail, accommodation/food, health care, and professional/scientific, since those drive different daypart traffic
- A **day/night divergence read**: does this ring gain or lose people during the workday, and by how much
- POI counts within each ring by category from the Overture slice, split into:
  - **Competitive** — same-format retail
  - **Complementary** — grocery, pharmacy, gym, quick-service food, banking
  - **Anchor** — hospital, university, school, civic, large employer
- Road hierarchy context: which OSM road classes front or bound the site, and distance to the nearest interstate ramp
- **Barrier / severance flag** — the interim answer to the fact that a straight-line ring assumes travel is equally easy in every direction, which in Jacksonville it is not.

  **A feature is not a barrier; a lack of crossings is.** The skepticism about highways is well-placed — an arterial with an underpass every quarter mile costs a driver nothing, and flagging every limited-access road would produce a flag that fires on almost every site and therefore means nothing. So the test is **crossing spacing**, not feature presence:

  - Water (the St. Johns, the Intracoastal) is a barrier by default. Crossings are bridges, they are few, they are named, and detouring to one is measured in miles.
  - A limited-access highway counts as a barrier **only where crossing spacing within the ring exceeds a configured threshold**. Where crossings are dense, it is scored as friction and reported in the appendix, not raised as a flag.
  - Rail corridors and controlled-access ramps get the same spacing test, since a grade-separated rail line with one crossing in three miles severs a catchment as effectively as a river.

  For each ring, produce:
  - which candidate barrier features intersect the ring, and each one's crossing count and mean crossing spacing within the ring
  - the share of ring **area** cut off from the site by each qualifying barrier, via polygon-split of the ring against the barrier geometry
  - the share of apportioned ring **population** falling on the far side
  - a plain-language severance summary naming the feature and the crossings
- A first-pass node typology label (retail node / office node / institutional / industrial-logistics / residential-dominant / mixed), using the same heuristic pattern as the D4 job-center interpretation in the Industry section

**Acceptance criteria:**
- [ ] A Jacksonville Overture + OSM extract exists at `outputs/jacksonville_fl/` following the Richmond output shape and manifest convention
- [ ] POI category assignment uses explicit allowlists / taxonomy fields, not substring matching
- [ ] Ring POI counts are computed from point-in-ring, not tract apportionment
- [ ] Day/night divergence is presented as a ratio and an absolute count, so a small ring and a large ring are not read as equivalent
- [ ] Typology label is derived from thresholds recorded in config, not hardcoded in the render path
- [ ] Barrier geometry is sourced from the existing OSM water, rail, and highway layers — no new ingest
- [ ] Water is treated as a default barrier; highway and rail qualify only via the crossing-spacing test, with the threshold in config
- [ ] Crossing detection is validated by hand against at least one known Jacksonville case (a site within 3 miles of the St. Johns) before the flag is trusted
- [ ] Barrier flag runs per ring and reports both severed area share and severed population share; a site with no qualifying barrier returns a clean null result rather than an error
- [ ] When severed population share exceeds a configured threshold on the primary ring, it surfaces in the site card and not only in the appendix
- [ ] Copy states that proximity is straight-line, not network or drive-time, and that the barrier flag is a screening heuristic rather than a routing result

**⛔ STOP GATE — end of Phase 1.** The agent halts here. Before any Phase 2 or Phase 3 work begins, it produces a written methods memo covering: the apportionment method actually implemented and why, the POI taxonomy and classification rules chosen, any density or clustering method used and its parameters, the barrier thresholds selected and how they were validated, and every judgment call made under ambiguity. It should also list the foundations-promotion candidates it identified along the way. This gate is for review and teaching, not sign-off theater — do not proceed past it on assumption.

---

# Phase 2 — New ingests (conditional)

**Governing rule: light or v2.** Neither of these blocks v0. Each gets a timeboxed spike; if the source does not yield cleanly inside its box, it is cut, the gap is stated plainly in the app, and it ships in v2. Neither goes into Gold in this pass — both write to `outputs/jacksonville_fl/` alongside the spatial cache, following the existing manifest convention.

These are ordered by expected cost, not by value. D5 is likely an hour. D4 is the one with real value and real risk.

### D4 — Traffic counts (AADT)

**Why it matters:** for a retail deal, cars past the door is the number the brief exists to provide, and it is the one thing in this spec that has no substitute anywhere else in the stack.

**What it produces:**
- FDOT AADT segments and/or count stations clipped to the market bbox
- AADT on the frontage road(s) for the site, defined as the nearest N segments within a documented snap tolerance
- Ranked AADT of all segments within the 1-mile ring, so the site's corridor can be positioned against nearby corridors
- Multi-year AADT trend for the frontage segment where the source supports it

**Acceptance criteria:**
- [ ] Source format, license, and update cadence confirmed and recorded in a source contract before ingestion code is written
- [ ] Snap-to-nearest-segment logic has an explicit distance tolerance and fails loudly rather than silently attaching a distant segment
- [ ] The brief states the count year and that AADT is an annual average, not a peak or observed count
- [ ] Ingest runs from a bbox + state parameter, not a Jacksonville-specific file path

**Cut rule — half-day spike, hard stop.** If the layer is not downloadable as a clean statewide geospatial file inside half a day, cut it. Scraping, per-county manual downloads, or PDF count reports all mean v2. If it is cut, the app says so explicitly rather than quietly omitting the most important number in a retail brief — an investor who notices the absence should see it acknowledged, not discover it.

---

### D5 — Flood risk

**Why it matters:** Jacksonville. Also this is the single fastest way for the brief to be *wrong in a way an investor notices*, so it is worth being conservative in the copy.

**Two sources, different cost profiles:**

- **FEMA NRI — already held.** Confirm the table name and grain first. If tract-grain NRI is present, it apportions through D1 like any other tract metric and needs no ingest work at all. Produces composite risk score, top hazard drivers, and expected annual loss context for the catchment and the CBSA.
- **FEMA NFHL — new, but light.** The zone lookup is a point-in-polygon query against a published REST service. Timebox: one hour. This is the deal-relevant number — an investor cares whether the parcel sits in a Special Flood Hazard Area, because that determines mandatory insurance, not whether the county scores high on a composite index.

**What it produces:**
- Flood zone designation at the site point (X / AE / VE / etc.), SFHA yes-no, and panel effective date
- Share of each ring's area by flood zone class
- NRI composite risk and top hazard drivers for the catchment, benchmarked against the CBSA

**Acceptance criteria:**
- [ ] NRI availability and grain confirmed before any assumption is built on it
- [ ] Zone lookup returns the designation for the site point and states the NFHL panel effective date
- [ ] Copy explicitly states this is a screening-level read from published FEMA mapping and is not a flood determination, elevation certificate, or insurance rating
- [ ] Ring flood-zone area shares are computed in a projected CRS
- [ ] NRI and NFHL are presented as answering different questions, not as two versions of the same risk read

---

# Phase 3 — The brief

### D6 — Site context app

**Format:** Streamlit, following the Metro Deep Dive Industry section pattern. Charts come from the existing `chart_engine` `render()` orchestrator (Altair for standard types, matplotlib/geopandas for static spatial). The context map is an interactive `pydeck` map, same decision and for the same reason as Industry D2 — scrolling and zooming are part of the requirement.

**Two organizing principles that resolve the ten-pages problem:**

**1. One map, many layers.** The instinct to give access, risk, POIs, and context each their own map is what produces ten pages. They are not different maps; they are different layers over the same map. Build the context map once with a layer toggle — rings, POIs by category, road network weighted by AADT, flood zones, severed area shading, tract fill by selected metric — and let each tab set the default layer state. This answers "how do we visualize access" and "is risk just a map and a table" at the same time: access is a road layer plus one ranked table, risk is a flood layer plus one small table, and neither needs its own page.

**2. Trajectory is a view, not a section.** Correct instinct — fold it in. Every metric panel gets a change-over-time companion rather than a separate section, exactly as the Industry section treats the bump chart as a view of D1 rather than its own deliverable. Direction belongs next to level, because the pairing is the insight: 78th-percentile income and falling is a different deal from 60th and rising.

**Five tabs:**

| Tab | Contents |
|---|---|
| **1. Overview** | Site card (address, typology label, primary-ring headline numbers with CBSA percentile and 5yr direction, barrier flag if it trips, flood zone) sitting directly above the interactive context map at default layer state. Everything a reader needs to orient. |
| **2. People** | Who lives here and who works here, together — they answer one question, which is "who is actually in range of this site and when." Ring gradient across 1/3/5 mi, age distribution, income and education with percentile markers, then day/night divergence, workplace jobs by industry, jobs-to-workers ratio. Each panel carries its 5yr change. |
| **3. Place** | The physical context: co-tenancy and POI density, competitive vs. complementary breakdown, nearest anchors, road hierarchy and AADT corridor table, barrier/severance detail, flood zone shares. Map layers default to POI + roads + flood. |
| **4. Market** | Jacksonville CBSA context — industry mix, GDP, employment, housing market trend. Existing Gold, no new analysis. See the note below. |
| **5. Methods** | Apportionment method and assumptions, weight-table diagnostics, per-ring reliability flags, source vintages, geocode match quality, what was unavailable and why. |

**On the Market tab:** the reverse-engineering idea is the right one. Build this tab by asking what a site-level reader actually needs from metro context, then check that against what Metro Deep Dive currently produces. Whatever earns its place here is a candidate for a standardized MDD summary component — a market one-pager that every Deep Dive issue can open with. That is a genuine foundations promotion candidate and should be flagged as one, not built twice.

**Acceptance criteria:**
- [ ] App runs end-to-end from `site.yaml`, following the Industry `data_prep.py` + `app.py` split
- [ ] Prep layer returns dataframes with no Streamlit imports, so a static export path can be added later without a rewrite
- [ ] The context map is built once and reused across tabs with per-tab default layer state — not re-instantiated per section
- [ ] Every chart carries a source and vintage label; panels do not imply a common year across sources
- [ ] Every number that came through apportionment is visually distinguishable from a directly-observed number
- [ ] No composite score appears anywhere
- [ ] Each tab renders independently, so an incomplete deliverable can be hidden without breaking the app
- [ ] Running against a second Jacksonville address produces a correct, different result with no code changes

## Non-goals

| Not doing | Why |
|---|---|
| A static/PDF export | v0 is a Streamlit app on a proven pattern. Keep prep render-agnostic so this is additive later, but do not build it now. |
| ZIP-level Zillow / FHFA overlay | Better catchment read than county, but introduces a third geography for one metric family. v2. Do not spend build time investigating. |
| Drive-time isochrones | Needs a routing engine. The D3 barrier flag is the deliberate interim substitute: it catches the specific failure mode that would otherwise make a straight-line ring wrong in Jacksonville, at a fraction of the cost. If the flag trips hard on real sites, that is the signal to build routing for v1. |
| Foot traffic (Placer, SafeGraph) | Paid. The brief is useful without it. |
| Lease comps, sales-per-sqft, cap rates | Not public data. Out of scope permanently, not just for v0. |
| Parcel ownership and assessment detail | ROF has a path to FL parcel data; not needed to answer the trade-area question. |
| Composite site score | Frames are lenses, not scorecards. Also, a made-up score is the fastest way to lose an investor's trust. |
| Multi-site comparison / ranking | v1.1. Nothing here should block it, but do not build for it. |
| Residential and tourist variants | Same engine, different question templates. Spec separately after v0 ships. |
| Retrofitting this into ROF | ROF was deliberately absorbed into Metro Deep Dive as reference. Do not reopen it. |
| Promoting AADT or NFHL into Gold | Phase 2 outputs stay app-local, same as the Richmond spatial cache. Foundations promotion is a later decision. |

## Open decisions

| Decision | Blocks | Status |
|---|---|---|
| Ring distances and primary ring | D1 | **Resolved** — 1/3/5 mi computed, 3 mi primary. Balances Florida's car-first travel behavior against the fact that realized trade areas are smaller than drivable ones. `primary_ring_mi` stays config so tenant format can override. |
| Apportionment method | D1 | Proposed — areal-weighted baseline, with dasymetric building-footprint weighting as a half-day conditional upgrade. `weight_method` carries provenance either way. |
| Whether Overture buildings can be pulled without new plumbing | D1 | Open — determines whether dasymetric weighting is in v0 or v1. Agent should answer this early, since it is cheap to check and changes the D1 build. |
| Tract vs. block group grain | D1, D2 | **Downgraded to non-urgent** by the 3-mile primary ring — a 28 sq mi ring contains enough whole tracts that areal weighting holds. Revisit only if the 1-mile gradient figures prove too noisy to publish. |
| Barrier severance threshold | D3, D6 | Open — what severed-population share should promote the barrier flag to the site card. Needs a look at real Jacksonville sites before picking a number; do not guess it into config. |
| Median handling under apportionment | D1, D2 | Open — approximate weighted median vs. dropping medians in favor of means. Leaning toward showing the CBSA-percentile position instead of a synthetic ring median. |
| Whether NRI is in v0 | D5 | **Likely resolved** — reported as already held. Agent confirms table name and grain first; if tract-grain is present it costs nothing. |
| Barrier crossing-spacing threshold | D3 | Open — what spacing qualifies a highway or rail line as a barrier rather than friction. Validate against a real Jacksonville case before setting it. |
| Output format | D6 | **Resolved** — Streamlit, Industry section pattern. Static export deferred, prep layer kept render-agnostic to allow it. |
| Whether the Market tab becomes a reusable MDD component | D6, Metro Deep Dive | Open and worth answering — a standardized market one-pager would serve both this app and every Deep Dive issue. Reverse-engineer from what the site reader needs. |
| Whether this ships publicly as a post | — | Open. There is a good methodology piece in D1 alone ("why the circle around your property is lying to you"). Decide after the brief lands. |

## Relationship to existing work

This is a **detour** from the industry-mix theme and the Richmond act sequence, taken deliberately because an outside party asked for output. It is timeboxed accordingly.

Reuse-first obligations:
- The spatial ingest path (`ingest_spatial.py` pattern, output shape, manifest fields) comes from the Richmond D4 work — run it for Jacksonville, do not rewrite it.
- The app skeleton comes from the Industry section: `data_prep.py` + `app.py`, prep returns dataframes, app renders them.
- The typology heuristic mirrors the D4 job-center interpretation logic.
- Chart rendering goes through the existing `chart_engine` `render()` orchestrator.
- Benchmark construction should anticipate, but not wait for, the vertical benchmark contract work.

**Foundations promotion candidates — a standing deliverable of this build.** The agent has read access across `foundations/`, `metro-deep-dive/`, `publisher/`, and `intelligence/` specifically so it can notice when something exists in one place and is about to be needed in a second. Candidates get *proposed with rationale* at the D3 stop gate, not silently refactored. Known candidates going in:

- **D1's apportionment engine — promote regardless of whether v0 ships.** Point-in-space enrichment against a tract-grain warehouse is a primitive this platform will need repeatedly: Stoop, any future site work, any parcel- or address-level question. Build it in `foundations/` from the start rather than promoting it later.
- **Geocoding + tract resolution** — needed anywhere an address enters the system.
- **The benchmark/percentile stack** — if it comes out clean here, it is the vertical benchmark contract in miniature.
- **A standardized market summary component** — see the D6 Market tab note; serves this app and every Deep Dive issue.
- **The context map with layer toggles** — if it generalizes past this one site, it is a reusable spatial component rather than app-local code.