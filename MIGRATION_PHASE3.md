# Phase 3 Migration: metro-deep-dive, exploration, area-explorer

Migration of existing notebooks, apps, and prototype code into the three remaining
product folders. The goal is fast: copy the right files to the right places, fix
the minimum required environment variable pointers, and move on to new builds.
Do not spend time making old notebooks run perfectly — the long-term value here
is in the new builds these folders will eventually house.

**Rule:** Copy files in; do not modify or delete source repos until all product
folders are verified to exist and contain the right files.

---

## Folder purposes (quick reference)

| Folder | Purpose | Build status |
|---|---|---|
| `metro-deep-dive/` | Market-specific deep dives — structured, repeatable, publishable. Wilmington and Jacksonville notebooks are the prototypes. | Migration only; new builds depend on F3 + F5 (Phase 8) |
| `exploration/` | Ad hoc analysis that isn't structured toward a published output — national metric EDA, one-off studies | Migration only; add new notebooks here as needed |
| `area-explorer/` | Interactive CBSA exploration tool — the data platform's research surface | Bare-bones MVP copied in; full build is Phase 2 in the roadmap |

---

## Status

Completed in the monorepo on 2026-06-06.

- [x] Copied the shared R utility files into `foundations/etl/R/`
- [x] Migrated the ROF app, source library, tests, and market notebooks into `metro-deep-dive/`
- [x] Migrated ad hoc notebooks into `exploration/`
- [x] Migrated the Area Explorer MVP into `area-explorer/`
- [x] Added the minimum README files for all three product folders
- [x] Removed copied generated artifacts like notebook `outputs/` folders and shapefile cache directories

Unplanned but required:

- [x] Adjusted the shared R utility destination from `foundations/R/` to `foundations/etl/R/` to match the monorepo's existing ETL layout

## What does NOT belong here — already in `foundations/`

The R utility functions in `metro_deep_dive/R/` are shared infrastructure, not
metro-deep-dive-specific. They belong in `foundations/etl/R/` alongside the ETL.

| Asset | Source | Destination |
|---|---|---|
| `acs_drop_moe.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |
| `acs_ingest.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |
| `acs_standardize_cols.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |
| `add_growth_cols.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |
| `benchmark_summary.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |
| `generic_functions.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |
| `rebase_cbsa_from_counties.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |
| `standardize_acs_df.R` | `metro_deep_dive/R/` | `foundations/etl/R/` |

Copy these as part of this migration so `foundations/etl/R/` is complete. Any notebook
that sources these files will need its `source()` path updated to point at
`foundations/etl/R/` — flag these but do not fix them now (notebooks are not expected
to run immediately post-migration).

Note: six of these files were already present in `foundations/etl/R/`; this phase added the missing `acs_drop_moe.R` and `acs_standardize_cols.R`.

---

## Target structures

### `metro-deep-dive/`

```
metro-deep-dive/
├── app/                     ← ROF Streamlit apps; prototype for Metro Deep Dive interactive surface
│   ├── zone_explorer_app.py
│   ├── retail_parcel_explorer_app.py
│   └── data_qa_app.py
├── src/
│   └── retail_opportunity_finder/   ← ROF core library; zone scoring, parcel transforms, geo utils
├── sql/                     ← ROF DDL and queries
│   └── ddl/
├── config/                  ← ROF config; data_sources.example.yaml committed, data_sources.yaml gitignored
├── markets/
│   ├── jacksonville/        ← ROF notebook sequence; zone/parcel prototype
│   │   ├── 01_setup/
│   │   ├── 02_market_overview/
│   │   ├── 03_eligibility_scoring/
│   │   ├── 04_zones/
│   │   ├── 05_parcels/
│   │   ├── 06_conclusion_appendix/
│   │   ├── _shared/
│   │   └── OUTPUT_CONTRACTS.md
│   └── wilmington/          ← narrative deep dive notebooks
│       ├── wilmington_overview.Rmd
│       └── wilmington_geo_built_env.Rmd
├── tests/                   ← ROF test suite
├── templates/               ← empty scaffold; generalized report template built here (Phase 8)
├── requirements.txt
└── README.md
```

### `exploration/`

```
exploration/
├── national_analyses/       ← cross-CBSA metric EDA; one-off national studies
│   ├── eda/
│   └── real_personal_income/
├── tx_school_districts/     ← TX ISD analysis; not a generalizable deep dive template
│   ├── data/
│   ├── school_district_scoring.Rmd
│   └── tx_isd_lead_scoring_report.Rmd
└── README.md
```

### `area-explorer/`

```
area-explorer/
├── app/
│   ├── data_explorer.py     ← copied from metro_deep_dive_chatbot/reference_dashboard/
│   └── explorer_utils.py    ← already wired to DB_CONNECTION env var
└── README.md
```

---

## Phase 1 — File copy

### 1.1 R utilities → `foundations/etl/R/`

```bash
SRC=<local-projects-root>/metro_deep_dive
DEST=<monorepo-root>/foundations/etl

mkdir -p $DEST/R
cp $SRC/R/acs_drop_moe.R             $DEST/R/
cp $SRC/R/acs_ingest.R               $DEST/R/
cp $SRC/R/acs_standardize_cols.R     $DEST/R/
cp $SRC/R/add_growth_cols.R          $DEST/R/
cp $SRC/R/benchmark_summary.R        $DEST/R/
cp $SRC/R/generic_functions.R        $DEST/R/
cp $SRC/R/rebase_cbsa_from_counties.R $DEST/R/
cp $SRC/R/standardize_acs_df.R       $DEST/R/
```

Do NOT copy `metro_deep_dive/R/visual/` — those are in `foundations/visual_library/` already.

### 1.2 `metro-deep-dive/` — ROF app + notebooks

```bash
MDD_SRC=<local-projects-root>/metro_deep_dive
ROF_SRC=<local-projects-root>/retail_opportunity_finder
DEST=<monorepo-root>/metro-deep-dive

mkdir -p $DEST/app
mkdir -p $DEST/src
mkdir -p $DEST/sql
mkdir -p $DEST/config
mkdir -p $DEST/markets/jacksonville
mkdir -p $DEST/markets/wilmington
mkdir -p $DEST/tests
mkdir -p $DEST/templates

# ROF app — Streamlit apps and source library
cp $ROF_SRC/app/zone_explorer_app.py          $DEST/app/
cp $ROF_SRC/app/retail_parcel_explorer_app.py $DEST/app/
cp $ROF_SRC/app/data_qa_app.py                $DEST/app/
cp -r $ROF_SRC/src/retail_opportunity_finder/ $DEST/src/retail_opportunity_finder/
cp -r $ROF_SRC/sql/                           $DEST/sql/
cp    $ROF_SRC/config/data_sources.example.yaml $DEST/config/
cp    $ROF_SRC/config/settings.yaml             $DEST/config/
cp -r $ROF_SRC/tests/                          $DEST/tests/
cp    $ROF_SRC/requirements.txt                $DEST/

# Jacksonville — ROF notebook sequence (zone/parcel prototype)
cp -r $MDD_SRC/notebooks/retail_opportunity_finder/sections/01_setup/              $DEST/markets/jacksonville/01_setup/
cp -r $MDD_SRC/notebooks/retail_opportunity_finder/sections/02_market_overview/    $DEST/markets/jacksonville/02_market_overview/
cp -r $MDD_SRC/notebooks/retail_opportunity_finder/sections/03_eligibility_scoring/ $DEST/markets/jacksonville/03_eligibility_scoring/
cp -r $MDD_SRC/notebooks/retail_opportunity_finder/sections/04_zones/              $DEST/markets/jacksonville/04_zones/
cp -r $MDD_SRC/notebooks/retail_opportunity_finder/sections/05_parcels/            $DEST/markets/jacksonville/05_parcels/
cp -r $MDD_SRC/notebooks/retail_opportunity_finder/sections/06_conclusion_appendix/ $DEST/markets/jacksonville/06_conclusion_appendix/
cp -r $MDD_SRC/notebooks/retail_opportunity_finder/sections/_shared/               $DEST/markets/jacksonville/_shared/
cp    $MDD_SRC/notebooks/retail_opportunity_finder/sections/OUTPUT_CONTRACTS.md    $DEST/markets/jacksonville/

# Wilmington — narrative deep dive notebooks
cp $MDD_SRC/notebooks/wilmington_overview.Rmd       $DEST/markets/wilmington/
cp $MDD_SRC/notebooks/wilmington_geo_built_env.Rmd  $DEST/markets/wilmington/
```

### 1.3 `exploration/` — ad hoc notebooks

```bash
SRC=<local-projects-root>/metro_deep_dive
DEST=<monorepo-root>/exploration

# National analyses — cross-CBSA EDA
cp -r $SRC/notebooks/national_analyses/  $DEST/national_analyses/

# TX school districts — one-off study
cp -r $SRC/notebooks/tx_school_districts/ $DEST/tx_school_districts/
```

### 1.4 `area-explorer/` — bare-bones MVP

```bash
SRC=<local-projects-root>/metro_deep_dive_chatbot/reference_dashboard
DEST=<monorepo-root>/area-explorer

mkdir -p $DEST/app
cp $SRC/data_explorer.py   $DEST/app/
cp $SRC/explorer_utils.py  $DEST/app/
```

---

## Phase 2 — Minimum required fix: `area-explorer/` DB path

`explorer_utils.py` already reads `DB_CONNECTION` from the environment with a
fallback to a hardcoded local path. The fallback path (`parent.parent / "data" / "duckdb" / "metro_deep_dive_runtime.duckdb"`) will resolve incorrectly in the new location. The env var is already the right mechanism — just ensure it's set.

**No code change needed.** Just set the env var before running:

```bash
export DB_CONNECTION=<absolute-path-to-monorepo>/foundations/data/foundations.duckdb
```

Or if using the metro_deep_dive DuckDB locally in the interim:

```bash
export DB_CONNECTION=<local-projects-root>/metro_deep_dive/data/duckdb/metro_deep_dive_runtime.duckdb
```

Document the required env var in `area-explorer/README.md` (see Phase 3).

**That's the only required change.** Do not attempt to make the app run fully
against the foundations DuckDB until the foundations ETL is complete — the app
may show empty charts or missing metrics until then, and that's acceptable.

---

## Phase 3 — Write README files

These are the minimum context files needed so the folders make sense when you
return to them. Keep them short.

### `metro-deep-dive/README.md`

```markdown
# metro-deep-dive

Long-form, market-specific deep dives. Structured, repeatable, and publishable.

## What's here

- `app/` — ROF Streamlit apps (zone explorer, parcel explorer, data QA). The
  working prototype for the Metro Deep Dive interactive surface.
- `src/retail_opportunity_finder/` — ROF core library: zone scoring, parcel
  transforms, geo utilities. Reference material for the future generalized build.
- `markets/jacksonville/` — ROF notebook sequence; the full zone/parcel prototype.
  Sections: setup, market overview, eligibility scoring, zones, parcels, conclusion.
- `markets/wilmington/` — narrative overview and built-environment notebooks.
- `templates/` — empty; generalized market-agnostic report template built here
  (Phase 8, depends on F3 Intelligence Catalog + F5 Zones datamart).

## Running the ROF apps

These apps are migration-state reference — not expected to run cleanly without
path updates. When ready to explore:

```bash
cd <monorepo-root>/metro-deep-dive
PYTHONPATH=src streamlit run app/zone_explorer_app.py
```

Config lives in `config/data_sources.yaml` (local-only, gitignored). Copy from
`config/data_sources.example.yaml` and set `source_database_path` to your local
DuckDB path.

## R utilities

Shared R functions live in `foundations/R/`. Source them from there, not from
the old `metro_deep_dive/R/` path.
```

### `exploration/README.md`

```markdown
# exploration

Ad hoc analysis, one-off studies, and EDA that isn't structured toward a
publishable deep dive. This folder never ships.

## Contents

- `national_analyses/` — cross-CBSA metric EDA; national trend and income studies
- `tx_school_districts/` — TX ISD lead scoring analysis

## Usage

Add new ad hoc notebooks here. If a notebook grows into something structured and
repeatable, promote it to `metro-deep-dive/markets/` or a product folder.
```

### `area-explorer/README.md`

```markdown
# area-explorer

Interactive CBSA exploration tool. The research surface for the data platform —
exploratory and iterative, not a publishing pipeline.

## Current state

Bare-bones MVP: `app/data_explorer.py` and `app/explorer_utils.py` copied from
`metro_deep_dive_chatbot/reference_dashboard/`. Supports CBSA choropleth and
metric picker over the Gold layer.

## Running the app

```bash
export DB_CONNECTION=<absolute-path-to>/foundations/data/foundations.duckdb
cd <monorepo-root>/area-explorer
PYTHONPATH=app streamlit run app/data_explorer.py
```

## Build roadmap

- Phase 1 (current): CBSA choropleth + metric picker + ranking table — runnable
  on existing Gold tables today
- Phase 2: Intelligence Frames (Character, Livability, Opportunity) — depends on
  F3 + F5
- Phase 3: Zone layer (tract-level clusters) — depends on F5 zones datamart

See `notes/patterns_in_place_notes/Products/Area Explorer.md` for the full
phase plan and discovery analysis map.
```

---

## Completion summary

The migration assets are now in place in the monorepo with the minimum cleanup needed to make the new product folders legible:

- `metro-deep-dive/` contains the ROF prototype apps, source library, tests, Jacksonville notebook sequence, Wilmington notebooks, and a top-level README
- `exploration/` contains the national analyses and TX school district notebooks plus a README
- `area-explorer/` contains the MVP app files plus a README documenting the required `DB_CONNECTION` env var
- `foundations/etl/R/` now has the full shared helper set expected by the older metro deep-dive notebooks

Follow-up work intentionally left for later:

- updating legacy notebook `source()` paths from `metro_deep_dive/R/` to `foundations/etl/R/`
- making the migrated apps and notebooks fully runnable against the monorepo data platform

## Leave behind (do not copy from any source repo)

| File / folder | Reason |
|---|---|
| `metro_deep_dive/R/visual/` | In `foundations/visual_library/` |
| `metro_deep_dive/scripts/etl/` | In `foundations/etl/` |
| `metro_deep_dive/visual_library/` | In `foundations/visual_library/` |
| `metro_deep_dive/config/` | Stale; `visual_registry.yml` already in `foundations/` |
| `metro_deep_dive/products/` | Stale product-level experiments |
| `metro_deep_dive/documents/` | Stale DB design docs |
| `metro_deep_dive/outputs/` | Generated artifacts |
| `metro_deep_dive/notebooks/retail_opportunity_finder/data_platform/` | Platform docs — superseded by monorepo |
| `metro_deep_dive/notebooks/retail_opportunity_finder/legacy/` | Stale |
| `retail_opportunity_finder/config/data_sources.yaml` | Gitignored — copy manually to `metro-deep-dive/config/data_sources.yaml` and update paths |
| `retail_opportunity_finder/app/__pycache__/` | Generated |
| `retail_opportunity_finder/data/` | Local data files — gitignored, re-derivable |
| `retail_opportunity_finder/docs/` | Stale planning docs — superseded by monorepo notes |
| `retail_opportunity_finder/scripts/` | One-off scripts — omit |
| `metro_deep_dive_chatbot/reference_dashboard/__pycache__/` | Generated |
