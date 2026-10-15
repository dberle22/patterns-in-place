# foundations

**Status:** Active
**Updated:** 2026-09-29

The shared data platform every product builds on: the ETL pipeline, the DuckDB warehouse, the semantic layer, the data dictionary, the visual library, and the loaders that publish Intelligence outputs. It's a dependency, not a product: products read from it and never keep their own copies of its assets.

What's next: [ROADMAP.md](ROADMAP.md). How it fits the rest of the repo: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## What's here

| Folder | What it is | Start with |
|---|---|---|
| `etl/` | R and SQL pipeline: staging → Silver → Gold, plus the geography and app marts | [etl/README.md](etl/README.md) |
| `loaders/` | Publish Intelligence Framework outputs into `mart_intelligence` | [loaders/README.md](loaders/README.md) |
| `semantic_layer/` | YAML catalogs defining tables, metrics, joins, themes, questions and chart rules | [semantic_layer/README.md](semantic_layer/README.md) |
| `data_dictionary/` | Per-source and per-table documentation for staging, Silver and Gold | [data_dictionary/README.md](data_dictionary/README.md) |
| `visual_library/` | Chart specs, R render functions and the Python chart engine | [visual_library/README.md](visual_library/README.md) |
| `benchmarking_py/` | Python package for benchmark lookups against `mart_benchmarking` | [benchmarking_py/README.md](benchmarking_py/README.md) |
| `archive/` | Finished plans (platform completion plan, county-first refresh) | — |

## How to run it

The warehouse is `foundations/etl/data/duckdb/patterns_in_place.duckdb`, set through `DB_PATH` in `.Renviron`. R scripts run from the repo root with `Rscript`; see [etl/README.md](etl/README.md) for the build order.

## Depends on / depended on by

- **Reads:** public data sources (Census, BEA, BLS, HUD, EPA, FEMA, LEHD, IRS, Zillow and others), with API keys in `.Renviron`.
- **Read by:** every other area. The Metro Deep Dive program, the public CBSA panel, Area Explorer and Publisher all query the warehouse and use the semantic layer or visual library.

## Rules

- Build one layer at a time: stage, inspect, then Silver, then Gold. DuckDB writes run sequentially. Full rules: [AGENTS.md](../AGENTS.md) §5.1.
- An engine from the Metro Deep Dive program is promoted here once two consumers use it unchanged.
