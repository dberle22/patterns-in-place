# Place Intelligence Data Products

This note describes the concrete data products the Place Intelligence build now creates, where they live, and which code paths materialize them.

## Build entrypoints

- Artifact build CLI: `metro-deep-dive/metro-area-explorer/place_intelligence/build_site_artifacts.py`
- Artifact writer/reader: `metro-deep-dive/metro-area-explorer/place_intelligence/artifact_store.py`
- Prep/business logic: `metro-deep-dive/metro-area-explorer/place_intelligence/site_prep.py`
- Default site configs:
  - `metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_v0.yaml`
  - `metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_downtown_v0.yaml`

Run one site:

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/build_site_artifacts.py \
  metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_v0.yaml
```

Run every discovered site config:

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/build_site_artifacts.py --all-sites
```

## Materialized output layout

Artifacts are written per site under:

```text
metro-deep-dive/metro-area-explorer/place_intelligence/outputs/jacksonville_fl/site_artifacts/<site_id>/
```

The artifact directory is the app-facing contract. Streamlit pages read from these files instead of recomputing D1-D5 at page load.

## Product inventory

### 1. Build manifest and site metadata

Files:

- `manifest.json`
- `site.json`
- `resolved_site.json`

What they hold:

- site id, market id, source config filename, UTC build timestamp
- per-step build timings in `step_timings_seconds`
- authored site config and resolved geocode/tract metadata

Materialized by:

- `artifact_store.build_site_artifacts()`

### 2. D1 base catchment products

Files:

- `base_weight_table.csv`
- `base_coverage_diagnostic.csv`

What they hold:

- tract-to-ring apportionment weights
- coverage/reliability diagnostics for the site rings

Materialized by:

- `site_prep.build_site_base_payload()`
- `apportion.apportion_weights()`
- `apportion.coverage_diagnostic()`

### 3. D2 catchment profile products

Files:

- `d2_catchment_profile.csv`
- `d2_benchmark_table.csv`
- `d2_skip_reasons.csv`

What they hold:

- apportioned ring metrics at the site level
- CBSA/county/state/national benchmark rows for the primary ring
- explicit reasons for tract-grain metrics that could not be rendered

Materialized by:

- `site_prep.build_d2_profile_payload()`

Primary upstream tables:

- `patterns_in_place.gold.population_demographics`
- `patterns_in_place.gold.economics_income_wide`
- `patterns_in_place.gold.housing_core_wide`
- `patterns_in_place.gold.transport_built_form_wide`

### 4. D3 place and daytime-context products

Files:

- `d3_daytime_population.csv`
- `d3_poi_counts.csv`
- `d3_road_context.json`
- `d3_barrier_summary.csv`
- `d3_ring_variants_comparison.csv`
- `d3_meta.json`

What they hold:

- jobs/workers and day-night divergence by ring
- competitive/complementary/anchor POI counts
- roadway/barrier context
- baseline versus water-adjusted ring comparison
- node typology label, rationale, and page-copy note

Materialized by:

- `site_prep.get_d3_context_payload()`

Primary upstream products:

- `silver.lehd_lodes_wac`
- `silver.lehd_lodes_rac`
- `outputs/jacksonville_fl/overture_pois.parquet`
- normalized OSM outputs under `outputs/jacksonville_fl/`

### 5. D4 traffic products

Files:

- `d4_frontage_segments.csv`
- `d4_frontage_trend.csv`
- `d4_ranked_segments_1mi.csv`
- `d4_meta.json`

What they hold:

- snapped frontage-road AADT rows
- frontage trend series
- ranked nearby corridor table
- count year and copy note

Materialized by:

- `site_prep.get_d4_traffic_payload()`

Primary upstream products:

- `outputs/jacksonville_fl/fdot_aadt_segments.parquet`
- `outputs/jacksonville_fl/fdot_aadt_historical_segments.parquet`

### 6. D5 flood products

Files:

- `d5_nri_catchment_scores.csv`
- `d5_nri_catchment_top_hazards.csv`
- `d5_nri_cbsa_benchmark.csv`
- `d5_nri_cbsa_top_hazards.csv`
- `d5_nfhl_site_zone.csv`
- `d5_nfhl_ring_shares.csv`
- `d5_meta.json`

What they hold:

- tract-apportioned FEMA NRI risk context
- CBSA benchmark hazard context
- live NFHL site-point flood zone lookup
- ring-level flood-zone area shares
- NFHL service status/error fields for fail-soft rendering

Materialized by:

- `site_prep.get_d5_flood_payload()`

Primary upstream products:

- `patterns_in_place.silver.fema_nri`
- live FEMA NFHL ArcGIS service

### 7. Market-tab products

Files:

- `market_employment_mix.csv`
- `market_gdp_mix.csv`
- `market_housing_context.csv`
- `market_meta.json`

What they hold:

- compact metro context for employment mix, GDP mix, and housing trend

Materialized by:

- `site_prep.build_market_context_payload()`

### 8. Shared D6 map products

Files:

- `map/tract_fill_<metric>.geojson`
- `map/rings.geojson`
- `map/water_adjusted_rings.geojson`
- `map/severed_area.geojson`
- `map/roads.geojson`
- `map/flood.geojson`
- `map/poi_rows.csv`
- `map/meta.json`

What they hold:

- one tract-fill layer per supported metric
- baseline and adjusted catchment geometry
- severed-area shading geometry
- road, flood, and POI overlays
- site point, view state, and tract-fill provenance metadata

Materialized by:

- `artifact_store._build_context_map_artifacts()`
- `site_prep.build_context_map_payload()`
- `site_prep.build_context_tract_fill()`

## Materialization design choices

### Site-scoped, not global

The current product boundary is one artifact folder per site config. We are not materializing a global Place Intelligence warehouse layer yet; we are materializing app-facing products for a specific site/market run.

### Derived products versus raw caches

The Jacksonville market caches under `outputs/jacksonville_fl/` are upstream inputs.

Examples:

- Overture POI parquet
- normalized OSM parquet layers
- FDOT AADT parquet layers
- manifests describing those extracts

The `site_artifacts/<site_id>/` directory is the downstream derived product layer for the app.

### Fail-soft live dependencies

NFHL remains a live dependency at build time rather than a repo-local cached layer. That means:

- the build can still succeed when NFHL is temporarily unavailable
- `d5_meta.json` and `map/meta.json` record service status for the UI
- D5 and flood overlays degrade cleanly instead of breaking the entire brief

### Timed build manifest

`manifest.json` now records per-step timings so we can see which stage dominates a slow site build without adding ad hoc instrumentation each time.

## Current operational gaps

- The Baymeadows site config is the primary validated run.
- The downtown Jacksonville config now exists and is discoverable by the app/build CLI.
- The remaining open validation step is a full end-to-end downtown artifact build and app sanity check against live inputs.
