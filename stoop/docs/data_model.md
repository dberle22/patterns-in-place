# Data Model Contracts

This document is the data contract for the MVP DuckDB
`property_explorer_gold` layer.
The contracts are intentionally decision-ready: confirmed choices are separated
from open questions so schema changes can follow review instead of drifting into
the app by accident.

## Property Explorer Gold Layer Principles

- Property Explorer gold tables are app-facing product interfaces.
- Raw exports stay under `data/raw` and should not be checked in.
- Geometry is stored as WKT in DuckDB for the starter version; active spatial
  logic runs in GeoPandas/Shapely.
- Table rebuilds are replace-first for MVP unless a table explicitly says it is
  user-authored.
- Crime and safety metrics are deferred until there is a stronger source and
  product framing.

## How This Doc Fits With The Build

Use this document as the product-facing contract for DuckDB tables in
`property_explorer_gold`. It should answer three questions for each table:

- What is the grain and primary key?
- Which raw or upstream source owns the values?
- Which build entrypoint writes the table for the app?

`docs/source_inventory.md` remains the longer source notebook: external URLs,
source decisions, local path conventions, caveats, and open source questions
belong there. The compact manifest below pulls the MVP source inventory into
this contract so a reader can move from app surface to table to source to build
script without bouncing across several files.

## MVP Source And Build Manifest

| Product area | Source inventory entry | Local/default source path | Gold table(s) | Build entrypoint |
| --- | --- | --- | --- | --- |
| Database schema | DDL | `sql/ddl/001_gold_tables.sql`, `sql/ddl/002_public_poi_table.sql` | All `property_explorer_gold` tables | `src/nyc_property_finder/pipelines/init_database.py` |
| Tract/NTA mapping | Tract-to-NTA equivalency | `data/raw/geography/tract_to_nta_equivalency.csv` | `dim_tract_to_nta` | `src/nyc_property_finder/pipelines/build_tract_to_nta.py` via `run_equivalency()` |
| Tract geometry | Census tract boundaries | `data/raw/geography/census_tracts.geojson` | App geometry input; optional `geometry_wkt` QA | Read by `src/nyc_property_finder/app/base_map.py` and `build_property_context.py` |
| Neighborhood geometry | NYC NTA boundaries | `data/raw/geography/nta_boundaries.geojson` | Fallback mapping source | `src/nyc_property_finder/pipelines/build_tract_to_nta.py` via centroid fallback `run()` |
| Subway stops | MTA static GTFS or normalized stops CSV | `data/raw/transit/gtfs_subway.zip` or `data/raw/transit/subway_stops.csv` | `dim_subway_stop` | `src/nyc_property_finder/pipelines/ingest_subway_stops.py` |
| Public POI baseline | NYC Open Data, MTA GTFS, OSM, GBFS, NYPL API | `data/raw/public_poi/` (dated snapshots per source) | `dim_public_poi` | `src/nyc_property_finder/pipelines/ingest_public_poi.py` |
| Curated POIs | Google Maps Takeout CSVs, resolved via Google Places API | `data/raw/google_maps/poi_nyc/` | `dim_user_poi_v2` | `src/nyc_property_finder/pipelines/ingest_curated_poi_google_takeout.py` |
| Listing geocodes | Address geocoding cache/quarantine | `data/interim/geocoding/listing_geocodes.csv` | Inputs to `dim_property_listing` | `src/nyc_property_finder/services/geosearch.py` through `ingest_property_file.py` |
| Property listings | Manual listing CSV/JSON | `data/raw/listings_sample.csv`; future default `data/raw/property_listings.csv` | `dim_property_listing` | `src/nyc_property_finder/pipelines/ingest_property_file.py` |
| Tract/NTA features | Metro Deep Dive tract features | configured in ignored `config/data_sources.yaml` | `fct_tract_features`, `fct_nta_features` | `src/nyc_property_finder/pipelines/build_neighborhood_features.py` via `run_metro_deep_dive()` |
| Property context | Gold dimensions and facts plus tract geometry | DuckDB plus `data/raw/geography/census_tracts.geojson` | `fct_property_context` | `src/nyc_property_finder/pipelines/build_property_context.py` |
| Shortlist | Streamlit user actions | DuckDB local table | `fct_user_shortlist` | `src/nyc_property_finder/app/explorer.py` helpers used by `app/streamlit_app.py` |

Source configuration should live in `config/data_sources.yaml`, created from
`config/data_sources.example.yaml` for local paths and private source database
locations. App defaults live in `config/settings.yaml`.

## Current App Consumption

The current Streamlit surface has two app layers:

| App | Code | Required data | Current purpose |
| --- | --- | --- | --- |
| Stoop Explore (main focus) | `app/stoop_explore.py`, `app/streamlit_app_v2.py`, `src/nyc_property_finder/app/base_map.py`, `src/nyc_property_finder/app/stoop_explore.py` | `dim_tract_to_nta`, `fct_tract_features`, `fct_nta_features`, `dim_user_poi_v2`, `dim_public_poi`, `neighborhood_character_mart.nta_category_controls`, `neighborhood_character_mart.nta_category_density`, `neighborhood_character_mart.nta_character_profile`, and `data/raw/geography/census_tracts.geojson` | Five-borough neighborhood explorer with curated/public POI overlays, configuration-backed category intelligence, and supporting demographic/context review. |
| Neighborhood Data QA | `app/neighborhood_qa_app.py`, `src/nyc_property_finder/app/neighborhood_qa.py` | `dim_tract_to_nta`, `fct_tract_features`, `fct_nta_features`, `dim_user_poi_v2`, `dim_public_poi`, curated staging tables, and configured source paths | QA surface for table readiness, demographic coverage, curated/public POI inventory coverage, and freshness/source-path status. |
| Property Explorer V1 (on ice) | `app/streamlit_app.py`, `src/nyc_property_finder/app/explorer.py` | `fct_property_context`, `dim_user_poi_v2`, `dim_subway_stop`, `fct_nta_features`, `fct_user_shortlist` | Listing map/list/detail workflow, score filters, POI/subway overlays, and local shortlist persistence. Paused while V2 is the active development focus. |

Stoop Explore is intentionally evidence-led: it can render boundaries even when
demographic metric values are null, while neighborhood character claims come
from the precomputed `neighborhood_character_mart` instead of runtime analysis.
Neighborhood Data QA owns metric coverage and source-readiness review so
missing Metro Deep Dive values stay visible outside the main exploration
surface.

## Contract And DDL Change Checklist

`docs/data_model.md` is the table contract, while `sql/ddl/001_gold_tables.sql`
is the executable starter schema. When a gold table contract changes, update
the following in the same workstream:

1. Update the table section in this document, including grain, source, required
   columns, validation, and downstream uses.
2. Update `sql/ddl/001_gold_tables.sql` when a persisted gold column or table
   changes.
3. Update the writing pipeline under `src/nyc_property_finder/pipelines/` or
   the relevant transform under `src/nyc_property_finder/transforms/`.
4. Update app-facing helpers under `src/nyc_property_finder/app/` when the app
   reads, filters, sorts, or displays the changed field.
5. Update focused tests under `tests/`, especially `tests/test_schema.py` for
   table shape and the pipeline/app tests listed in the QA matrix below.
6. Update `docs/source_inventory.md` when the change introduces a new source,
   URL, path, owner, caveat, or deferred-source decision.
7. Update `docs/pipeline_plan.md` when the change alters build order, command
   shape, or required local inputs.

## Table QA Matrix

| Table or artifact | Contract owner | DDL owner | Build owner | Primary QA checks | Focused tests |
| --- | --- | --- | --- | --- | --- |
| `dim_property_listing` | This doc, listing contract | `sql/ddl/001_gold_tables.sql` | `ingest_property_file.py`, listing transforms, geocoding service | Required fields populated after geocoding; positive prices; valid listing types; NYC coordinate bounds; duplicate `property_id` collapsed. | `tests/test_property_file_ingestion.py`, `tests/test_geosearch.py`, `tests/test_schema.py` |
| `dim_tract_to_nta` | This doc, geography source notes | `sql/ddl/001_gold_tables.sql` | `build_tract_to_nta.py`, geography transforms | One row per tract; NTA ID/name present; Manhattan/Brooklyn coverage; unmapped tracts are zero or explained. | `tests/test_tract_to_nta.py`, `tests/test_geo.py`, `tests/test_schema.py` |
| `dim_subway_stop` | This doc, transit source notes | `sql/ddl/001_gold_tables.sql` | `ingest_subway_stops.py`, transit transforms | Stop IDs unique; stop name present; coordinates in NYC bounds; GTFS route lines preserved enough for display/counts. | `tests/test_subway_ingestion.py`, `tests/test_schema.py` |
| `dim_public_poi` | This doc, `docs/poi_categories.md` | `sql/ddl/002_public_poi_table.sql` | `ingest_public_poi.py`, public_poi source modules | 27 categories present; all rows have coordinates in NYC bounds; `poi_id` unique; `snapshotted_at` populated. | `tests/test_public_poi_pipeline.py`, `tests/test_schema.py` |
| `dim_user_poi_v2` | This doc, `docs/poi_categories.md` | `sql/ddl/001_gold_tables.sql` | `ingest_curated_poi_google_takeout.py`, `curated_poi/google_takeout` package | POI IDs stable; names present; category/subcategory taxonomy preserved; all rows have Google Place ID and coordinates; private exports stay local. | `tests/test_poi_parsing.py`, `tests/test_schema.py` |
| `fct_tract_features` | This doc, Metro Deep Dive source notes | `sql/ddl/001_gold_tables.sql` | `build_neighborhood_features.py`, `sql/gold/fct_tract_features.sql` | Tract IDs join to mapping; percent scale documented; null metrics are explicit and do not produce precise-looking scores. | `tests/test_neighborhood_features.py`, `tests/test_base_map_app.py`, `tests/test_schema.py` |
| `fct_nta_features` | This doc, Metro Deep Dive source notes | `sql/ddl/001_gold_tables.sql` | `build_neighborhood_features.py`, `sql/gold/fct_nta_features.sql` | One row per NTA; `borough` and `tract_count` populated; aggregation method documented; names present; null metric coverage visible in Neighborhood Data QA. | `tests/test_neighborhood_features.py`, `tests/test_base_map_app.py`, `tests/test_schema.py` |
| `fct_property_context` | This doc, scoring config | `sql/ddl/001_gold_tables.sql` | `build_property_context.py`, scoring transforms | Context row count matches listings; tract/NTA joins valid; subway distance non-negative; POI JSON valid; scores are null for documented reasons or `0-100`. | `tests/test_property_context_pipeline.py`, `tests/test_property_explorer_app.py`, `tests/test_schema.py` |
| `fct_user_shortlist` | This doc, app helper contract | `sql/ddl/001_gold_tables.sql` | `src/nyc_property_finder/app/explorer.py`, Streamlit actions | One current row per `user_id`/`property_id`; controlled status values; rebuilds do not replace user-authored rows. | `tests/test_property_explorer_app.py`, `tests/test_schema.py` |
| Stoop Explore app artifact | `docs/app/neighborhood_explorer_app.md`, this doc | N/A | `app/stoop_explore.py`, `app/streamlit_app_v2.py`, `src/nyc_property_finder/app/base_map.py`, `src/nyc_property_finder/app/stoop_explore.py` | Five-borough boundaries render with or without metric values; the right-side Explore intelligence panel reads from the mart; category-backed rankings, selected-neighborhood highlight, and POI layer toggles work. | `tests/test_base_map_app.py`, `tests/test_stoop_explore.py` |
| Neighborhood Data QA app artifact | `docs/app/neighborhood_explorer_app.md`, this doc | N/A | `app/neighborhood_qa_app.py`, `src/nyc_property_finder/app/neighborhood_qa.py` | Table readiness, metric coverage, curated/public POI inventory coverage, and freshness/source-path status are visible outside the explorer. | `tests/test_neighborhood_qa.py` |

## MVP Table Status

| Table | MVP Status | Notes |
| --- | --- | --- |
| `property_explorer_gold.dim_property_listing` | Required | Manual CSV/JSON is the current source path. |
| `property_explorer_gold.dim_tract_to_nta` | Required | NTA is the UI neighborhood language; tracts support ACS features. |
| `property_explorer_gold.dim_subway_stop` | Active (legacy) | Supports nearest stop and mobility score. Subway stations also in `dim_public_poi`; these two tables serve different purposes. |
| `property_explorer_gold.dim_public_poi` | Active — complete | 56,540 rows across 27 categories as of 2026-04-23. See `docs/poi_categories.md`. |
| `property_explorer_gold.dim_user_poi_v2` | Active | Curated POIs normalized through the new category/subcategory/descriptor model. Legacy rows exist for bookstores, record stores, and museums; the full `poi_nyc/` directory is ready for WS2 batch loading. |
| `property_explorer_gold.fct_tract_features` | Required | Metro Deep Dive-derived tract metrics. Crime is deferred. |
| `property_explorer_gold.fct_nta_features` | Required | Materialized NTA summaries for panels, filters, and neighborhood-first map/tooltips. |
| `property_explorer_gold.fct_property_context` | Required | App-ready enriched listing rows and score components. |
| `property_explorer_gold.fct_user_shortlist` | Required | Persisted local saves and notes. App helpers own user-authored rows. |
| Listing snapshot/history table | Deferred | `active` on listings is enough for now. |
| Amenity bridge table | Deferred | Keep `amenities` as optional JSON/text for first pass. |
| Listing images/media table | Deferred | Source URL is enough for now. |

## `property_explorer_gold.dim_property_listing`

Grain: one normalized listing record per `property_id`. MVP queries should
default to `active = true`, but inactive records may remain for review.

Primary key: `property_id`.

Refresh behavior: replace from the current manual listing file for MVP, with
`active` indicating whether the listing is present/current in the latest input.
If multiple rows produce the same `property_id`, keep the latest row by
`source_updated_at` when available, otherwise the latest ingested row.

Source: manual listing CSV or JSON under `data/raw/property_listings.csv`.
StreetEasy and Zillow are the first expected manual source workflows. Future
adapters should normalize into the same contract.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `property_id` | string | no | Stable internal ID generated from source/source ID/address/coordinates unless provided. |
| `source` | string | no | File label or provider, for example `manual_csv`, `streeteasy_saved`, `renthop_export`. |
| `source_listing_id` | string | yes | Source-native ID when available. Strongly preferred for dedupe. |
| `address` | string | no | Display address or source title if exact address is unavailable. |
| `lat` | double | no | WGS84 latitude after any geocoding step. |
| `lon` | double | no | WGS84 longitude after any geocoding step. |
| `price` | double | no | Monthly rent for rentals; asking price for sales. USD. |
| `beds` | double | no | Studio can be `0`. |
| `baths` | double | no | Supports half baths. |
| `listing_type` | string | no | Controlled values: `rental`, `sale`. |
| `active` | boolean | no | True when current in the latest source refresh/file. |
| `url` | string | yes | Source listing URL. |
| `ingest_timestamp` | timestamp | no | UTC timestamp when normalized into the local DB. |

Recommended columns for the first app detail/card:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `neighborhood_label` | string | yes | Source-provided neighborhood, separate from computed NTA. |
| `borough` | string | yes | Source-provided or geography-derived. |
| `unit` | string | yes | Apartment/unit label. |
| `sqft` | double | yes | Interior square footage. |
| `available_date` | date | yes | Rental availability or listing availability date. |
| `no_fee` | boolean | yes | Important rental affordability field. Required for rental CSV rows, nullable for sales. |
| `broker_fee` | string | yes | Amount, percent, or free-text if source is inconsistent. |
| `amenities` | string | yes | JSON array text or delimiter-separated list. |
| `description` | string | yes | Short source description for detail/search. |
| `source_updated_at` | timestamp | yes | Source listing updated/listed timestamp when available. |
| `coordinate_quality` | string | yes | Proposed values: `exact_address`, `approximate`, `geocoded`, `source_provided`, `unknown`. |
| `geocoded_from_address` | boolean | yes | True when missing coordinates were filled by address geocoding. |
| `geocode_source` | string | yes | Source used to create coordinates, such as `nyc_geosearch`, `nyc_geoclient`, or `manual`. |

Validation:

- `listing_type` must be `rental` or `sale`.
- Rental rows should include `no_fee`; sale rows may leave it null.
- `price` must be positive.
- `beds` and `baths` must be non-negative.
- Raw listing rows may omit coordinates when a valid address is present, but
  `lat` and `lon` must be populated before writing `property_explorer_gold.dim_property_listing`.
- Rows that cannot be geocoded should be quarantined rather than silently
  loaded into map/scoring paths.
- Approximate coordinates are acceptable in MVP when exact coordinates are not
  available, but coordinate quality should be visible for QA.
- `lat` should be between `40.45` and `40.95`; `lon` should be between `-74.30`
  and `-73.65` for the NYC MVP coverage.
- `url` should be present for real manually collected records.
- `active` defaults to `true` for rows in the manual file.

Downstream app uses: listing cards, map markers, filters, selected property
detail, source link, shortlist joins, property context build.

## `property_explorer_gold.dim_tract_to_nta`

Grain: one census tract assignment to one NTA.

Primary key: `tract_id`.

Refresh behavior: replace when geography source files change.

Source priority: use a tabular tract-to-NTA equivalency source first, preferably
NYC Open Data's 2020 Census Tracts to 2020 NTAs and CDTAs Equivalency dataset.
Use tract and NTA geometries under `data/raw/geography/` for QA, fallback
assignment, and map boundaries.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `tract_id` | string | no | Full tract GEOID preferred. |
| `nta_id` | string | no | NYC NTA code. |
| `nta_name` | string | no | Display label for the app. |
| `borough` | string | yes | Borough label or code when provided by the source. |
| `cdta_id` | string | yes | Community District Tabulation Area ID when provided by the source. |
| `cdta_name` | string | yes | CDTA name when provided by the source. |
| `geometry_wkt` | string | yes | Tract geometry WKT for QA/debug if geometries are loaded. |

Assignment rule proposal: prefer the official/source-provided equivalency table.
If an equivalency row is missing or the source cannot be loaded, fall back to a
documented geospatial assignment. Centroid assignment is the simplest fallback;
largest-intersection can replace it if QA finds boundary misses.

QA checks:

- Every loaded tract has one and only one NTA assignment.
- All five-borough tracts represented by the current tract geometry are
  covered or explicitly explained.
- Unmapped tract count is zero or explained.
- NTA IDs/names are not blank.

Downstream app uses: computed NTA labels, NTA filters, tract feature aggregation,
property context enrichment.

## `property_explorer_gold.dim_subway_stop`

Grain: one subway stop/station point.

Primary key: `subway_stop_id`.

Refresh behavior: replace from the current transit source file.

Source: MTA GTFS stops or an NYC Open Data station/stops CSV normalized under
`data/raw/transit/subway_stops.csv`.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `subway_stop_id` | string | no | GTFS stop ID or generated stable ID. |
| `stop_name` | string | no | Display stop/station name. |
| `lines` | string | yes | Delimited served routes such as `A,C,E`. |
| `lat` | double | no | WGS84 latitude. |
| `lon` | double | no | WGS84 longitude. |

Validation:

- Coordinates must be present and within the NYC bounding box.
- Duplicate stop IDs should collapse to one point.
- `lines` should preserve enough route detail for line count and display.

Downstream app uses: transit map layer, nearest subway display, subway distance,
mobility score, listing card badge.

## `property_explorer_gold.dim_user_poi_v2`

Grain: one canonical curated place per physical location, currently keyed by
resolved Google Place ID.

Primary key: `poi_id`.

Refresh behavior: replace on each full canonical merge run. User-reviewed
resolution cache at `data/interim/google_places/` persists across runs so API
calls are not repeated. WS2.5 introduces a staged-ingest direction where
Google Takeout, web scraping, and manual upload land in source-specific staging
tables first, then merge into this canonical table.

Source: curated source rows from one or more ingestion methods. The current
live path is Google Takeout CSV exports under `data/raw/google_maps/poi_nyc/`,
one file per source list or sub-list (for example `poi_bakeries_nyc.csv`).
WS2.5 sets the target pattern to:

- `stg_user_poi_google_takeout`
- `stg_user_poi_web_scrape`
- `stg_user_poi_manual_upload`

Those staging tables should preserve source-specific metadata, then feed a
final canonical merge into `dim_user_poi_v2`. The active Google Takeout
implementation lives in `src/nyc_property_finder/curated_poi/google_takeout/`
and resolves places to Google Place IDs via Google Places API. See
`docs/poi_categories.md` for the current category list and taxonomy rules.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `poi_id` | string | no | Stable hash from name and rounded coordinates. |
| `source_systems` | string | no | JSON text array of contributing ingestion methods, for example `["google_maps_takeout"]`. |
| `primary_source_system` | string | no | Canonical source/method label preferred for downstream readers. |
| `source_list_names` | string | no | JSON text array of contributing source lists. |
| `category` | string | no | Canonical top-level category for the place. Additive WS2.5 field; downstream readers should migrate here from `primary_category`. |
| `subcategory` | string | no | Canonical filter bucket for the place. Blank source values should fall back to `category`. Additive WS2.5 field. |
| `detail_level_3` | string | yes | Canonical primary descriptor token when one exists. Additive WS2.5 field. |
| `categories` | string | no | JSON text array of category values across contributing source rows. |
| `primary_category` | string | no | Primary category used by current app filters. |
| `subcategories` | string | no | JSON text array of curated subcategory values. |
| `primary_subcategory` | string | yes | Primary curated subcategory for one place. |
| `detail_level_3_values` | string | yes | JSON text array of flexible descriptor tags derived from curated source metadata. |
| `primary_detail_level_3` | string | yes | First descriptor tag when available. |
| `input_title` | string | no | Original title from the source row used for resolution. |
| `note` | string | yes | JSON text array of source note values. |
| `tags` | string | yes | JSON text array of raw source tags. |
| `comment` | string | yes | JSON text array of raw source comments. |
| `source_url` | string | yes | JSON text array of source URLs. |
| `google_place_id` | string | no | Canonical Google Places identifier used for deduplication. |
| `match_status` | string | yes | Match outcome from the resolve step. |
| `address` | string | yes | Google-standardized formatted address. |
| `name` | string | no | Place name. |
| `lat` | double | no | WGS84 latitude. |
| `lon` | double | no | WGS84 longitude. |
| `has_place_details` | boolean | no | True when the canonical row has fetched Google Place Details / geo enrichment available. |
| `details_fetched_at` | timestamp | yes | Timestamp for the cached Place Details payload used to build the row. |
| `rating` | double | yes | Google star rating from Place Details. |
| `user_rating_count` | integer | yes | Number of Google user ratings for the place. |
| `business_status` | string | yes | Raw Google business status enum such as `OPERATIONAL` or `CLOSED_TEMPORARILY`. |
| `editorial_summary` | string | yes | Google-authored short place summary text when available. |
| `editorial_summary_language_code` | string | yes | Language code paired with `editorial_summary`, for example `en`. |
| `price_level` | string | yes | Raw Google price-level enum such as `PRICE_LEVEL_MODERATE`. |
| `website_uri` | string | yes | Official place website URL from Google Place Details when available. |

Taxonomy rule: curated source rows normalize through
`config/poi_categories.yaml` into `category`, `subcategory`, and optional
flexible level-3 descriptors. Restaurant-family files roll up under
`category="restaurants"` and use subcategory/detail rules from the taxonomy
config.

Normalization rule: level 2 (`subcategory`) should be the one stable,
filterable bucket for the row. Level 3 is a flexible descriptor layer that can
hold one or many tags and can be recalculated later without changing the top
level taxonomy. Blank top-level category values fall back to `other`. Blank
subcategory values fall back to the resolved category. Example: a row can be
`category="restaurants"`, `subcategory="sandwiches"`, and level-3 descriptors
`["deli", "italian"]`.

Validation:

- Coordinates must be present and within the NYC bounding box for MVP scoring.
- Blank names should be rejected or labeled during QA.
- Unknown categories map to `other`.
- Blank subcategories map to the resolved category.
- Canonical place rows should represent one physical location; repeated source
  mentions belong in source-membership fields or staging tables, not duplicate
  rows in this table.
- True legacy/new overlaps should merge into one canonical place row, with
  source lineage preserved and suspicious overlaps retained in QA outputs for
  manual review.
- Sensitive raw exports stay local and out of git.

Downstream app uses: POI map layer, nearby POI counts, category filters, listing
detail summaries, personal fit score.

## `property_explorer_gold.fct_tract_features`

Grain: one feature row per tract.

Primary key: `tract_id`.

Refresh behavior: replace after Metro Deep Dive/source refresh.

Source: Metro Deep Dive DuckDB-derived tract features or exported files derived
from the local path configured in `config/data_sources.yaml`. The initial MVP
path should reuse the existing local feature work before adding Census API
automation. The exact source table/view still needs to be selected.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `tract_id` | string | no | Must join to `dim_tract_to_nta`. |
| `median_income` | double | yes | USD. |
| `median_rent` | double | yes | USD/month. |
| `median_home_value` | double | yes | USD. |
| `pct_bachelors_plus` | double | yes | Percent, preferably `0-100`. |
| `median_age` | double | yes | Years. |

Deferred column:

| Column | Status | Notes |
| --- | --- | --- |
| `crime_rate_proxy` | deferred | Keep nullable if present in starter DDL, but do not use in MVP scoring. |

Validation:

- Tract IDs should match geography IDs.
- Percent metrics should use one scale consistently.
- Missing feature values should not block listing context, but score behavior
  must be explicit.

Downstream app uses: tract/NTA feature summaries, neighborhood score, detail
view metrics.

## `property_explorer_gold.fct_nta_features`

Grain: one feature row per NTA.

Primary key: `nta_id`.

Refresh behavior: replace after tract features or tract-to-NTA assignments
change.

Source: aggregate from `property_explorer_gold.fct_tract_features` joined through
`property_explorer_gold.dim_tract_to_nta`.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `nta_id` | string | no | NYC NTA code. |
| `nta_name` | string | no | Display label. |
| `borough` | string | yes | Collapsed borough label for the NTA. Cross-borough NTAs join labels such as `Bronx / Manhattan`. |
| `tract_count` | integer | no | Count of mapped tracts contributing to the NTA row. |
| `median_income` | double | yes | Median or weighted/tract aggregate; method must be documented before production use. |
| `median_rent` | double | yes | NTA-level summary. |
| `median_home_value` | double | yes | NTA-level summary. |
| `pct_bachelors_plus` | double | yes | NTA-level summary. |
| `median_age` | double | yes | NTA-level summary. |

Deferred column:

| Column | Status | Notes |
| --- | --- | --- |
| `crime_rate_proxy` | deferred | Do not display or score in MVP. |

Validation:

- All five-borough NTAs represented by the current crosswalk have rows where
  source coverage allows.
- NTA IDs are unique.
- `tract_count` is positive.
- Aggregation method is visible in pipeline docs/tests.

Downstream app uses: neighborhood panel, NTA filters, neighborhood tooltip
context, neighborhood score inputs.

## `property_explorer_gold.fct_property_context`

Grain: one enriched row per property listing.

Primary key: `property_id`.

Refresh behavior: replace after any upstream listing, geography, transit, POI,
or neighborhood feature refresh.

Source: build from Property Explorer gold dimensions/facts. Sprint 3 depends on
`dim_property_listing`, `dim_tract_to_nta`, `dim_subway_stop`, `dim_user_poi`,
`fct_tract_features`, `fct_nta_features`, and an NYC 2020 tract geometry file
for point-in-polygon property assignment.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| Listing fields | mixed | see listing contract | Carry enough listing fields for app read simplicity. |
| `tract_id` | string | yes | Null only when property cannot be assigned. |
| `nta_id` | string | yes | Null only when property cannot be assigned. |
| `nta_name` | string | yes | App display label from `dim_tract_to_nta`; add to DDL in Sprint 3 if not already present. |
| `nearest_subway_stop` | string | yes | Display name or stop ID. |
| `nearest_subway_distance_miles` | double | yes | Straight-line distance for MVP. |
| `subway_lines_count` | integer | yes | Count from nearest stop's normalized `lines` value. |
| `poi_data_available` | boolean | no | False when POI table is absent/empty, so missing POI data is distinct from zero nearby matches. |
| `poi_count_nearby` | integer | no | Preferred new field name for straight-line nearby POI count. |
| `poi_count_10min` | integer | yes | Existing starter/legacy field name; if kept, document it as a straight-line proxy, not real walking time. |
| `poi_category_counts` | string | no | JSON object text by category. |
| `neighborhood_score` | double | yes | `0-100` proposed. |
| `neighborhood_score_status` | string | no | `scored`, `partial`, or `unavailable`. |
| `mobility_score` | double | yes | `0-100` proposed. |
| `personal_fit_score` | double | yes | `0-100` proposed. |
| `personal_fit_score_status` | string | no | `scored` or `unavailable`. |
| `property_fit_score` | double | yes | Weighted total score. |
| `property_fit_score_status` | string | no | `scored`, `reweighted_missing_components`, or `unavailable`. |

Required Sprint 3 input columns:

| Source Table | Columns |
| --- | --- |
| `property_explorer_gold.dim_property_listing` | `property_id`, `source`, `source_listing_id`, `address`, `lat`, `lon`, `price`, `beds`, `baths`, `listing_type`, `active`, `url`, `ingest_timestamp` |
| `property_explorer_gold.dim_tract_to_nta` | `tract_id`, `nta_id`, `nta_name`, `borough`, `cdta_id`, `cdta_name` |
| `property_explorer_gold.dim_subway_stop` | `subway_stop_id`, `stop_name`, `lines`, `lat`, `lon` |
| `property_explorer_gold.dim_user_poi_v2` | `poi_id`, `name`, `category`, `source_list_name`, `lat`, `lon` |
| `property_explorer_gold.fct_tract_features` | `tract_id`, `median_income`, `median_rent`, `median_home_value`, `pct_bachelors_plus`, `median_age` |
| `property_explorer_gold.fct_nta_features` | `nta_id`, `nta_name`, `borough`, `tract_count`, `median_income`, `median_rent`, `median_home_value`, `pct_bachelors_plus`, `median_age` |

Scoring proposal:

- Use existing weights from `config/scoring_weights.yaml` unless review changes
  product emphasis.
- Use straight-line subway/POI distances for MVP and label them as proxies.
  Walking-time proxies are post-MVP.
- If user POI data is absent, set `personal_fit_score` to null. This score is
  the property/rental personal-fit component based on nearby Google Maps POIs,
  not a separate score for the POI records themselves.
- If neighborhood metrics are all null, set `neighborhood_score` to null or mark
  it with an explicit degraded status. Do not compute a precise-looking score
  from zero-filled metric values.
- If a score component is null, `property_fit_score` must follow a documented
  missing-component rule: either remain null, or reweight available components
  while exposing which component is missing.
- Keep `crime_rate_proxy` out of MVP scoring even if the legacy nullable column
  exists.

Sprint 3 QA checks:

- Context row count equals listing row count.
- Active context row count equals active listing row count.
- Assigned `tract_id` values join to exactly one NTA record.
- `nta_id` and `nta_name` are non-null when `tract_id` is assigned.
- `nearest_subway_distance_miles` is non-null and non-negative when subway data
  is populated.
- `poi_category_counts` is valid JSON, and total nearby POI count matches the
  sum of category counts.
- Score fields are null for documented missing-data reasons or between `0` and
  `100`.

Downstream app uses: primary app query for map/list/filter/detail, score
breakdown, listing cards, context inspection.

## `property_explorer_gold.fct_user_shortlist`

Grain: one current saved-listing row per `user_id` plus `property_id`.

Primary key: `shortlist_id`; unique constraint proposal on
`(user_id, property_id)`.

Refresh behavior: user-authored table. Do not replace during data rebuilds
unless explicitly requested.

Source: Streamlit save/archive/reject actions.

Required columns:

| Column | Type | Nulls | Notes |
| --- | --- | --- | --- |
| `shortlist_id` | string | no | Stable ID from `user_id` and `property_id`, or generated UUID. |
| `user_id` | string | no | Local user identifier. Start with a config/default value; app-entered user names are a scale-up path. |
| `property_id` | string | no | Joins to listing/context. |
| `saved_timestamp` | timestamp | no | UTC timestamp of first save. |
| `updated_timestamp` | timestamp | no | UTC timestamp of latest note/status update. |
| `status` | string | no | Controlled values: `active`, `archived`, `rejected`. |
| `notes` | string | yes | User-authored notes. |
| `metadata_json` | string | yes | Lightweight app metadata as JSON text. |

Validation:

- `status` must be controlled.
- One current row per user/listing pair.
- App should join current listing/context at read time rather than denormalizing
  listing facts in MVP.

Downstream app uses: shortlist panel, comparison view, notes, local persistence.

## First App Surface Mapping

| App Surface | Required Tables | Required Fields |
| --- | --- | --- |
| Listing cards | `fct_property_context` | price, beds, baths, address, listing type, source, no-fee badge, NTA/name, nearest subway, score components, active flag |
| Map markers | `fct_property_context`, `dim_user_poi`, `dim_subway_stop` | lat/lon, display labels, type/category, scores |
| Filters | `fct_property_context`, `fct_nta_features` | price, beds, baths, listing type, source, borough/NTA, scores, subway distance, POI category counts |
| Detail view | `fct_property_context`, `fct_nta_features` | listing facts, source URL, subway context, POI summary, neighborhood metrics, scores |
| Shortlist | `fct_user_shortlist`, `fct_property_context` | user_id, property_id, status, notes, current listing/context fields |

## Confirmed Decisions

- MVP supports rentals and sales.
- Manual listing CSV/JSON is the first real listing source path, with
  StreetEasy and Zillow as the first expected manual sources.
- The first listing set can mix rentals and sales, leaning toward rentals.
- Listing images are post-MVP; source URL is enough for MVP.
- `no_fee` is part of the rental CSV contract.
- `days_on_market` is deferred until scraper/adapter data exists.
- Missing listing coordinates can be filled by a geocoding step before scoring.
- Approximate coordinates are acceptable when clearly marked.
- All five boroughs are the current real geography coverage target.
- NTA is the primary neighborhood UI language.
- Google Maps saved places are a core input, resolved via Google Places API.
  Active curated categories: bookstores, record_stores, museums (loaded);
  15 additional `poi_nyc/` CSVs pending ingestion. See `docs/poi_categories.md`.
- Keyword-based POI categorization is enough for MVP.
- Straight-line distance is the MVP proximity method.
- Tract-to-NTA mapping should prefer an official/source equivalency table before
  centroid or other geometry fallback.
- Metro Deep Dive DuckDB-derived features are the first neighborhood feature
  source path. The local database path belongs in ignored
  `config/data_sources.yaml`.
- Metro Deep Dive tract features should be assembled by a Sprint 2 SQL query
  because the needed data is likely spread across multiple tables/views.
- Shortlists persist in DuckDB.
- Shortlist is one current row per `user_id` plus `property_id`.
- The first shortlist `user_id` should be read from `config/settings.yaml`.
- Missing POI data should leave `personal_fit_score` null.
- Listing `active` stays on `dim_property_listing`; full snapshot/history is
  deferred.
- Crime/safety is deferred.

## Open Questions For Review

1. ~~Which exact Google Maps custom lists will be exported for the first demo?~~ Resolved: 15 curated lists in `data/raw/google_maps/poi_nyc/`; see `docs/poi_categories.md`.
2. What exact Metro Deep Dive source tables/views should the tract feature SQL query use?
