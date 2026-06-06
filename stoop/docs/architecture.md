# Architecture

Stoop Explore is the active neighborhood discovery surface in this local NYC
property and place research tool. It combines demographic neighborhood
context, baseline public amenity data, curated places, and property listings
into a single DuckDB database that powers two Streamlit apps.

The system has three layers: a **Data Platform** (what data we have and where
it lives), **Pipelines** (how raw sources become app-ready tables), and
**Frontend Applications** (what the user sees).

For table-level contracts use `docs/data_model.md`. For the operational build
runbook use `docs/pipeline_plan.md`. For POI category definitions and ingestion
status use `docs/poi_categories.md`.

---

## Data Platform

Four data domains each write into `property_explorer_gold` in DuckDB. The
database lives at `data/processed/nyc_property_finder.duckdb` (local only,
not committed).

### Foundational Demographics

Census tract and NTA (Neighborhood Tabulation Area) geometry and metrics.
This is the base layer for all neighborhood comparisons and property context.

| Table | Contents |
| --- | --- |
| `dim_tract_to_nta` | Crosswalk from census tract GEOID to NTA name and ID |
| `fct_tract_features` | Tract-level metrics: income, rent, home value, education, age |
| `fct_nta_features` | NTA-level aggregated metrics plus neighborhood-native metadata (`borough`, `tract_count`) |

Geometry (census tracts, NTA boundaries) is loaded at runtime from
`data/raw/geography/` and is not stored as a DuckDB table.

Status: active. Current coverage is all five boroughs. The tract geometry file
now contains 2,325 tract shapes, while the current feature tables materialize
2,327 tract rows and 262 NTA rows from Metro Deep Dive. That small tract count
mismatch is expected because the shoreline-clipped tract geometry excludes a
couple of water-only feature rows. Source: Metro Deep Dive DuckDB, path
configured in local-only `config/data_sources.yaml`.

### Public POI Baseline

Official and open-source place data for transit, parks, everyday retail, civic
facilities, and cultural institutions. This tier answers coverage questions:
"Is there a grocery store within 10 minutes?" rather than "Is it a good one?"

| Table | Contents |
| --- | --- |
| `dim_public_poi` | 56,540 rows across 27 categories, all with coordinates |

Status: complete. All 5 ingestion waves finished 2026-04-23. See
`docs/poi_categories.md` for the full category list, source datasets, and row
counts.

### Curated POI

Personal, taste-driven place lists — bookstores, record stores, restaurants,
bars, music venues, etc. This tier answers curation questions: "Is there a
great natural wine bar nearby?" Sources are personal Google Maps saved lists,
editorial article scrapes, and crowd-sourced Excel uploads.

| Table | Contents |
| --- | --- |
| `dim_user_poi_v2` | Curated POIs with Google Places-backed coordinates plus category, subcategory, and flexible descriptor tags |

Status: active development. Three legacy categories loaded (37 bookstores, 29
record stores, 25 museums). Fifteen new `poi_nyc/` CSVs are raw and pending
ingestion on the `curated-poi-ingestion` branch. Scraping and Excel upload
paths are planned but not yet built. See `docs/poi_categories.md` for full
status.

### Real Estate Listings

Property listings with price, beds, baths, address, and source URL, enriched
with tract/NTA assignment, subway distance, nearby POI counts, and a composite
score.

| Table | Contents |
| --- | --- |
| `dim_property_listing` | Property listings with coordinates |
| `fct_property_context` | Listings joined to geography, transit, POIs, and scores |

Status: placeholder. A minimal 22-row sample exists for app validation.
Scraping adapters for StreetEasy and RentHop are scaffolded but not yet built.
Manual CSV ingestion is the current working path.

---

## Pipelines

Pipelines read from `data/raw/` and write app-ready tables to DuckDB. Each
subject area below has its own ingestion concerns and refresh cadence.

`init_database` must run first on any new machine to create DuckDB schemas and
tables:

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.init_database
```

See `docs/pipeline_plan.md` for the full build order and commands.

### Demographic Data Foundations

Builds the geography crosswalk and tract/NTA metrics that underpin all
neighborhood context.

| Step | Script | Status | Output |
| --- | --- | --- | --- |
| Tract-to-NTA mapping | `pipelines/build_tract_to_nta.py` | active | `dim_tract_to_nta` |
| Neighborhood features | `pipelines/build_neighborhood_features.py` | active | `fct_tract_features`, `fct_nta_features` |

Raw inputs: `data/raw/geography/tract_to_nta_equivalency.csv`,
`data/raw/geography/census_tracts.geojson`, Metro Deep Dive DuckDB (local path
in `config/data_sources.yaml`).

### Public POI

A single pipeline entry point (`ingest_public_poi`) runs all source modules in
wave order and replaces `dim_public_poi` on each full run. Source modules live
in `src/nyc_property_finder/public_poi/sources/`. Snapshots are dated files
under `data/raw/public_poi/`; today's files are reused if they exist.

| Wave | Categories | Source modules | Status |
| --- | --- | --- | --- |
| 1 — Transit | subway stations/lines, bus stops, Citi Bike, ferry terminals, PATH stations, bike lanes | `mta_subway.py`, `mta_bus.py`, `gbfs_citibike.py`, `ferry_path.py`, `nyc_open_data.py` | complete |
| 2 — Parks & Recreation | parks, playgrounds, dog runs | `nyc_open_data.py` | complete |
| 3 — Everyday Retail | grocery stores, pharmacies, laundromats, dry cleaners, banks, ATMs, hardware stores | `nyc_open_data.py`, `osm.py` | complete |
| 4 — Civic & Community | public libraries (NYPL/BPL/QPL), post offices, public schools, farmers markets, hospitals, urgent care, gyms | `nypl_api.py`, `nyc_open_data.py`, `osm.py` | complete |
| 5 — Culture & Heritage | landmarks, historic districts, institutional museums, public art | `nyc_open_data.py` | complete |

Entry point: `pipelines/ingest_public_poi.py`

### Curated POI

Curated POI code now lives under `src/nyc_property_finder/curated_poi/`.
Each ingestion path gets its own subpackage, while `public_poi/` remains a
separate baseline-data system. All curated paths are expected to normalize into
the same taxonomy contract and write to `dim_user_poi_v2`.

Current curated package layout:

| Package | Purpose | Status |
| --- | --- | --- |
| `curated_poi/google_takeout/` | Google Takeout saved-list ingestion, cache-first Places resolution, dry-run planning, and `dim_user_poi_v2` build | active |
| `curated_poi/web_scraping/` | Editorial article extraction and normalization into curated POI inputs, organized by publication | active scaffold |
| `curated_poi/excel_upload/` | Shared Excel or CSV submission workflow into curated POI inputs | planned |
| `curated_poi/shared/` | Shared helpers meant to be reused across curated POI source paths | reserved |

#### Google Takeout (active)

Personal Google Maps saved lists exported via Google Takeout, processed through
a resolve → enrich → deduplicate pipeline.

Raw files: `data/raw/google_maps/poi_nyc/poi_<category>_nyc.csv`

| Step | Script | Status |
| --- | --- | --- |
| Parse Takeout CSVs | `curated_poi/google_takeout/parse_takeout.py` | active |
| Resolve to Place IDs | `curated_poi/google_takeout/resolve.py` | active — cache-first, API call caps |
| Enrich with details | `curated_poi/google_takeout/enrich.py` | active |
| Dry-run planning | `curated_poi/google_takeout/dry_run.py` | active |
| Write `dim_user_poi_v2` | `curated_poi/google_takeout/build_dim.py` | active |

Primary entry point: `pipelines/ingest_curated_poi_google_takeout.py`

Compatibility alias: `pipelines/ingest_google_places_poi.py`

#### Article Scraping (active scaffold)

Identify editorial articles (Eater NYC maps, NYT lists, Pitchfork guides, etc.)
and extract place name + metadata via publication-specific scrapers or a
semi-manual fallback for one-off articles. The locked design is file-first:
capture raw article output locally, normalize it into a shared CSV contract,
review it, then feed it into the same Places resolve/enrich flow used by
Google Takeout.

Package shape:

```text
src/nyc_property_finder/curated_poi/web_scraping/
  base.py
  normalize.py
  registry.py
  publications/
    eater.py
```

Supporting config:

```text
config/curated_scrape_articles.yaml
```

Current first implemented slice:

- locked Eater article registry
- config-backed article inventory and status tracker
- local HTML or live URL export workflow for Eater
- normalized CSV writer for QA review
- publication-specific parser contract under `publications/`
- no staging-table writer yet

Recommended capture modes:

- `parser`: structured publication-specific extraction
- `semi_manual`: save page text or HTML locally, then run a lightweight extractor
- `manual_seed`: hand-enter a normalized CSV when the source is low-volume or awkward

Recommended file flow:

```text
article html/text
  -> data/raw/scraped/raw/<publication>/<slug>_<date>.{html,txt,json}
  -> data/raw/scraped/normalized/<category>_<publication>_<slug>_<date>.csv
  -> property_explorer_gold.stg_user_poi_web_scrape
  -> property_explorer_gold.dim_user_poi_v2
```

Normalized scrape rows should preserve enough metadata to support QA and strong
Places matching. The minimum shared fields are:

- `publisher`
- `article_title`
- `article_url`
- `source_list_name`
- `item_rank`
- `item_name`
- `item_url`
- `raw_address`
- `raw_description`
- `raw_neighborhood`
- `raw_borough`
- `category`
- `subcategory`
- `detail_level_3`
- `scraped_at`

Normalization rules:

- split multi-address mentions into distinct source rows before Places resolution
- treat `item_name + raw_address` as the pre-resolution location grain
- derive `category` and `subcategory` from article identity first
- use description keywords only as fallback taxonomy hints
- use Google Places metadata later for resolution and enrichment, not as the
  primary taxonomy source

Current entry point:

`pipelines/export_curated_poi_eater_article.py`

Status: first Eater publication scaffold is built for raw HTML or live URL
capture into normalized CSVs. Downstream staging-table write and canonical
merge work remain future tasks. See `docs/poi_categories.md` for the
publication-organized target article list and taxonomy mapping.

#### Public Excel Upload (planned)

A shared Excel/CSV template where collaborators can submit places. Output
normalized to `data/raw/public_submissions/` and fed into the resolve/enrich
step.

Status: package path reserved at `curated_poi/excel_upload/`, implementation
not yet built.

### Properties

Two ingestion paths and one enrichment step feed the property tables.

#### Manual CSV (active — placeholder)

Hand-curated listings CSV ingested directly into `dim_property_listing`.

| Step | Script | Status |
| --- | --- | --- |
| Ingest listing file | `pipelines/ingest_property_file.py` | active — minimal 22-row sample |

Raw input: `data/raw/listings_sample.csv`

#### Scraping (planned)

Source-specific adapters for StreetEasy and RentHop. Scripts are scaffolded but
not built. Legal/terms review required before implementation.

| Step | Script | Status |
| --- | --- | --- |
| StreetEasy adapter | `pipelines/ingest_property_streeteasy.py` | planned — not built |
| RentHop adapter | `pipelines/ingest_property_renthop.py` | planned — not built |

#### Property Context Enrichment (active)

Joins listings to geography, transit, POIs, and neighborhood metrics to produce
the scored context table.

| Step | Script | Status |
| --- | --- | --- |
| Build property context | `pipelines/build_property_context.py` | active |

Output: `fct_property_context`

---

## Frontend Applications

### Stoop Explore — main focus

Interactive map for browsing NYC neighborhoods through curated place signals,
ranking intelligence, and supporting demographic context.

| | |
| --- | --- |
| Entry point | `app/stoop_explore.py` |
| Core logic | `src/nyc_property_finder/app/base_map.py` |
| Data consumed | `fct_tract_features`, `fct_nta_features`, `dim_user_poi_v2`, `dim_public_poi`, `neighborhood_character_mart.nta_category_controls`, `neighborhood_character_mart.nta_category_density`, `neighborhood_character_mart.nta_character_profile` |
| Review | `docs/neighborhood_explorer_app_review.md` |

Current capabilities: tract and NTA geography across all five boroughs,
selectable context metrics, curated and public POI overlays, an above-the-map
Explore intelligence panel, configuration-backed category visibility,
selected-neighborhood highlight behavior, and explicit missing-data handling.
Public POIs are kept off on first load and lazy-loaded when the toggle is
enabled so the initial map draw stays focused on curated places.

Current coverage is all five boroughs. The default app state is neighborhood
geography, curated POIs on, public POIs off, `restaurants` as the first Explore
category, and `subway_station` as the initial public overlay category once
enabled.

Recent performance refactor: the expensive tract/NTA geometry assembly is now
cached separately from metric-specific formatting, so metric switches are fast
after the first geography load. A timing pass on 2026-04-28 showed roughly
`1.37s` for the shared geography load, `0.04s` for a metric rebuild from that
cached geography object, `0.07s` for curated POI loading, and `0.06s` for a
single-category public POI load.

### Neighborhood QA App

Companion tool for reviewing data coverage: tract and NTA metric gaps, POI
counts, build state. Not user-facing.

| | |
| --- | --- |
| Entry point | `app/neighborhood_qa_app.py` |

### Property Search Helper V1 — on ice

Original property listing explorer with map, filters, and shortlist. Paused
while V2 is the development focus.

| | |
| --- | --- |
| Entry point | `app/streamlit_app.py` |
| Core logic | `src/nyc_property_finder/app/explorer.py` |

---

## Stack

- **Database**: DuckDB (`property_explorer_gold` schema)
- **Spatial operations**: GeoPandas / Shapely; results stored as WKT in DuckDB
- **Pipelines**: Python, under `src/nyc_property_finder/`
- **Frontend**: Streamlit + PyDeck
- **POI resolution**: Google Places API v2 (Text Search + Place Details), cache-first
