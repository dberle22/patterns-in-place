# foundations/etl

**Status:** Active
**Updated:** 2026-09-29

The pipeline that builds the shared warehouse: source downloads land in `staging`, get standardized in `silver`, and are combined into wide `gold` tables. Geography marts are built here too.

## How to run it

Run from the repo root. Scripts read `DB_PATH` (and API keys) from `.Renviron`.

```bash
Rscript foundations/etl/create_DB.R     # full build: staging, then Silver, then Gold, in a fixed order
Rscript foundations/etl/build_silver.R  # rebuild Silver only
```

To work on one source, run its scripts one layer at a time (for example `staging/get_<source>.R`, then `silver/<source>_silver.R`, then the Gold SQL), inspecting each layer before the next. Never run DuckDB writes in parallel.

## What's here

| Path | What it is |
|---|---|
| `create_DB.R` | Full build; the script lists define the run order |
| `build_silver.R` | Rebuilds Silver tables |
| `staging/` | One `get_<source>.R` script per source: download, parse, land source-faithful tables. Index: `staging/SOURCES.md` |
| `silver/` | Standardize grain and keys; ACS tables come as `_base` / `_kpi` pairs |
| `gold/` | SQL for the wide Gold tables |
| `geo/` | TIGER geometries and the governed geography build (`mart_geography`) |
| `mart_geography/`, `mart_area_explorer/` | SQL for those marts |
| `R/` | Shared R functions used across layers |
| `reference/` | Reference mappings (e.g. the BLS QCEW industry map) |
| `pipeline_manifest.yml` | Declared step order and dependencies; documentation only, not yet executable (see `pipeline_manifest.md`) |
| `seed_staging.R`, `seed_geo.R`, `seed_staging_lexar_test.R` | One-time copies from the pre-monorepo database (`OLD_DB_PATH`); not part of normal builds |
| `utils.R` | Package-loading helper, sourced by some staging scripts |
| `data/duckdb/` | The warehouse file (gitignored) |

## Documentation

Each table's contract lives in `foundations/data_dictionary/` (sources, staging, Silver and Gold). Update the dictionary and pipeline wiring after the code for a layer works.
