# Context Layer
This document is the shared context for the Patterns in Place projects. It includes the Metro Deep Dive, Stoop NYC, and Metro Deep Dive Chatbot repos.

# Metro Deep Dive — Platform Context

This section is the shared context anchor for work across the Metro Deep Dive platform and its related project repos. It is written to give an AI agent or new collaborator a complete working picture without needing to read the full repo.

---

## What This Platform Is

`metro_deep_dive` is a shared analytics platform and product workspace for US metro-level and national demographic and economic data products.

It serves four functions:

1. **Shared platform** — reusable ETL, analytics functions, documentation, and a visual system used across products and analyses
2. **Active product development** — Retail Opportunity Finder (flagship), US Demographic Chatbot (in development), Texas School District analysis (secondary)
3. **Data warehouse** — a medallion architecture DuckDB warehouse built from public US datasets
4. **Semantic and visual infrastructure** — a data dictionary, metric catalog, and visual library intended to support both human workflows and AI-assisted analytics

---

## Data Architecture

### Medallion Layers

| Layer | Purpose | Location |
|---|---|---|
| Bronze | Raw extracts, source CSVs, API outputs — preserved as-is | `data/` |
| Staging | Source-shaped landed tables; one family doc per source/theme, not one doc per geography replica | `scripts/etl/staging/`, `schemas/data_dictionary/layers/staging/` |
| Silver | Standardized, lightly transformed, analysis-ready wide tables with consistent geo/time keys | `scripts/etl/silver/`, `schemas/data_dictionary/layers/silver/` |
| Gold | Curated cross-domain marts and decision-ready KPIs; primary query target for products | `scripts/etl/gold/`, `schemas/data_dictionary/layers/gold/` |

**Key conventions:**
- Silver ACS tables follow a `<theme>_base` / `<theme>_kpi` pair pattern
- Gold default grain is always `(geo_level, geo_id, geo_name, year)` — `period` is reserved for non-ACS economic series
- Gold is built in DuckDB SQL first; R is used only where SQL becomes procedurally awkward
- CBSA is derived from 2023 Census county membership with county-to-CBSA rebasing

### Geography Hierarchy

```
Census Tract → County → CBSA → State → Division → Region → US
```

All Gold tables carry `(geo_level, geo_id, geo_name, year)` as the primary key grain. Crosswalks live in `silver.xwalk_*` tables.

**Supported geography grains:** US, Region, Division, State, CBSA, County, Census Place, Census Tract, ZCTA

---

## Data Sources In Scope

| Source | What It Provides |
|---|---|
| ACS (Census Bureau) | Age, race, education, income, labor, housing, migration, transportation, social infrastructure — 5-year rolling estimates via `tidycensus` |
| BEA Regional API | GDP by metro, personal income, Regional Price Parity (MARPP) |
| BLS | Labor force and unemployment (LAUS); QCEW is a later candidate |
| BPS (Census Bureau) | Building permits by metro |
| HUD | Fair Market Rent (FMR), rent burden (CHAS) |
| Zillow | ZHVI (home values), ZORI (observed rent index) — public CSVs |
| IRS | County-to-county migration flows — planned v1.1 |
| TIGER/Line + Census | Geography geometries, crosswalk tables |
| Later candidates | FEMA, FHFA, NOAA, CHR, IPEDS |

---

## Gold Layer — Current Tables

These Gold tables are implemented and documented in `schemas/data_dictionary/layers/gold/`:

| Table | Domain | Key Inputs |
|---|---|---|
| `gold.population_demographics` | Population, age, race, education | ACS |
| `gold.economics_income_wide` | Income, earnings, RPP | ACS, BEA |
| `gold.economics_gdp_wide` | GDP by metro | BEA |
| `gold.economics_labor_wide` | Labor force, unemployment | ACS, BLS LAUS |
| `gold.economics_industry_wide` | Sector shares, HHI, GDP by industry | BEA |
| `gold.housing_core_wide` | Vacancy, tenure, rent, home value, permits, burden | ACS, HUD FMR, BPS |
| `gold.affordability_wide` | Rent-to-income, value-to-income, FMR gap | Gold housing + income |
| `gold.migration_wide` | ACS mobility shares, nativity (IRS flows deferred) | ACS |
| `gold.transport_built_form_wide` | Drive alone, transit, WFH, commute time, no-vehicle | ACS |
| `gold.tx_isd_metrics` | Texas school district metrics | ACS + ISD data |

**Normalization supplements:** Separate supplemental Gold tables for z-scores, percentiles, and min-max values — not embedded in base marts.

---

## Advanced Composite Scores (Planned)

These scores are in design; none are in production yet. They depend on completing base Gold marts and getting weights approved.

- `affordability_score` — rent/value to income, burden, FMR gap, RPP adjustment
- `housing_market_overheating_index` — price/rent growth vs income growth, permit intensity, vacancy trend
- `economic_strength_index` — income per capita, real GDP growth, employment strength
- `industry_concentration_score` — sector shares, HHI, location quotients
- `migration_attractiveness_score` — inflow/outflow, net migration, origin breadth
- `quality_of_life_index` — broadband, transit, WFH, higher-ed, health outcomes
- `risk_resilience_index` — FEMA NRI, flood/heat risk (blocked on source ingestion)
- `investment_score` — composite of all above (last to ship)

---

## Visual Library

**Location:** `visual_library/`

A reusable visual system combining chart specifications, shared R prep/render functions, data contract standards, benchmark defaults, and sample SQL/outputs.

**15 chart types implemented** (each has spec, question coverage doc, sample SQL, sample output, decisions log):
bar, line, scatter, choropleth, slopegraph, bump chart, heatmap table, age pyramid, hexbin, highlight context map, proportional symbol map, bivariate choropleth, correlation heatmap, strength strip, boxplot

**Key files:**
- `visual_library/README.md` — primary entry point and source-of-truth hierarchy
- `visual_library/visual_style_guide_and_standards.md` — canonical visual rules
- `visual_library/sample_library.md` — chart catalog and canonical question patterns
- `visual_library/agent.md` — chart build workflow for agents
- `visual_library/shared/` — shared `prep_*.R`, `render_*.R`, `standards.R`, `data_contracts.R`
- `visual_library/contracts/data_contract_dictionary.md` — shared contract vocabulary
- `visual_library/benchmark_defaults.md` — default benchmark sets by geography

**Tech:** R + ggplot2. All chart outputs are PNG. Charts accept a structured data contract from `prep_*.R` functions before rendering.

---

## Products

### 1. Retail Opportunity Finder (ROF)
**Status:** Flagship product, most mature. Has modular section architecture, integration flow, output contracts, and a published MVP payload.

**Location:** `notebooks/retail_opportunity_finder/`, `docs/rof-mvp/`

**Purpose:** Identify, score, zone, and shortlist retail opportunity areas and parcels by market.

**Sections:** 01–06 modular sections with SQL feature queries, shared runtime/config, validation summaries, and published output.

---

### 2. US Demographic and Economic Analytics Chatbot
**Status:** In design/early development. Spec complete. Being planned for migration to a standalone repo.

**Location:** `products/chatbot/`

**Purpose:** A constrained analytical copilot that answers natural language questions about US demographic and economic data.

**User workflow:**
1. User enters a question
2. System parses intent, metrics, geography, timeframe
3. Maps to approved semantic layer metadata
4. Generates SQL against Gold tables
5. Validates SQL
6. Executes query
7. Profiles result shape
8. Selects chart type
9. Renders chart via visual library
10. Returns: written answer + chart + table + SQL + metric definitions

**Tech stack:**
- Backend: Python + FastAPI
- Frontend: Streamlit (MVP)
- Data layer: DuckDB querying Gold schema
- LLM: Claude API (intent parsing, query planning, constrained SQL generation, chart selection, response writing)
- Visualization: R visual library (ggplot2)

**Design principles:** Reliability over openness, transparent analytics (SQL always visible), controlled SQL generation (grounded in metadata — no free-form LLM invention), visual consistency, iterative scope.

**MVP subject areas:** Population, income/earnings, housing/rent, labor market, education, migration

**MVP chart types:** Bar, line, scatter, choropleth, boxplot, histogram, heatmap table, highlight context map

**Chatbot docs:**
- `products/chatbot/README.md` — product overview
- `products/chatbot/us_demographic_economic_analytics_chatbot_spec.md` — full product spec
- `products/chatbot/MIGRATION.md` — guide for standing up as a standalone repo
- `products/chatbot/docs/` — architecture, semantic layer, frontend, visual library integration

---

### 3. Texas School District Analysis
**Status:** Secondary analysis track, partial. Two notebooks, one rendered output map.

**Location:** `notebooks/tx_school_districts/`

**Purpose:** School district scoring and reporting using ACS and ISD data. Has its own Gold table (`gold.tx_isd_metrics`).

---

## Shared Platform Code

**R functions:** `R/` — reusable analytics functions used across the pipeline
- `R/acs_ingest.R`, `R/acs_standardize_cols.R`, `R/acs_drop_moe.R` — ACS ingestion utilities
- `R/add_growth_cols.R`, `R/benchmark_summary.R` — analytics helpers
- `R/rebase_cbsa_from_counties.R` — CBSA rebasing logic
- `R/visual/` — shared chart prep/render functions (mirrors `visual_library/shared/`)

**Scripts:** `scripts/etl/` — named ETL workflow scripts (ingest, standardize, model, QA, publish)

**Config:** `config/project.yml` — project configuration including GEOID, year range, feature toggles

**Tests:** `scripts/testthat.R` and `tests/` — testthat-based automated checks; CI runs on push/PR to main via `.github/workflows/ci.yml`

---

## Data Dictionary

**Location:** `schemas/data_dictionary/`

The durable metadata layer for the warehouse. Covers:
- Table-level metadata: purpose, grain, keys, time coverage, geo coverage
- Column-level metadata: type, null %, distinct count, definitions
- Lineage: upstream sources, ETL scripts, write targets
- KPI definitions

**Structure:** Each Silver and Gold table has a YAML + Markdown pair (`<schema>__<table>.yml` and `.md`). Staging uses family-level contracts rather than one file per geography replica.

**Key governance docs:**
- `schemas/data_dictionary/docs/governance/coverage_checklist.md`
- `schemas/data_dictionary/docs/governance/data_quality_checklist.md`
- `schemas/data_dictionary/agent.md` — how agents should use and update the dictionary

---

## Semantic Layer (In Progress)

The chatbot requires a machine-readable semantic layer that the warehouse does not yet fully expose. Planned components:

- **Metric catalog** — name, definition, formula, valid grains, source table, caveats
- **Table catalog** — schema, grain, time field, geography fields, subject area
- **Join catalog** — approved join paths, keys, cardinality notes
- **Geography hierarchy catalog** — Tract → County → CBSA → State → Region relationships
- **Chart recommendation rules** — maps question type + result shape to allowed chart types
- **Example question library** — tagged NL questions, sample SQL, chart type, expected output

---

## Current Implementation Status

| Area | Status |
|---|---|
| Bronze/Staging ingestion | Working; staging docs being standardized to family-level contracts |
| Silver layer | Mostly complete; social infrastructure Silver still in progress; CAINC4 bug pending fix |
| Gold base marts | 9 tables complete as of April 2026 |
| Gold normalization supplements | Planned; not started |
| Gold composite scores | Design complete; blocked on base mart stability and weight approvals |
| Visual library | All 15 chart types structurally present; shared layer mature; some chart implementations still partial |
| ROF product | Working MVP; sections 01–03 most portable; 04–06 still transitional |
| Chatbot product | Spec and architecture complete; migration to standalone repo in progress |
| Texas school districts | Partial; secondary track |
| Semantic layer for chatbot | Not yet built |

---

## Cross-Repo Connection Points

If you are working in a downstream repo (e.g., the chatbot repo), the interfaces to this platform are:

| Interface | What It Is | Location in this repo |
|---|---|---|
| DuckDB Gold layer | Primary query target; `.duckdb` file or Parquet exports | `data/` or specified output path |
| Gold table specs | YAML + Markdown table contracts | `schemas/data_dictionary/layers/gold/` |
| Visual library | R-based chart functions; call `prep_*.R` then `render_*.R` | `visual_library/shared/` and `R/visual/` |
| Example question library | Tagged NL questions with SQL and chart types | `products/chatbot/data/` |
| Gold SQL definitions | Source SQL models for all Gold tables | `scripts/etl/gold/` |
| Config conventions | Geo level codes, field naming, grain standards | `DBDesign.md`, `schemas/data_dictionary/` |

---

## Key Conventions Quick Reference

- **Geo key fields:** `geo_level`, `geo_id`, `geo_name`
- **Time field:** `year` (default); `period` only for non-ACS BEA/BLS series
- **CBSA:** Derived from 2023 county membership; rebased from county data where direct CBSA values are unavailable
- **Silver pattern:** `<theme>_base` (ACS-aligned) + `<theme>_kpi` (business semantics)
- **Gold pattern:** Wide tables per domain; supplement tables for normalization; composite scores separate
- **RPP backfill order:** County → CBSA → State MARPP
- **Geo scope for ratios (e.g., rent-to-income):** Compute for all supported geographies
- **IRS migration:** Not in Gold v1; ACS mobility and nativity ship first
- **Zillow:** Supplement Gold table, not integrated into housing_core_wide v1
- **Language preference:** SQL first (DuckDB); R where SQL is awkward; Python only as last resort

# Platform Context — Stoop NYC & Demographic Data Projects

Last updated: 2026-05-10

This section is the shared context file for a Claude project that spans multiple
repos. It covers the full platform ecosystem, how the repos relate, current state
in each, and conventions an agent needs to work effectively across them.

---

## Ecosystem Overview

Three repos form an interconnected demographic and real estate data platform:

| Repo | Role | Stack |
|---|---|---|
| `metro_deep_dive` | Upstream demographic data pipeline. Produces tract-level ACS metrics for any US metro. | R, DuckDB |
| `rental_area_search` | Stoop NYC — neighborhood discovery platform for NYC. Consumes `metro_deep_dive` outputs. | Python 3.12, DuckDB, Streamlit, GeoPandas |
| `retail_opportunity_finder` | Southeast US retail investment opportunity explorer. Also consumes `metro_deep_dive`. | Python 3.12, DuckDB, Streamlit, GeoPandas |

A fourth repo, `metro_deep_dive_chatbot`, provides a conversational interface to
`metro_deep_dive` data; it is less tightly coupled to the other two.

**Data flow**:
```
metro_deep_dive.duckdb  ──export──►  rental_area_search (fct_tract_features, fct_nta_features)
                        ──export──►  retail_opportunity_finder (rof_gold schema)
```

The `metro_deep_dive` DuckDB path is local-only on the developer's machine. It
is configured in each consumer repo's ignored `config/data_sources.yaml`.

---

## Shared Tech Conventions

All three consumer repos follow the same stack and patterns:

- **Database**: DuckDB with a named gold schema (`property_explorer_gold`,
  `rof_gold`). Tables are replace-first unless explicitly user-authored.
- **Geometry**: WGS84. GeoJSON geometry loaded at runtime from `data/raw/geography/`;
  not stored in DuckDB. Spatial joins run in GeoPandas/Shapely; results stored
  as WKT in DuckDB.
- **Frontend**: Streamlit + PyDeck.
- **Pipelines**: Python modules under `src/<package>/pipelines/`. Entry points
  are invoked from repo root with `PYTHONPATH=src`.
- **Config**: `config/settings.yaml` (committed), `config/data_sources.yaml`
  (local-only, gitignored). Templates in `config/data_sources.example.yaml`.
- **Proximity**: straight-line distance for MVP; walking-time proxies are deferred.
- **Linting**: Ruff.
- **Testing**: Pytest.

---

## Repo 1: `metro_deep_dive`

**Path**: `<local-projects-root>/metro_deep_dive`

**Purpose**: Modular R pipeline that ingests ACS Census data and produces a
multi-layer DuckDB with tract-level demographic and housing metrics for US
metros. This is the upstream demographic source for both `rental_area_search`
and `retail_opportunity_finder`.

**Key layers**:
- `foundation.tract_features` — raw tract-level ACS metrics
- `gold.housing_core_wide` — cleaned housing metrics per tract
- `gold.population_demographics` — cleaned population/age/education metrics per tract

**Key outputs consumed by downstream repos**:
- Median income, median rent, median home value, `pct_bachelors_plus`, median age
  — all at tract grain

**Important caveat**: as of 2026-04-17, the local `metro_deep_dive` DuckDB does
not expose NYC tract metric rows. `rental_area_search` currently materializes
Brooklyn/Manhattan tract and NTA feature rows with null metric values as an
explicit MVP fallback, and renders null metrics gracefully in the app rather than
producing false scores.

**Stack**: R, DuckDB. Parameterized by GEOID and year range in `config/project.yml`.

---

## Repo 2: `rental_area_search` (Stoop NYC)

**Path**: `<local-projects-root>/rental_area_search`
**Python package**: `nyc_property_finder` (under `src/`)
**Database**: `data/processed/nyc_property_finder.duckdb`, schema `property_explorer_gold`

### Platform Vision

Stoop NYC is a neighborhood intelligence platform for New York City. The name
reflects that a stoop is where NYC neighborhood life happens — local, intimate,
particular. The platform earns its value from a curation layer on top of public
data: personal Google Maps lists, editorial article scrapes, and crowd
contributions that no generic map product has.

### Five Data Products

| Product | Gold Table(s) | Status |
|---|---|---|
| **Curated Places** — personal and editorial place lists | `dim_user_poi_v2` | Active. Google Takeout + 19 article scrapes loaded. Hotels live. Excel upload pending. |
| **City Baseline** — open/official place data (transit, parks, everyday retail, civic) | `dim_public_poi` | Complete. 57,346 rows, 28 categories. Crime and school quality pending. |
| **Neighborhood Context** — ACS tract and NTA metrics | `fct_tract_features`, `fct_nta_features`, `dim_tract_to_nta` | Active. Five-borough geography live. Full NTA metric coverage partial (source: Metro Deep Dive). |
| **Property Listings** — listings enriched with geography, transit, POI context | `dim_property_listing`, `fct_property_context` | Placeholder. 22-row sample only. |
| **Shortlists** — user-authored saves for neighborhoods and properties | `fct_user_shortlist` | Partial. Property shortlist in on-ice Property Explorer V1. Neighborhood shortlist not built. |

### Neighborhood Character Mart

A pre-computed intelligence layer lives in the `neighborhood_character_mart` DuckDB
schema. It is rebuilt by `pipelines/build_neighborhood_character_mart.py`.

Key tables:
- `nta_category_density` — NYC percentile ranking per (NTA × category). Primary
  table for "Top neighborhoods for X" in Stoop Explore.
- `nta_character_profile` — one row per NTA with destination/strong categories,
  top category, and raw livability counts. Primary table for the neighborhood
  character panel.
- `nta_category_controls` — configuration table controlling which categories are
  surfaced in the v1 Explore UI and their evidence thresholds.

Analytics logic: curated POIs and public POIs are spatially joined to NTA
boundaries via GeoPandas (point-in-polygon), then SQL computes per-NTA density
and NYC-relative PERCENT_RANK per category. All mart outputs are pre-computed;
the app reads them directly.

### Two Apps

**Stoop Explore** (`app/stoop_explore.py`)
- Primary question: Where should I spend a day? What is this neighborhood like?
- Audience: NYC residents and suburban day-trippers exploring neighborhoods.
- Core surface: five-borough NTA map, curated POI layer, Explore intelligence
  panel ("Best neighborhoods for X", "What this neighborhood is known for"),
  hotel coverage, public POI overlays.
- Status: active. Sprint 3 surface is built. Sprint 3 launch tasks (UX review,
  smoke test, announcement) remain.
- Entry point: `app/stoop_explore.py`
- Core logic: `src/nyc_property_finder/app/base_map.py`,
  `src/nyc_property_finder/app/stoop_explore.py`

**Stoop Search** (not yet started as a standalone app)
- Primary question (Phase 1): Is this neighborhood somewhere I would like to live?
- Primary question (Phase 2): Does this specific listing work for my life?
- Audience: People evaluating NYC neighborhoods for a move.
- Phase 1 needs: crime, school quality, livability scoring. Buildable after Sprint 1 data work.
- Phase 2 needs: Property Listings data product.

### Key Pipeline Commands

```bash
# Initialize database on a new machine
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.init_database

# Build neighborhood features from Metro Deep Dive
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.build_neighborhood_features

# Rebuild City Baseline (all public POI waves)
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_public_poi

# Ingest curated POIs from Google Takeout
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_curated_poi_google_takeout

# Rebuild neighborhood character mart
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.build_neighborhood_character_mart
```

### Curated POI Taxonomy

Taxonomy is driven by `config/poi_categories.yaml`. Three fields form the
canonical taxonomy: `category / subcategory / detail_level_3`.

Three ingestion paths all write to `dim_user_poi_v2`:
1. **Google Takeout** — exported CSV lists from personal Google Maps saved places.
2. **Article Scraping** — publication parsers (Eater, Time Out) and semi-manual
   extractors for editorial sources. Entry: `pipelines/ingest_curated_poi_web_scrape.py`
3. **Excel Upload** — planned; package path reserved at `curated_poi/excel_upload/`.

Canonical grain is one row per physical location (Google Place ID). Raw exports
stay local under `data/raw/google_maps/` and must never be committed.

Current coverage (categories with ≥ 20 NYC-wide curated POIs): restaurants,
bakeries, shopping, hotels, food markets, specialty grocery, bookstores, movie
theaters, record stores. Bars and museums are close to threshold.

### Geography

- Primary neighborhood unit: NTA (Neighborhood Tabulation Area). 262 NTAs cover
  all five boroughs.
- Tract-to-NTA mapping: `dim_tract_to_nta`, built from NYC Open Data equivalency
  table `hm78-6dwm`.
- Geometry files live in `data/raw/geography/` (not committed to git):
  - `census_tracts.geojson`
  - `nta_boundaries.geojson`
  - `tract_to_nta_equivalency.csv`

### Key Decisions

| Decision | Rationale |
|---|---|
| Intelligence outputs pre-computed in DuckDB at pipeline time | Fast app reads, stable contract, reproducible validation. |
| NTA is the primary neighborhood UI language | More legible than census tracts for app users. |
| Rankings use raw POI count as primary sort, not density | Density penalizes large residential NTAs. Stored for future use. |
| Ties broken by subcategory diversity then NTA name | Rewards depth, not just mass, especially for restaurants. |
| Straight-line proximity for MVP | Simpler to implement and explain; walking-time is post-MVP. |
| Crime/safety deferred | Needs stronger source choice and careful product framing. |
| App renders null metrics gracefully | Metro Deep Dive NYC coverage is still partial; never produce false scores. |
| Google Places API used for curated POI resolution | Cache-first; resolved IDs persist locally to minimize API calls. |
| DuckDB file committed to repo for Streamlit Cloud deployment | Sufficient for current scale; MotherDuck is the scale-up path. |

### Current Sprint Status (as of 2026-05-10)

- **Sprint 1** (Data Platform Foundation): Hotels complete. Crime, school quality,
  and crowd upload still open.
- **Sprint 2** (Analysis & Intelligence Design): Explore intelligence spec
  complete. Stoop Search livability scoring design not started.
- **Sprint 3** (Stoop Explore V1 Launch): App surface built. Final UX review,
  smoke test, and public announcement remain.
- Active branch: `stoop-v1`

Full backlog: `docs/planning/current_backlog.md`

---

## Repo 3: `retail_opportunity_finder`

**Path**: `<local-projects-root>/retail_opportunity_finder`
**Database**: `data/processed/rof_app.duckdb`, schema `rof_gold`

**Purpose**: Interactive Streamlit app for exploring retail investment
opportunities across Southeast US markets. Combines census tract demographics,
cluster-based investment zones, and parcel-level data to identify and evaluate
retail sites.

**Architecture**:
```
metro_deep_dive.duckdb  ──export──►  rof_app.duckdb  ──reads──►  Streamlit apps
parcel_geom/fl/*.rds    ──ingest──►  rof_app.duckdb
```

**Three app surfaces**:
1. Zone Explorer — CBSA / tract / zone map with demographic metrics and scoring
2. Retail Parcel Explorer — parcel candidate browser with filters, scoring, and shortlist
3. Data QA App — coverage and data health dashboard

**Cloud deploy subset**: `data/exports/jacksonville_rof.duckdb` (Jacksonville-
scoped subset committed to git for Streamlit Community Cloud).

This repo is structurally similar to `rental_area_search`: same Python/DuckDB/
Streamlit/GeoPandas stack, `src/<package>/` layout, `config/settings.yaml` +
ignored `config/data_sources.yaml`, and a `rof_gold` schema pattern matching
`property_explorer_gold`.

---

## Cross-Repo Dependency Notes

### metro_deep_dive → rental_area_search

- `rental_area_search` reads tract features from the local Metro Deep Dive DuckDB.
- Source path is local-only in `config/data_sources.yaml` (gitignored).
- Fields consumed: `median_income`, `median_rent`, `median_home_value`,
  `pct_bachelors_plus`, `median_age` at tract grain.
- NYC coverage in the local DuckDB is partial as of the last known state.
  `build_neighborhood_features.py` materializes NTA rows with null metrics when
  the source does not cover a tract. The app handles nulls explicitly.

### metro_deep_dive → retail_opportunity_finder

- `retail_opportunity_finder` uses a pipeline step (`export_from_metro.py`) to
  copy a market slice from `metro_deep_dive.duckdb` into `rof_app.duckdb`.
- The R-based Metro Deep Dive pipeline must run first whenever demographic inputs
  need refreshing.

### rental_area_search ↔ retail_opportunity_finder

- No direct data dependency. These are independent consumer apps.
- They share the same developer, stack, and many structural conventions.
- Both use Streamlit Community Cloud for deployment with a committed DuckDB file.

---

## File Conventions Shared Across Repos

| Convention | Rule |
|---|---|
| No absolute paths in committed files | Use repo-relative paths. Never include `/Users/<name>/...` in docs, config, or code. |
| Raw data files are local-only | `data/raw/` and `data/processed/` are gitignored except for committed DB subsets. |
| Config templates committed; actuals gitignored | `config/data_sources.example.yaml` committed; `config/data_sources.yaml` gitignored. |
| Gold tables are replace-first | Unless the table is explicitly user-authored (shortlists). |
| No comments explaining what code does | Only add comments for non-obvious WHY (hidden constraints, subtle invariants). |
| Decision log updated on new decisions | `docs/decision_log.md` in `rental_area_search` is the authoritative record. |

---

## What To Look Up In Each Repo

| Question | Where to look |
|---|---|
| Stoop NYC product strategy and app definitions | `rental_area_search/docs/product_strategy.md` |
| Active sprint tasks and assignments | `rental_area_search/docs/planning/current_backlog.md` |
| DuckDB table contracts and column definitions | `rental_area_search/docs/data_model.md` |
| Pipeline build order and commands | `rental_area_search/docs/pipeline_plan.md` |
| Neighborhood character mart schema and analytics logic | `rental_area_search/docs/data_products/neighborhood_character/neighborhood_character_mart.md` |
| Curated POI taxonomy and ingestion status | `rental_area_search/docs/data_products/curated_places/poi_categories.md` |
| System architecture and pipeline flows | `rental_area_search/docs/architecture.md` |
| Key decisions and rationale | `rental_area_search/docs/decision_log.md` |
| Metro Deep Dive layer structure | `metro_deep_dive/documents/repo_taxonomy.md` |
| Retail Opportunity Finder architecture | `retail_opportunity_finder/PLAN.md` |

# Metro Deep Dive — Shared Project Context

**Purpose of this document:** Cross-repo context for any Claude project that spans the Metro Deep Dive ecosystem. Keep it current as phases complete and architecture decisions change.

Last updated: 2026-05-10

---

## The Ecosystem

Three repos form the core of this work:

| Repo | Language | Role |
|---|---|---|
| `metro_database_build` | SQL / dbt / DuckDB | Builds the Bronze → Silver → Gold data layers from raw sources |
| `metro_deep_dive` | R | Analytics platform: reusable functions, visual library, Retail Opportunity Finder product, secondary analyses |
| `metro_deep_dive_chatbot` | Python + R | NL-to-SQL chatbot over the Gold layer; portfolio app for non-technical analysts |

The chatbot is a consumer of the Gold layer built by `metro_database_build`. The R visual library in `metro_deep_dive` is the chart rendering engine for the chatbot.

**Shared data path (dev):** `/Users/danberle/Documents/projects/data/duckdb/metro_deep_dive.duckdb`

---

## What the Chatbot Is

A constrained analytical chatbot where users ask natural language questions about US demographic and economic data and receive:
- a short written answer
- a chart (rendered by R)
- a supporting data table
- the SQL used
- metric definitions and assumptions

**Core design principle:** Reliability over openness. Answer a narrow set of questions well; reject or clarify everything outside scope rather than improvising.

**Audience:** Portfolio demo + small group of non-technical analysts. Deploy target: Streamlit Cloud.

---

## Build Status (as of 2026-05-10)

| Phase | Status | What it delivered |
|---|---|---|
| 0 — Environment | ✅ Complete | Local DuckDB, Ollama, R all verified |
| 1 — Semantic layer | ✅ Complete | `semantic_layer/` YAML catalogs for tables, metrics, geography, joins, chart rules, query templates |
| 2 — SQL pipeline | ✅ Complete | Deterministic SQL generation, validation, DuckDB execution |
| 3 — LLM orchestration | ✅ Complete | NL → structured query plan → SQL via Ollama/Groq |
| 4 — Chart rendering | ✅ Complete | R subprocess bridge; result profiling and chart selection |
| 4.5 — Pipeline hardening | ✅ Complete | QA tooling, batch runner, artifact saving, QA prompt library |
| **Reference dashboard** | ✅ Complete | `reference_dashboard/data_explorer.py` — Streamlit choropleth + data table for QA ground-truth lookup |
| **5 — Streamlit frontend** | 🔲 Pending | Chat UI over the orchestrator |
| **6 — Cloud deployment** | 🔲 Pending | MotherDuck migration, Streamlit Cloud deploy |

---

## Repo Structure

```
metro_deep_dive_chatbot/
├── app/
│   ├── orchestrator.py          ← end-to-end pipeline (parse → plan → SQL → execute → chart → assemble)
│   ├── intent/parser.py         ← LLM intent parsing → QueryPlan (Pydantic)
│   ├── llm/provider.py          ← OllamaProvider / GroqProvider (OpenAI-compatible interface)
│   ├── query/
│   │   ├── planner.py           ← QueryPlan → PlannedQuery
│   │   ├── generator.py         ← PlannedQuery → SQL (Jinja2 templates from semantic layer)
│   │   ├── validator.py         ← SQL safety + semantic layer compliance checks
│   │   └── executor.py          ← DuckDB query runner
│   ├── charts/
│   │   ├── profiler.py          ← result DataFrame → ResultProfile (shape inference)
│   │   ├── selector.py          ← question_type + profile → chart type (from chart_rules.yml)
│   │   └── renderer.py          ← subprocess R bridge (CSV + JSON config → PNG)
│   ├── response/assembler.py    ← answer text assembly
│   └── scripts/
│       ├── ask.py               ← CLI entrypoint; --output-dir saves full artifact set
│       └── qa_batch.py          ← batch QA runner
├── semantic_layer/
│   ├── table_catalog.yml        ← approved tables: schema, grain, geo fields, time field
│   ├── metric_catalog.yml       ← metrics: source column, unit_format, growth eligibility
│   ├── geography_catalog.yml    ← geo levels, hierarchy, rollup rules
│   ├── join_catalog.yml         ← approved join paths between Gold tables
│   ├── chart_rules.yml          ← question_type + result shape → approved chart types
│   └── query_templates.yml      ← 6 SQL template patterns (Jinja2)
├── data_dictionary/
│   └── layers/gold/             ← YAML + MD definitions for each Gold table
├── visual_library/              ← R chart library (shared with metro_deep_dive)
│   └── shared/render/           ← render_{chart_type}.R scripts (CLI: --config --data --output)
├── reference_dashboard/
│   ├── data_explorer.py         ← Streamlit data explorer (choropleth + table for QA)
│   └── explorer_utils.py        ← DuckDB helpers, GeoJSON builder, formatters
├── frontend/
│   ├── streamlit_app.py         ← Chat UI (Phase 5, in progress)
│   ├── qa_review.py             ← QA review surface
│   └── qa_utils.py
├── examples/
│   └── question_library.yml     ← 20-30 tagged examples with expected query plans + SQL
├── qa/
│   └── qa_prompt_library.yml    ← QA prompt library (golden / paraphrase / clarification categories)
├── tests/
├── analysis/                    ← Short-form manual analyses (leading indicator for chatbot)
├── BUILD_PLAN.md                ← Phase-by-phase implementation plan with completion status
├── QA_FRAMEWORK.md              ← QA layer definitions, scoring, prompt category specs
├── QA_TUNING_LOG.md             ← Loop-by-loop QA scoreboard and fix history
├── DASHBOARD_SPEC.md            ← Reference dashboard full spec
└── DASHBOARD_BACKLOG.md         ← Reference dashboard sprint tasks (all complete)
```

---

## Tech Stack

| Concern | Choice | Notes |
|---|---|---|
| Backend | Python + FastAPI | Orchestration layer |
| Frontend (chatbot) | Streamlit | Deploy to Streamlit Cloud |
| Data (dev) | Local DuckDB | `DB_CONNECTION` env var |
| Data (prod) | MotherDuck | Phase 6 migration |
| LLM (dev) | Ollama + Llama 3.2 3B | Intel Mac CPU |
| LLM (prod) | Groq API (Llama 3) | Free tier, fast, same model family |
| LLM interface | OpenAI-compatible chat completions | Swap via `LLM_PROVIDER` env var — no code change |
| Python-to-R bridge | subprocess | temp CSV + JSON config → Rscript → PNG |
| Semantic layer format | YAML files in repo | Human-readable, version-controlled |
| Map library (dashboard) | Plotly Express choropleth_mapbox | carto-positron tiles, no API key |

**Do not suggest Claude API, OpenAI API, or rpy2.** The LLM choice (Ollama/Groq) is intentional for learning local/open-source model workflows.

---

## Gold Layer Tables

These live in `gold.*` in DuckDB. All are defined in `data_dictionary/layers/gold/`.

| Table | Subject | Status in chatbot |
|---|---|---|
| `gold.population_demographics` | Population, age, demographics | ✅ Active (MVP) |
| `gold.housing_core_wide` | Housing units, tenure, costs | ✅ Active (MVP) |
| `gold.economics_income_wide` | Income, earnings, per capita | ✅ Active (MVP) |
| `gold.economics_labor_wide` | Employment, wages, unemployment | Deferred |
| `gold.affordability_wide` | Rent burden, value-to-income ratios | Deferred |
| `gold.economics_gdp_wide` | Regional GDP | Deferred |
| `gold.migration_wide` | Domestic migration flows | Deferred |
| `gold.transport_built_form_wide` | Transit, density, walkability | Deferred |
| `gold.tx_isd_metrics` | Texas school district metrics | Deferred |

All Gold tables share a common grain: `one row per geo_level + geo_id + year`.

Common join keys across tables: `geo_id`, `geo_level`, `year`.

---

## Geography Model

**Supported levels:** `region`, `division`, `state`, `cbsa`, `county`
**Deferred:** `zcta`, `census_tract`

**48-state rule (reference dashboard):** Contiguous US + DC only. Exclude Alaska (FIPS 02), Hawaii (FIPS 15), territories (FIPS ≥ 57 except DC=11).

**Hierarchy:**
```
county → cbsa (partial: not all counties are in a CBSA)
county → state
state → division → region
```

Region/Division geometries: dissolved from `geo.states` via `silver.xwalk_state_region`. No separate geometry table.

Geometry tables in DuckDB: `geo.states`, `geo.counties`, `geo.cbsas` — use `ST_AsGeoJSON(geom)` via DuckDB spatial extension.

---

## Application Pipeline (end-to-end)

```
User question
    ↓
IntentParser (app/intent/parser.py)
  - LLM call with system prompt built from semantic layer catalogs + few-shot examples
  - Returns QueryPlan (Pydantic) or ClarificationRequest
    ↓ (if QueryPlan)
QueryPlanner (app/query/planner.py)
  - Validates plan against semantic layer
  - Returns PlannedQuery
    ↓
QueryGenerator (app/query/generator.py)
  - Selects template from query_templates.yml
  - Renders SQL with Jinja2
    ↓
QueryValidator (app/query/validator.py)
  - Checks: approved tables, approved metrics, approved joins, read-only, valid geo level
    ↓
QueryExecutor (app/query/executor.py)
  - Runs against DuckDB; returns pandas DataFrame
    ↓
ResultProfiler (app/charts/profiler.py)
  - Infers result shape: row_count, has_time_series, dimension_count, inferred_shape
    ↓
ChartSelector (app/charts/selector.py)
  - Looks up chart_rules.yml → returns chart type
    ↓
ChartRenderer (app/charts/renderer.py)
  - subprocess: writes CSV + JSON config → calls Rscript → returns PNG path
    ↓
ResponseAssembler (app/response/assembler.py)
  - Assembles answer text, chart path, table, SQL, assumptions
    ↓
OrchestrationResult
```

---

## Supported Question Types and SQL Templates

| Question type | Template | Chart type(s) |
|---|---|---|
| `ranking` | Top/bottom N by metric, optional geo filter | Bar (horizontal) |
| `trend` | Metric over time for one or more geos | Line |
| `compare_selected` | Metric across user-specified geos | Bar or slopegraph |
| `distribution` | Spread of metric across all geos at a grain | Boxplot or histogram |
| `benchmark` | Target geo vs. US / region / state / peers | Bar with reference line |
| `growth` | Point-in-time growth over N years (LAG or CTE) | Bar |

Growth windows: 1yr, 3yr, 5yr. Default: 5yr.

---

## QueryPlan Schema

```python
class QueryPlan(BaseModel):
    question_type: str        # ranking, trend, compare_selected, distribution, benchmark, growth
    subject_area: str
    metric_id: str
    geo_level: str
    geo_filter: dict | None
    benchmark_type: str | None
    time_range: dict | None
    growth_window: int | None
    sort: str | None
    limit: int | None
```

---

## QA Framework Summary

**QA layers (evaluated per run):**
1. Intent QA — correct question_type, metric, geo_level, geo_ids
2. Query Plan QA — complete + valid plan
3. SQL QA — SQL matches plan, correct table/column, read-only
4. Data / Result QA — rows returned, plausible values
5. Chart QA — appropriate type, correct labels and formatting
6. Answer Text QA — accurate, specific, non-hallucinated
7. End-to-End Regression QA — consistency across known prompts

**Prompt categories in `qa/qa_prompt_library.yml`:**
- `golden` — exact regression anchors (run deterministically)
- `provider_paraphrase` — reworded variants to test LLM generalization (run with `--force-provider`)
- `clarification` — underspecified prompts to test clarification behavior

**Current QA scores (Loop 3, 2026-05-02, 20 cases):**
10 pass / 6 partial / 4 fail

**Known weak areas:** benchmark cases, growth-with-explicit-template (model prefers precomputed growth columns), clarification message language (too technical).

**Artifact saved per run:** `qa_run.json` (canonical QA record), `query_plan.json`, `result.sql`, `result.csv`, `chart.png`, `answer.txt`

---

## Reference Dashboard

`reference_dashboard/data_explorer.py` — a separate Streamlit app (not the chatbot). Used as a QA ground-truth lens on the Gold layer.

**What it does:** Filter by geo level, subject area, KPI, year, and KPI range. Renders a Plotly choropleth map and a formatted, downloadable data table. Growth columns always included.

**Launch:** `.venv/bin/python -m streamlit run reference_dashboard/data_explorer.py`

**Status:** Complete (all 5 sprints done).

---

## Analysis Folder

`analysis/` — short-form manual analyses for quick insights. Structured as `analysis/<topic>/` with SQL, R, and chart outputs. Intended as a leading indicator for new chatbot question types. May be deeper or more tuned than the chatbot question library.

---

## Key Constraints and Guardrails

- **Read-only queries only.** The validator rejects any non-SELECT SQL.
- **Approved tables only.** No ad-hoc table references — everything must be in `table_catalog.yml` with `status: active`.
- **LLM does not write SQL.** It produces a structured plan; the template engine writes SQL.
- **Charts come from the visual library.** No ad-hoc Plotly/matplotlib in the chatbot response path.
- **Clarify rather than improvise.** Underspecified questions get a clarification request, not a guess.
- **MVP geo scope:** No ZCTA or census tract. No maps in the chatbot (choropleth deferred to v1.1).

---

## Open Work (as of 2026-05-10)

| Item | Phase | Notes |
|---|---|---|
| Streamlit chat UI | 5 | `frontend/streamlit_app.py` — chat input, response history, chart + table + SQL display, clarification routing, session state, follow-up merging |
| MotherDuck migration | 6 | Export local Gold tables; update `DB_CONNECTION` |
| Streamlit Cloud deploy | 6 | `packages.txt` (r-base), `setup.sh` (R packages), secrets for Groq + MotherDuck |
| Benchmark QA fixes | Loop 4 | `gold.benchmark_reference` view exists; benchmark template still weakest area |
| Clarification message language | Loop 4 | Field names exposed to users should map to plain English |
| Growth template forcing | Loop 4 | Model prefers precomputed growth columns over explicit growth template |
| `analysis/` expansion | Ongoing | Add more manual analyses as chatbot leading indicators |

---

## Environment Variables

```bash
# Data
DB_CONNECTION=/Users/danberle/Documents/projects/data/duckdb/metro_deep_dive.duckdb

# LLM — local dev
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# LLM — production
LLM_PROVIDER=groq
GROQ_API_KEY=...
```
