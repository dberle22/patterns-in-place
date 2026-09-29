# Explanation Catchment Spec

**Status:** Epic 1 audited; V1 scope agreed and ready to build

**Build order:** E1, first in the Explanation sequence

**Primary surface:** `EXPLANATION_CATCHMENT_NOTEBOOK.py` plus a small
analysis-local `catchment.py` helper (not yet written)

**Default site:** Jacksonville Baymeadows (`jacksonville_fl_baymeadows_v0`),
market `27260`

**Initial method:** `catchment_v1`

**Dependencies:** Shared DuckDB through `DB_PATH`,
`mart_geography.rollup_tract_to_cbsa`, V1's explicitly declared legacy
`geo.tracts_all_us` geometry, governed ACS/LODES relations, the governed POI
mart where available, and analysis-local method code selectively ported from
Place Intelligence.

## Audit basis

Epic 1 is complete. See
[EXPLANATION_CATCHMENT_AUDIT.md](EXPLANATION_CATCHMENT_AUDIT.md) for the
field-level evidence, live DuckDB checks, artifact results, test findings, and
reuse verdict.

This spec records the post-audit V1 boundary agreed in the build-plan review.
The first version deliberately fixes the low-lift correctness issues while
keeping the port small.

## Goal

Build one Marimo notebook that produces, for a declared point, the population,
demographic, housing, employment, amenity, and physical-context evidence within
a declared cumulative reach—with an explicit tract-to-band/reach contribution
table as the canonical reusable output.

Profiles, benchmarks, and maps are downstream products of that weight table.
They are not the product.

## Why this analysis goes first

Most of the method already exists in the Jacksonville Place Intelligence build.
This is the fastest path to a working Explanation notebook, and a good place to
establish what an Explanation spec and notebook should look like before the
harder analyses open.

## Product Boundary

**Promote the transparent method, not the app.** The Streamlit Place
Intelligence app is not the Catchment product and should not be carried forward.
What we want is the underlying method: geocode a point, build projected rings,
apportion tracts to those rings, and aggregate carefully.

**National posture: point scoped.** No national run is expected. Reuse comes
from consistent weighting, metrics, and QA rather than an all-market ranking.
This analysis should not build national coverage tables, national distributions,
or national threshold sensitivity — per Section 2.2 of the family plan, it
declares a posture that does not call for them.

The first build is deliberately notebook-first and property-driven:

- read-only DuckDB inputs
- one Marimo notebook as the primary human surface
- one small analysis-local helper module for reusable data-frame patterns
- an optional second method-review notebook only if the main notebook becomes
  difficult to use
- no separate headless runner until the method has stable expectations worth
  testing outside Marimo
- no new mart, engine, or promoted Foundations package

## What the audit established

This is a **selective port**, not a repoint or rewrite.

Reusable method logic:

- projected local-UTM buffers
- overlap-based tract inclusion
- areal tract-share weights
- non-overlapping bands as a computational primitive
- cumulative conversion for “within X miles” outputs
- geocode/manual-override provenance
- extensive count aggregation

Required corrections:

- adopt `DB_PATH` and remove hidden database access from geometry functions
- choose and record a tract geometry role and boundary vintage
- distinguish bands from cumulative reaches in names and schema
- reconstruct rates from apportioned numerators and denominators
- exclude or clearly label approximate medians
- replace inherited reliability grades with interpretable QA
- remove multi-tract-total versus single-tract percentile comparisons
- restore households in the new registry and bypass the stale D2 compatibility
  surface

App-shaped YAML orchestration, artifact stores, Streamlit contracts, cloud
bundles, Jacksonville filesystem aliases, and D4–D6 logic do not carry forward.

## Inputs

These are the V1 input bindings. Their grain, vintage, and limitations remain
visible in notebook output.

| Input | Role |
|---|---|
| Point or address | The subject of the analysis, with geocoding provenance |
| `geo.tracts_all_us` | V1 apportionment geometry; explicitly label its role `legacy_unclassified` and geometry vintage unknown |
| `mart_geography.rollup_tract_to_cbsa` | Scopes tract loading to one market and supplies 2020 tract / 2023 CBSA identity vintages |
| Tract numerator, denominator, and count measures | The standard profile inputs; current ACS Silver tables retain the needed universes |
| LODES WAC/RAC | Cumulative daytime jobs/workers context; currently 2023 |
| `mart_poi.poi_classified_place` | Direct point-in-reach amenity counts where the selected market is materialized |

## V1 method

1. Resolve a point or address, retaining provenance and a manual-coordinate
   override path.
2. Validate that the point and declared market agree.
3. Build projected Euclidean bands with explicit inner and outer distances,
   using editable 1/3/5-mile defaults.
4. Create the tract-to-band areal contribution table, recording geometry and
   method provenance.
5. Derive explicitly labeled cumulative reaches for “within X miles” views.
6. Aggregate additive counts. Reconstruct rates and shares from apportioned
   numerators and denominators.
7. Keep median-like measures out of the standard profile and show their
   contributing-tract distributions for exploration instead.
8. Add cumulative daytime jobs/workers and direct point-in-reach POI counts.
9. Show physical context through the point/reach/tract/POI map without barrier
   adjustment or routed-access claims.

Areal weighting is V1. Density-based (dasymetric) weighting is a V2 candidate
that needs evidence, not a prerequisite. Routed network reach is a later
challenger with a stated trigger.

## Minimum outputs

- resolved point with geocode provenance
- band and cumulative reach geometries with unambiguous labels
- **tract contribution/weight table—the canonical reusable output**
- area reconciliation, contribution coverage, missingness, and sensitivity QA
- long metric profile
- benchmark table
- daytime context
- availability-aware governed POI views

## Two roles beyond the point analysis

- **Toward specific properties.** Catchment is how the family moves from broad
  question-style analyses to individual sites. It is used closely with Parcel
  Watch but does not build on it.
- **Second half of the 15-minute work.** Q2 identifies a center; Catchment
  measures what is within reach of it.

Neither role is in scope for the first build. They are why the weight table
matters more than the profile.

## Standard profile after the audit

The V1 catalog is:

- population and households
- under-18 and 65+ shares
- White non-Hispanic, Black non-Hispanic, and Hispanic shares
- BA+ share
- per-capita income and poverty rate
- owner/renter split, vacancy, and multifamily share
- drive-alone, work-from-home, and zero-vehicle-household shares

Every share or rate requires its source count numerator and denominator. Median
age, median household income, median home value, median gross rent, and mean
travel time are not standard V1 metrics; reconsider them only after their
aggregation contracts are approved.

## Deferred decisions

- when a governed analysis-role tract geometry should replace the declared
  legacy V1 input
- whether a second method-review notebook improves usability
- whether a later default distance set should vary by property question
- whether a labeled median approximation is useful enough to add
- what evidence would justify dasymetric weights, barrier-adjusted geometry, or
  a routed network method
- whether proven Catchment helpers eventually merit promotion beyond this
  analysis

## Guardrails

- do not promote the Streamlit app as the Catchment product
- do not allocate a non-additive measure without a declared method
- do not use a generic areal-weighted mean for a rate when numerator and
  denominator counts exist
- do not average a median silently
- do not compare a multi-tract reach total with a single-tract distribution
- do not call legacy cartographic geometry governed analytical geometry without
  an approved exception and recorded provenance
- do not use `ring_mi` for both annular bands and cumulative reaches
- do not infer travel or access from straight-line rings
- do not build national scaffolding this posture does not need
- keep final chart styling and issue narrative out of the notebook

## References

- Section 5.9 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_CATCHMENT_AUDIT.md](EXPLANATION_CATCHMENT_AUDIT.md)
- [EXPLANATION_CATCHMENT_BUILD_PLAN.md](EXPLANATION_CATCHMENT_BUILD_PLAN.md)
- `metro-deep-dive/metro-area-explorer/place_intelligence/METHODS_MEMO.md`
- `metro-deep-dive/metro-area-explorer/place_intelligence/DATA_PRODUCTS.md`
