# Architecture

**Status:** Active
**Updated:** 2026-09-29

How data moves through Patterns in Place, what lives in the warehouse, and which folders build and read each part. This is the map; detailed contracts live in the docs linked from each section. The diagram version is [diagrams/platform_overview.drawio](diagrams/platform_overview.drawio), which has pages for the platform and for the Metro Deep Dive program.

---

## Data flow

```
Public sources (Census, BEA, BLS, HUD, EPA, FEMA, LEHD, IRS, Zillow, ...)   POI + parcel sources
        │                                                                       │
        ↓  foundations/etl/staging    source-faithful landing                   │
    staging  ──→  silver  ──→  gold  ────────────────────────────────┐          │
                  foundations/etl/silver   foundations/etl/gold      │          │
                                             │                       ↓          ↓
                                             │               mart_* schemas (built by foundations
                                             │               or by the product that owns them)
                                             ↓                       │
                              semantic layer (foundations/semantic_layer/*.yml)
                                             │                       │
                                             ↓                       ↓
                       products: Metro Deep Dive program, public CBSA panel, paused apps
```

Build rules (full list in [AGENTS.md](../AGENTS.md) §5.1):

- Stage first, then Silver, then Gold. Each layer is inspected before the next is designed.
- Staging stays source-faithful. Geographic joins, key validation and contracts happen in Silver.
- DuckDB writes run sequentially, never in parallel.

## The warehouse

One DuckDB file: `foundations/etl/data/duckdb/patterns_in_place.duckdb`, about 19GB, gitignored and built locally. Code finds it through `DB_PATH` (see the root [README.md](../README.md#warehouse) for per-tool variable names).

Schemas as of 2026-09-29:

| Schema | Tables | What it holds | Built by | Read by |
|---|---|---|---|---|
| `staging` | 230 | Source-shaped landed tables, one per source × geography | `foundations/etl/staging/` | Silver builds |
| `silver` | 102 | Standardized tables with consistent geo and time keys; crosswalks | `foundations/etl/silver/` | Gold builds, some analyses |
| `gold` | 22 | Wide cross-topic tables; the main query target | `foundations/etl/gold/` | Everything, including the public panel |
| `geo` | 10 | Geometries for display and analysis | `foundations/etl/` (`seed_geo.R`, `geo/`) | Visual library, Publisher, MDD program |
| `mart_geography` | 20 | Governed geography relationships: identities, memberships, rollups, allocation weights | `foundations/etl/geo/` | MDD program, foundations |
| `mart_intelligence` | 10 | Frame scores, Cross-Frame, trajectory, tract and ZCTA zones | `foundations/loaders/`; trajectory tables also from the MDD time-series engine | MDD program, Area Explorer, research tool |
| `mart_area_explorer` | 2 | App-serving CBSA profile and long metric tables | `foundations/etl/mart_area_explorer/` | Area Explorer, research tool |
| `mart_benchmarking` | 4 | Benchmark sets, members and metrics | MDD `engines/benchmarking/` | `foundations/benchmarking_py`, MDD program |
| `mart_poi` | 4 | Classified POIs, taxonomy tags, geography assignment | MDD `engines/poi/` | MDD program |
| `mart_explanation_q1`, `_q2`, `_q3` | 2–10 each | Per-question marts for Explanation analyses | MDD `analyses/explanation/` | The same analyses |
| `mart_explanation_q6` | 10 | Q6 anchor and place-context tables | No builder found (see Open items) | Nothing |
| `mart_housing` | 2 | Housing core metrics and overheating matrix | `publisher/content/housing/sql/` (`core_metrics.sql`, `overheating_matrix.sql`), run by hand | Publisher housing content |

There is no Bronze schema: raw downloads live on disk under the `DATA_RAW` path, not in DuckDB.

**Stoop is separate.** It uses its own database (`stoop/data/processed/nyc_property_finder.duckdb`), not the shared warehouse.

## Conventions inside the warehouse

- **Standard grain:** `(geo_level, geo_id, geo_name, year)`. Any two Gold tables at the same grain join on those keys without a catalog entry.
- **Geography levels:** US, region, division, state, CBSA, county, place, ZCTA, tract. CBSAs are derived from county membership.
- **ACS Silver tables** come in pairs: `<theme>_base` (normalized raw columns) and `<theme>_kpi` (derived ratios and growth).
- **BEA Silver tables** come in long, wide and reference forms.
- **Crosswalks** are named `xwalk_<from>_<to>`. Governed relationships and rollups live in `mart_geography`.
- **Gold** is built in DuckDB SQL first; R only where SQL gets procedurally awkward.

Detail: [data_dictionary/README.md](../foundations/data_dictionary/README.md) (per-table dictionaries, layer checklists) and [data_platform_architecture.md](../foundations/data_dictionary/docs/data_platform_architecture.md) (source mapping and ingestion scope).

## Places and Points

The warehouse above is the **Places** layer: aggregate facts about geographies.

The **spatial layer** covers three kinds of data that attach to Places:

| Type | What it is | Examples |
|---|---|---|
| Points | A location with a latitude and longitude | Restaurant, school, transit stop |
| Parcels | The legal land unit from tax or assessor records | Tax lot |
| Polygons | A named zone that maps up toward Places | Zoning district, flood zone, NTA |

Points are built today inside the MDD program's POI engine (`mart_poi`) and, separately, inside Stoop for NYC. Promoting a shared Points pipeline into `foundations/` is future work.

## The semantic layer

The contract between the warehouse and anything that queries it. It is a set of YAML files in `foundations/semantic_layer/`, in three tiers:

| Tier | Files | Answers |
|---|---|---|
| Infrastructure | `table_catalog`, `metric_catalog`, `join_catalog`, `geography_catalog`, `points_catalog` | What exists, what each column means, how tables join |
| Intelligence | `intelligence_catalog` | How metrics combine into frame scores and clusters |
| Navigation | `theme_catalog`, `question_catalog`, `query_templates`, `chart_rules` | How products surface metrics, questions, SQL and charts |

Meaning flows top down: theme → topic → metric → table → source. Agents and the chatbot resolve a question by walking down that chain until they can write SQL. Detail: [semantic_layer/README.md](../foundations/semantic_layer/README.md).

## Folder dependencies

| Folder | Reads from | Read by |
|---|---|---|
| `foundations/` | Public sources | Every other folder |
| `metro-deep-dive-program/` | Mostly `mart_intelligence`, `gold`, `silver`, `mart_geography`, `geo`; its own `mart_poi`, `mart_benchmarking`, `mart_explanation_*`; some legacy code in `metro-deep-dive/metro-area-explorer/` | Nothing yet; engines promote into `foundations/` |
| `public-cbsa-panel/` | Three `gold` tables and two `silver` crosswalks | External users, through releases |
| `metro-deep-dive/` (legacy) | `gold`, `silver`, `geo`, `mart_intelligence`, `mart_area_explorer` | `metro-deep-dive-program/` (place intelligence, industry) |
| `area-explorer/` | `gold`, `mart_area_explorer`, `mart_intelligence` | — |
| `publisher/` | `gold`, `mart_housing`, `geo`, `silver`, semantic layer, visual library | — |
| `stoop/` | Its own DuckDB | — |

## Open items

- `mart_explanation_q6` has no builder in the repo or its git history, and nothing reads it: the Q6 notebook computes its results live from `q6_one_metro/sql/`. It looks like a leftover from an earlier prototype. Decide whether to drop it when the Metro Deep Dive cleanup (Section E of the docs overhaul) comes up.
- `mart_housing` is built from two `SELECT` files with no runner script, so rebuilding it is a manual step. Add a runner when Publisher resumes.
- The Intelligence universe differs by surface: 401 CBSAs in the roadmap, 396 in the frame marts, 925 in the zone model. Documented as a known limitation in the framework overview.
