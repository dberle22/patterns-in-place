# Property Explorer App

## Purpose

`app/streamlit_app.py` is the main property review surface. It lets the user
inspect listings with map/list/detail workflows, contextual filters, personal
POI and subway overlays, score/status fields, and local shortlist persistence.

The app should remain a direct consumer of app-ready gold tables. It should not
own source parsing, geocoding, tract assignment, or scoring logic.

## Run

```bash
PYTHONPATH=src .venv/bin/streamlit run app/streamlit_app.py
```

## Code

- `app/streamlit_app.py`: Streamlit page assembly and UI rendering.
- `src/nyc_property_finder/app/explorer.py`: testable app helpers for loading
  tables, filtering listings, parsing POI category counts, sorting, and
  shortlist state.
- `tests/test_property_explorer_app.py`: regression tests for app helper
  behavior.

## Data Inputs

The app reads from the local DuckDB database configured in
`config/settings.yaml`.

Required gold tables:

| Table | App use |
| --- | --- |
| `property_explorer_gold.fct_property_context` | Primary listing facts, geography labels, transit context, POI counts, and score/status fields. |
| `property_explorer_gold.dim_user_poi` | Optional personal POI map layer and category context. |
| `property_explorer_gold.dim_subway_stop` | Optional transit map layer. |
| `property_explorer_gold.fct_nta_features` | Neighborhood detail metrics. |
| `property_explorer_gold.fct_user_shortlist` | Local saved/archived/rejected listings and notes. |

## Current Behavior

- Defaults to active listings unless the user includes inactive records.
- Sorts and filters against `fct_property_context`.
- Treats missing score components as explicit status, not as zero-quality
  listings.
- Stores shortlist state in DuckDB so it survives Streamlit session restarts.
- Joins shortlist rows back to current listing/context facts instead of
  denormalizing listing details into the shortlist table.

## QA Focus

- App should render useful empty states when optional POI, subway, or NTA
  feature tables are empty.
- Score labels should show unavailable or reweighted status where applicable.
- Shortlist writes should not be replaced by data rebuilds.
- Map/list/detail views should read from `fct_property_context` rather than
  reconstructing pipeline logic in Streamlit.
