# Google Maps Saved Lists to Structured Dataset

## Overview

This workflow converts Google Maps Saved Lists exported via Google Takeout into a structured, geocoded dataset that can be used for mapping, analysis, or internal tools.

The main constraint is simple:

- Google Takeout exports do not include coordinates or structured place data
- Google Places API does not expose your private saved lists or personal notes

Because of that, the right design is a two stage pipeline:

1. Free matching to resolve each place to a Google `place_id`
2. Selective enrichment to fetch coordinates and structured metadata

## Input Data from Google Takeout

Example CSV structure:

| Title | Note | URL | Tags | Comment |
| | | | | |
| Carino patisserie |  | https://www.google.com/maps/place/... |  |  |
| Donovan's Pub |  | https://www.google.com/maps/place/... |  |  |

### Key fields

- `Title` is the primary search key
- `URL` contains the Google Maps link and is useful for fallback parsing
- `Note`, `Tags`, and `Comment` are your own metadata and should be preserved as is

### Important limitation

The URL contains an internal identifier such as:

```text
0x1361b1e9fc7e0875:0x9a39680ac4b69529
```

That is not the same as a Google Places API `place_id` and cannot be used directly with Place Details.

## Target Output Schema

The final dataset should look something like this:

| list_name | title | note | tags | comment | source_url | match_status | google_place_id | matched_name | address | latitude | longitude |
|---|---|---|---|---|---|---|---|---|---|---:|---:|

### Column definitions

- `list_name`: original list name such as Restaurants, Bars, or Bookstores
- `title`: original place name from the export
- `note`, `tags`, `comment`: preserved user metadata
- `source_url`: original Google Maps link from Takeout
- `match_status`: quality of the place match
- `google_place_id`: canonical place identifier returned by Places API
- `matched_name`: standardized place name returned by Places API
- `address`: formatted address returned by Places API
- `latitude`, `longitude`: coordinates for mapping

## Pipeline Architecture

## Stage 1: Free Matching

Goal: resolve each place to a Google `place_id` at zero cost.

### Method

For each row:

1. Extract the `title`
2. Call Places API Text Search with an IDs only field mask
3. Store the returned `place_id`
4. Assign a `match_status`

### Example request

```http
POST https://places.googleapis.com/v1/places:searchText
X-Goog-Api-Key: YOUR_API_KEY
X-Goog-FieldMask: places.id

{
  "textQuery": "Donovan's Pub Queens NY"
}
```

### Example response

```json
{
  "places": [
    {
      "id": "places/ChIJxxxxxxxxxxxx"
    }
  ]
}
```

### Match status logic

| Status | Description |
|---|---|
| exact_match | clear single match |
| likely_match | good match with minor ambiguity |
| ambiguous | multiple plausible matches |
| no_match | no results |

### Query optimization

You will get better results if you enrich the title with geography when needed.

Examples:

- `Donovan's Pub Queens NY`
- `Wylie's Astoria NYC`
- `ICHIRAN Ramen Times Square New York`

## Stage 2: Selective Enrichment

Goal: fetch coordinates and structured metadata for valid matches.

### Method

For rows where `match_status` is `exact_match` or `likely_match`, call Place Details with only the fields you need.

### Example request

```http
GET https://places.googleapis.com/v1/places/PLACE_ID
X-Goog-Api-Key: YOUR_API_KEY
X-Goog-FieldMask: location,formattedAddress,displayName
```

### Example response

```json
{
  "location": {
    "latitude": 40.706,
    "longitude": -74.001
  },
  "formattedAddress": "123 Example St, New York, NY",
  "displayName": {
    "text": "Donovan's Pub"
  }
}
```

### Fields to request for cost control

Request only:

- `location`
- `formattedAddress`
- `displayName`

Avoid requesting fields like reviews, ratings, hours, or photos unless you truly need them, because those can push you into higher pricing tiers.

## Pricing Strategy

### Free path

- Text Search IDs only
- Place Details IDs only

### Paid path

- Place Details Essentials for fields like `location`, `formattedAddress`, and `displayName`

### Approximate costs

| Number of places | Estimated cost |
|---|---:|
| 1,000 | about $0.50 |
| 2,000 | about $1.00 |
| 10,000 | about $5.00 |

These estimates assume you stay in the basic details tier and only request minimal fields.

## Data Processing Logic

### Step 1: Parse CSV

Extract:

- `title`
- `note`
- `tags`
- `comment`
- `url`
- `list_name`, usually from file name, folder name, or import metadata

### Step 2: Normalize text

- trim whitespace
- standardize capitalization if needed
- decode the URL slug from `/place/.../` when useful

Example:

`/place/Carino+patisserie/` becomes `Carino patisserie`

### Step 3: Match places

Use this order of operations:

1. Start with `title`
2. Use URL slug as a fallback or helper field
3. Append geography such as `NYC`, `Queens`, or `Astoria` when the title is ambiguous

### Step 4: Store an intermediate match table

| title | google_place_id | match_status |
|---|---|---|

### Step 5: Enrich valid matches

For accepted rows, append:

- `matched_name`
- `address`
- `latitude`
- `longitude`

## System Design Principles

### Separate responsibilities

- Google Takeout is the source of truth for your personal metadata
- Google Places API is the source of truth for structured place data

### Store place IDs

Persist `google_place_id` so you can refresh details later without re-running search.

### Make the pipeline idempotent

The process should be safe to rerun without creating duplicate outputs or duplicate API calls.

### Include manual review

You should review rows marked:

- `ambiguous`
- `no_match`

## Optional Enhancements

### Confidence scoring

You can score matches using:

- string similarity between `title` and `matched_name`
- geography consistency
- category consistency

### Batch processing

Add:

- chunking
- retry logic
- rate limiting

### Caching

Cache title to place ID mappings so repeat runs cost less and execute faster.

### Multi list deduplication

If the same place appears across multiple lists, use `google_place_id` to unify it.

## Recommended Final Architecture

Your final workflow should treat:

- the Google Takeout CSV as the source of truth for list organization, notes, tags, and comments
- the Google Places API as an enrichment layer for geolocation and standardized metadata

That gives you a clean final table ready for internal tools, notebooks, dashboards, or mapping apps.

## Suggested Implementation Modules

A clean repo structure could look like this:

```text
/google-maps-lists/
  README.md
  /data_raw/
  /data_processed/
  /src/
    parse_takeout.py
    normalize_places.py
    match_places_ids.py
    enrich_place_details.py
    review_matches.py
    export_final_dataset.py
  /config/
    settings.yaml
```

## Summary

This design:

- preserves your personal organization
- adds structured geospatial data
- minimizes API cost through a two step pipeline
- creates a reusable dataset for mapping and analysis

Core principle:

> Use Google Places API as an enrichment layer, not as the source of truth for your saved lists.

## Project Implementation Notes

These notes adapt the generic workflow above to the current
`rental_area_search` project.

### Current Goal

Build a dedicated Google Places-backed ingestion pipeline whose main product is
`property_explorer_gold.dim_user_poi_v2`. Keep the existing `dim_user_poi`
table intact so the current app path is not disturbed while v2 matures.

The first implementation should optimize for:

- one Google Takeout saved-list CSV as input
- NYC-only place search
- one row per unique place in `dim_user_poi_v2`
- combined saved-list/category metadata when the same place appears more than
  once
- dry-run and cache-first behavior before any paid enrichment calls

The existing NYC GeoSearch ingestion path should remain available, but this
Google Places resolver should be callable as a separate pipeline.

### Pipeline Entry Point

Proposed module:

```text
src/nyc_property_finder/pipelines/ingest_google_places_poi.py
```

Workflow-owned implementation modules should live together:

```text
src/nyc_property_finder/google_places_poi/
  __init__.py
  config.py
  parse_takeout.py
  dry_run.py
  cache.py
  client.py
  build_dim.py
  pipeline.py
```

The repo-level pipeline entry point should stay small and delegate to
`nyc_property_finder.google_places_poi.pipeline`.

Proposed run modes:

| Mode | Purpose | API calls |
| --- | --- | --- |
| `dry_run=True` | Parse input, inspect cache coverage, estimate calls/cost, and write a preview. | None unless explicitly allowed. |
| `resolve_only=True` | Resolve uncached CSV rows to Google place IDs and update the resolution cache. | Text Search ID-only calls for uncached rows. |
| `enrich=True` | Fetch details for accepted place IDs and build `dim_user_poi`. | Place Details calls for uncached details. |
| `review=True` | Emit a review file from cache/output for manual QA. | None. |

### Local Artifacts

Intermediate artifacts are useful because they make reruns idempotent and keep
API spend under control.

Use:

```text
data/interim/google_places/place_resolution_cache.csv
data/interim/google_places/place_details_cache.jsonl
data/interim/google_places/place_resolution_quarantine.csv
data/interim/google_places/place_resolution_review.csv
```

Suggested grain:

- `place_resolution_cache.csv`: one source row or source signature to resolved
  Google place ID.
- `place_details_cache.jsonl`: one Google place ID to raw minimal details
  payload.
- `place_resolution_quarantine.csv`: unresolved, malformed, or manually
  rejected rows.
- `place_resolution_review.csv`: human-readable QA export after matching and
  enrichment.

### Search Cost And Accuracy Strategies

The first implementation should only accept the top candidate. To keep costs
low, do not request extra candidate metadata during the search call unless a
later review pass proves it is necessary.

| Strategy | Query example | Cost profile | Accuracy profile | Initial recommendation |
| --- | --- | --- | --- | --- |
| Title only | `Donovan's Pub` | Cheapest search payload. | More false matches for generic names and chains. | Too loose for NYC unless reviewed heavily. |
| Title plus NYC | `Donovan's Pub New York, NY` | Same number of calls; no paid detail fields in search. | Better for NYC-only workflow. | Use as default. |
| Title plus list/category plus NYC | `Donovan's Pub bar New York, NY` | Same number of calls. | Can help generic names, but category words may distort unusual places. | Optional config, off by default. |
| Title plus URL slug plus NYC | `Carino patisserie New York, NY` from URL slug fallback | Same number of calls. | Useful when `Title` is abbreviated or messy. | Use slug only as fallback/helper when title is weak. |
| Location bias/restriction | Places API location bias around NYC | Same call count; request body is more specific. | Better geographic targeting without changing query text. | Add after basic title-plus-NYC works. |
| Multi-candidate scoring | Request names/addresses for candidates and score locally. | Higher search field usage and/or extra calls. | Best automated quality. | Defer; user wants top candidate only. |

Default search behavior:

1. Normalize the `Title`.
2. Search for `"{title} New York, NY"`.
3. Request only `places.id` from Text Search.
4. Accept the first returned place ID as `match_status = top_candidate`.
5. Quarantine rows with no returned place.
6. Use the review flow to inspect and correct suspicious matches later.

### Output Table Contract

`dim_user_poi_v2` should be source-aware so other POI sources can be added
later. The first pass should not change the legacy `dim_user_poi` contract.

Proposed columns:

| Column | Source | API cost tier / notes |
| --- | --- | --- |
| `poi_id` | Internal hash. | Free. Prefer hash of `source_system` plus stable source key, with Google Places using `google_place_id`. |
| `source_system` | Pipeline constant, e.g. `google_places`. | Free. |
| `source_record_id` | Internal hash of source file/list/title/url before matching. | Free. |
| `source_list_names` | Takeout CSV file/list metadata, combined across duplicates. | Free. |
| `categories` | Cleaned list names, combined across duplicates as JSON text. | Free. Initially list-name based. |
| `primary_category` | First or preferred cleaned list category. | Free. Useful for existing app filters. |
| `name` | Google Place Details `displayName.text`, fallback to CSV `Title`. | Paid Place Details Essentials when fetched. |
| `input_title` | Takeout `Title`. | Free. |
| `note` | Takeout `Note`, combined as JSON array text. | Free. |
| `tags` | Takeout `Tags`, combined as JSON array text. | Free. |
| `comment` | Takeout `Comment`, combined as JSON array text. | Free. |
| `source_url` | Takeout `URL`. | Free. |
| `google_place_id` | Text Search ID-only response. | ID-only search path; intended low/no-cost identifier lookup. |
| `match_status` | Pipeline-assigned. | Free. |
| `address` | Google Place Details `formattedAddress`. | Paid Place Details Essentials. |
| `lat` | Google Place Details `location.latitude`. | Paid Place Details Essentials. |
| `lon` | Google Place Details `location.longitude`. | Paid Place Details Essentials. |
| `details_fetched_at` | Pipeline timestamp. | Free. |

The existing app expects `dim_user_poi` columns `poi_id`, `name`, `category`,
`source_list_name`, `lat`, and `lon`. For now, leave that table alone and write
the richer Google Places output to `dim_user_poi_v2`.

### Deduplication Rules

Use one row per unique place.

Deduplication priority:

1. `google_place_id` when available.
2. If no Google ID exists, a source-specific key based on source system, title,
   source URL, and list name.

For duplicates:

- combine source list names
- combine list-derived categories
- keep all source URLs if they differ
- preserve notes/tags/comments as JSON array text when duplicate rows have
  different personal metadata

### POI ID Strategy

Use a source-aware stable hash:

```text
poi_<sha256(source_system + "|" + stable_source_key)[:16]>
```

For Google Places rows:

```text
stable_source_key = google_place_id
```

For future non-Google sources:

```text
stable_source_key = source-native ID if present, otherwise normalized name plus rounded coordinates
```

This avoids tying the whole table to Google while still making Google-backed
rows stable across reruns.

### Credential Handling

Current local storage in `config/data_sources.yaml` works because that file is
ignored, but it is still easy to accidentally print or copy.

Safer default:

1. Store the key in `.env` as `GOOGLE_MAPS_API_KEY=...`.
2. Keep `.env` ignored.
3. Let `config/data_sources.yaml` describe non-secret Places settings such as
   default search context, cache paths, dry-run default, and cost guardrails.
4. Load the actual secret from the environment at runtime.

Optional later hardening:

- macOS Keychain or 1Password CLI for local secret retrieval
- a small `config/api_keys.yaml` only if environment variables are too awkward;
  this file is already ignored
- fail closed if both dry-run is false and no API key is available

### Small Implementation Chunks

1. Document pipeline decisions and table contract.
2. Add config defaults and API-key environment lookup.
3. Add a CSV parser that preserves `Title`, `Note`, `URL`, `Tags`, `Comment`,
   and list name.
4. Add dry-run planning: row count, unique source rows, cache hits, estimated
   Text Search calls, estimated Details calls.
5. Add resolution cache read/write with a fake fetcher for tests.
6. Add Google Text Search ID-only client.
7. Add details cache read/write with a fake fetcher for tests.
8. Add Google Place Details client for `location`, `formattedAddress`, and
   `displayName`.
9. Build the source-aware `dim_user_poi` dataframe with deduplication.
10. Write `dim_user_poi_v2` and update schema/tests without changing the app.
11. Add review export and quarantine handling.

### Open Decisions

- Future migration strategy from `dim_user_poi_v2` into the app once the review
  flow is trusted.
- Whether a future bridge table should replace JSON text for multi-list
  categories and source-list membership.
- Whether to add NYC location bias in the first client implementation or wait
  until the title-plus-NYC query has been tested on real exports.
