# Catchment Analysis

**Build order:** E1 — first in the Explanation sequence

**Status:** Epics 1--4 complete; ready to prove reuse in a second market.

**Question:** What population, demographic, housing, employment, amenity, and
physical-context evidence falls within a declared reach of a specific point?

Purpose:

- promote the existing transparent point-catchment method rather than the app
- produce a reusable tract-to-ring weight/contribution table as the canonical
  output, with profiles and maps as downstream products
- serve as the second half of the 15-minute-city work: Q2 identifies a center,
  Catchment measures what is within reach of it

**Primary analytical unit:** point × ring/reach × contributing tract

**National posture:** point scoped. No national run is expected; reuse comes from
consistent weighting, metrics, and QA.

## Why this goes first

Most of the method already exists. The main task is porting the property-analyzer
work from the old Metro Deep Dive folder — geocoding points, building projected
Euclidean rings, and producing tract-ring weight tables. That makes this the
fastest path to a working Explanation notebook, and a good place to shake out
what an Explanation spec should look like before the harder analyses.

## Source material to port

- `metro-deep-dive/metro-area-explorer/place_intelligence/` — `apportion.py`,
  `geocode.py`, and the D1–D3 functions
- [`METHODS_MEMO.md`](../../../../metro-deep-dive/metro-area-explorer/place_intelligence/METHODS_MEMO.md)
- [`SPEC_PLACE_INTELLIGENCE.md`](../../../../metro-deep-dive/metro-area-explorer/place_intelligence/SPEC_PLACE_INTELLIGENCE.md)

The working Jacksonville build contains catchment, tract apportionment,
demographic/profile, daytime population, POI, and barrier workflows.

## Relationship to Parcel Watch

Catchment is a separate analytical process. It does not build on Parcel Watch,
but the two are used closely together — Catchment supplies the "what is within X
of this parcel" read. It is also how the family moves from broad question-style
analyses toward specific properties.

## V1 direction

- one property-exploration notebook plus a small reusable helper module
- editable property/address/coordinate, market, and distance inputs
- explicit band contributions plus derived cumulative reaches
- areal weighting with corrected numerator/denominator rate aggregation
- no aggregated catchment medians or incompatible count percentiles
- direct QA measures instead of inherited reliability grades
- cumulative LODES employment context and governed POI counts where available
- no barrier adjustment, routing, app port, or new geometry build

See [EXPLANATION_CATCHMENT_AUDIT.md](EXPLANATION_CATCHMENT_AUDIT.md) for the
evidence and selective-port verdict,
[EXPLANATION_CATCHMENT_SPEC.md](EXPLANATION_CATCHMENT_SPEC.md) for the revised
analysis boundary and inputs, and
[EXPLANATION_CATCHMENT_BUILD_PLAN.md](EXPLANATION_CATCHMENT_BUILD_PLAN.md) for
the agreed V1 implementation sequence.

Section 5.9 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
## Catchment V1 helper

`catchment.py` is the analysis-local, read-only helper used by the forthcoming
property-exploration notebook. It accepts a `PropertyInput`, resolves and
validates its point and market, produces explicit annular `band_contributions`,
then derives separately labeled cumulative reaches. `STANDARD_METRICS` carries
the numerator/denominator contract for every profile measure; medians are
returned only as contributing-tract evidence.

Run its focused Jacksonville Baymeadows fixture with:

```sh
.venv312/bin/python -m pytest metro-deep-dive-program/analyses/explanation/catchment/test_catchment.py -q
```

## Property exploration

[EXPLANATION_CATCHMENT_NOTEBOOK.py](EXPLANATION_CATCHMENT_NOTEBOOK.py) is a
cell-based Python notebook. Edit only its `PROPERTY` input cell to change the
property, market, coordinates/address, or reach distances. It exposes the map,
canonical allocation tables, profile, QA, compatible benchmarks, tract median
evidence, 2023 LODES context, governed POI counts, and interpretation limits
in the active session; it does not write artifacts or DuckDB tables.

## V1 contracts and limitations

| Output | Grain and contract |
|---|---|
| `band_contributions` | property × non-overlapping band × tract; `tract_share` is areal intersection / tract area |
| `cumulative_reach_contributions` | property × within-distance reach × tract; summed from the disjoint bands |
| `standard_profile` | property × cumulative reach × metric; counts are additive and rates reconstruct source numerators / denominators |
| `compatible_benchmarks` | metric × same-year CBSA/county/state; only shares, rates, and per-capita income |
| `tract_median_evidence` | reach × contributing tract × median measure; not a catchment median |
| `lodes_context` | reach × 2023 LODES jobs/workers and selected sectors |
| `poi_counts` | reach × governed POI category/subcategory; direct point-in-reach counts |

V1 uses `mart_geography.rollup_tract_to_cbsa` (2020 tract / 2023 CBSA
identity vintages) to scope the market, then allocates from
`geo.tracts_all_us`. That geometry is explicitly `legacy_unclassified` with
an unknown vintage. Profile inputs are the current common year in ACS Silver
(2024 in the Jacksonville and Richmond verification runs); LODES is 2023; POI
release and mapping version are retained in the output.

Reaches are straight-line Euclidean distances, not routing or accessibility.
Areal allocation is not population-weighted or dasymetric. No catchment median
is published, and the notebook makes no barrier, water-adjustment, or national
coverage claim.

## Reuse verification and V2 candidates

The focused test suite verifies the Jacksonville Baymeadows manual-coordinate
fixture and the Census-address-geocoded Richmond fixture at `1814 Carter St,
Richmond, VA 23220` (CBSA 40060). Both use the same helper surface and
1/3/5-mile defaults; no market-specific code or database write is required.

Concrete V2 candidates are an approved governed tract geometry, evidence-based
dasymetric weighting, routed/network reaches, and a separately approved median
approximation. They are not implied by V1 outputs.
