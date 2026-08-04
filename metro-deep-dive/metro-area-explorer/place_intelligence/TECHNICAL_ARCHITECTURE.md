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

## 7.1 Page review framework

Because the pages are now interconnected and performance issues are surfacing at the app level, page review should happen in one consistent structure:

1. what the page renders for the user
2. which payloads it loads today
3. which artifact files those payloads read
4. which upstream prep/build functions produced those files
5. which dependencies are truly required for first paint
6. what should be refactored for page-level performance

This keeps the review grounded in outputs rather than abstract modules.

## 7.2 Page inventory at a glance

This is the working page-by-page dependency map to expand as the review proceeds.

| Page | User-facing purpose | Current payload families | Review status |
|---|---|---|---|
| `pages/d_overview.py` | Orientation-first site summary and map | D1 base, D2 summary/profile, D3 summary, D5 site flood note, shared map payload | Reviewed below |
| `pages/d_people.py` | Catchment population and household profile | D2, likely shared map payload | Pending |
| `pages/d_place.py` | Daytime activity, POIs, roads, barriers, and place context | D3, D4, D5, shared map payload | Pending |
| `pages/d_market.py` | Market-wide context and benchmarks outside the catchment | D2 benchmarks, market payload, possibly D4/D5 context | Pending |
| `pages/d_methods.py` | Methods, caveats, and diagnostic transparency | D1 diagnostics plus selected D2-D5 metadata | Pending |

## 7.3 App content inventory

This section is the working guide to what the app is supposed to show and what it actually shows today.

For each page, it records:

- the page job in the product
- the current visible sections in the Streamlit implementation
- the current charts, tables, cards, and maps
- the insight the page is supposed to help a reader answer
- the main gaps between the current implementation and the spec

This is intentionally more output-oriented than the dependency review. It is the section to use when deciding what to build next on each page.

### `pages/d_overview.py`

**Page job**

Orient the reader quickly to the site, its primary catchment, and the highest-priority screens that should shape the rest of the read.

**Current visible sections**

- top-line site metrics row
- resolved coordinate / geocode caption
- context map
- primary-ring headline table
- flags and caveats

**Current UI elements**

- cards / metrics:
  - site address
  - node typology
  - 3-mile population
  - 3-mile household income
  - site flood zone
- map:
  - shared context map with default tract fill and rings on
- tables:
  - primary-ring headline table for a small metric set
  - flags and caveats table for barrier and flood notes

**Current insight question**

- What is this site, broadly speaking?
- How big and how affluent is the primary ring?
- Is there an obvious flood or severance note that should frame the rest of the analysis?

**Spec-aligned intended insight**

From `SPEC.md`, the Overview tab should be the one-screen orientation layer: site card, primary-ring headline numbers, percentile and 5-year direction, barrier flag when triggered, flood zone, and the interactive context map directly beneath it.

**Current gaps vs spec**

- the top-line cards do not yet consistently expose percentile and 5-year direction the way the spec describes
- the headline table is present, but the page still feels more like a data summary than a finished orientation narrative
- the current map is technically reusable, but still heavier than a summary page should need

### `pages/d_people.py`

**Page job**

Explain who lives near the site, who works near the site, and how that changes across distance bands.

**Current visible sections**

- ring gradient
- benchmark companion
- day and night divergence
- workplace industry breakout

**Current UI elements**

- controls:
  - metric selector for the ring-gradient section
  - ring selector for workplace industry breakout
- charts:
  - ring-gradient bar chart for one selected D2 metric
  - 5-year change bar chart for the selected metric when available
  - jobs-to-workers ratio bar chart by ring
  - workplace jobs by industry bar chart for one selected ring
- tables:
  - benchmark companion table with primary-ring value and CBSA percentile
  - day/night divergence table with jobs, resident workers, ratio, and net change

**Current insight question**

- Who is in range of the site?
- How does the catchment change from 1 to 3 to 5 miles?
- Does the area gain people during the workday or lose them?

**Spec-aligned intended insight**

From `SPEC.md`, the People tab should combine residents and workers into one story: ring gradient, age distribution, income and education with percentile markers, day/night divergence, workplace jobs by industry, jobs-to-workers ratio, and 5-year direction attached to each panel.

**Current gaps vs spec**

- age distribution is not yet a dedicated section; only `median_age` is available through the generic ring-gradient selector
- income and education exist as selectable metrics, but not yet as intentional, named panels
- percentile context appears in the benchmark table, but not yet embedded cleanly into each substantive panel
- the page is analytically useful already, but it still reads like a flexible diagnostic surface rather than a finished reader flow

### `pages/d_place.py`

**Page job**

Explain the physical and commercial environment around the site: what is nearby, how the corridor works, what barriers matter, and what flood or hazard context should be noted.

**Current visible sections**

- context map
- POI mix
- road hierarchy and corridor traffic
- barrier and severance detail
- flood screening

**Current UI elements**

- map:
  - shared context map with POIs, roads, flood, and severed-area layers on by default
- controls:
  - ring selector for POI counts
- charts:
  - POI class bar chart for the selected ring
  - top 1-mile corridor segments by AADT bar chart
  - frontage AADT trend line chart when trend rows are available
  - flood-zone area-share bar chart by ring
- tables:
  - POI counts table
  - frontage roadway table
  - barrier/severance detail table
  - ring-variants comparison table
  - NFHL site-zone table
  - NRI catchment scores table

**Current insight question**

- What kind of place is this site in?
- Is the area commercially active, accessible, severed, or flood-exposed in ways that matter for the brief?

**Spec-aligned intended insight**

From `SPEC.md`, the Place tab should cover co-tenancy and POI density, competitive vs complementary breakdown, nearest anchors, road hierarchy, AADT corridor context, severance detail, and flood-zone shares, with the shared map defaulting to POIs plus roads plus flood.

**Current gaps vs spec**

- nearest-anchor logic is not surfaced as its own reader-facing panel
- POI density and co-tenancy narrative are still represented mainly as counts by class
- barrier detail is present and strong, but the page does not yet synthesize it into a concise “what this means for the site” read
- NRI and NFHL are shown, but the distinction between catchment hazard context and parcel/site flood screening could still be clearer in the UX

### `pages/d_market.py`

**Page job**

Give the reader just enough metro-level context to understand the site inside the broader Jacksonville market without overwhelming the site brief.

**Current visible sections**

- industry mix
- housing market trend

**Current UI elements**

- controls:
  - employment vs GDP basis radio toggle
- charts:
  - industry-share bar chart for the selected basis
  - ZHVI trend line chart
  - ZORI trend line chart
- tables:
  - top-sector market table
  - housing context table

**Current insight question**

- What kind of metro is this site sitting in?
- Is the surrounding market growing or expensive in ways that matter for site interpretation?

**Spec-aligned intended insight**

From `SPEC.md`, the Market tab should provide Jacksonville CBSA context: industry mix, GDP, employment, and housing market trend, using existing Gold data and staying intentionally compact.

**Current gaps vs spec**

- the tab is compact as intended, but still looks like a raw market-context utility more than a polished market one-pager
- employment and GDP mix are present, but the narrative bridge back to site relevance is still thin
- if this becomes a reusable Metro Deep Dive component, the output shape likely needs one clearer “market read” summary block

### `pages/d_methods.py`

**Page job**

Make the brief inspectable and trustworthy by exposing method assumptions, diagnostics, source vintages, geocode provenance, and missing-data explanations.

**Current visible sections**

- apportionment and reliability
- geocode provenance
- unavailable metrics and skip reasons
- source vintages
- method notes

**Current UI elements**

- tables:
  - coverage diagnostic table
  - geocode provenance table
  - D2 skip-reasons table
  - source-vintages table
- notes:
  - short bullet list of core method caveats

**Current insight question**

- How were these numbers built?
- Which parts are approximate, missing, or fail-soft?

**Spec-aligned intended insight**

From `SPEC.md`, the Methods tab should cover apportionment assumptions, weight-table diagnostics, per-ring reliability flags, source vintages, geocode match quality, and what was unavailable and why.

**Current gaps vs spec**

- reliability flags are present through coverage diagnostics, but not yet clearly framed as a reader-facing reliability interpretation
- method notes are brief and useful, but could grow into a stronger appendix-style explanation block
- this page is already aligned with the spec conceptually, but may need better copy structure more than new analytics

### Build sequence recommendation

For section-by-section work, the best current order is:

1. `Overview`
2. `People`
3. `Place`
4. `Market`
5. `Methods`

That order matches both the reader journey and the dependency risk:

- `Overview` sets the summary contract and first-paint expectations
- `People` clarifies the D2 presentation model
- `Place` is the richest mixed-surface page and will benefit from having the first two pages settled
- `Market` is comparatively compact
- `Methods` should close by documenting the final shape honestly

## 7.4 Page review: `pages/d_overview.py`

### What the page renders

The Overview page is the orientation page for one site. It renders:

- five top-line metrics:
  - site address
  - node typology
  - primary-ring population
  - primary-ring median household income
  - site flood zone
- resolved site/geocode metadata
- the shared context map
- a small primary-ring headline table
- a small flags/caveats table

Architecturally, this page should be one of the lightest pages in the app. It is summary-first and does not need the full analytical surface to achieve first paint.

### What the page loads today

`pages/d_overview.py` now calls:

- `load_overview_payload(site_config_path)`
- `render_context_map(...)`

The page code itself is thin. The summary path is now smaller and more explicit, and the main remaining performance question is the breadth of the shared context-map payload.

### Required data contract

The Overview page only needs the following data to render its summary correctly:

- site identity:
  - site address
  - site id
  - primary ring distance
- resolved-site provenance:
  - resolved latitude
  - resolved longitude
  - geocode source
  - match type
- site-card metrics:
  - node typology label
  - primary-ring population
  - primary-ring population CBSA percentile
  - primary-ring median household income
  - primary-ring median household income 5-year change
  - site flood zone
- headline table rows:
  - population
  - households
  - median household income
  - BA+ share
  - median home value
  - for each row: primary-ring value, CBSA percentile, 5-year change, year, source table
- site-card flags:
  - any barrier rows where `site_card_flag = true`
  - flood-zone panel date note when available

Everything above now fits a compact Overview-specific artifact rather than requiring the full D1, D2, D3, and D5 payload bundles.

### Where that data sits

The required fields come from these existing upstream artifacts and prep outputs:

- `site.json`
  - site identity
- `resolved_site.json`
  - resolved coordinates and geocode provenance
- `d2_metric_summary.csv`
  - primary-ring values
  - CBSA percentiles
  - 5-year changes
  - source/year metadata for headline rows
- `d3_meta.json`
  - node typology label
- `d3_barrier_summary.csv`
  - site-card barrier rows
- `d5_nfhl_site_zone.csv`
  - flood zone and panel date

Those sources are now collapsed into:

- `overview.json`

That file is the intended app contract for the summary portion of the Overview page.

#### Shared map payload

`render_context_map()` calls `load_context_map_payload(site_config_path, fill_metric, include_flood_context)`.

For Overview, the default layer state is:

- tract fill on
- rings on
- POIs off
- roads off
- flood off
- severed off

Even with those defaults, `load_context_map_payload()` still reads:

- `map/tract_fill_<metric>.geojson`
- `map/rings.geojson`
- `map/water_adjusted_rings.geojson`
- `map/severed_area.geojson`
- `map/poi_rows.csv`
- `map/roads.geojson`
- `map/meta.json`
- `d3_barrier_summary.csv`

And it conditionally skips only:

- `map/flood.geojson`

So the current shared map contract is convenient, but it is not layer-lazy. The Overview page loads POIs, roads, severed polygons, and barrier summary even when those layers are off on first paint.

### Upstream builders behind the Overview page

The Overview page is downstream of the following build path:

- D1 base:
  - `site_prep.build_site_base_payload()`
  - written by `artifact_store.build_site_artifacts()`
- D2 summary/profile:
  - `site_prep.build_d2_profile_payload()`
  - `site_prep._build_d2_metric_summary()`
  - written by `artifact_store.build_site_artifacts()`
- D3 node typology and barrier summary:
  - `site_prep.get_d3_context_payload()`
  - written by `artifact_store.build_site_artifacts()`
- D5 site flood zone:
  - `site_prep.get_d5_flood_payload()`
  - written by `artifact_store.build_site_artifacts()`
- shared map assets:
  - `artifact_store._build_context_map_artifacts()`
  - `site_prep.build_context_map_payload()`
  - `site_prep.build_context_tract_fill()`

This is a good read-only architecture. The problem is not that Overview computes too much on page load. The problem is that the artifact bundles are too coarse for a summary page.

### Performance judgment for Overview

The main bottlenecks visible from code review are:

1. summary path overfetch was the first issue

- this has now been reduced by collapsing the Overview summary contract into `overview.json`
- the page no longer needs to read the full D1, D2, D3, and D5 bundles for its cards, caption, headline table, and flags

2. map payload overfetch

- the shared map loader eagerly reads multiple heavy layers even when they are turned off by default
- `water_adjusted_rings_geojson` is loaded for Overview but not used in the render path

3. file-shape inefficiency

- the app contract is spread across many CSV and GeoJSON files
- that is inspectable and easy to debug, but it increases read and deserialization overhead for a page that mostly wants compact summary records

4. duplicated D2 access paths were another issue

- this has now been reduced on the Overview page by relying on the summary artifact path instead of a `catchment_profile` fallback
- the broader D2 transitional shape still exists for the other pages

### Refactors recommended for Overview first

These are the highest-value refactors for `d_overview.py`.

#### 1. Add a compact overview payload

Status: completed.

The Overview page now has a purpose-built artifact:

- `overview.json`

It contains:

- site metadata needed for the header
- resolved coordinates and geocode note
- node typology label
- primary-ring population card
- primary-ring income card
- site flood zone
- barrier/flood flag rows
- headline table rows for the Overview metric set

That lets the page avoid loading:

- `base_weight_table.csv`
- `base_coverage_diagnostic.csv`
- `d2_metric_long.csv`
- `d2_benchmark_table.csv`
- most of the D3 bundle
- most of the D5 bundle

#### 2. Split the shared map payload into a minimal first-paint bundle plus optional layers

For Overview, first paint only needs:

- `map/meta.json`
- one `map/tract_fill_<metric>.geojson`
- `map/rings.geojson`
- site point metadata

Optional lazy layers should be read only when the corresponding checkbox is enabled:

- `map/poi_rows.csv`
- `map/roads.geojson`
- `map/severed_area.geojson`
- `map/flood.geojson`

If we keep one shared map API, it should still support layer-lazy reads under the hood.

#### 3. Remove the D2 fallback path once `metric_summary` is trusted

Status: completed for Overview.

Overview now relies on the Overview summary artifact path instead of reading `catchment_profile` directly.

That reduces:

- branching in the page
- repeated formatting logic
- the need to load `d2_catchment_profile.csv` for this page

#### 4. Add page-level timing visibility

The repo already has:

- build-step timing in `manifest.json`
- `profile_d6_pages.py`

But there are no built manifests checked into the current repo snapshot, so page review cannot yet compare theory to observed timings from artifacts alone.

The next performance pass should capture, for at least one real site:

- artifact build timings by step
- page load timings by payload loader
- map layer toggle timings

Without that, we can identify architecture debt confidently, but not rank every hotspot empirically.

### Recommended target state for Overview

The Overview page should eventually depend on:

- one compact summary payload
- one minimal map payload
- optional layer-specific map loads triggered only when a layer is turned on

That would make Overview a true summary page again and would also establish the pattern the other pages can follow.

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
