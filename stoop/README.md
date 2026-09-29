# Stoop

**Status:** Paused since 2026-06. Stoop Explore v1 is live; Stoop Search is scaffolded only.
**Updated:** 2026-09-29

Stoop is a set of data products and apps for understanding New York City neighborhoods at the NTA level. It combines curated places, open public data and demographic context. **Stoop Explore** is a map of neighborhoods and points of interest for people exploring the city. **Stoop Search**, for people deciding where to live, hasn't been built.

## How to run it

Stoop has its own DuckDB (`data/processed/nyc_property_finder.duckdb`, set in `config/settings.yaml`), separate from the shared warehouse. The Python package is `src/nyc_property_finder/`.

Run commands from the `stoop/` folder:

```bash
PYTHONPATH=src .venv/bin/streamlit run app/stoop_explore.py
```

There's no `stoop/.venv` in the monorepo yet; the docs assume one from before the migration. Create it from `requirements.txt` (or `pyproject.toml`) before running. The full rebuild sequence is in [docs/app/stoop_explore_launch_runbook.md](docs/app/stoop_explore_launch_runbook.md).

## Key docs

1. [docs/README.md](docs/README.md): the docs index and which doc owns what
2. [docs/product_strategy.md](docs/product_strategy.md): what Stoop is for
3. [docs/architecture.md](docs/architecture.md) and [docs/data_model.md](docs/data_model.md): how it's built
4. [docs/planning/current_backlog.md](docs/planning/current_backlog.md): where work stopped

## Depends on / depended on by

- **Reads:** its own DuckDB, built from NYC open data, OSM, Google Maps takeouts and editorial scrapes. It doesn't read the shared warehouse.
- **Read by:** nothing in the monorepo reads its data. The Metro Deep Dive POI engine audited Stoop's public and curated POI contracts and reuses their governance pattern (see `metro-deep-dive-program/engines/poi/NOTES.md`).

## Where we left off

- Explore v1 is live; Search is scaffolded only.
- On return, start with v2 planning. The open product questions are at the end of [docs/README.md](docs/README.md).
- The migration left one manual step: copy `data/raw/geography/nta_boundaries.geojson` into `stoop/data/` (data folders are gitignored). The migration plan is archived in `archive/2026-09_monorepo_migration/`.
