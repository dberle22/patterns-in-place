# Explanation Q4 — Livability Amenities and POI Clusters Build Plan

**Status:** Epics 1–3 complete. The first hub candidate build uses all mapped
POIs; Epic 2 now provides basket-specific workbench views for review.

**Pilot markets:** Richmond, VA (`40060`) and Jacksonville, FL (`27260`)

## How this plan works

Q4 begins by making governed POI evidence and its spatial organization
reviewable. It produces amenity hubs, cluster typologies, and tract context for
future analyses. A network/barrier/access method is explicitly deferred.

## Epic 1 — Audit the POI Surface

- [x] Confirm two source-faithful, classified, tract-assigned pilot runs:
  Richmond and Jacksonville.
- [x] Confirm POI geography assignment: all retained points are assigned to
  tract and county by point-in-polygon; provider ZIP is address evidence, not
  a ZCTA assignment.
- [x] Quantify taxonomy coverage: 96.7% mapped in Richmond and 96.2% mapped in
  Jacksonville, across 22 categories and 117 subcategories.
- [x] Review observed category frequencies in both markets; broad livability
  and errands/essentials baskets are supportable, subject to declared rules.
- [x] Confirm that missing optional taxonomy Detail is not a failure of the
  governed Category/Subcategory mapping.
- [x] Inspect the tract-population posture: ACS-derived context is documented,
  while the live serving interface and vintage remain an implementation check.
- [x] Read Q2's method boundary: it provides job-center physical proximity,
  not a 15-minute/access definition for Q4 to adopt.
- [x] State the decision: proceed with a POI-first cluster-and-context pilot;
  defer access scoring, network, barrier, and national work.

**Done:** [EXPLANATION_Q4_AUDIT.md](EXPLANATION_Q4_AUDIT.md) records the
evidence and the revised scope.

## Epic 2 — Build the POI Workbench and Basket Catalog

- [x] Define the POI-level workbench contract: retained point identity,
  source/run provenance, governed category/subcategory, mapping/review state,
  coordinates, and tract assignment.
- [x] Define versioned basket membership over the governed taxonomy, beginning
  with broad livability and errands/essentials.
- [x] Build coverage and category-composition views for both pilot markets.
- [x] Retain unclassified and excluded POIs as visible coverage states.
- [x] Verify the consumer-facing POI interface/run status for both markets:
  direct pilot artifacts are usable in Q4 but not yet a promoted shared mart.
- [x] Build the read-only Marimo workbench for market/basket review before
  advancing to cluster profiles or typologies.

**Done:** [q4_amenity_baskets.yml](q4_amenity_baskets.yml) declares the basket
catalog; [EXPLANATION_Q4_NOTEBOOK.py](EXPLANATION_Q4_NOTEBOOK.py) is the review
surface; and [`outputs/q4_poi_workbench_v1/`](outputs/q4_poi_workbench_v1/)
contains the POI, membership, coverage, composition, and catalog artifacts.

The initial workbench contains 52,550 Richmond and 74,279 Jacksonville broad-
livability POIs, plus 3,859 and 4,782 errands/essentials POIs respectively.
It retains 2,054 Richmond and 3,336 Jacksonville unclassified POIs as visible
coverage states.

## Epic 3 — Construct and Review Spatial Amenity Hubs

*Completed before Epic 2 by mistake. Its all-mapped-POI candidate remains a
pre-basket spatial baseline; do not treat it as the final basket-specific hub
construction without a later rerun and review.*

- [x] Explore direct POI point-pattern cluster candidates and record each
  method's parameters and sensitivity versions.
- [x] Build map-ready candidate hub geometry and POI-to-cluster membership.
- [x] Review membership reconciliation, category-mix surfaces, candidate scale,
  and fragmentation; retain SVG maps for later visual domain review.
- [x] Select `grid_250m_min_20` for the first workbench review and retain
  `grid_500m_min_60` as a sensitivity. This is not a basket-specific or
  cross-analysis promotion.
- [x] Publish a versioned amenity-hub inventory, method record, and review.

**Done:** [`outputs/q4_amenity_hub_grid_v1/`](outputs/q4_amenity_hub_grid_v1/)
contains the candidate geometry, POI membership, category mix, maps, and
manifest. [EXPLANATION_Q4_AMENITY_HUB_METHOD_RECORD.md](outputs/q4_amenity_hub_grid_v1/EXPLANATION_Q4_AMENITY_HUB_METHOD_RECORD.md)
and [EXPLANATION_Q4_AMENITY_HUB_REVIEW.md](EXPLANATION_Q4_AMENITY_HUB_REVIEW.md)
record the construction and selection.

## Epic 4 — Profile Hubs and Build Amenity-Environment Typologies

- [x] Define the cluster-composition features used for typology; keep these
  noncontiguous composition groups distinct from geographic hubs.
- [x] Build cluster profiles for basket coverage, category mix, diversity, and
  visible infrastructure context.
- [x] Choose and document the cluster-to-tract context association rule.
- [x] Build the tract context matrix using declared population density, income,
  poverty, rent burden, rents/values, housing, household, and demographic
  measures with source vintages and complete-case coverage.
- [x] Produce descriptive cluster-context comparisons without causal claims.

**Done when:** reviewers can inspect both where a hub is and what kind of
amenity environment it represents, alongside transparent tract context.

**Done:** `outputs/q4_epic4_profiles_v1/` contains category/subcategory
profiles, dominant-category typologies, POI-member tract associations, and
latest-year descriptive housing/demographic context. The association rule is
membership-based, not a tract catchment or resident-access assumption.

## Epic 5 — Compare, Review, and Decide What Reuses

- [ ] Compare amenity hubs and typologies with Q2 reviewed job-center evidence
  as a descriptive employment-context layer.
- [ ] Compare the two pilots for taxonomy coverage, cluster stability,
  composition, and urban-form sensitivity.
- [ ] Record where a later network/barrier method would materially change the
  interpretation, without inventing an access result now.
- [ ] Decide whether the POI cluster inventory is stable enough for Catchment,
  Corridor, and other named consumers.
- [ ] Decide whether the basket catalog, POI interface, and cluster method are
  mature enough for broader-market or national work.

**Done when:** Q4 has a reviewed two-market workbench, reusable cluster outputs,
and a clear go/no-go decision for each proposed next consumer or scale-out.

## What not to do

- do not treat POI counts as proof of resident access, amenity quality, or
  living standards;
- do not call the pilot a 15-minute, walkability, travel-time, or barrier
  analysis;
- do not use tract demographics to select clusters;
- do not rewrite POI classification, provenance, identity, or assignment;
- do not conflate geographic hubs with composition-based typologies; and
- do not scale nationally before the two-market workbench is reviewed.
