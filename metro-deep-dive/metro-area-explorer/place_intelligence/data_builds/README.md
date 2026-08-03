# Place Intelligence Data Builds

This README is the working implementation playbook for splitting the Place Intelligence build system into small, debuggable, product-scoped steps.

This is not the artifact inventory. `DATA_PRODUCTS.md` remains the inventory of what gets materialized and where it lands. This README is the guide for how we continue splitting the build architecture and how we validate each step.

## Purpose And Rules

The build architecture should follow these rules:

- each build product gets its own script
- each script owns one output responsibility
- page builders only assemble already-built products
- shared helpers live in `data_builds/common.py` or a small `helpers/` package
- app pages must never recompute analysis
- compatibility wrappers may exist temporarily, but `data_builds/` is the source of truth

Current defaults locked in:

- `data_builds/README.md` is the working refactor guide
- `DATA_PRODUCTS.md` stays the artifact inventory
- `artifact_store.py` remains read-only app contract code plus temporary compatibility wrapper
- all build orchestration lives under `data_builds/`

## Current State

As of Sunday, August 2, 2026, the repo has an intermediate split in place:

- `data_builds/common.py`
- `data_builds/build_base.py`
- `data_builds/build_d2.py`
- `data_builds/build_d3.py`
- `data_builds/build_d4.py`
- `data_builds/build_d5.py`
- `data_builds/build_market.py`
- `data_builds/build_overview.py`
- `data_builds/build_context_map.py`
- `data_builds/build_all.py`
- `data_builds/foundations/`
- `data_builds/pages/`

The `foundations/` and `pages/` packages now exist and the first wrapper migrations have started, but the flat scripts are still present as compatibility entrypoints. This is an improvement over the previous monolithic builder, but it is still an intermediate step. The flat scripts are not the final target layout.

## Target Folder Structure

The end-state structure should look like this:

```text
data_builds/
  README.md
  common.py
  build_all.py

  foundations/
    build_site_identity.py
    build_base_geometry.py
    build_base_weights.py
    build_base_diagnostics.py

  d2/
    build_d2_metric_long.py
    build_d2_catchment_profile.py
    build_d2_benchmarks.py
    build_d2_metric_summary.py
    build_d2_skip_reasons.py

  d3/
    build_d3_daytime_population.py
    build_d3_poi_counts.py
    build_d3_road_context.py
    build_d3_barrier_summary.py
    build_d3_ring_variants.py
    build_d3_node_typology.py

  d4/
    build_d4_frontage_segments.py
    build_d4_frontage_trend.py
    build_d4_ranked_segments.py
    build_d4_meta.py

  d5/
    build_d5_nri_scores.py
    build_d5_nri_top_hazards.py
    build_d5_nfhl_site_zone.py
    build_d5_nfhl_ring_shares.py
    build_d5_meta.py

  market/
    build_market_employment_mix.py
    build_market_gdp_mix.py
    build_market_housing_context.py
    build_market_meta.py

  maps/
    build_map_core.py
    build_map_tract_fill.py
    build_map_pois.py
    build_map_roads.py
    build_map_flood.py
    build_map_severed_area.py
    build_map_meta.py

  pages/
    build_overview_page.py
    build_people_page.py
    build_place_page.py
    build_market_page.py
    build_methods_page.py
```

Notes:

- the current flat scripts under `data_builds/` are intermediate wrappers or stepping stones
- we should prefer moving one product family at a time into the target subfolders
- `build_all.py` should remain the orchestration entrypoint for a full app-facing build

## Product Catalog And Dependencies

The table below is the source-of-truth dependency map for the split.

| Product | Outputs | Inputs | Downstream consumers |
|---|---|---|---|
| `foundations.site_identity` | `site.json`, `resolved_site.json` | site yaml, geocoder/manual override | all downstream builds |
| `foundations.base_geometry` | cumulative/base ring geometries | resolved site | `d3`, `d4`, `d5`, `maps` |
| `foundations.base_weights` | `base_weight_table.csv` | resolved site, tract geometry | `d2`, `d3`, `d5` |
| `foundations.base_diagnostics` | `base_coverage_diagnostic.csv` | weight table | `pages.methods` |
| `d2.metric_long` | canonical D2 fact table | weight table, Gold metric surfaces | `d2` derivatives, `pages.methods` |
| `d2.catchment_profile` | `d2_catchment_profile.csv` | `d2.metric_long` | `pages.people` |
| `d2.benchmarks` | `d2_benchmark_table.csv` | Gold surfaces | `pages.people`, optionally `pages.market` |
| `d2.metric_summary` | `d2_metric_summary.csv` | `d2.metric_long` | `pages.overview`, `pages.people` |
| `d2.skip_reasons` | `d2_skip_reasons.csv` | D2 build state | `pages.methods` |
| `d3.daytime_population` | `d3_daytime_population.csv` | weight table, LEHD | `pages.people` |
| `d3.poi_counts` | `d3_poi_counts.csv` | ring geometry, Overture POIs | `pages.place` |
| `d3.road_context` | `d3_road_context.json` | ring geometry, OSM lines | `pages.place` |
| `d3.barrier_summary` | `d3_barrier_summary.csv` | ring geometry, weight table, OSM barriers | `pages.overview`, `pages.place` |
| `d3.ring_variants` | `d3_ring_variants_comparison.csv` | barrier summary, ring geometry | `pages.place`, `maps` |
| `d3.node_typology` | `d3_meta.json` or split typology/meta file | daytime, POIs, roads | `pages.overview`, `pages.place` |
| `d4.frontage_segments` | `d4_frontage_segments.csv` | site geometry, FDOT segments | `pages.place` |
| `d4.frontage_trend` | `d4_frontage_trend.csv` | frontage segments, historical AADT | `pages.place` |
| `d4.ranked_segments` | `d4_ranked_segments_1mi.csv` | ring geometry, FDOT segments | `pages.place` |
| `d5.nri_scores` | NRI score and hazard tables | weight table, FEMA NRI | `pages.place` |
| `d5.nfhl_site_zone` | `d5_nfhl_site_zone.csv` | site point, NFHL service | `pages.overview`, `pages.place` |
| `d5.nfhl_ring_shares` | `d5_nfhl_ring_shares.csv` | ring geometry, NFHL service | `pages.place` |
| `market.*` | market tables and meta | Gold market surfaces | `pages.market` |
| `maps.core` | site point, view state, rings | resolved site, ring geometry | all map-capable pages |
| `maps.tract_fill` | one file per metric | metric surfaces, tract geometry | `pages.overview`, `pages.place` |
| `maps.pois` | POI overlay rows | Overture POIs, ring geometry or map extent | `pages.overview`, `pages.place` |
| `maps.roads` | road overlay geometry | OSM or FDOT layers | `pages.overview`, `pages.place` |
| `maps.flood` | flood overlay geometry | NFHL geometry/ring context | `pages.overview`, `pages.place` |
| `maps.severed_area` | severed-area overlay geometry | ring variants, water barriers | `pages.overview`, `pages.place` |
| `pages.overview` | `overview.json` | `site_identity`, `d2.metric_summary`, `d3.node_typology`, `d3.barrier_summary`, `d5.nfhl_site_zone` | Streamlit Overview page |
| `pages.people` | `people.json` or page-ready summary contract | `d2.catchment_profile`, `d2.metric_summary`, `d3.daytime_population` | Streamlit People page |
| `pages.place` | `place.json` | `d3.*`, `d4.*`, `d5.*`, optional map layers | Streamlit Place page |
| `pages.market` | `market_page.json` | `market.*` | Streamlit Market page |
| `pages.methods` | `methods.json` | `site_identity`, `base_diagnostics`, `d2.skip_reasons`, `d2.metric_long` | Streamlit Methods page |

### Important Page Dependency Rule

`pages.overview` must not require:

- `d4`
- `market`
- full map overlays that are not needed for first paint

That rule is intentionally strict because Overview is the template for cleaner page-scoped contracts.

## Shared Helper Boundaries

### Keep In `site_prep.py` For Now

Keep business logic and compute functions in `site_prep.py` temporarily when they are already shared across multiple builders and are not yet worth re-homing.

Examples:

- geospatial ring construction helpers
- D2 metric-surface query logic
- D3 barrier and typology logic
- D4 traffic computation logic
- D5 flood and NFHL logic

### Move Or Expose Into `data_builds/common.py` Or `data_builds/helpers/`

Shared build support belongs in `data_builds/common.py` now, and later in a small helper package as needed.

Current or intended shared helper categories:

- artifact path helpers
- manifest read/write helpers
- CSV/JSON read/write helpers
- prerequisite checks
- step timing/logging
- common CLI site selection
- page-contract assembly helpers such as Overview summary row extraction

### Helper Constraints

Helper modules must not:

- call Streamlit
- mix read-side app payload loading with build orchestration
- hide cross-product dependencies implicitly

Each build script should:

- declare prerequisites explicitly in code
- declare prerequisites explicitly in this README

## Phased Refactor Sequence

### Phase 1: Document The Architecture

- add `data_builds/README.md`
- define target structure, product catalog, dependency graph, helper boundaries, and migration rules

Status on August 2, 2026:

- in progress with this README

### Phase 2: Stabilize The Current Intermediate Split

- keep existing flat scripts working
- confirm `build_base.py`, `build_d2.py`, `build_d3.py`, `build_d4.py`, `build_d5.py`, `build_market.py`, `build_overview.py`, `build_context_map.py`, `build_all.py`
- make `artifact_store.py` read-only plus compatibility wrapper only

Expected result:

- the app can still read existing loader contracts
- individual build products can be run and debugged independently

### Phase 3: Split Foundations

- separate site identity, geometry, weights, diagnostics
- make all downstream scripts depend on the smallest required foundation artifact
- ensure `Overview` only depends on the products it actually needs

Priority inside this phase:

1. `site_identity`
2. `base_geometry`
3. `base_weights`
4. `base_diagnostics`

### Phase 4: Split D2 And D3

- split D2 first because it feeds both `Overview` and `People`
- separate metric-long, summary, benchmarks, skip reasons
- split D3 into independent daytime, POI, roads, barrier, ring-variant, typology builders

Priority order:

1. `d2.metric_long`
2. `d2.metric_summary`
3. `d2.catchment_profile`
4. `d2.benchmarks`
5. `d2.skip_reasons`
6. `d3.daytime_population`
7. `d3.poi_counts`
8. `d3.road_context`
9. `d3.barrier_summary`
10. `d3.ring_variants`
11. `d3.node_typology`

### Phase 5: Split Maps And Page Contracts

- move map outputs into layer-specific scripts
- keep page builders as pure assembly from prior artifacts
- ensure toggled map layers are not prerequisites for first paint unless required

Priority order:

1. `pages.overview`
2. `pages.people`
3. `maps.core`
4. `maps.tract_fill`
5. remaining optional map overlays
6. `pages.place`
7. `pages.market`
8. `pages.methods`

### Phase 6: Clean Up Compatibility

- decide whether to keep `build_site_artifacts.py`
- decide whether to keep flat `data_builds/build_*.py` wrappers after subfolders exist
- update docs and remove stale build paths once all pages use the new contracts

Compatibility cleanup should happen last, not during the earlier split, so the app remains usable while the architecture changes underneath it.

## Test And Verification Plan

### Static Checks

- every build script compiles
- every build script has a clear prerequisite failure message
- no build script imports Streamlit
- `artifact_store.py` does not orchestrate domain builds directly beyond compatibility wrapper

Suggested command:

```bash
python3 -m py_compile metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/*.py
```

### Runtime Checks

- `build_base.py` writes only base artifacts and updates `manifest.json`
- `build_overview.py` succeeds when only its true prerequisites exist
- `build_overview.py` does not require `d4`, market, or full map artifacts
- `build_d2.py` and `build_d3.py` can be run independently after `base`
- `build_all.py` produces the full app-facing bundle in deterministic order
- `artifacts_exist()` returns `False` until required app steps are complete

### Acceptance Scenarios

Fresh site workflow:

1. run `build_base.py`
2. inspect outputs
3. run `build_d2.py`
4. inspect outputs
5. run `build_d3.py`
6. inspect outputs
7. run `build_overview.py`
8. confirm `overview.json`
9. run `build_all.py`
10. confirm the remaining steps materialize

Suggested commands:

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/build_base.py \
  metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_v0.yaml
```

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/build_d2.py \
  metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_v0.yaml
```

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/build_d3.py \
  metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_v0.yaml
```

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/build_overview.py \
  metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_v0.yaml
```

```bash
.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/build_all.py \
  metro-deep-dive/metro-area-explorer/place_intelligence/site_jacksonville_v0.yaml
```

## Compatibility And Migration Defaults

Lock these defaults unless there is a strong reason to revisit them:

- keep existing artifact filenames unless there is a strong reason to change them
- prefer adding smaller build steps before renaming outputs
- keep `artifact_store.py` loader APIs stable during the split
- keep `build_site_artifacts.py` as a compatibility wrapper during the migration
- do not change page rendering contracts and build layout in the same step unless the page contract is the explicit goal
- prioritize `Overview` and `People` first because they define the cleaner page-contract pattern

## Public Contract Notes

Important interface expectations:

- `data_builds/README.md` is now the canonical working doc for build architecture
- `data_builds/` is the source-of-truth build system
- `artifact_store.py` remains the public read-side loader contract for the app
- `build_site_artifacts.py` remains temporary and should only wrap `data_builds/build_all.py`
- `manifest.json` must track both `completed_steps` and `step_timings_seconds`
- page builders are allowed, but only as assembly of already-built products

## Immediate Next Steps

The next implementation pass should do the following in order:

1. confirm the current flat build scripts are stable enough to act as wrappers
2. split `foundations` into separate scripts
3. split `d2` into smaller products
4. split `d3` into smaller products
5. move `Overview` to the smallest true dependency set
6. move `People` to the same page-contract pattern

Do not start by reorganizing everything at once. Move one product family at a time, keep the manifest contract stable, and preserve the current app loader interface until the smaller products are proven.

## Assumptions

- the default plan doc location is `place_intelligence/data_builds/README.md`
- `DATA_PRODUCTS.md` stays an output inventory rather than becoming the working refactor guide
- current flat build scripts are intermediate and will later become wrappers or move into subfolders
- this is a build-architecture split and testability refactor, not a redesign of analytical methods
- SQL is allowed for future product scripts where a product is naturally table-shaped, but no SQL migration is required in this first README-driven pass
