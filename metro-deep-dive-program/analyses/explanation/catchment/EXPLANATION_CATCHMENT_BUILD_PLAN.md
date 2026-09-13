# Explanation Catchment Build Plan

**Status:** V1 complete; Epics 1--5 closed

This is a simple selective port into a property-exploration notebook, not a new
engine, app, artifact pipeline, or geometry project.

## V1 shape

V1 has one required notebook and one small analysis-local helper module:

- `catchment.py` holds the reusable, testable data-frame patterns.
- `EXPLANATION_CATCHMENT_NOTEBOOK.py` is the property-exploration surface.
- A second method-review notebook is allowed only if the QA and comparison
  material makes the primary notebook difficult to use. Do not create it by
  default.

An analyst should be able to enter a property id/label, address or manual
coordinates, market id, and reach distances without creating site YAML,
running an artifact builder, or changing app code.

## V1 decisions from the audit review

- **Database:** use `DB_PATH` and read-only DuckDB connections, matching the
  Position notebooks.
- **Geometry:** use `geo.tracts_all_us` for V1 so the port is not blocked, but
  label it exactly as the Geography catalog does: `legacy_unclassified` with
  unknown legacy geometry vintage. Use
  `mart_geography.rollup_tract_to_cbsa` for tract/market membership and its
  explicit 2020 tract and 2023 CBSA identity vintages.
- **Reach model:** keep non-overlapping bands as the canonical allocation
  primitive and derive a separate cumulative contribution table for “within X
  miles.” Never use one ambiguous `ring_mi` field for both.
- **Distances:** retain editable 1/3/5-mile defaults for V1. They are defaults,
  not a universal standard.
- **Weighting:** use areal weighting only. Dasymetric and routed methods remain
  post-V1 challengers.
- **Counts and rates:** apportion additive counts; build rates/shares by
  apportioning their source numerators and denominators separately.
- **Medians:** do not publish an aggregated catchment median in V1. Show the
  contributing-tract distribution when useful and retain the source median as
  tract evidence.
- **QA:** retain whole/fragment counts as descriptive diagnostics, but remove
  inherited reliability labels. Use direct, interpretable checks without
  invented score thresholds.
- **Benchmarks:** do not compare multi-tract count totals with a tract
  distribution. Benchmarks are limited to compatible rates, shares, and
  per-capita measures in V1.
- **Context:** include cumulative LODES jobs/workers. Use the governed POI mart
  for amenity counts when the selected market is materialized. Do not port the
  Jacksonville-local POI allowlists or barrier-adjusted geometry.
- **Legacy code:** do not repair the old Streamlit app, artifact builders, D2
  wrappers, or legacy tests as part of Catchment. Add focused tests for the new
  helper surface instead.

## Epic 1 — Audit What Already Exists

- [x] Confirm which DuckDB the existing catchment code reads, and whether it is
  the same governed database the Position notebooks use.
- [x] Confirm the tract geometry and CBSA-county crosswalk it depends on: table
  names, row counts, grain, vintage, and whether the spatial extension loads.
- [x] Inventory the reusable method surface in `apportion.py`, `geocode.py`, and
  `site_prep.py`—what each function takes, returns, and assumes.
- [x] Record the existing weight-table schema field by field, including
  `weight_method`, `containment`, and `centroid_in`.
- [x] Record the existing reliability flags and their thresholds, and judge
  whether they are defensible or merely inherited.
- [x] Record how medians and rates are currently handled, and whether the guard
  is sufficient.
- [x] Determine what the water-adjusted and barrier logic actually does, and
  whether it belongs in V1 or is optional.
- [x] Separate genuinely reusable method code from app-shaped assumptions.
- [x] Identify which existing metrics are in the D2 profile and which belong in
  the new standard profile.
- [x] State plainly whether this is a repoint, a port, or a rewrite.

**Completed:**
[EXPLANATION_CATCHMENT_AUDIT.md](EXPLANATION_CATCHMENT_AUDIT.md) records the
selective-port verdict, and the spec has been rewritten against it.

## Epic 2 — Port the Core Catchment Pattern

- [x] Add a small analysis-local `catchment.py`; port only the projected-buffer,
  tract-intersection, cumulative-conversion, and point-resolution patterns the
  notebook needs.
- [x] Add the property input contract: property id/label, address, optional
  manual latitude/longitude, market id, and editable reach distances.
- [x] Resolve `DB_PATH`, open DuckDB read-only, and load the spatial extension.
- [x] Load V1 tract geometry through
  `mart_geography.rollup_tract_to_cbsa` plus `geo.tracts_all_us`, carrying the
  identity vintages and legacy geometry warning into output metadata.
- [x] Port address geocoding and manual-coordinate precedence with provenance.
- [x] Validate that the resolved tract belongs to the declared market and make
  a mismatch a visible error.
- [x] Build explicit non-overlapping band geometries and a canonical
  `band_contributions` table with `band_inner_mi`, `band_outer_mi`, tract id,
  tract share, areas with units, method id, and geometry provenance.
- [x] Derive `cumulative_reach_contributions` and cumulative circle geometries
  from the band table for each requested outer distance.
- [x] Add focused tests for ring area, band non-overlap, weight bounds,
  per-tract band sums, cumulative construction, point/market validation, and
  provenance fields.

**Done when:** Baymeadows reproduces the existing areal weights within numeric
tolerance, while the new outputs distinguish 1–3-mile bands from 0–3-mile
cumulative reaches and expose their source limitations.

**Completed:** `catchment.py` is the reusable, read-only helper surface.
`test_catchment.py` uses the Jacksonville Baymeadows manual-coordinate fixture
to reproduce all 75 legacy band contributions within `1e-10`, test explicit
band/reach semantics, and test point-market validation and provenance.

## Epic 3 — Add the Corrected Profile and QA Patterns

- [x] Define the compact V1 metric registry with a source numerator,
  denominator where applicable, aggregation type, label, unit, year, and source
  relation for every metric.
- [x] Add population and correctly aliased households as apportioned counts.
- [x] Add age, race/ethnicity, education, poverty, housing, commute, and vehicle
  shares by apportioning source numerators and denominators separately.
- [x] Add per-capita income with an explicit population-weighted construction.
- [x] Exclude aggregated median age, household income, home value, and rent from
  the standard profile; expose their contributing-tract distributions for
  exploration instead.
- [x] Remove the old population-versus-tract percentile. Add only compatible
  CBSA/county/state benchmark rows for rates, shares, and per-capita measures.
- [x] Replace `reliability_flag` with visible QA tables covering key/null/weight
  checks, band-area and market-geometry coverage, fragment counts, metric join
  coverage, and contribution concentration.
- [x] Add tests that reproduce the household alias bug and generic-rate bug,
  then verify the corrected count and numerator/denominator results.

**Done when:** every standard profile value has an inspectable aggregation
contract, no V1 median is presented as a true catchment median, and QA labels
describe measured quantities rather than implied reliability.

**Completed:** the compact metric registry aggregates two counts and 15
rates/shares from Silver source numerators and denominators. It provides same-
year compatible CBSA/county/state benchmarks, tract-level median evidence, and
measured contribution and join-coverage QA. The Baymeadows test fixture proves
the occupied-household alias and rejects an areal-weighted tract-rate shortcut.

## Epic 4 — Build the Property-Exploration Notebook

- [x] Add editable property/address/coordinate, market, and distance controls.
- [x] Show the resolved point, tract, market validation, geocode provenance,
  geometry provenance, and method warning at the top.
- [x] Map the point, cumulative reaches, bands, and contributing tracts.
- [x] Make `band_contributions` and `cumulative_reach_contributions` primary
  inspectable tables rather than hidden intermediate data.
- [x] Show the corrected standard profile, compatible benchmarks, median tract
  distributions, and QA views.
- [x] Add cumulative 2023 LODES workplace jobs, resident workers, selected job
  groups, and the jobs-to-workers ratio.
- [x] Add an analysis-owned amenity basket over governed
  `mart_poi.poi_classified_place` categories. Count POIs directly within
  cumulative reach geometry and retain source release/mapping provenance.
- [x] Show a clear unavailable state when the selected market has no governed
  POI materialization; do not fall back to legacy local caches.
- [x] Keep physical context in V1 to the reach/tract/POI map and source
  limitations. Do not add water-adjusted geometry or claim routed access.
- [x] Keep computation in the notebook session and shared helper; do not add
  YAML, artifact-store, cloud-bundle, or Streamlit contracts.

**Done when:** an analyst can explore a new property by changing notebook
inputs only and can trace every displayed result back to the contribution
table, source metric contract, or direct point-in-reach POI calculation.

**Completed:** `EXPLANATION_CATCHMENT_NOTEBOOK.py` is the single editable
property-exploration surface. It starts with the Jacksonville Baymeadows
fixture, displays the resolved point and geometry limitations, maps bands and
reaches, retains every output in an `outputs` session dictionary, and adds
2023 LODES context plus a governed amenity basket. It returns an explicit POI
unavailable state for markets without retained governed places.

## Epic 5 — Prove Reuse and Close V1

- [x] Run Baymeadows and one Richmond property through the same helper and
  notebook path without market-specific code changes.
- [x] Check at least one manual-coordinate case and one address-geocoded case.
- [x] Confirm the notebook and helper never write to DuckDB.
- [x] Review notebook length and usability; add a second method-review notebook
  only if moving QA/comparison material materially improves property review.
- [x] Record the final V1 output schemas, limitations, source vintages, and
  reusable function contracts in the Catchment README/spec.
- [x] Note any concrete V2 candidates without implementing them.

**Done when:** the same small pattern supports two markets, a new property can
be explored without scaffolding work, and V1 limitations are visible at the
point of interpretation.

**Completed:** Jacksonville Baymeadows verifies the manual-coordinate path and
reproduces the legacy band weights; `1814 Carter St, Richmond, VA 23220`
verifies the Census-address-geocoded path in CBSA 40060. Both produce the same
band/reach, profile, and QA contracts without market-specific code. The helper
opens DuckDB read-only and the notebook retains results in-session only. The
README records final schemas, source vintages, limitations, and explicitly
deferred V2 candidates. A second notebook would duplicate the primary review
surface, so it was not added.

## Explicitly out of V1

- new Geography geometry materialization or migration
- dasymetric weighting
- routed travel-time catchments
- water-adjusted/barrier geometry
- a national run or national ranking
- legacy app, artifact, compatibility-wrapper, or test cleanup
- a new engine, mart, Foundations package, or headless product runner
- final issue chart styling or narrative
