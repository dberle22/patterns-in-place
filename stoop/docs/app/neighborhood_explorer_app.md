# Stoop Explore App

## Summary

`app/stoop_explore.py` is the durable Streamlit entry point for Stoop Explore.
It currently delegates to `app/streamlit_app_v2.py` during the transition, keeps
`app/streamlit_app.py` Property Explorer intact, and builds on the shared
geography and demographic foundation:

- NYC five-borough census tracts from `data/raw/geography/census_tracts.geojson`.
- Tract-to-neighborhood labels from
  `property_explorer_gold.dim_tract_to_nta`.
- Tract demographic metrics from
  `property_explorer_gold.fct_tract_features`.
- Neighborhood demographic metrics from
  `property_explorer_gold.fct_nta_features`.
- Explore intelligence controls and rankings from
  `neighborhood_character_mart.nta_category_controls`,
  `neighborhood_character_mart.nta_category_density`, and
  `neighborhood_character_mart.nta_character_profile`.

The current product surface is a neighborhood-first explorer with a right-side
intelligence panel above the map. Users choose an Explore category such as
restaurants or hotels, see the current "Top neighborhoods for X" ranking,
select a neighborhood, and then review what that neighborhood is known for
before dropping into the full-width map.

## Run

```bash
PYTHONPATH=src .venv/bin/streamlit run app/stoop_explore.py
```

For table readiness, metric coverage, POI inventory QA, and source/freshness
checks, use the separate QA surface:

```bash
PYTHONPATH=src .venv/bin/streamlit run app/neighborhood_qa_app.py
```

## Code

- `app/stoop_explore.py`: durable Stoop Explore entry point for local and cloud
  launch.
- `app/streamlit_app_v2.py`: active Stoop Explore layout, map rendering, and
  intelligence panel composition.
- `app/neighborhood_qa_app.py`: QA surface for table readiness, demographic and
  POI coverage, and configured source/freshness status.
- `src/nyc_property_finder/app/stoop_explore.py`: lightweight app-side mart
  readers for Explore categories, rankings, and neighborhood character
  profiles.
- `src/nyc_property_finder/app/base_map.py`: reusable data-loading,
  tract/NTA geometry assembly, demographic formatting, color ramp generation,
  PyDeck layer creation, POI count enrichment, selected-neighborhood highlight,
  and cached geography loading.
- `src/nyc_property_finder/app/neighborhood_qa.py`: reusable QA summaries for
  source paths, DuckDB tables, demographic coverage, POI inventories, and
  freshness signals.
- `tests/test_base_map_app.py`: regression tests for metric formatting,
  missing-value colors, target borough filtering, metric joins, and selected
  NTA highlighting.
- `tests/test_stoop_explore.py`: regression tests for Explore category controls,
  rankings, and profile parsing.
- `tests/test_neighborhood_qa.py`: regression tests for QA table summaries,
  metric coverage, POI inventory coverage, and configured source status.

## Data Inputs

The app reads paths from `config/settings.yaml` and `config/data_sources.yaml`.
The census tract source uses `sources.census_tracts.path` and
`sources.census_tracts.id_column`; the current local contract points at
`data/raw/geography/census_tracts.geojson` with `GEOID` as the tract ID.

The current tract geometry and feature build support all five boroughs. Public
and curated POI points are filtered against the loaded tract geometry at app
load, so records can remain in the underlying tables for future regional
expansion without drawing outside the supported map footprint today.

`fct_nta_features` now follows a stronger neighborhood-native contract and
includes `borough` and `tract_count` alongside the demographic metrics.

## Current UX

- Default geography is `Neighborhoods`
- Default Explore category is `Restaurants`
- The Explore intelligence panel sits above the map on the right side
- Curated POIs are on by default
- Curated POIs can auto-focus on the selected Explore category
- Public POIs are off by default and lazy-loaded only when toggled on
- Public POI selection starts at `subway_station`
- The selected neighborhood is highlighted on the map when chosen from the
  intelligence panel
- The table beneath the map shows the core context metrics together and
  sorts by the selected metric
- Polygon tooltips include demographic context plus curated/public POI counts
  for quick neighborhood or tract review

## Performance Notes

A timing pass on 2026-04-28 showed that the shared geography load is now the
main backend cost, while metric switches are cheap after the refactor:

- `load_base_geography_data`: about `1.37s`
- `build_base_map_data_from_loaded(...)`: about `0.04s` per metric switch
- `load_poi_map_data`: about `0.07s`
- `load_public_poi_map_data(subway_station)`: about `0.06s`

The remaining perceived delay is more likely dominated by Streamlit rendering
and browser-side map draw cost than by repeated backend data assembly.

## QA Surface

The app handles null demographic metrics explicitly so the map can still render
boundaries without precise-looking demographic color. It also handles sparse
Explore categories explicitly: no fake "known for" label appears when the mart
does not support that claim, and no empty ranking is shown as if it were a real
leaderboard. The dedicated QA app is where missing data should be reviewed. If
the local DuckDB has boundary tables but metric columns are empty, the QA app
will show metric coverage as `0.0%`. Rebuild
`property_explorer_gold.fct_tract_features`,
`property_explorer_gold.fct_nta_features`, and
`neighborhood_character_mart` from the configured sources to refresh the full
surface.
