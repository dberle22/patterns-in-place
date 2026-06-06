# Stoop Explore Launch Runbook

Last updated: 2026-05-10

## Purpose

This note covers the minimum rebuild and launch path for the public Stoop
Explore MVP.

## Core App Entry Point

Run the app from the repository root:

```bash
PYTHONPATH=src .venv/bin/streamlit run app/stoop_explore.py
```

## Rebuild Sequence

Rebuild the core supporting tables in this order when curated sources or
neighborhood context changes:

```bash
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.init_database
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.build_tract_to_nta
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.build_neighborhood_features
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_public_poi
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.ingest_curated_poi_google_takeout
PYTHONPATH=src .venv/bin/python -m nyc_property_finder.pipelines.build_neighborhood_character_mart
```

If article-based curated sources were refreshed, run those article pipelines
before rebuilding the neighborhood character mart.

## What To Refresh For Explore

- Curated category changes: rebuild `dim_user_poi_v2`, then rebuild
  `neighborhood_character_mart`.
- Public POI changes: rebuild `dim_public_poi`, then rebuild
  `neighborhood_character_mart`.
- Metric/context changes: rebuild `fct_tract_features` and `fct_nta_features`.
- Explore category visibility or thresholds: rebuild
  `neighborhood_character_mart` after editing
  `sql/marts/neighborhood_character/nta_category_controls.sql`.

## Quick Validation

Run the focused regression suite:

```bash
PYTHONPATH=src .venv/bin/pytest tests/test_stoop_explore.py tests/test_base_map_app.py -q
```

Then boot the app locally and confirm:

- The right-side intelligence panel renders above the map.
- `Restaurants` loads as the default Explore category.
- The map can auto-focus curated places onto the selected Explore category.
- The selected neighborhood is highlighted on the map.
- Sparse categories show fallback copy instead of fake rankings or labels.

## Known Blind Spots In The Public MVP

- Category coverage is still uneven. `restaurants`, `shopping`, and `hotels`
  are stronger than categories like `bars` or `museums`.
- "Known for" is intentionally narrow. Some neighborhoods will show only strong
  signals rather than a full destination claim.
- The app does not yet use map click as the primary neighborhood selector. The
  intelligence panel currently drives the selected neighborhood state.
- Demographic metrics remain supporting context, not the core Explore ranking
  logic.
- Streamlit Cloud launch is only as good as the committed repo assets and the
  bundled DuckDB inputs it can see at runtime.
