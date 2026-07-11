# metro-deep-dive

Long-form, market-specific deep dives. Structured, repeatable, and publishable.

## What's here

- `app/` - ROF Streamlit apps (zone explorer, parcel explorer, data QA). The working prototype for the Metro Deep Dive interactive surface.
- `src/retail_opportunity_finder/` - ROF core library: zone scoring, parcel transforms, geo utilities. Reference material for the future generalized build.
- `markets/jacksonville/` - ROF notebook sequence; the full zone/parcel prototype.
- `markets/wilmington/` - narrative overview and built-environment notebooks.
- `templates/` - empty scaffold for the future market-agnostic deep-dive template.

## Running the ROF apps

These apps are migration-state reference and are not expected to run cleanly without local path updates. When you want to inspect them:

```bash
cd metro-deep-dive
PYTHONPATH=src streamlit run app/zone_explorer_app.py
```

Config lives in `config/data_sources.yaml` (local-only, gitignored). Copy from `config/data_sources.example.yaml` and point `source_database_path` at your local DuckDB.

## Running the Research Tool

The active Deep Dive research app lives at `metro-deep-dive/research-tool/app.py`.

From the repo root:

```bash
scripts/start_research_tool.sh
```

That launcher resolves the repo root automatically, sets `DB_PATH` to `foundations/etl/data/duckdb/patterns_in_place.duckdb` by default, and prefers a Python 3.12 environment if one is available.

If you want a true one-command launcher from anywhere, add an alias in your shell config:

```bash
alias dd-research='~/Documents/projects/patterns_in_place/scripts/start_research_tool.sh'
```

## R utilities

Shared R functions now live in `foundations/etl/R/`. Some migrated notebooks still source the old `metro_deep_dive/R/` paths and will need follow-up path updates when those notebooks are brought back into active use.
