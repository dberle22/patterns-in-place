# Package Guide

This document explains the Python package layout under
`src/nyc_property_finder/`, what each package owns, and how the major packages
interact.

Use this doc when you are deciding:

- where new code should live
- whether a behavior belongs in a pipeline package or an app package
- how curated POI, public POI, and property workflows connect

For system-level data flow, use `architecture.md`.
For table contracts, use `data_model.md`.
For executable commands, use `pipeline_plan.md`.

---

## Package Map

The main package root is:

```text
src/nyc_property_finder/
```

Current top-level packages:

| Package | Purpose |
| --- | --- |
| `app/` | Streamlit-facing logic, map prep, and app helper functions |
| `curated_poi/` | Curated POI ingestion paths and shared curated-POI logic |
| `models/` | Typed data structures and domain models where needed |
| `pipelines/` | CLI-style entry points and build orchestration |
| `public_poi/` | Baseline public/open-data POI ingestion |
| `scrapers/` | Property-listing scrapers and non-curated-POI scrape helpers |
| `services/` | Config, DuckDB, schema, and other infrastructure services |
| `transforms/` | Reusable normalization and scoring transforms |
| `utils/` | Lower-level utility helpers, especially spatial helpers |

---

## Ownership Rules

### `pipelines/`

This package owns command-oriented entry points.

What belongs here:

- modules that are invoked with `python -m ...`
- orchestration that stitches together lower-level package functions
- compatibility wrappers for renamed commands

What does not belong here:

- detailed source-specific parsing logic
- reusable business logic that another package may need directly

Examples:

- `pipelines/ingest_curated_poi_google_takeout.py`
- `pipelines/ingest_public_poi.py`
- `pipelines/build_property_context.py`

### `curated_poi/`

This package owns all curated place ingestion paths that eventually normalize
into `dim_user_poi_v2`.

Current layout:

```text
curated_poi/
  google_takeout/
  web_scraping/
  excel_upload/
  shared/
```

#### `curated_poi/google_takeout/`

Owns the active curated POI ingestion path based on Google Takeout saved lists.

What it currently does:

- parse Takeout CSVs
- normalize category, subcategory, and level-3 descriptor taxonomy
- estimate API work in dry-run mode
- resolve rows to Google Place IDs
- enrich with versioned shared Place Details metadata
- build the deduplicated `dim_user_poi_v2` output

Important modules:

- `parse_takeout.py`
- `dry_run.py`
- `resolve.py`
- `enrich.py`
- `build_dim.py`
- `pipeline.py`

#### `curated_poi/web_scraping/`

Reserved for curated POIs extracted from editorial articles and similar web
sources.

Expected role:

- scrape article inputs
- normalize extracted place rows into the curated POI schema
- hand off to shared or source-specific resolution/enrichment flow

#### `curated_poi/excel_upload/`

Reserved for curated POIs submitted through a shared Excel or CSV template.

Expected role:

- validate incoming template files
- normalize contributor rows into the curated POI schema
- hand off to shared or source-specific resolution/enrichment flow

#### `curated_poi/shared/`

Reserved for helpers that should be shared across Takeout, scraping, and Excel
submission paths.

Good future candidates:

- shared curated-row schema helpers
- taxonomy validation helpers
- common dedupe or QA helpers

### `public_poi/`

This package owns baseline public/open-data POI ingestion that writes
`dim_public_poi`.

What belongs here:

- source fetch/load logic for official or open data
- category-specific loaders under `public_poi/sources/`
- public POI build pipeline and dim builder

What does not belong here:

- curated/editorial place lists
- Google Places API resolution for taste-driven lists

### `app/`

This package owns UI-facing data prep and app helpers.

What belongs here:

- map-ready formatting
- app-level filtering helpers
- lightweight data reshaping needed specifically for Streamlit or PyDeck

What does not belong here:

- raw-source ingestion
- DuckDB schema creation
- heavy source normalization logic

### `services/`

This package owns infrastructure services used by many parts of the system.

Examples:

- config loading
- DuckDB access
- schema initialization

### `transforms/`

This package owns reusable domain transforms that are broader than one source
pipeline or one app.

Examples:

- POI normalization helpers
- scoring transforms

### `utils/`

This package owns low-level helpers that are broadly reusable and do not define
business ownership on their own.

Examples:

- spatial counting helpers
- geometry utilities

---

## Interaction Model

The normal dependency direction should be:

```text
raw files / source APIs
  -> source package logic
  -> pipeline entry point
  -> DuckDB tables
  -> app package readers / formatters
```

More concretely:

```text
curated_poi/google_takeout/*
  -> pipelines/ingest_curated_poi_google_takeout.py
  -> property_explorer_gold.dim_user_poi_v2
  -> app/base_map.py and downstream scoring/context code
```

And:

```text
public_poi/sources/*
  -> public_poi/pipeline.py
  -> pipelines/ingest_public_poi.py
  -> property_explorer_gold.dim_public_poi
  -> app/base_map.py and downstream scoring/context code
```

Shared dependencies that many packages may call:

- `services/config.py`
- `services/duckdb_service.py`
- `services/schema.py`
- `utils/geo.py`

---

## Curated POI Flow

Current active flow:

```text
data/raw/google_maps/poi_nyc/*.csv
  -> curated_poi/google_takeout/parse_takeout.py
  -> curated_poi/google_takeout/dry_run.py
  -> curated_poi/google_takeout/resolve.py
  -> curated_poi/google_takeout/enrich.py
  -> curated_poi/google_takeout/build_dim.py
  -> property_explorer_gold.dim_user_poi_v2
```

Key design point:

- `subcategory` is the one stable filter bucket
- `detail_level_3` is a flexible descriptor layer that may contain multiple tags

This lets a place be modeled as:

```text
category=restaurants
subcategory=sandwiches
detail_level_3=deli|italian
```

---

## Package Placement Guidelines

When adding new code, use these rules:

1. If it is a user-run command, start in `pipelines/`.
2. If it is source-specific curated POI logic, put it in `curated_poi/<source_path>/`.
3. If it is source-specific public/open-data POI logic, put it in `public_poi/`.
4. If it is app-only formatting or filtering, put it in `app/`.
5. If it is infrastructure used across domains, put it in `services/`.
6. If it is a reusable domain transform, put it in `transforms/`.
7. If it is a low-level helper with no strong domain ownership, put it in `utils/`.

---

## Current Notes

- `pipelines/ingest_google_places_poi.py` still exists as a compatibility
  wrapper and should remain valid until we intentionally remove it.
- The old `google_places_poi/` code package has been replaced by
  `curated_poi/google_takeout/`.
- Planned curated paths for `web_scraping/` and `excel_upload/` now have real
  package homes even though implementation is still pending.
