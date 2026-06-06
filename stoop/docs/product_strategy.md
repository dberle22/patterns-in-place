# Stoop NYC — Product Strategy

Last updated: 2026-04-30

Stoop NYC is a suite of data products and apps for understanding New York City
neighborhoods. The platform combines personal editorial curation, open public
data, and demographic context to help two distinct audiences: people exploring
the city and people deciding where to live.

For the active backlog and sprint assignments see `docs/planning/backlog.md`.
For table contracts see `docs/data_model.md`.
For system architecture and pipeline flows see `docs/architecture.md`.

---

## Platform Vision

Most maps show you where things are. Stoop shows you what a neighborhood is
like — its character, its everyday texture, and whether it fits your life. The
platform earns its value from the curation layer on top of public data: personal
Google Maps lists, editorial article scrapes, and crowd contributions that no
generic map product has.

The name reflects that: a stoop is where NYC neighborhood life happens. Local,
intimate, particular.

---

## Data Products

Five data products form the shared foundation. All apps read from the same
underlying tables — they differ in what they surface and how they frame it.

### 1. Curated Places

Personal and editorial place lists normalized into a single clean taxonomy with
Google Places-backed coordinates, ratings, and enrichment.

| | |
| --- | --- |
| Gold table | `property_explorer_gold.dim_user_poi_v2` |
| Staging tables | `stg_user_poi_google_takeout`, `stg_user_poi_web_scrape`, `stg_user_poi_manual_upload` |
| Taxonomy config | `config/poi_categories.yaml` |
| Status | Active — WS1–6 complete. Google Takeout + Eater + Time Out + semi-manual sources (Wanderlog, Michelin, Bon Appetit, NY Mag, Vogue) ingested. Hotels pending. Excel upload (WS7) pending. |

Three ingestion paths feed this product:

- **Google Takeout** — personal saved lists exported from Google Maps, processed
  through resolve → enrich → deduplicate. Entry point:
  `pipelines/ingest_curated_poi_google_takeout.py`
- **Article Scraping** — publication-specific parsers (Eater, Time Out) and
  semi-manual extractors (Wanderlog, Michelin, Bon Appetit, NY Mag, Vogue)
  normalized into a shared CSV contract before Places resolution. Entry point:
  `pipelines/ingest_curated_poi_web_scrape.py`
- **Crowd / Excel Submissions** — shared template for contributor-submitted
  places. Package path reserved at `curated_poi/excel_upload/`. Planned.

All three paths normalize to the same `category / subcategory / detail_level_3`
taxonomy and resolve through Google Places API before writing to the canonical
table. The canonical grain is one row per physical location (Google Place ID).

### 2. City Baseline

Open and official place data for transit, parks, everyday retail, civic
facilities, and public institutions. This product answers coverage questions
objectively: "Is there a subway station within walking distance?"

| | |
| --- | --- |
| Gold table | `property_explorer_gold.dim_public_poi` |
| Status | Complete — 56,540 rows across 27 categories as of 2026-04-23. |
| Entry point | `pipelines/ingest_public_poi.py` |

Categories cover: subway stations, bus stops, Citi Bike, ferry terminals, PATH
stations, bike lanes, parks, playgrounds, dog runs, grocery stores, pharmacies,
laundromats, dry cleaners, banks, ATMs, hardware stores, public libraries, post
offices, public schools, farmers markets, hospitals, urgent care, gyms,
landmarks, historic districts, institutional museums, public art.

Two categories are planned but not yet ingested:

- **Hotels** — OSM or editorial source (Eater/Condé Nast). Needed for Stoop
  Explore and eventually Stoop Visit.
- **Crime** — NYC Open Data. Deferred to date; needed for Stoop Search Phase 1.
- **School quality** — NYC DOE performance data (location already present as
  `public_school`; quality scores are the gap). Needed for Stoop Search Phase 1.

### 3. Neighborhood Context

Census-derived tract and NTA metrics that provide demographic and economic
character for every neighborhood in NYC.

| | |
| --- | --- |
| Gold tables | `property_explorer_gold.fct_tract_features`, `property_explorer_gold.fct_nta_features`, `property_explorer_gold.dim_tract_to_nta` |
| Status | Active — five-borough geography live; full NTA metric coverage partial (87 of 262 NTAs have all metrics). Source: Metro Deep Dive DuckDB. |
| Entry points | `pipelines/build_tract_to_nta.py`, `pipelines/build_neighborhood_features.py` |

Current metrics: median income, median rent, median home value, share with
bachelor's degree or higher, median age.

Planned additions for Stoop Search Phase 1: renter-occupied share, vacancy rate,
population density, transit commute share. These are available from ACS and
strengthen the livability framing without requiring a new source.

### 4. Property Listings

Real estate listings enriched with geography, transit proximity, POI context,
and neighborhood scores.

| | |
| --- | --- |
| Gold tables | `property_explorer_gold.dim_property_listing`, `property_explorer_gold.fct_property_context` |
| Status | Placeholder — 22-row sample for app validation. Real listing ingestion not yet built. |
| Entry points | `pipelines/ingest_property_file.py`, `pipelines/build_property_context.py` |

Two parser targets are planned: StreetEasy saved-listing HTML and Zillow
saved-listing HTML. Both follow the same pattern as article scraping — save pages
locally, run a parser, normalize into the listing CSV contract. No live network
dependency, no ToS exposure at the save-and-parse level.

This product is the core of Stoop Search Phase 2. It is intentionally deferred
until the neighborhood-level intelligence layer (Phase 1) is validated.

### 5. Shortlists

User-authored saves for neighborhoods and properties. Currently a local DuckDB
table (`fct_user_shortlist`). Eventually shareable across users.

| | |
| --- | --- |
| Gold table | `property_explorer_gold.fct_user_shortlist` |
| Status | Partially built — property shortlist exists in Property Explorer V1 (on ice). Neighborhood shortlist not yet built. Sharing requires user identity, which is deferred. |

Two grain levels are planned:

- **Neighborhood shortlists** — saved NTAs, relatively stable, driven by
  personal preference.
- **Property shortlists** — saved listings, time-sensitive as inventory changes.

Sharing requires a user identity layer that does not yet exist. The near-term
path is local persistence in Stoop Search with a designed-for-sharing data model
so the upgrade path is clear when the backend is ready.

---

## Apps

### Stoop Explore

**Primary question**: Where should I spend a day? What's this neighborhood like?

**Audience**: NYC residents, suburban day-trippers, people who know the city and
want to go deeper into neighborhoods they haven't fully explored.

**Data consumed**: Curated Places (primary), City Baseline (secondary), light
Neighborhood Context (character framing).

**Core experience**:
- Five-borough map with NTA neighborhood boundaries
- Curated POI layer: restaurants, bars, coffee, music venues, bookstores, record
  stores, museums, shopping, hotels
- City Baseline layer: parks, subway stations, Citi Bike, landmarks
- Neighborhood character panel: dominant POI categories, demographic character,
  top-ranked places
- Intelligence surface: "Best neighborhoods for X" ranking by selected POI
  category density

**Not in scope**: crime, school quality, listing prices, commute analysis.

**Status**: Active development. Current app (`app/streamlit_app_v2.py`) is a
strong foundation. Needs rebranding, intelligence panel, hotel category, and UX
reframe around the primary question before public launch.

---

### Stoop Search

**Primary question**: Is this neighborhood somewhere I'd like to live? (Phase 1)
Does this specific listing work for my life? (Phase 2)

**Audience**: People evaluating NYC neighborhoods for a move — either broadly
prioritizing areas (Phase 1) or assessing specific properties (Phase 2).

**Data consumed**:
- Phase 1: Neighborhood Context (primary), City Baseline — livability signals
  (grocery, pharmacy, transit, schools, crime), some Curated Places.
- Phase 2: adds Property Listings, Shortlists.

**Core experience (Phase 1)**:
- Neighborhood map with NTA boundaries and demographic overlays
- Livability panel: transit coverage, grocery/pharmacy access, school
  quality/proximity, crime context
- Neighborhood comparison view: put two or three NTAs side by side on key
  dimensions
- "Does this neighborhood fit my lifestyle?" intelligence framing

**Core experience (Phase 2)**:
- Listing layer on the map
- Property cards: price vs. NTA median rent, transit from listing, nearby POI
  summary
- Property shortlist with local persistence
- "Is this listing in a neighborhood that fits my life?" synthesis view

**Status**: Not yet started as a standalone app. Phase 1 is buildable now with
existing data plus crime and school quality additions. Phase 2 requires the
Property Listings data product.

---

### Stoop Visit (Future)

**Primary question**: I'm visiting NYC from out of town — where should I stay
and what should I do?

**Audience**: Tourists with no prior NYC context.

**Data consumed**: City Baseline (hotels, transit, landmarks), Curated Places
(top-tier editorial picks), light Neighborhood Context.

**Status**: Deferred. Build after Stoop Explore is live and validated. Requires
a hotel data source and a simplified UX for users who don't know the borough
structure.

---

## Product Dependency Map

```
Data Products                    Apps

Curated Places   ─────────────► Stoop Explore  (tourist/local explorer)
City Baseline    ─────────────► Stoop Explore
City Baseline    ────────────────────────────► Stoop Search  (neighborhood + property)
Neighborhood Context ───────────────────────► Stoop Search
Curated Places   ────────────────────────────► Stoop Search
Property Listings ──────────────────────────► Stoop Search (Phase 2)
Shortlists       ────────────────────────────► Stoop Search (Phase 2)

All three data products ────────────────────► Stoop Visit  (future)
```

---

## Deployment

Both Stoop Explore and Stoop Search will be deployed on Streamlit Community
Cloud. The DuckDB file is committed to the repository and loaded at app startup.
This is sufficient for the current data scale and launch phase.

Long-term scaling path (when data volume or concurrent users require it):
- Move to MotherDuck as a hosted DuckDB backend
- Introduce a lightweight backend service for shortlist writes when sharing is
  needed
- User identity layer (auth) is a prerequisite for shared shortlists; defer
  until Phase 2 of Stoop Search is ready to ship

---

## What This Platform Is Not

- A real-time listing scraper or automated feed. Listing ingestion is
  intentionally manual-first (save pages, run parser).
- A routing or turn-by-turn navigation tool. Proximity is straight-line for
  MVP; walking-time proxies are post-Phase 2.
- A review aggregator. Ratings come from Google Places as a signal, not as the
  primary surface.
- A crime or safety scoring app. Crime context will be added as one livability
  signal among many, not as a headline feature.
