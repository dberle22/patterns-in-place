# AGENTS.md

See `<monorepo-root>/AGENTS.md` for full behavioral guidelines. This file
contains stoop-specific additions only.

## Stoop-specific: Completing Planned Work

When working on a stoop sprint or task series:
- Tick off tasks in the active planning doc as you complete them.
- Add any unplanned tasks that were required and tick them off once done.
- Update `docs/decision_log.md` with any new decisions made during the work.

## Stoop orientation

- Entry point: `app/stoop_explore.py` -> calls `streamlit_app_v2.main()`
- Production app: `app/streamlit_app_v2.py`
- QA tool: `app/neighborhood_qa_app.py`
- Core library: `src/nyc_property_finder/`
- Pipelines: `src/nyc_property_finder/pipelines/`
- Config: `config/settings.yaml` (committed), `config/data_sources.yaml` (local-only, gitignored)
- DuckDB: `data/processed/nyc_property_finder.duckdb` (local-only, gitignored)

Cross-folder references to `foundations/` must use the `MONOREPO_ROOT` or
`FOUNDATIONS_PATH` env var - never hardcoded absolute paths. See monorepo root
AGENTS.md Section 6.
