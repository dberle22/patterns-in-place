# area-explorer

Interactive CBSA exploration tool. This is the research surface for the data platform: exploratory and iterative, not a publishing workflow.

## Current state

Bare-bones MVP: `app/data_explorer.py` and `app/explorer_utils.py`, migrated from `metro_deep_dive_chatbot/reference_dashboard/`. It supports CBSA exploration over Gold-layer metrics.

## Running the app

```bash
export MONOREPO_ROOT=/path/to/patterns_in_place
export DB_CONNECTION="$MONOREPO_ROOT/foundations/data/foundations.duckdb"
cd "$MONOREPO_ROOT/area-explorer"
PYTHONPATH=app streamlit run app/data_explorer.py
```

The app already reads `DB_CONNECTION` from the environment. Leave the fallback path alone and use the env var instead.

## Build roadmap

- Phase 1 (current): CBSA choropleth, metric picker, and ranking table
- Phase 2: Intelligence Frames (depends on F3 + F5)
- Phase 3: Zone layer (depends on the F5 zones datamart)

See `notes/patterns_in_place_notes/Products/Area Explorer.md` for the broader roadmap.
