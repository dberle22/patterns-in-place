# Stoop NYC — Backlog

Last updated: 2026-05-12

This is the active product backlog. Work is organized into sprints. Each task
is labeled `[agent]`, `[you]`, or `[you+agent]`.

WS1–WS6 are complete. See `docs/planning/workstreams.md` for the full historical
record of that work. The sprints below pick up from the current state of the
repo.

For product strategy and data product definitions see
`docs/planning/product_strategy.md`.

---

## Current State Snapshot

| Data Product | Status |
| --- | --- |
| Curated Places (`dim_user_poi_v2`) | Active — Google Takeout + 19 article scrapes loaded, including hotels. Crowd upload pending. |
| City Baseline (`dim_public_poi`) | Complete — 57,346 rows, 28 categories. Hotels live; crime and school quality pending. |
| Neighborhood Context (`fct_tract/nta_features`) | Active — five-borough geography live; full NTA metric coverage partial. |
| Property Listings (`dim_property_listing`) | Placeholder — 22-row sample only. |
| Shortlists (`fct_user_shortlist`) | Partial — property shortlist in on-ice Property Explorer V1. Neighborhood shortlist not built. |

| App | Status |
| --- | --- |
| Stoop Explore | Active — durable entry point live at `app/stoop_explore.py`; Explore intelligence panel, category-backed rankings, and selected-neighborhood highlight are in place. |
| Stoop Search | Not started as standalone app. Phase 1 buildable now after Sprint 1 data work. |
| Stoop Visit | Deferred. |

---

## Goals & Milestones

These are the four strategic outcomes that the sprints below are working toward:

1. **Launch Stoop Explore publicly** — a credible neighborhood explorer for
   locals and day-trippers, with curated POI depth, hotel coverage, and a
   "where should I spend a day" intelligence layer.
   - S1: Hotels
   - S1: Review Curated POIs
   - S2: Stoop Explore Intelligence
   - S2: Architecture Decision
   - S3: All

2. **Launch Stoop Search Phase 1 publicly** — a standalone neighborhood
   livability app with crime, schools, transit, and demographic context for
   people evaluating where to live.
   - S1: Crime
   - S1: School Quality
   - S2: Stoop Search Livability Scoring
   - S2: Architecture Decision

3. **Complete the data platform foundation** — all five data products at
   production quality: hotels in Curated Places and City Baseline, crime in
   City Baseline, school quality in City Baseline, crowd upload path live.
   - S1: All
   - S5: All

4. **Build Property Listings and Stoop Search Phase 2** — real listing data
   from StreetEasy and Zillow flowing into Stoop Search, with property-specific
   intelligence and shortlists.
   - S6: All

---

## Sprint 1 — Data Platform Foundation

**Goal**: Complete the data platform before building new app surfaces. All new
data should flow through existing ingestion patterns where possible.

**Outcome**: City Baseline has hotels, crime, and school quality. Curated Places
has hotels. Crowd upload path is live.

### Hotels

- [x] `[you+agent]` Decide hotel sourcing strategy: OSM pull (comprehensive
  baseline) vs. editorial scrape (Eater, Condé Nast — curated top picks). Both
  can coexist: OSM → City Baseline, editorial → Curated Places.
- [x] `[agent]` Add `hotel` category to `dim_public_poi` from OSM NYC hotel
  data via the existing `osm.py` source module in Wave 3/4 pattern.
- [x] `[agent]` Add `hotels` to `config/poi_categories.yaml` curated taxonomy
  and identify one editorial source article (e.g. Eater or Condé Nast best
  hotels NYC) to register in `config/curated_scrape_articles.yaml`.
- [x] `[you]` Save the target editorial hotel article HTML locally and run the
  parser; review normalized CSV before Places resolve.
- [x] `[agent]` Run hotel article through `ingest_curated_poi_web_scrape`,
  review QA outputs, mark `loaded` in config.

### Crime

- [ ] `[agent]` Identify the best NYC Open Data crime dataset: NYPD Complaint
  Data (historic) or NYPD Shooting Incident Data, and confirm the API endpoint
  and field contract.
- [ ] `[you]` Review the identified dataset and approve the field contract before
  ingestion is built.
- [ ] `[agent]` Build a crime ingestion module under `public_poi/sources/` or a
  new `neighborhood_context/` package (decide based on whether crime is a point
  layer or an NTA-level aggregate).
- [ ] `[agent]` Write crime data to a new gold table or extend
  `fct_nta_features` with an NTA-level crime rate metric. Update
  `docs/data_model.md` and DDL accordingly.
- [ ] `[agent]` Add crime coverage to the QA app panel.
- [ ] `[you]` Review crime data quality in QA app before proceeding.

### School Quality

- [ ] `[agent]` Identify the NYC DOE dataset that provides school-level quality
  signals (School Quality Reports or Progress Reports) and confirm the source
  URL and field contract.
- [ ] `[you]` Approve the DOE field contract and decide the grain: keep as point
  data (school locations + quality score) or aggregate to NTA level.
- [ ] `[agent]` Build school quality ingestion; extend `dim_public_poi` with a
  quality score field for `public_school` rows, or write a separate
  `dim_school_quality` table if the grain warrants it.
- [ ] `[agent]` Update `docs/data_model.md` and DDL for any schema additions.
- [ ] `[you]` Review school quality data in QA app before proceeding.

### Crowd / Excel Upload (WS7)

- [ ] `[you]` Define the submission template fields: at minimum name, address
  (optional), URL, category, submitter notes.
- [ ] `[you+agent]` Design the normalization pipeline: template → normalize →
  Places resolve → `stg_user_poi_manual_upload` → canonical merge into
  `dim_user_poi_v2`. Must use staged-accumulation pattern (new batches merge
  with existing staging rows, not replace them).
- [ ] `[agent]` Implement template reader and normalization module under
  `curated_poi/excel_upload/`.
- [ ] `[agent]` Implement `stg_user_poi_manual_upload` staging writer and
  canonical merge promotion path following the same pattern as
  `stg_user_poi_web_scrape`.
- [ ] `[agent]` Build CLI entry point: `pipelines/ingest_curated_poi_manual_upload.py`.
- [ ] `[agent]` Document the submission workflow in `docs/user_guide.md` and
  `docs/poi_categories.md`.
- [ ] `[you]` Test with a small sample submission CSV before signing off.

### Review Curated POIs

- [x] `[agent]` Query `dim_user_poi_v2` and produce a full `category × subcategory`
  breakdown with row counts; flag any rows where `subcategory` is blank, `other`,
  or falls back to the parent category name (e.g. `subcategory = "restaurants"`
  on a row that should be more specific).
- [x] `[agent]` Specifically audit restaurant-family files: for each of
  `poi_restaurants_nyc.csv`, `poi_pizza_nyc.csv`, `poi_rest_chinese_nyc.csv`,
  `poi_rest_japanese_nyc.csv`, `poi_sandwich_nyc.csv` — report how many rows
  resolved to a specific subcategory vs. fell through to the generic
  `"restaurants"` default. Surface top `detail_level_3` values actually present.
- [x] `[you]` Review the audit output and flag any subcategory rules in
  `config/poi_categories.yaml` that need tightening — whether `tag_aliases`,
  `subcategory_from_tags_or_comment` rules, or per-file defaults.
- [x] `[agent]` Apply agreed taxonomy corrections and re-run affected files
  through the ingestion pipeline to update `dim_user_poi_v2`.
- [x] `[you]` Spot-check 10 restaurant rows across different subcategories to
  confirm corrections look right before closing this task.
- [x] `[agent]` Add an end-to-end Curated POI architecture diagram showing:
  source files and article scrapes, staging / canonical merge into
  `dim_user_poi_v2`, classification mart build, manual override flow, and the
  final curated POI table consumed by the app. See
  `docs/curated_poi_e2e_architecture.md`.

---

## Sprint 2 — Analysis & Intelligence Design

**Goal**: Lock the intelligence definitions for both apps before building any
analysis surfaces. Scoring models and ranking logic should be written down and
validated against known neighborhoods before any code is written. This sprint
is design-only — no new app surfaces or tables.

**Outcome**: A one-page design doc for Stoop Explore intelligence and a
one-page design doc for Stoop Search livability scoring. Both validated against
known neighborhoods. Architecture decision made on pre-compute vs. runtime.

### Stoop Explore Intelligence

- [x] `[you+agent]` Write a one-page design doc: what does "neighborhood
  character" mean, how do we rank NTAs by category density, what is the output
  shape (ranked list, score, character tag)?
- [x] `[you+agent]` Build out the Character section in
  `docs/neighborhood_character/narrative_concepts.md` so it moves from abstract
  framing into a v1 product language for Stoop Explore.
- [x] `[you+agent]` Define 4 to 6 initial Character story types for v1 Explore
  intelligence. Start with narrative concepts such as destination food
  district, cultural core, nightlife scene, specialty shopping area, local
  neighborhood main street, and quiet residential enclave.
- [x] `[you+agent]` For each Character story type, map the supporting evidence:
  primary curated categories, optional public/civic support signals, what
  counts as strong evidence, and what should not be allowed to dominate the
  story.
- [x] `[you+agent]` Lock the MVP ranking unit and geography. Use NTA-level
  rankings, compare neighborhoods within NYC only, and keep the core Explore
  surface focused on category rankings rather than narrative labels.
- [x] `[you]` Finalize the MVP category set for the Explore intelligence panel.
  Start with the curated categories that are already meaningful in current data
  coverage: restaurants, museums, bookstores, shopping, and hotels. Decide
  whether bakeries, food markets, specialty grocery, movie theaters, record
  stores, bars, and music venues should be included in v1, and keep coffee
  hidden until the evidence threshold is met.
- [x] `[you+agent]` Lock the scoring formula for "great neighborhood for X."
  For MVP, use pre-computed NTA curated POI counts with NYC-relative ranking and
  evidence thresholds, not radius searches, ratings weighting, or blended
  curated+public formulas. Document the exact sort order, thresholds, and
  fallback behavior when category coverage is sparse.
- [x] `[agent]` Define the first app-facing intelligence outputs for Explore:
  `Top neighborhoods for X`, `What this neighborhood is known for`, supporting
  evidence fields, and an optional short headline label for the selected NTA.
- [x] `[agent]` Turn the framework into an app-ready output contract. Confirm
  the fields Stoop Explore needs for (a) top neighborhoods for a selected
  category and (b) what a selected neighborhood is known for, using the mart
  shape in `docs/data_products/neighborhood_character/neighborhood_character_mart.md`.
- [x] `[agent]` Build the validation set for 5 to 8 known neighborhood ×
  category expectations (for example Williamsburg/bars, Greenwich
  Village/bookstores or coffee, LES/music, Chelsea/galleries, Midtown/hotels)
  and record where the current rankings match intuition vs. miss.
- [x] `[you+agent]` Review the validation output and decide the first tuning
  pass. Only adjust category inclusion, thresholds, tie-breaking, and "known
  for" labeling rules in Sprint 2. Defer richer composite scoring and
  narrative-generation logic to later work.
- [x] `[you]` Sign off on the final MVP Explore intelligence spec so Sprint 3
  can build the surface directly against the pre-computed outputs.

### Stoop Search Livability Scoring

- [ ] `[you+agent]` Write a one-page design doc: what inputs feed the livability
  score, what weights, what does the output look like (0–100 score? ranked list?
  traffic-light per dimension?)?
- [ ] `[you]` Define "good transit" concretely: number of subway stations within
  0.5 miles? number of distinct lines served? This needs a specific formula
  before building.
- [ ] `[you]` Define "good school access" concretely: nearest school quality
  score? average of schools within 1 mile? elementary schools only or all grades?
- [ ] `[agent]` Validate the proposed livability scoring against 5 known
  neighborhoods (e.g. Park Slope, Astoria, Mott Haven) and confirm scores match
  common understanding before building the app surface.
- [ ] `[you]` Sign off on livability scoring design or redirect.

### Architecture Decision

- [x] `[you+agent]` Decide: intelligence outputs (rankings, scores) should be
  pre-computed and stored in DuckDB at pipeline time, not computed at app
  runtime from raw tables. This keeps app reads fast, makes outputs testable,
  and gives Sprint 3 a stable contract. Documented in `docs/decision_log.md`.

---

## Sprint 3 — Stoop Explore V1 Launch

**Goal**: Rebrand and polish the current Neighborhood Explorer into Stoop
Explore with a clear "where should I spend a day" intelligence layer, hotel
coverage, and a public launch.

**Outcome**: Stoop Explore is live on Streamlit Cloud, announced on LinkedIn,
Reddit, and Substack.

### Explore App Foundation

- [x] `[agent]` Rename or alias the current app entry point so Stoop Explore has
  a durable app path (`app/stoop_explore.py` or equivalent). Update any local
  launcher and Streamlit Cloud entry configuration.
- [x] `[agent]` Audit the current `app/streamlit_app_v2.py` Neighborhood
  Explorer flow and identify which components should be preserved for Stoop
  Explore versus removed or de-emphasized.
- [x] `[agent]` Rebrand visible app copy, navigation labels, and page metadata
  from Neighborhood Explorer / Property Explorer language to Stoop Explore.
- [x] `[agent]` Add a lightweight data-read layer for
  `neighborhood_character_mart` so the app consumes pre-computed outputs rather
  than exploratory queries.

### Intelligence MVP

- [x] `[you+agent]` Lock the exact MVP Explore intelligence UI: where `Top
  neighborhoods for X` appears, where `What this neighborhood is known for`
  appears, and what the default selected category should be on first load.
- [x] `[agent]` Add the first MVP intelligence panel to Stoop Explore using
  `neighborhood_character_mart.nta_character_profile`: selected NTA, top
  category, destination categories, strong categories, and lightweight
  supporting counts.
- [x] `[agent]` Add the `Top neighborhoods for X` ranking surface using
  `neighborhood_character_mart.nta_category_density` filtered through
  `nta_category_controls`.
- [x] `[agent]` Surface the enabled Explore category set from
  `nta_category_controls` so category visibility is configuration-backed rather
  than hard-coded in the app.
- [x] `[agent]` Add graceful fallback states for sparse or hidden categories:
  no misleading empty rankings, no fake `"known for"` labels, and clear copy
  when coverage is still limited.
- [x] `[you]` Review the MVP intelligence panel in-app and confirm the outputs
  feel descriptive, playful, and evidence-led rather than over-claimed.

### POI and Map Experience

- [x] `[agent]` Add hotel coverage cleanly to the Explore experience: category
  availability, legend/filter treatment, and any map/panel references needed to
  make hotels feel like a first-class Explore input.
- [x] `[agent]` Review current map layers and category interactions so the app
  feels like a neighborhood-day-out explorer, not a generic POI browser.
- [x] `[agent]` Decide how the selected NTA and selected category interact: map
  click, sidebar ranking, and intelligence panel should feel like one coherent
  flow.
- [x] `[you]` Test the map and panel behavior on a small set of known
  neighborhoods and confirm the interaction model feels intuitive.

### QA and Tuning

- [x] `[agent]` Add a small QA workflow for Explore intelligence outputs:
  enabled categories, threshold behavior, destination-category generation, and
  top-ranking sanity checks.
- [x] `[agent]` Run the Explore validation set after app integration and record
  any regressions between mart output and app rendering.
- [x] `[you+agent]` Do one final Sprint 3 tuning pass limited to copy, category
  visibility, and presentation. Do not reopen the core Sprint 2 ranking logic
  unless a serious bug appears.
- [x] `[you]` Sign off on the public MVP category set and the final `"known
  for"` experience.

### Launch Readiness

- [x] `[agent]` Update supporting docs for the live app: `docs/README.md`,
  `docs/architecture.md`, and `docs/app/neighborhood_explorer_app.md` or its
  replacement so the app and data flow are documented under Stoop Explore.
- [x] `[agent]` Add a short launch note / runbook covering how to rebuild the
  mart, how to refresh curated sources, and what known blind spots remain in the
  public MVP.
- [x] `[agent]` Prepare the Streamlit Cloud deployment path and confirm the app
  boots against committed repo assets and the expected DuckDB inputs.
- [x] `[you]` Smoke-test the deployed app on desktop and mobile before public
  announcement.

### Bars Coverage Expansion (Pre-Launch)

The goal is to add one or more Eater bars articles to `dim_user_poi_v3` before
Stoop Explore V1 goes live, so the `bars` category has credible coverage at
launch. The pipeline already supports Eater articles end-to-end; this is a
run-the-playbook task.

**Step 1 — Register the articles**

- [x] `[you]` Provide the Eater bars article URL(s) to register (e.g. "Best Bars
  in NYC", "Best Wine Bars", etc.).
- [x] `[agent]` Add each article to `config/curated_scrape_articles.yaml` with
  `publisher: Eater`, `parser_name: eater`, `capture_mode: parser`,
  `category: bars`, and the correct `subcategory` and `detail_level_3` values.
  Mark `status: loaded` after successful ingestion.

**Step 2 — Parse and export the normalized CSV**

- [x] `[you]` Save the article HTML locally (or confirm the live URL is
  fetchable).
- [x] `[agent]` Run the export pipeline for each article:
  ```
  python -m nyc_property_finder.pipelines.export_curated_poi_eater_article \
    --article-slug <slug> --html <saved.html>
  ```
  Output lands in `data/raw/scraped/normalized/` as
  `bars_eater_<slug>_<date>.csv`.
- [x] `[you]` Review the normalized CSV: check that venue names, addresses, and
  descriptions look correct before hitting any APIs.

**Step 3 — Resolve place IDs (Google Text Search)**

- [x] `[agent]` Run `ingest_curated_poi_web_scrape` for each article CSV:
  ```
  python -m nyc_property_finder.pipelines.ingest_curated_poi_web_scrape \
    --csv data/raw/scraped/normalized/bars_eater_<slug>_<date>.csv
  ```
  This calls the Google Places Text Search API to resolve each venue to a
  `google_place_id` and writes results to the resolution cache. It also checks
  for canonical duplicates against `dim_user_poi_v2` before making API calls.

**Step 4 — Fetch place metadata (Google Place Details)**

The same `ingest_curated_poi_web_scrape` call above also runs the Place Details
step automatically after resolution — it fetches ratings, business status,
editorial summaries, and coordinates for all newly resolved place IDs, then
merges everything into `stg_user_poi_web_scrape` and rebuilds `dim_user_poi_v2`.

- [x] `[you]` Review the QA output at `data/interim/google_places/web_scrape_qa.csv`
  and the summary at `data/interim/google_places/web_scrape_summary.json`.
  Confirm resolve rate and flag any low-confidence matches before proceeding.

**Step 5 — Classify and promote to `dim_user_poi_v3`**

- [x] `[agent]` Re-run the classification mart to score the new rows:
  ```
  python -m nyc_property_finder.pipelines.build_place_classification_mart
  ```
- [x] `[agent]` Rebuild `dim_user_poi_v3` with the promoted classifications:
  ```
  python -m nyc_property_finder.pipelines.build_curated_poi_v3
  ```
- [x] `[agent]` Rebuild the neighborhood character mart so the new bars coverage
  flows into the intelligence rankings:
  ```
  python -m nyc_property_finder.pipelines.build_neighborhood_character_mart
  ```
- [x] `[you]` Spot-check bars coverage in the Stoop Explore map and intelligence
  panel for 3–4 known neighborhoods (e.g. Williamsburg, LES, East Village)
  before signing off.

Completed 2026-05-12:
- Registered and loaded 6 Eater bars articles from the attached CSV.
- Exported 96 normalized source rows, resolved 96 of 96 rows to Google place IDs, and landed all 96 with coordinates.
- Rebuilt `dim_user_poi_v3` and `neighborhood_character_mart`; bars now total 108 curated places citywide, with East Village, West Village, Williamsburg, Astoria (Central), and Lower East Side surfacing near the top of the bars rankings.

### Launch and Follow-Through

- [ ] `[you+agent]` Draft the public positioning for launch: what Stoop Explore
  is, what question it answers, and what is intentionally still MVP.
- [ ] `[you]` Publish Stoop Explore on Streamlit Cloud.
- [ ] `[you]` Announce on LinkedIn.
- [ ] `[you]` Announce on Reddit.
- [ ] `[you]` Announce on Substack.
- [ ] `[you+agent]` Capture first feedback and turn it into the first post-launch
  backlog slice, especially for category coverage expansion (`bars`, shopping,
  art galleries, bookstores / record stores depth).

---

## Sprint 4 — Full Neighborhood Intelligence Platform

**Goal**: Expand beyond Explore v1 into a full neighborhood intelligence
platform with mature Character, Livability, and Opportunity outputs backed by
durable pre-computed marts and narrative generation logic.

**Outcome**: Stoop has a reusable multi-lens intelligence layer that supports
Explore, Search, and future market expansion.

### Intelligence Platform Foundation

- [ ] `[you+agent]` Define the v1.5/v2 scope for the full platform: which parts
  of Character, Livability, and Opportunity become productized first, and which
  remain future research.
- [ ] `[agent]` Materialize the neighborhood intelligence mart in DuckDB and
  formalize refresh/build steps so the app reads from stable output tables, not
  exploratory queries.
- [ ] `[agent]` Add QA checks for intelligence outputs: category coverage,
  evidence-threshold behavior, percentile sanity, and neighborhood profile
  completeness.
- [ ] `[you+agent]` Define how intelligence outputs should version over time:
  category additions, threshold changes, label changes, and validation signoff.

### Character Platform Expansion

- [ ] `[you+agent]` Expand Character from category rankings into a structured
  label system: dominant label, supporting sublabels, and evidence traces.
- [ ] `[agent]` Build narrative generation rules that turn structured Character
  signals into short neighborhood summaries without relying on a black-box score.
- [ ] `[you]` Review 15 to 20 neighborhood profiles and refine labels that feel
  generic, misleading, or overly data-driven.

### Livability Platform

- [ ] `[you+agent]` Complete the Livability framework using transit, parks,
  grocery, pharmacy, libraries, school quality, and crime context.
- [ ] `[agent]` Build pre-computed livability dimension outputs by NTA with
  explainable components rather than one opaque score.
- [ ] `[you]` Validate livability outputs against known neighborhood patterns
  before surfacing them in Stoop Search.

### Opportunity Platform

- [ ] `[you+agent]` Define the first practical Opportunity story: job access,
  commercial energy, business density, visitor economy, or growth signals.
- [ ] `[agent]` Identify which existing data lanes can support Opportunity now
  and which new source acquisitions would be needed.
- [ ] `[you]` Decide whether Opportunity is a user-facing lens in the next app
  release or remains an internal framework until data quality improves.

### Cross-Product Intelligence

- [ ] `[you+agent]` Define a shared intelligence contract so Explore and Search
  can consume the same NTA-level outputs with different UI framing.
- [ ] `[agent]` Document the full Intelligence Platform architecture: source
  lanes, mart layers, validation workflow, and app-facing outputs.
- [ ] `[you]` Decide when the platform is ready to expand beyond NYC-relative
  comparisons into broader metro or cross-market framing.

### Rebrand and Docs Alignment

- [ ] `[agent]` Rename app entry point from `streamlit_app_v2.py` to
  `app/stoop_explore.py` (or add alias). Update Streamlit Cloud config.
- [ ] `[agent]` Update `docs/architecture.md`, `docs/README.md`,
  `docs/app/neighborhood_explorer_app.md`, and `docs/planning/product_strategy.md`
  to use Stoop Explore naming consistently.
- [ ] `[agent]` Update `docs/data_model.md` "Current App Consumption" table to
  reflect Stoop Explore and Stoop Search as the two primary apps.

### Intelligence Layer

- [ ] `[you+agent]` Design the neighborhood character panel: what fields to show,
  what the "best neighborhoods for X" ranking should look like, how it anchors to
  the primary question.
- [ ] `[agent]` Add neighborhood character summary panel to Stoop Explore:
  dominant POI categories for the selected NTA, top-3 curated places by
  category, key demographic tone (income band, median age).
- [ ] `[agent]` Add "Top neighborhoods for [category]" ranking surface: sidebar
  or panel that ranks NTAs by curated POI density for the currently selected
  category filter.
- [ ] `[agent]` Add hotel POI layer to Stoop Explore once Sprint 1 hotel
  ingestion is complete.

### UX Polish

- [ ] `[you]` Full UX review pass: walk through the "where should I spend
  Saturday in NYC" workflow and note anything broken, confusing, or missing.
- [ ] `[agent]` Implement agreed UX fixes from review.
- [ ] `[you]` Final sign-off before launch.

### Public Launch

- [ ] `[you]` Write LinkedIn post, Reddit post, Substack intro announcing Stoop
  Explore.
- [ ] `[you]` Monitor early feedback and log actionable items.

---

## Sprint 4 — Stoop Search Phase 1

**Goal**: Build a standalone app that answers "is this neighborhood somewhere I
would like to live?" using the livability data from Sprint 1.

**Outcome**: Stoop Search Phase 1 is live with crime, schools, transit, grocery,
and demographic context visible per neighborhood.

### App Foundation

- [ ] `[you+agent]` Design Stoop Search Phase 1: which panels, what the
  neighborhood livability summary looks like, what the comparison view shows.
- [ ] `[agent]` Create `app/stoop_search.py` as a new Streamlit entry point
  sharing the same data product layer as Stoop Explore.
- [ ] `[agent]` Build livability panel per NTA: transit coverage (subway station
  count and lines within walk distance), grocery/pharmacy access, school
  proximity and quality score, crime context.
- [ ] `[agent]` Build neighborhood comparison view: select 2–3 NTAs and compare
  side by side on livability dimensions plus demographic metrics.
- [ ] `[agent]` Add livability scoring or ranking surface so the app helps
  answer "which neighborhoods score well on what I care about?" rather than just
  displaying raw data.

### Demographic Expansion

- [ ] `[agent]` Identify ACS variables for renter-occupied share, vacancy rate,
  population density, and transit commute share. Confirm they are available in
  the existing Metro Deep Dive source.
- [ ] `[you]` Approve the additional ACS metrics before ingestion.
- [ ] `[agent]` Add new metrics to `fct_tract_features`, `fct_nta_features`,
  DDL, pipeline, and QA checks.

### Launch

- [ ] `[you]` Full UX review: walk through "would I like living in Crown
  Heights?" workflow end to end.
- [ ] `[agent]` Implement agreed fixes from review.
- [ ] `[you]` Launch Stoop Search Phase 1.

---

## Sprint 5 — Shortlists MVP

**Goal**: Allow users to save neighborhoods and (eventually) properties with a
data model designed for future sharing.

**Outcome**: Neighborhood shortlist is live in Stoop Search with local
persistence. Property shortlist architecture is designed and ready for Phase 2.

### Design

- [ ] `[you+agent]` Lock the shortlist data model: fields for neighborhood saves
  (nta_id, nta_name, notes, saved_at, status), fields for property saves (to be
  finalized in Sprint 5), and the sharing model design (user identity approach).
- [ ] `[agent]` Remove shortlist UI from current app frontend (Property Explorer
  V1 is already on ice; confirm nothing in Stoop Explore surfaces shortlist
  features).

### Neighborhood Shortlist

- [ ] `[agent]` Add `fct_user_neighborhood_shortlist` table to DDL and data
  model.
- [ ] `[agent]` Implement neighborhood save/archive/note actions in Stoop Search.
- [ ] `[agent]` Add shortlist panel to Stoop Search sidebar: saved neighborhoods
  with notes, quick-compare shortcut.
- [ ] `[you]` Review shortlist UX.

### Sharing Architecture (Design Only)

- [ ] `[you+agent]` Design the user identity model needed for shared shortlists:
  what auth approach (email link, simple passcode, Streamlit auth), what the
  shared shortlist UX looks like, what the backend requirement is.
- [ ] Document the decision in `docs/decision_log.md`. Implementation is
  deferred to a future sprint.

---

## Sprint 6 — Property Listings + Stoop Search Phase 2

**Goal**: Real listing data from StreetEasy and Zillow flowing into Stoop Search
with property-specific intelligence and shortlists.

**Outcome**: Stoop Search Phase 2 shows real listings on the map, price vs. NTA
median, transit from listing, and a working property shortlist.

### Listing Parsers

- [ ] `[you]` Save 10–20 StreetEasy listing HTML pages locally under
  `data/raw/scraped/raw/streeteasy/`.
- [ ] `[you]` Save 10–20 Zillow listing HTML pages locally under
  `data/raw/scraped/raw/zillow/`.
- [ ] `[agent]` Inspect saved StreetEasy HTML and build parser: extract price,
  beds, baths, address, unit, no_fee, available_date, source URL. Normalize into
  `contracts/listing_csv_contract.md`.
- [ ] `[agent]` Inspect saved Zillow HTML and build parser with the same output
  contract.
- [ ] `[agent]` Build CLI entry points: `pipelines/ingest_property_streeteasy.py`
  and `pipelines/ingest_property_zillow.py`.
- [ ] `[you]` Review first normalized listing CSVs for each source before
  running geocoding and DuckDB load.
- [ ] `[agent]` Run parsers end to end: normalize → geocode → load
  `dim_property_listing` → build `fct_property_context`.

### Stoop Search Phase 2 App Layer

- [ ] `[agent]` Add listing map layer to Stoop Search: listing points sized or
  colored by price, filterable by beds and price range.
- [ ] `[agent]` Add listing detail panel: price vs. NTA median rent, subway
  lines within walk, grocery/pharmacy count nearby, curated POI density.
- [ ] `[agent]` Implement property shortlist in Stoop Search: save, archive, add
  notes. Follows the model from Sprint 4.
- [ ] `[you]` Full end-to-end review of Stoop Search Phase 2.
- [ ] `[you]` Launch Stoop Search Phase 2.

---

## Deferred

These are agreed future work items that are out of scope for the current sprints.

| Item | Reason deferred |
| --- | --- |
| Stoop Visit (out-of-town tourist app) | Build after Stoop Explore is live and validated. Needs hotel data and simpler UX. |
| Shared shortlists / user identity | Requires auth backend. Design in Sprint 4, implement when Phase 2 ships. |
| MotherDuck / hosted DuckDB | Not a blocker at current scale. Revisit when data volume or concurrent user load requires it. |
| Public POI refresh cadence + incremental ingest design | New public POI categories should not require rerunning the full `ingest_public_poi` pipeline every time. Decide category-level incremental update path plus a separate cadence for full baseline refreshes of older public POI data. |
| NYTimes Top 100 Restaurants ingest | Paywalled; HTML too large to auto-parse. First use case for the manual CSV upload path (Sprint 1 Crowd / Excel Upload). Ingest once that path is live. |
| Walking-time proximity (vs. straight-line) | Post-Phase 2. Routing API adds complexity. |
| Listing snapshot / price history | Post-Phase 2. Requires repeated scrape runs. |
| Itinerary / day-plan generation | Far future. Ranked POI lists serve the near-term need. |
| Multi-city expansion | After NYC apps are validated and stable. |
