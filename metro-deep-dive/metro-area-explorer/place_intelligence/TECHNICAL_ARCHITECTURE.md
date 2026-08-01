# Place Intelligence Technical Architecture

Last updated: 2026-08-01

This document explains how the Place Intelligence system is structured today:

- what each module does
- how data is ingested, transformed, materialized, and rendered
- what the data products are
- how those products fit together
- how the app turns materialized products into analysis
- where the current design is intentionally transitional

It is written as a system review document, not a spec.

## 1. System purpose

Place Intelligence is a site-level analysis system for producing a forwardable context brief around one property address.

The current v0 product is a Streamlit app backed by prebuilt site artifacts. The core idea is:

1. start from one site config
2. resolve the site to geometry and tract context
3. compute reusable analytical products for that site
4. materialize those products to disk
5. render the app entirely from those materialized products

This means the analytical system is not the app itself. The app is the final consumer of a site-scoped artifact layer.

## 2. Architecture at a glance

```text
site YAML
  -> geocode / tract resolution
  -> D1 catchment geometry + weights
  -> D2 demographic/economic/housing/commute metrics
  -> D3 place + daytime context
  -> D4 traffic context
  -> D5 flood / hazard context
  -> D6 map-specific derived layers
  -> site_artifacts/<site_id>/...
  -> Streamlit pages read artifacts only
```

There are four major layers:

1. configuration layer
2. analytical prep layer
3. materialized artifact layer
4. rendering layer

## 3. Module map

### 3.1 Config and orchestration

`site_jacksonville_v0.yaml`
`site_jacksonville_downtown_v0.yaml`

- site-level configuration inputs
- define the site id, address, coordinates, market id, asset type, and ring structure

`build_site_artifacts.py`

- thin CLI entrypoint
- builds artifacts for one or more site configs
- intended batch/materialization entrypoint

`artifact_store.py`

- owns artifact materialization and artifact reads
- is the boundary between analytical prep and app rendering
- writes the app-facing contract under `outputs/<market>/site_artifacts/<site_id>/`
- records per-step timings in the build manifest

### 3.2 Analytical prep layer

`site_prep.py`

- main analytical composition module
- owns D2-D5 payload construction and shared D6 map payload logic
- reads from DuckDB, parquet caches, and selected live services
- returns structured dataframes/dicts that are suitable for artifact writing
- deliberately contains no Streamlit imports

`apportion.py`

- D1 analytical foundation
- builds ring geometries
- computes tract-to-ring weight tables
- applies extensive/intensive metric apportionment
- computes coverage diagnostics

`geocode.py`

- site resolution utilities
- handles Census geocoder path and manual override path
- resolves tract geography for a configured site

### 3.3 Ingest and cache builders

`ingest_jax_overture.py`

- Jacksonville Overture POI ingest
- builds the place-level POI cache used by D3 and map overlays

`ingest_jax_osmextract.R`
`promote_jax_osmextract.py`

- Jacksonville OSM extract and normalization path
- builds normalized transport/water/rail layers used by D3 and D6

`ingest_fdot_aadt.py`

- FDOT AADT ingest and local cache builder
- produces traffic context inputs for D4

These are not the app-facing products. They are upstream cache-builders that feed the site-level artifact layer.

### 3.4 Rendering layer

`app.py`

- thin multi-page Streamlit shell
- owns page config, site selector, and page dispatch

`app_overview.py`
`app_people.py`
`app_place.py`
`app_market.py`
`app_methods.py`

- standalone single-page entrypoints for targeted review/debugging

`shared_ui.py`

- shared rendering utilities
- site selector
- artifact existence checks
- chart helpers
- context-map rendering
- artifact payload loading with Streamlit caching

`pages/d_overview.py`
`pages/d_people.py`
`pages/d_place.py`
`pages/d_market.py`
`pages/d_methods.py`

- page modules
- each exposes one `render_page(site_config_path)` function
- each is intended to degrade cleanly if one upstream payload is missing or incomplete

### 3.5 Profiling and review utilities

`profile_d6_pages.py`

- lightweight profiling harness for payload timing
- useful for measuring prep/runtime cost by page-oriented bundle

### 3.6 Review and design docs

`SPEC.md`

- product and analytical requirements

`METHODS_MEMO.md`

- methodology explanation and rationale

`DATA_PRODUCTS.md`

- inventory of materialized products

`decisions.md`
`notes.md`

- build-time decisions, validation notes, source-contract notes

## 4. Core design principle

The most important architectural decision is:

**the app should read artifacts, not compute analysis on page load**

That decision drives the current split:

- `site_prep.py` computes analytical payloads
- `artifact_store.py` materializes them
- `shared_ui.py` and `pages/` render them

This keeps:

- analytical logic separate from UI logic
- expensive work out of Streamlit page refreshes
- site runs reproducible and inspectable
- outputs reviewable outside the app

## 5. Data flow by layer

## 5.1 Input layer

Inputs come from three categories.

### Authored config

- site YAML files

### Internal persisted data

- DuckDB tables under `patterns_in_place`
- parquet and geo outputs under `outputs/jacksonville_fl/`

### Live services

- Census geocoder
- FEMA NFHL service

Live services are intentionally fail-soft where possible.

## 5.2 D1: Site geometry and apportionment

Primary modules:

- `geocode.py`
- `apportion.py`
- `site_prep.build_site_base_payload()`

Outputs:

- resolved site metadata
- ring geometry
- tract weight table
- coverage diagnostic

This is the foundation for all tract-based analysis.

The core analytical object is the tract-to-ring weight table. Every tract-derived metric depends on it.

## 5.3 D2: Catchment metrics

Primary module:

- `site_prep.py`

Current D2 design has two layers:

### Canonical analytical base

`metric_long`

This is the intended database-style fact table for D2.

Each row represents one metric observation at one analytical grain for one site:

- catchment metric rows
- benchmark rows

Shared columns include:

- `site_id`
- `market_id`
- `record_type`
- `metric`
- `metric_label`
- `topic`
- `ring_mi`
- benchmark metadata
- `value`
- `year`
- `source_table`
- change metadata
- percentile metadata

This is the correct durable shape for analytical storage because it is:

- composable
- easy to group/pivot
- easy to extend with more metrics
- easy to query like a fact table

### App-facing derived surface

`metric_summary`

This is a convenience table derived from `metric_long`.

It has one row per metric and pre-aggregated columns like:

- `ring_1_value`
- `ring_3_value`
- `ring_5_value`
- primary ring change
- primary ring percentile
- benchmark values by geography

This is not the canonical analytical store. It is the render-optimized view for the app.

### Legacy compatibility outputs

The system still also emits:

- `catchment_profile`
- `benchmark_table`

These are now derived views preserved for compatibility with existing pages/tests and for gradual migration.

## 5.4 D3: Place and daytime context

Primary module:

- `site_prep.get_d3_context_payload()`

Inputs:

- LEHD tables
- Overture POI cache
- normalized OSM cache
- D1 weight table

Outputs:

- daytime population by ring
- POI counts by ring and class
- road context summary
- barrier summary
- ring-variant comparison
- node typology label and rationale

Conceptually, D3 combines:

- apportionment-based tract analysis
- direct spatial joins
- heuristic classification

This is the most mixed analytical layer in the system.

## 5.5 D4: Traffic context

Primary module:

- `site_prep.get_d4_traffic_payload()`

Inputs:

- FDOT AADT caches
- site geometry
- cumulative rings

Outputs:

- frontage segments
- ranked nearby segments
- frontage trend

D4 is mostly direct spatial matching plus a small amount of business logic around snapping and selection.

## 5.6 D5: Flood and hazard context

Primary module:

- `site_prep.get_d5_flood_payload()`

Inputs:

- D1 weight table
- FEMA NRI silver table
- live FEMA NFHL service

Outputs:

- tract-apportioned hazard context
- CBSA hazard benchmark context
- site flood-zone lookup
- ring-level flood-zone area shares
- service status metadata

D5 intentionally splits:

- modeled catchment risk context from NRI
- parcel/ring flood-screening context from NFHL

## 5.7 D6: Map-specific derived products

Primary modules:

- `site_prep.build_context_map_payload()`
- `site_prep.build_context_tract_fill()`
- `artifact_store._build_context_map_artifacts()`

Outputs:

- tract fill geojson
- ring geojson
- adjusted ring geojson
- severed area geojson
- roads geojson
- flood geojson
- POI rows
- map metadata

This layer is important architecturally because it is not “analysis” in the same sense as D1-D5. It is:

- map packaging
- geometry serialization
- render-oriented derivation

## 6. Materialized data products

Artifacts are site-scoped and live under:

`outputs/jacksonville_fl/site_artifacts/<site_id>/`

The artifact directory is the app contract.

### Manifest and metadata

- `manifest.json`
- `site.json`
- `resolved_site.json`

### D1 products

- `base_weight_table.csv`
- `base_coverage_diagnostic.csv`

### D2 products

- `d2_metric_long.csv`
- `d2_metric_summary.csv`
- `d2_catchment_profile.csv`
- `d2_benchmark_table.csv`
- `d2_skip_reasons.csv`

### D3 products

- `d3_daytime_population.csv`
- `d3_poi_counts.csv`
- `d3_road_context.json`
- `d3_barrier_summary.csv`
- `d3_ring_variants_comparison.csv`
- `d3_meta.json`

### D4 products

- `d4_frontage_segments.csv`
- `d4_frontage_trend.csv`
- `d4_ranked_segments_1mi.csv`
- `d4_meta.json`

### D5 products

- `d5_nri_catchment_scores.csv`
- `d5_nri_catchment_top_hazards.csv`
- `d5_nri_cbsa_benchmark.csv`
- `d5_nri_cbsa_top_hazards.csv`
- `d5_nfhl_site_zone.csv`
- `d5_nfhl_ring_shares.csv`
- `d5_meta.json`

### Market products

- `market_employment_mix.csv`
- `market_gdp_mix.csv`
- `market_housing_context.csv`
- `market_meta.json`

### Shared map products

- `map/tract_fill_<metric>.geojson`
- `map/rings.geojson`
- `map/water_adjusted_rings.geojson`
- `map/severed_area.geojson`
- `map/roads.geojson`
- `map/flood.geojson`
- `map/poi_rows.csv`
- `map/meta.json`

## 7. How rendering works

Rendering is intentionally read-only with respect to analysis.

### Step 1: app boot

`app.py` starts Streamlit, renders the site selector, and chooses a page.

### Step 2: artifact existence check

`shared_ui.require_built_artifacts()` ensures the selected site already has built artifacts.

### Step 3: cached artifact reads

`shared_ui.py` loads payloads via:

- `load_site_base_payload`
- `load_d2_payload`
- `load_d3_payload`
- `load_d4_payload`
- `load_d5_payload`
- `load_market_payload`
- `load_context_map_payload`

These are Streamlit-cached wrappers around `artifact_store.py`.

### Step 4: page-specific rendering

Each page module:

- reads only the payloads it needs
- applies minor selection/filtering
- renders charts, tables, and maps
- degrades cleanly if a payload is empty

### Step 5: charting and map rendering

- charts are routed through shared helpers and chart-engine adapters in `shared_ui.py`
- maps are built from serialized geojson/csv artifacts, not from live recomputation

## 8. How data becomes analysis

There are two distinct transformations happening in the system.

### 8.1 Measurement

This is where raw or upstream data is turned into site-relevant numbers.

Examples:

- tract values become ring values through apportionment
- POI rows become counts by class and ring
- AADT segments become frontage-road context
- flood polygons become area shares

### 8.2 Interpretation

This is where measurements become analysis-friendly outputs.

Examples:

- percentile positions
- 5-year changes
- node typology
- barrier summaries
- benchmark comparisons
- primary-ring site cards

The system today performs both measurement and interpretation in the prep layer, then persists the interpreted outputs as artifacts for the app.

## 9. Current D2 architecture judgment

The D2 system is in the middle of moving from a “loop over metrics and emit page tables” design to a better product shape.

The better shape is:

1. one canonical long fact table
2. one or more derived render-friendly views

That is the right architecture for a future database-backed system because:

- SQL-style group by / pivot logic becomes straightforward
- new metrics do not require new bespoke render tables
- analysis can be run outside the app
- multiple products can share the same D2 base

The remaining technical debt is that parts of D2 still compute through Python loops before landing in the long table, rather than building the long surface through a more direct table-oriented unpivot/groupby flow at the source-table level.

## 10. Current strengths

- strong separation between prep and rendering
- materialized artifact layer already exists
- site configs make the system multi-site in principle
- D2 now has a much better canonical data-product shape
- page modules are thin and fail-soft
- app can be reasoned about as a consumer rather than a compute engine

## 11. Current weaknesses and transitional areas

### D2 still has transitional computation paths

The current D2 architecture is better than before, but not yet fully expressed as:

- source-table long base
- pure grouped aggregation
- pure pivoted summary

That is where the next cleanup should go.

### Build runtime is still too opaque on second-site live runs

The downtown artifact build remains the practical runtime bottleneck under live conditions.

We now have timing metadata, but the build path still needs one more performance/debug pass.

### Site artifacts are product-quality, but upstream caches are still mixed

Some upstream inputs are:

- local, stable, repo-managed caches

Others are:

- live services with fail-soft handling

That is acceptable for v0, but it is not yet a fully closed reproducible warehouse.

## 12. If we were formalizing this into a cleaner product architecture

The clean target architecture would be:

### Layer 1: source/cache layer

- Overture cache
- OSM normalized cache
- FDOT traffic cache
- optional cached flood extracts
- DuckDB analytical warehouse

### Layer 2: site analytical base

- site geometry
- tract weights
- canonical D2 long fact table
- D3/D4/D5 site analytical tables

### Layer 3: product views

- app summary tables
- map-ready geometry products
- investor-facing export products

### Layer 4: renderers

- Streamlit app
- static report export
- future API or notebook consumers

That would make Place Intelligence not just an app, but a reusable site-analysis product system.

## 13. Review questions

The main questions worth reviewing now are:

1. Is `site_artifacts/<site_id>/` the right product boundary?
2. Should D2 move fully to a source-table unpivot/groupby architecture next?
3. Which live-service dependencies should become cached products?
4. Which outputs are analytical base products versus purely render-oriented products?
5. Which modules are candidates for promotion into a shared `foundations/` layer?

## 14. Recommended next steps

1. Finish the D2 refactor so the canonical long table is built from source-table long surfaces rather than metric-by-metric loops.
2. Complete the downtown artifact validation run and record which remaining stage dominates runtime.
3. Update `DATA_PRODUCTS.md` so its D2 section explicitly includes `d2_metric_long.csv` and `d2_metric_summary.csv`.
4. Decide whether NFHL should remain live at build time or be cached into a reproducible local product.
