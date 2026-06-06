# sql/gold - Temporary

These scripts build the `fct_tract_features` and `fct_nta_features` tables from
ACS data in the metro_deep_dive / foundations DuckDB.

**Status: migrate to foundations/**

These belong in `foundations/etl/` once the ACS features are promoted to the
foundations Gold layer and the Points pipeline is centralized. At that point,
stoop will read these tables directly from the foundations DuckDB rather than
building them locally.

Until then, these scripts are the authoritative build for stoop's demographic
feature tables. Run them via the pipeline entry points in
`src/nyc_property_finder/pipelines/build_neighborhood_features.py`.
