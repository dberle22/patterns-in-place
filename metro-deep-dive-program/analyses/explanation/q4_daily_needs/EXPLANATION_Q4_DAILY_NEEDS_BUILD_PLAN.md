# Explanation Q4 — Livability Amenities and POI Clusters Build Plan

**Status:** Epic 1 complete. The next build is a POI-first, two-market
workbench—not a Q2-derived access score.

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

- [ ] Define the POI-level workbench contract: retained point identity,
  source/run provenance, governed category/subcategory, mapping/review state,
  coordinates, and tract assignment.
- [ ] Define versioned basket membership over the governed taxonomy, beginning
  with broad livability and errands/essentials.
- [ ] Build coverage and category-composition views for both pilot markets.
- [ ] Retain unclassified and excluded POIs as visible coverage states.
- [ ] Verify the consumer-facing POI interface/run status for both markets
  before treating the workbench as reusable outside Q4.

**Done when:** a reviewer can filter and map the governed POI inventory by
category and basket, and can distinguish an observed zero from incomplete
classification or source coverage.

## Epic 3 — Construct and Review Spatial Amenity Hubs

- [ ] Explore direct POI point-pattern cluster candidates and record each
  method's parameters and sensitivity versions.
- [ ] Build map-ready candidate hub geometry and POI-to-cluster membership.
- [ ] Review cluster membership, category mix, fragmentation, and implausible
  bridges against the POI and infrastructure map.
- [ ] Apply explicit human review to select or reject a V1 hub construction.
- [ ] Publish a versioned amenity-hub inventory and method record.

**Done when:** each selected hub has transparent POI membership, a declared
construction rule, sensitivity evidence, and a reviewer-approved status.

## Epic 4 — Profile Hubs and Build Amenity-Environment Typologies

- [ ] Define the cluster-composition features used for typology; keep these
  noncontiguous composition groups distinct from geographic hubs.
- [ ] Build cluster profiles for basket coverage, category mix, diversity, and
  visible infrastructure context.
- [ ] Choose and document the cluster-to-tract context association rule.
- [ ] Build the tract context matrix using declared population density, income,
  poverty, rent burden, rents/values, housing, household, and demographic
  measures with source vintages and complete-case coverage.
- [ ] Produce descriptive cluster-context comparisons without causal claims.

**Done when:** reviewers can inspect both where a hub is and what kind of
amenity environment it represents, alongside transparent tract context.

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
