# Stoop Migration Plan

Migration of `rental_area_search` into `stoop/` within the `patterns-in-place` monorepo.

**Source repo:** `<local-projects-root>/rental_area_search`
**Destination:** `<monorepo-root>/stoop/`
**Rule:** Copy files in; do not modify or delete the source repo until all verification gates pass.

---

## Target folder structure

```
stoop/
├── app/
│   ├── stoop_explore.py          ← entry point / analytics wrapper (calls streamlit_app_v2.main)
│   ├── streamlit_app_v2.py       ← production app
│   ├── neighborhood_qa_app.py    ← QA tool
│   └── pages/                    ← currently empty; keep for future pages
├── sql/
│   ├── gold/                     ← TEMPORARY — move to foundations/ when Points pipeline centralizes
│   │   ├── fct_nta_features.sql
│   │   ├── fct_tract_features.sql
│   │   └── README.md
│   └── datamart/                 ← permanent stoop-specific SQL
│       ├── neighborhood_character/
│       │   ├── nta_category_controls.sql
│       │   ├── nta_category_density.sql
│       │   ├── nta_character_profile.sql
│       │   ├── nta_curated_poi_counts.sql
│       │   └── nta_public_poi_counts.sql
│       ├── place_classification/
│       │   ├── curated_places_classified.sql
│       │   ├── place_classification_recommendations.sql
│       │   ├── place_classification_review_queue.sql
│       │   ├── place_classification_scores.sql
│       │   ├── place_classification_text.sql
│       │   ├── place_keyword_mapping_seed.sql
│       │   ├── place_keyword_matches.sql
│       │   ├── place_matched_keywords.sql
│       │   ├── place_phrase_profile.sql
│       │   └── place_word_profile.sql
│       └── README.md
├── src/
│   └── nyc_property_finder/      ← full package copy
├── config/
│   ├── poi_categories.yaml
│   ├── scoring_weights.yaml
│   ├── settings.yaml
│   ├── curated_scrape_articles.yaml
│   └── data_sources.example.yaml ← template; create data_sources.yaml locally from this
├── docs/                         ← minus archive/; see leave-behind list
├── notebooks/
├── tests/
├── data/                         ← gitignored; DuckDB and raw geo files live here locally
│   ├── processed/
│   │   └── nyc_property_finder.duckdb   ← copy manually from rental_area_search
│   └── raw/
│       └── geography/                   ← copy manually from rental_area_search
│           ├── census_tracts.geojson
│           ├── nta_boundaries.geojson
│           └── tract_to_nta_equivalency.csv
├── pyproject.toml
├── requirements.txt
├── CLAUDE.md
├── AGENTS.md
└── MIGRATION.md                  ← this file
```

---

## Phase 0 — Pre-migration checklist

Before copying anything, confirm these are true:

- [x] `rental_area_search/app/stoop_explore.py` boots without error from the source repo
- [x] `rental_area_search/data/processed/nyc_property_finder.duckdb` exists and is readable
- [x] `rental_area_search/config/data_sources.yaml` exists locally (gitignored)
- [x] You know the local path to the `metro_deep_dive` DuckDB (referenced in `data_sources.yaml` as `source_database_path` under `metro_deep_dive_tract_features`)

Observed during verification on 2026-06-05:

- Import check passed in both the source repo and `stoop/` with `PYTHONPATH=app:src`.
- Importing from repo root without `app` on `PYTHONPATH` raises `ModuleNotFoundError: streamlit_app_v2`, which is a path-resolution quirk of the entrypoint rather than a migration regression.

---

## Phase 1 — File copy

Status on 2026-06-05:

- [x] 1.1 Automated copy completed into `stoop/`
- [x] 1.2 Manual copy completed for `nyc_property_finder.duckdb`, `census_tracts.geojson`, `tract_to_nta_equivalency.csv`, and `config/data_sources.yaml`
- [ ] 1.2 Manual copy still needed for `data/raw/geography/nta_boundaries.geojson`
- [x] 1.3 Leave-behind list respected during copy

### 1.1 Automated copy (can be scripted)

Run from `<monorepo-root>`:

```bash
SRC=<local-projects-root>/rental_area_search
DEST=<monorepo-root>/stoop

# App — production files only (leave streamlit_app.py V1 behind)
cp $SRC/app/stoop_explore.py          $DEST/app/
cp $SRC/app/streamlit_app_v2.py       $DEST/app/
cp $SRC/app/neighborhood_qa_app.py    $DEST/app/
cp -r $SRC/app/pages/                 $DEST/app/pages/

# SQL — gold and marts only (bronze and silver are empty)
cp $SRC/sql/gold/fct_nta_features.sql    $DEST/sql/gold/
cp $SRC/sql/gold/fct_tract_features.sql  $DEST/sql/gold/
cp $SRC/sql/gold/fct_nta_features.md     $DEST/sql/gold/
cp $SRC/sql/gold/fct_tract_features.md   $DEST/sql/gold/
cp -r $SRC/sql/marts/neighborhood_character/   $DEST/sql/datamart/neighborhood_character/
cp -r $SRC/sql/marts/place_classification/     $DEST/sql/datamart/place_classification/

# Source library
cp -r $SRC/src/  $DEST/src/

# Config — committed files only (data_sources.yaml is gitignored; handle manually in 1.2)
cp $SRC/config/poi_categories.yaml           $DEST/config/
cp $SRC/config/scoring_weights.yaml          $DEST/config/
cp $SRC/config/settings.yaml                 $DEST/config/
cp $SRC/config/curated_scrape_articles.yaml  $DEST/config/
cp $SRC/config/data_sources.example.yaml     $DEST/config/

# Docs — exclude archive/
rsync -av --exclude='archive/' $SRC/docs/  $DEST/docs/

# Notebooks, tests, project files
cp -r $SRC/notebooks/    $DEST/notebooks/
cp -r $SRC/tests/        $DEST/tests/
cp    $SRC/pyproject.toml  $DEST/
cp    $SRC/requirements.txt $DEST/
```

### 1.2 Manual copy (gitignored files — you must do these by hand)

These files are gitignored in the source repo and cannot be scripted into version control. Copy them locally to the new `stoop/` paths:

| Source path | Destination path | Notes |
|---|---|---|
| `rental_area_search/data/processed/nyc_property_finder.duckdb` | `stoop/data/processed/nyc_property_finder.duckdb` | Main app database |
| `rental_area_search/data/raw/geography/census_tracts.geojson` | `stoop/data/raw/geography/census_tracts.geojson` | NYC 2020 tract geometry |
| `rental_area_search/data/raw/geography/nta_boundaries.geojson` | `stoop/data/raw/geography/nta_boundaries.geojson` | NTA polygons |
| `rental_area_search/data/raw/geography/tract_to_nta_equivalency.csv` | `stoop/data/raw/geography/tract_to_nta_equivalency.csv` | Tract-to-NTA crosswalk |
| `rental_area_search/config/data_sources.yaml` | `stoop/config/data_sources.yaml` | Local source paths config |

After copying `data_sources.yaml`, update the `source_database_path` under `metro_deep_dive_tract_features` if the path has changed on your machine. Leave the metro_deep_dive path as-is for now — the ACS features connection is deferred.

Observed during copy on 2026-06-05:

- `rental_area_search/data/raw/geography/nta_boundaries.geojson` was not present in the source repo.
- `stoop/config/data_sources.yaml` currently points `metro_deep_dive_tract_features.source_database_path` to `/Users/danberle/Documents/projects/data/duckdb/metro_deep_dive.duckdb`.

### 1.3 Leave behind (do not copy)

| File / folder | Reason |
|---|---|
| `app/streamlit_app.py` | V1 Property Explorer — explicitly on ice per `docs/data_model.md` |
| `sql/bronze/` | Empty |
| `sql/silver/` | Empty |
| `sql/ddl/` | DDL is executed by Python pipelines, not standalone — copy if needed for reference only |
| `docs/archive/` | Stale sprint artifacts |
| `nyc_property_finder_spec.md` | Early scaffold doc, superseded |
| `nyc_repo_scaffold.md` | Early scaffold doc, superseded |
| `config/api_keys.yaml` | Secret keys — do not copy anywhere near version control |
| `data/raw/` (except geography files above) | Re-derivable from pipelines |
| `data/interim/` | Pipeline-generated scratch files |
| `output/` | Generated artifacts |
| `.git/` | Source repo history stays in the old repo |

---

## Phase 2 — Post-copy fixes

Complete all of these before running the verification gate.

Status on 2026-06-05:

- [x] 2.1 Added `stoop/data/` to the monorepo `.gitignore`
- [x] Confirmed `stoop/config/data_sources.yaml` is covered by the existing root `config/data_sources.yaml` ignore rule
- [x] 2.2 Updated `stoop/config/data_sources.example.yaml` with the monorepo comment for the future `foundations.duckdb` path
- [x] 2.3 Updated `stoop/docs/platform_context.md` to reflect the monorepo ecosystem and current temporary `metro_deep_dive` dependency
- [x] 2.4 Wrote `stoop/sql/gold/README.md`
- [x] 2.5 Wrote `stoop/sql/datamart/README.md`
- [x] 2.6 Replaced copied source-repo `AGENTS.md` and `CLAUDE.md` with stoop-specific monorepo versions

### 2.1 Add `stoop/data/` to monorepo `.gitignore`

Open `<monorepo-root>/.gitignore` and add:

```
stoop/data/
```

Confirm `stoop/config/data_sources.yaml` is also covered (it should be if the root gitignore already has `data_sources.yaml` — verify).

### 2.2 Update `config/data_sources.example.yaml`

The example file still has a placeholder value for `source_database_path`:

```yaml
metro_deep_dive_tract_features:
  source_database_path: /path/to/local/metro_deep_dive.duckdb
```

This is correct for a template. Add a comment clarifying where this points in the monorepo context:

```yaml
metro_deep_dive_tract_features:
  source_database_path: /path/to/local/metro_deep_dive.duckdb
  # In the patterns-in-place monorepo, this will eventually point to
  # <monorepo-root>/foundations/data/foundations.duckdb once the ACS
  # features are promoted to the foundations Gold layer. Until then,
  # set this to your local metro_deep_dive DuckDB path.
```

### 2.3 Update `docs/platform_context.md`

The platform context doc describes the old multi-repo ecosystem. Rewrite the ecosystem overview section to reflect the monorepo:

- Replace references to `rental_area_search` repo → `stoop/` folder in `patterns-in-place`
- Replace references to `metro_deep_dive` as a separate repo → `foundations/` (where the ETL will live)
- Remove references to `retail_opportunity_finder` as a peer (it's a separate track, not part of stoop)
- Update the data flow diagram to show `foundations.duckdb → stoop/` rather than `metro_deep_dive.duckdb → rental_area_search`
- Keep the note that the `metro_deep_dive` DuckDB path is still used locally until foundations ETL is complete

Do not change the technical conventions section — stack, geometry handling, config pattern, and proximity rules are all still accurate.

### 2.4 Write `sql/gold/README.md`

Create this file to mark the gold SQL as temporary:

```markdown
# sql/gold — Temporary

These scripts build the `fct_tract_features` and `fct_nta_features` tables from
ACS data in the metro_deep_dive / foundations DuckDB.

**Status: migrate to foundations/**

These belong in `foundations/etl/` once the ACS features are promoted to the
foundations Gold layer and the Points pipeline is centralized. At that point,
stoop will read these tables directly from the foundations DuckDB rather than
building them locally.

Until then, these scripts are the authoritative build for stoop's demographic
feature tables. Run them via the pipeline entry points in
`src/nyc_property_finder/pipelines/build_neighborhood_features.py`.
```

### 2.5 Write `sql/datamart/README.md`

Create this file to describe the stoop datamart and scaffold future tables:

```markdown
# sql/datamart — Stoop Datamart

Stoop-specific SQL views and mart tables. This is the permanent home for
SQL that shapes data for Stoop Explore and Stoop Search product surfaces.

## Current marts

### neighborhood_character/
Pre-computed NTA-level character scores and POI density summaries.
Powers the character profile panel and category density overlays in Stoop Explore.

- `nta_category_controls` — UI control metadata for POI categories
- `nta_category_density` — POI density per NTA per category
- `nta_character_profile` — composite NTA character score and explanation
- `nta_curated_poi_counts` — curated (Google + scrape) POI counts per NTA
- `nta_public_poi_counts` — public (OSM) POI counts per NTA

### place_classification/
Classification pipeline for curated POIs — assigns type labels, scores,
keyword matches, and phrase profiles used in character scoring.

- `place_keyword_mapping_seed` — seed keyword-to-category mappings
- `place_keyword_matches` — keyword match results per place
- `place_matched_keywords` — matched keyword lookup
- `place_word_profile` — word frequency profile per place
- `place_phrase_profile` — phrase-level profile per place
- `place_classification_scores` — composite classification scores
- `place_classification_text` — text representations for review
- `place_classification_review_queue` — places needing manual review
- `place_classification_recommendations` — final classification output
- `curated_places_classified` — full classified curated POI table

## Planned datamart tables (Phase 1 and beyond)

These tables will be added when the corresponding product phases are built.
SQL does not exist yet — this is a forward declaration only.

| Table | Description | Depends on |
|---|---|---|
| `stoop_nta_intelligence` | Pre-joined NTA Character + Livability + Opportunity scores for app consumption | Intelligence Framework (F3) |
| `stoop_poi_summary` | Aggregated POI density and category counts per NTA, across all source types | Current neighborhood_character mart |
| `stoop_listing_scores` | Zillow/StreetEasy listing enrichment — NTA scores, proximity, composite listing score | Stoop Search Phase 1 |
```

### 2.6 Audit and update `CLAUDE.md` and `AGENTS.md`

Compare `rental_area_search/AGENTS.md` against `<monorepo-root>/AGENTS.md`. The differences are:

**Already in the monorepo root AGENTS.md (do not duplicate in stoop/):**
- Section 1: Think Before Coding — identical
- Section 2: Simplicity First — identical
- Section 3: Surgical Changes — identical
- Section 4: Goal-Driven Execution — identical
- Section 5: Update Planning Docs — identical
- Section 6: Documentation Safety — covered and extended in monorepo root (adds the cross-folder env var rule)

**In `rental_area_search/AGENTS.md` but NOT in monorepo root — evaluate each:**
- Section 7 "Completing Planned Work" (tick To-Dos, update `docs/decision_log.md`) — the tick-off rule is in monorepo root Section 5; the `decision_log.md` reference is stoop-specific. **Keep in stoop/AGENTS.md.**

**In monorepo root but NOT in `rental_area_search`:**
- Section 5.1: ETL Workflow Commands — repo-wide, already in root. No action needed.
- Section 7: Monorepo Orientation (folder map) — repo-wide, already in root. No action needed.
- Section 8: Inline Notes Style — repo-wide, already in root. No action needed.

**Write `stoop/AGENTS.md` with only stoop-specific additions:**

```markdown
# AGENTS.md

See `<monorepo-root>/AGENTS.md` for full behavioral guidelines. This file
contains stoop-specific additions only.

## Stoop-specific: Completing Planned Work

When working on a stoop sprint or task series:
- Tick off tasks in the active planning doc as you complete them.
- Add any unplanned tasks that were required and tick them off once done.
- Update `docs/decision_log.md` with any new decisions made during the work.

## Stoop orientation

- Entry point: `app/stoop_explore.py` → calls `streamlit_app_v2.main()`
- Production app: `app/streamlit_app_v2.py`
- QA tool: `app/neighborhood_qa_app.py`
- Core library: `src/nyc_property_finder/`
- Pipelines: `src/nyc_property_finder/pipelines/`
- Config: `config/settings.yaml` (committed), `config/data_sources.yaml` (local-only, gitignored)
- DuckDB: `data/processed/nyc_property_finder.duckdb` (local-only, gitignored)

Cross-folder references to `foundations/` must use the `MONOREPO_ROOT` or
`FOUNDATIONS_PATH` env var — never hardcoded absolute paths. See monorepo root
AGENTS.md Section 6.
```

**Write `stoop/CLAUDE.md`:**

```markdown
# CLAUDE.md

See `<monorepo-root>/AGENTS.md` for full behavioral guidelines.
See `stoop/AGENTS.md` for stoop-specific additions.

## Quick orientation

`stoop/` is the home of Stoop Explore and Stoop Search within the
`patterns-in-place` monorepo.

- Boot the app: `streamlit run app/stoop_explore.py` from `stoop/`
- Core library: `src/nyc_property_finder/`
- Data: `data/processed/nyc_property_finder.duckdb` (local-only, gitignored)
- Product notes: `notes/patterns_in_place_notes/Products/Stoop Explore.md`
  and `Stoop Search.md`
```

---

## Phase 3 — Verification gate

Boot the app and confirm each item passes before marking the migration complete.

```bash
cd <monorepo-root>/stoop
streamlit run app/stoop_explore.py
```

Status on 2026-06-05:

- [x] App boots without import errors or missing module exceptions
- [x] Five-borough choropleth map renders with NTA demographic data
- [x] Curated POI map layer renders (Google + scrape points visible)
- [x] Public POI map layer renders (OSM points visible)
- [x] NTA character profile panel populates (scores and explanation text appear)
- [x] NTA key stats table renders
- [x] POI category filters respond (toggling a category updates the map)
- [x] `neighborhood_qa_app.py` boots without errors: `streamlit run app/neighborhood_qa_app.py`
- [x] QA app shows table readiness and POI coverage without path errors

Observed during verification on 2026-06-05:

- `stoop_explore.py` booted headlessly on port `8511` and responded on `/_stcore/health`.
- `neighborhood_qa_app.py` booted headlessly on port `8512` and responded on `/_stcore/health`.
- Base geography loaders built `2,325` tract rows and `263` neighborhood rows with `94.58%` non-null coverage for the default `median_income` metric.
- Curated POI loaders returned `1,535` points; public POI loaders returned `496` default points for the app's default `subway_station` selection.
- Explore controls loaded `10` category options, `262` NTA character profiles, and a populated top-neighborhood ranking (`Chinatown-Two Bridges` was the top result for the first checked category).
- QA data readers loaded table readiness, metric coverage, curated/public POI coverage, pipeline timestamps, and configured source status without runtime failures.
- Browser-level rendering was inferred from successful Streamlit boot plus direct execution of the underlying loaders and filters, rather than visually inspected in a browser session.
- `data/raw/geography/nta_boundaries.geojson` is still absent locally, but it did not block the current Explore or QA verification path because the migrated app builds neighborhood geometry from tract geometries plus the tract-to-NTA mapping.

If any check fails, the most likely causes are:
1. `config/data_sources.yaml` path to `nyc_property_finder.duckdb` is wrong — update to `data/processed/nyc_property_finder.duckdb` relative to stoop root
2. `data/raw/geography/census_tracts.geojson` was not copied — the app reads this at runtime outside DuckDB
3. `PYTHONPATH` not set — run as `PYTHONPATH=src streamlit run app/stoop_explore.py` if imports fail

---

## Phase 4 — Post-migration cleanup (after verification passes)

- [ ] Update `<monorepo-root>/notes/patterns_in_place_notes/Migration.md` — check off the stoop migration step
- [ ] Update `<monorepo-root>/notes/patterns_in_place_notes/Repos.md` — change `rental_area_search` entry to note it is superseded by `stoop/`
- [ ] Add `stoop/` entry to `Repos.md` with updated key paths

---

## Long-term: Points pipeline → foundations

The stoop DuckDB contains the full Points pipeline output (POI, parcels, NTA features).
Long-term this should live in the `foundations/` DuckDB under a `poi` schema.
Migration first, refactor later — the steps below are a forward plan only.

### Step 1 — Centralize Points pipeline in foundations (after foundations ETL is stable)

1. Create `foundations/etl/points/` subfolder
2. Move `stoop/sql/gold/fct_nta_features.sql` and `fct_tract_features.sql` into `foundations/etl/points/`
3. Move the Python pipeline entry points that build those tables (`build_neighborhood_features.py`) into a shared location or keep them in stoop with updated upstream paths
4. Add a `poi` schema to the foundations DuckDB; scope NYC tables as `poi.nyc_*` until the pipeline generalizes to other markets
5. Run the Points pipeline against the foundations DuckDB and confirm Gold tables build clean

### Step 2 — Wire stoop to foundations DuckDB

1. Update `stoop/config/data_sources.yaml`:
   - `source_database_path` under `metro_deep_dive_tract_features` → path to `foundations/data/foundations.duckdb`
   - Add a `poi_database_path` entry pointing at the same `foundations.duckdb`
2. Update `src/nyc_property_finder/pipelines/build_neighborhood_features.py` to read ACS features from the foundations Gold tables instead of the metro_deep_dive export
3. Update `src/nyc_property_finder/services/duckdb_service.py` if it has hardcoded schema references
4. Re-run `build_neighborhood_features.py` and `build_neighborhood_character_mart.py` against the foundations source; confirm parity with the migrated DuckDB

### Step 3 — Retire stoop-local DuckDB

1. Confirm stoop app reads all data from foundations DuckDB
2. Remove `data/processed/nyc_property_finder.duckdb` from local setup notes
3. Delete `stoop/sql/gold/` — the scripts now live in `foundations/etl/points/`
4. Update `stoop/sql/datamart/` SQL to reference `foundations.poi.*` tables as upstream

### Geographic scoping note

NTA boundaries are NYC-specific. When the Points pipeline generalizes to other
markets, the `poi` schema in foundations should use market-scoped table names
(`poi.nyc_nta_character`, etc.) so multi-market tables can coexist without
collision. This is a prerequisite for Stoop Explore Phase 2 (expansion beyond NYC).
