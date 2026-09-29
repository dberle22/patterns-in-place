# Explanation Catchment Epic 1 Audit

**Audit date:** September 11, 2026

**Status:** Complete

**Verdict:** Catchment is a **selective port**. It is not a repoint because the
legacy code already reads the same DuckDB file as the Position notebooks. It is
not a rewrite because the projected-ring and intersection method is sound and
reproducible. The data-access, aggregation, QA, and orchestration contracts do
need to be replaced or narrowed before the method is used in the new program.

## Executive findings

- The legacy code and the Position notebooks resolve to the same shared DuckDB
  today. The legacy code hardcodes a repo-relative location; Position uses
  `DB_PATH`. Catchment should adopt the Position convention.
- DuckDB's spatial extension loads in a read-only connection.
- `silver.xwalk_cbsa_county` is a governed OMB 2023 crosswalk. The tract
  geometry used by the old code, `geo.tracts_all_us`, is a legacy cartographic
  surface with no stored boundary vintage or geometry role. It cannot be
  described as governed analytical geometry without a deliberate exception.
- `build_rings()` and the tract-intersection calculation work. A live
  Baymeadows rerun reproduced all 75 saved weight rows, with a maximum absolute
  weight difference of approximately `1.1e-16`.
- The saved weight table contains **non-overlapping bands**: 0–1, 1–3, and 3–5
  miles. D2 uses those bands directly, while D3 converts them to cumulative
  0–1, 0–3, and 0–5 reaches. The current products therefore use `ring_mi` with
  two different meanings.
- Extensive aggregation is usable for additive counts. The current intensive
  aggregation is not sufficient: it averages tract rates using tract-area
  shares rather than reconstructing numerators and denominators.
- The median guard prevents an accidental call, but D2 automatically opts into
  an approximate average and does not carry that approximation into the output
  provenance. It is not a settled median method.
- The current reliability flags describe whether intersecting tracts are whole
  or fragmented. Their thresholds were inherited without empirical validation,
  and their `fragment_share` is not a share of ring area, population, or metric
  contribution. They are structural diagnostics, not reliability grades.
- The staged D2 build runs, but the older public wrappers and their tests are
  stale after the staged-build refactor. The current profile also drops
  `households` because `occ_occupied` is not renamed to the registered metric
  id.
- The current population percentile compares a multi-tract band total with
  individual tract totals. That benchmark is invalid and was already called
  misleading in the August 3 UI review.
- The water/barrier logic is useful evidence for a later optional module, but it
  depends on Jacksonville-local OSM artifacts and heuristics. It does not belong
  in the base v0 weight-table build.

## Evidence reviewed

The audit read the legacy method code, split build code, method notes, stored
Baymeadows artifacts, current DuckDB relations, Geography Engine contract, and
the Place Intelligence D1–D3/geocode tests. The main surfaces were:

- `metro-deep-dive/metro-area-explorer/place_intelligence/apportion.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/geocode.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/site_prep.py`
- `metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/`
- `metro-deep-dive/metro-area-explorer/place_intelligence/METHODS_MEMO.md`
- `metro-deep-dive/metro-area-explorer/place_intelligence/decisions.md`
- `metro-deep-dive-program/engines/geography/CONTRACT.md`
- `metro-deep-dive/tests/test_pi_d1.py`
- `metro-deep-dive/tests/test_pi_d2.py`
- `metro-deep-dive/tests/test_pi_d3.py`
- `metro-deep-dive/tests/test_pi_geocode.py`

No legacy code or stored data artifact was changed during the audit.

## 1. Database and geography audit

### Database identity

`apportion.py`, `geocode.py`, and `site_prep.py` construct the repo-relative
path `foundations/etl/data/duckdb/patterns_in_place.duckdb`. The Position
notebooks read `DB_PATH` from the environment or the repo `.Renviron`. On the
audit date, both resolved to the same file.

This is the same database, but not the same access contract. Catchment should
use `DB_PATH`, open it read-only, and receive the connection or data frame at the
method boundary rather than letting geometry functions open a hardcoded
database internally.

### Required relations

| Relation | Observed state | Audit judgment |
|---|---|---|
| `geo.tracts_all_us` | 84,119 rows and 84,119 distinct 11-digit tract GEOIDs; no null tract/county keys; no null or empty geometries; all 84,119 geometries pass `ST_IsValid()` | Usable legacy input, but not a governed analytical contract. It has no stored vintage or geometry role and is described by the Geography Engine as cartographic-boundary geometry. |
| `silver.xwalk_cbsa_county` | 1,915 unique CBSA-county rows; 935 CBSAs; OMB 2023 only; no null keys | Governed and reusable, though the current Geography mart should be considered as the newer containment interface. |
| `mart_geography.rollup_tract_to_cbsa` | Present in the current DuckDB | Candidate replacement for hand-joining tracts to the county crosswalk. The old code does not use it. |

For Jacksonville CBSA `27260`, the crosswalk contains five counties—Baker,
Clay, Duval, Nassau, and St. Johns—and selects 340 unique tract geometries.

The tract geometry coordinates have longitude/latitude extents consistent with
WGS84, and the old code assigns `EPSG:4326` after reading WKB. The database
relation itself does not carry CRS metadata that the audited DuckDB spatial
functions expose, which is another reason to make source provenance explicit.

### Metric inputs

The four D2 Gold tables each have Jacksonville tract coverage through 2024:

| Relation | Available years | Jacksonville rows at latest tract year |
|---|---:|---:|
| `gold.population_demographics` | 2012–2024 | 340 |
| `gold.economics_income_wide` | 2012–2024 | 340 |
| `gold.housing_core_wide` | 2012–2024 | 340 |
| `gold.transport_built_form_wide` | 2012–2024 | 340 |

The staged D2 join materializes 3,172 tract-year rows across those 340 tracts.
The corresponding Silver ACS tables retain the count universes needed to
aggregate rates correctly: age bands and population, race counts, education
counts and the 25+ universe, poverty counts and universe, housing counts, and
commute/vehicle counts.

The daytime module reads tract WAC/RAC data from
`silver.lehd_lodes_wac` and `silver.lehd_lodes_rac`. Both currently use 2023;
the existing saved Baymeadows output has cumulative jobs and workers for each
reach.

## 2. Reusable method surface

### `apportion.py`

| Function | Takes | Returns | Important assumptions | Disposition |
|---|---|---|---|---|
| `build_rings(lat, lon, rings_mi)` | One WGS84 point and a non-empty list of positive integer outer distances | Projected GeoDataFrame with `ring_mi`, band geometry, and `ring_area_sq_mi` | Estimates local UTM; sorts/deduplicates distances; emits non-overlapping bands | Reuse the projected-buffer algorithm. Add explicit inner/outer distance and reach semantics. |
| `apportion_weights(rings, market_id)` | Projected ring bands and a CBSA id | Nine-column tract-band DataFrame | Opens the hardcoded DuckDB; scopes through CBSA counties; treats the full tract polygon, including water, as the denominator; selects every positive-area intersection | Reuse the intersection formula, but inject the geometry input and record source/vintage/unit provenance. |
| `apportion(metric_series, weight_table, kind, method)` | Tract-indexed values, weights, extensive/intensive kind, optional method | Ring-indexed Series | Extensive values are additive; intensive values use only areal weights; median names require `method="approximate"` | Keep the extensive branch. Replace the generic intensive branch with numerator/denominator contracts. Do not promote the current median behavior as standard. |
| `coverage_diagnostic(weight_table)` | Band weight table | Per-band diagnostic table | Uses whole-tract count and sum of tract-share weights | Keep the raw structural fields only if useful; replace the reliability label and thresholds. |

`apportion.py` contains no Streamlit or artifact-store dependency. Its main
coupling is hidden data access, not UI code.

### `geocode.py`

| Function | Takes | Returns | Important assumptions | Disposition |
|---|---|---|---|---|
| `geocode_address(address)` | Non-empty U.S. address | `GeocodeResult(lat, lon, matched_address, match_type, tract_geoid, geocode_source)` | Census geocoder; hardcoded current benchmark/vintage ids; takes the first match; labels precision `address_range` | Port the small result/provenance contract. Keep geocoding as an explicit action, not a notebook-load side effect. |
| `resolve_site_geocode(site)` | App-shaped `Site` dataclass | `GeocodeResult` | Manual coordinates win when both are present; otherwise geocode; local tract point-in-polygon corrects Census disagreement | Reuse the precedence rule, but decouple it from the legacy `Site` type and validate point/market consistency. |
| `resolve_tract_from_coordinates(lon, lat)` | WGS84 point | Tract GEOID | Opens hardcoded DuckDB and uses `ST_Contains` against legacy geometry | Replace its data-access and geometry contracts. Define boundary-point behavior. |

The YAML field `geocode_source` is required by the old `Site` parser but is not
the authoritative output provenance; the resolved result overwrites it with
`manual_override` or Census response metadata. Catchment should avoid carrying
both concepts under the same name.

### `site_prep.py` and split data builds

The useful method concepts are small:

- convert band geometries/weights into cumulative reaches
- stage governed metric inputs once
- derive cumulative LODES counts
- count point POIs directly inside cumulative geometry
- keep a baseline geometry beside any adjusted companion

The file itself is not reusable as a Catchment dependency. It is 2,770 lines
and combines site YAML, app defaults, local artifact paths, D2–D6 logic,
Jacksonville aliases, Overture/OSM caches, traffic, flood, maps, and page
contracts. The `data_builds/` tree further assumes site YAML orchestration,
CSV/JSON artifact directories, manifests, and downstream Streamlit pages.

The following are explicitly app-shaped and should not be ported:

- `asset_type` validation and retail-specific site defaults
- site-config discovery and `primary_ring_mi` UI behavior
- artifact directories, schema sidecars, manifests, and cloud bundles
- Streamlit page payloads and compatibility wrappers
- Jacksonville filesystem aliases and locally cached OSM/Overture inputs
- D4 traffic, D5 flood, D6 map/page assembly

## 3. Existing weight-table contract

The stored Baymeadows table has 75 rows at grain
`site_id × band outer distance × intersecting tract`. The natural key
`(site_id, ring_mi, tract_geoid)` has no duplicates or nulls.

| Field | Observed type/value | Meaning and limitation |
|---|---|---|
| `site_id` | string | Legacy YAML identity. |
| `ring_mi` | integer; 1, 3, 5 | Outer edge of a non-overlapping band. It does not say that the row is a band or record the inner edge. |
| `tract_geoid` | 11-digit string | Contributing 2020 tract identity, though the table does not record the boundary vintage. |
| `weight` | double | `intersect_area / tract_area`; share of the source tract assigned to this band. |
| `weight_method` | string; `areal` | Method label. It omits geometry source/vintage and band/reach semantics. |
| `intersect_area` | double | Intersection area in square meters under the site-local projected CRS; the unit is not encoded in the name. |
| `tract_area` | double | Full tract geometry area in square meters under the same projected CRS. |
| `containment` | `full` or `fragment` | `full` when the tract weight is within `1e-9` of 1; otherwise `fragment`. |
| `centroid_in` | boolean | Diagnostic indicating whether the projected tract centroid is within the band. It is not an inclusion rule. |

The Baymeadows artifact and live rerun produced:

| Band | Intersecting tracts | Sum of tract-share weights | Whole tracts | Centroids in band | Reliability label |
|---:|---:|---:|---:|---:|---|
| 0–1 mi | 8 | 1.868243 | 0 | 2 | `fragment_only` |
| 1–3 mi | 22 | 10.819909 | 0 | 10 | `fragment_only` |
| 3–5 mi | 45 | 23.194178 | 5 | 24 | `fragment_heavy` |

Each tract's weights sum to at most 1 apart from floating-point tolerance; the
observed maximum was `1.0000000000000613`.

The v1 canonical table needs, at minimum, explicit `ring_inner_mi`,
`ring_outer_mi`, `reach_type`, geometry source/role/vintage, CRS or area-unit
provenance, and a method version. Epic 2 should decide whether the canonical
rows remain bands with cumulative reaches derived, or whether both row types
are stored. They must not share an ambiguous `ring_mi` label.

## 4. Reliability and aggregation audit

### Current reliability flags

The existing thresholds are:

- `fragment_only` when `whole_tract_count == 0`
- `fragment_heavy` when `fragment_share >= 0.75`
- `mixed` when `fragment_share >= 0.50`
- `stable` otherwise

`fragment_share` is calculated as the sum of tract-share weights on fragment
rows divided by the sum of all tract-share weights. Because a weight is a
fraction of its source tract—not a share of the ring—this does not measure the
share of ring area, population, households, or any metric contributed by
fragments. `total_weight_captured` is likewise an equivalent-tract count, not a
coverage percentage.

The labels are therefore not defensible as reliability grades. The underlying
counts can remain visible as diagnostics, but v1 needs QA tied to interpretable
quantities such as ring area reconciliation, contribution concentration,
missing metric coverage, and sensitivity to tract allocation assumptions.

### Counts, rates, and medians

- **Counts:** `sum(value × tract_share)` is a transparent areal interpolation
  for truly additive tract counts. It remains an estimate because the count is
  assumed uniform within the tract.
- **Rates and shares:** the current `sum(rate × tract_share) / sum(tract_share)`
  gives equal conceptual weight to very different source universes. V1 should
  apportion the source numerator and denominator separately, then divide.
- **Per-capita/mean values:** use an explicit population or applicable-universe
  denominator, not the generic intensive branch.
- **Medians:** the current code guard is useful, but D2 automatically passes
  `method="approximate"`. The output does not carry an approximation flag, the
  approximation uses area weights rather than a household/person proxy, and it
  is not a true catchment median. Median-like metrics should stay out of the
  standard v0 profile unless Epic 2 chooses and labels a defensible exploratory
  approximation.

### Band/reach inconsistency

`build_rings()` creates bands with areas approximately 3.137, 25.092, and
50.185 square miles. The cumulative 1-, 3-, and 5-mile circles have areas
approximately 3.137, 28.229, and 78.414 square miles.

D2 feeds the band table directly to `apportion()`. D3 explicitly accumulates
the bands before reporting jobs/workers and uses cumulative circle geometries
for POIs and barriers. A reader asking what is “within 3 miles” should receive
0–3 miles, not the 1–3-mile band. This semantic correction is required before
the notebook profile is built.

### Benchmark issue

D2 computes a primary-ring percentile against the CBSA tract distribution. For
rates this can be a labeled contextual comparison after rate aggregation is
fixed. For additive totals such as population, it compares a multi-tract
catchment total with single-tract totals and is not meaningful. V1 must remove
that comparison or define a reach-comparable benchmark universe.

## 5. Existing D2 profile and recommended v0 catalog

The old catalog declares 22 metrics. Twenty-one materialize for Baymeadows;
`households` is skipped because the staging query selects `occ_occupied` but
the merge expects a column named `households`.

### Recommended standard profile

Keep the standard v0 profile compact and only publish values with an explicit
aggregation universe:

- population and households as apportioned counts
- under-18 and 65+ shares from apportioned age counts / apportioned population
- White non-Hispanic, Black non-Hispanic, and Hispanic shares from apportioned
  race counts / apportioned race universe
- BA+ share from apportioned BA/graduate counts / apportioned age-25+ education
  universe
- per-capita income from an explicit population-weighted construction
- poverty rate from apportioned poverty count / apportioned poverty universe
- owner/renter split, vacancy, and multifamily share from their housing count
  numerators and denominators
- drive-alone, work-from-home, and zero-vehicle-household shares from their
  commute or household count universes

`renter_occ_rate` need not be a second independent KPI if it is displayed as
the complement of owner occupancy. The catalog should still preserve the
underlying numerator for a split view.

Defer `median_age`, `median_hh_income`, `median_home_value`,
`median_gross_rent`, and `mean_travel_time` from the standard profile until
their aggregation/interpretation contract is settled. The four medians may be
shown later as clearly labeled tract-based approximations; `mean_travel_time`
needs its exact source universe confirmed before reconstruction.

Daytime jobs, resident workers, and their ratio are a separate employment
context module. Their existing cumulative extensive aggregation is suitable as
a starting point once band/reach semantics and missing-source QA are explicit.

## 6. Water-adjusted and barrier logic

The inherited barrier method:

1. builds cumulative Euclidean rings
2. loads Jacksonville-local normalized OSM line and polygon caches
3. collapses highway and rail line components longer than 300 meters
4. groups named water lines and attaches nearby water surfaces within 30 meters
5. counts major-road/highway crossings and estimates mean spacing
6. automatically qualifies water; qualifies highway/rail when mean crossing
   spacing exceeds 1 mile
7. estimates far-side area and population
8. raises a site-card flag at a severed population share of at least 20%
9. creates a companion geometry by subtracting far-side pieces associated with
   qualified named water features

The thresholds were checked on only two Jacksonville sites. The saved
Baymeadows artifact contains 345 barrier rows, 20 qualified barriers, no
site-card flags, and only a `0.0066%` five-mile water adjustment. The legacy
decision note reports much larger downtown adjustments—`35.8%` at three miles
and `41.5%` at five miles—which demonstrates why the concept can be useful.

It is not a base-v0 dependency because:

- source loading is Jacksonville-local rather than a governed POI/Infrastructure
  handoff
- every named water feature qualifies regardless of severity
- synthetic tests cover mechanics, but threshold evidence is limited
- the result is a heuristic companion, not routed access
- water-adjusted geometry does not rebuild the canonical tract weight table

Keep baseline Euclidean reach canonical. Revisit barriers as an optional module
after the base method and governed source handoff are stable.

## 7. Test and staleness audit

The focused non-network test run produced **17 passed, 5 failed, 2 integration
tests deselected**. A separate live-DuckDB D1 integration smoke test passed.

All five failures are in the old D2 compatibility surface:

- `build_catchment_profile()` and `build_benchmark_table()` call the refactored
  staged helper without its required `tract_inputs` argument
- `compute_percentile()` imports a helper that no longer exists
- two tests monkeypatch old `site_prep.py` metric globals, while the active D2
  code now reads the separate `data_builds.d2.shared` module

The active staged D2 path was also executed directly against the current
read-only DuckDB. It produced 3,172 tract-input rows, 151 metric-long rows, 21
catchment metrics, and the expected `households` skip reason. This means the
staged path runs, but its method issues and stale compatibility surface remain.

The directly exercised D1 invariants remain useful:

- projected one-mile area sanity check
- per-tract band weights sum to at most one
- intersecting fragments are retained even when their centroid is outside
- median-like inputs require explicit approximation
- real Jacksonville weight build completes

Missing tests that should be added with the v1 method include cumulative-reach
semantics, rate numerator/denominator reconstruction, geometry provenance,
boundary-point behavior, QA metric definitions, missingness coverage, and a
guard against comparing multi-tract totals with tract distributions.

## 8. Port decision

### Reuse as method logic

- local projected buffering
- overlap-as-inclusion rule
- `intersection area / source tract area` areal weight
- non-overlapping band weights as a useful primitive
- centroid membership as a diagnostic only
- manual-coordinate precedence plus recorded geocode provenance
- cumulative conversion for downstream reach views
- extensive LODES apportionment

### Replace or revise

- hardcoded database and hidden data loading
- unvintaged legacy tract geometry contract
- ambiguous `ring_mi` semantics
- generic intensive aggregation
- median auto-approximation
- inherited reliability flags
- additive-total tract percentiles
- D2 `households` aliasing
- stale D2 wrappers and tests
- point-to-market validation and boundary handling

### Leave behind

- Streamlit app and page contracts
- artifact-store/cloud-bundle machinery
- retail `asset_type` and site YAML orchestration
- local Jacksonville file aliases
- D4/D5/D6 product logic
- app-specific POI allowlists and node typology

The next step is to review and rewrite Epics 2–5 around these findings before
implementing the notebook.
