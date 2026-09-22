# Explanation Q4 — Livability Amenities and POI Clusters Spec

**Status:** Revised after Epic 1 audit; ready to define the POI-first pilot.

**Build order:** E5 — a POI-first workbench that produces reviewed amenity
clusters and cluster context. It does not depend on a Q2 access method.

**Primary surface:** `EXPLANATION_Q4_NOTEBOOK.py` (not yet written)

**Pilot markets:** Richmond, VA (`40060`) and Jacksonville, FL (`27260`)

**Initial method:** `q4_livability_clusters_v1`

**Dependencies:** governed POI runs, POI point assignment, tract geometry and
demographic/housing context. Infrastructure is a mapped context layer only in
V1. No new engine is required for the first pilot.

## Goal

Build a reusable workbench for understanding how amenities are organized across
a metro. Start with standardized POI points, identify spatial amenity hubs and
their amenity mix, describe comparable but noncontiguous amenity environments,
and relate those results to the population, housing, and demographic context of
nearby tracts.

The durable output is a reviewed inventory of amenity clusters and their POI
membership for later corridor, catchment, housing, employment, and access work.
It is not a tract ranking or a universal daily-needs score.

## Analytical frame

Q4 is the program's introductory 15-minute-city **workbench**: it makes the
amenity landscape visible before asserting whether residents can reach it. The
first build can describe amenity concentration, diversity, and surrounding
context. It cannot claim 15-minute access, walkability, route quality, travel
time, or a barrier effect until a declared network and barrier method exists.

The primary evidence is POI-level, not tract-level. Tracts are a reproducible
context and aggregation surface: each retained POI has a governed tract
assignment, and tract demographic/housing measures help explain the areas in
and around an amenity cluster. They do not define the cluster by themselves.

## Products and grains

| Product | Grain | Purpose |
|---|---|---|
| POI amenity workbench | retained POI point | Preserves governed classification, basket membership, source/run provenance, and tract assignment for exploration and QA. |
| Basket catalog | basket version × governed category/subcategory | Declares broad livability, errands/essentials, and any later purpose-specific baskets without rewriting POI taxonomy. |
| Spatial amenity hub | market × reviewed cluster version × cluster | A direct point-pattern cluster with geometry, membership rule, size, category mix, diversity, and coverage flags. |
| POI cluster membership | cluster version × POI point | Makes each hub reproducible and reviewable. A POI may receive no cluster membership; multi-membership requires an explicit rule. |
| Amenity-environment typology | cluster version × cluster type | Groups noncontiguous hubs with similar POI composition. It is distinct from geographic clustering. |
| Tract context matrix | market × tract × snapshot | Supplies population density, income/poverty, rent burden, rents/values, housing stock, household/demographic context, POI counts, and basket summaries for interpretation. |
| Q2 comparison surface | cluster or tract × Q2 version | Compares amenity hubs with reviewed job-center evidence; it does not construct or validate either product. |

## What this analysis owns and borrows

**Owns:** analysis basket definitions, POI-cluster construction, cluster and
typology review, tract-context profiles, and the Q2 comparison.

**Borrows from the POI Engine:** source identity, source release, provenance,
governed taxonomy, point coordinates, and tract/county assignment. Q4 may not
reclassify, deduplicate, or silently drop POIs locally.

**Borrows from Infrastructure:** source-faithful roads, rail, and water only as
visual and descriptive context. The engine does not provide a network, routing,
walkability, or a barrier conclusion.

**Borrows from Q2:** reviewed job-center inventory and physical-proximity
evidence only as a comparison layer. Q2's current Haversine method explicitly
does not define access or a 15-minute-city result, so Q4 does not adopt it as
an access method.

## V1 method boundary

1. Start from retained, governed POI points in Richmond and Jacksonville and
   expose their categories, subcategories, mappings, source vintage, and tract
   assignments in a reviewable workbench.
2. Define a versioned basket matrix. The first required views are broad
   livability and errands/essentials; later baskets remain analysis-owned
   filters over the same governed taxonomy.
3. Explore direct spatial point-pattern candidates for amenity hubs. Select no
   automatic final cluster: record candidate parameters, membership, rejected
   candidates, and sensitivity versions for human review.
4. Use Q2's transparent review discipline—explicit thresholds, visible
   membership, contiguous-area review where useful, and retained
   sensitivities—but do not reuse its job-center selection rules. A tract may
   help describe or review a hub; POI points and their composition define it.
5. Build amenity-environment typologies from cluster composition, allowing two
   distant hubs with similar baskets to share a type without asserting that they
   are one geographic cluster.
6. Join tract context to clusters and their surrounding/containing tracts for
   descriptive comparison. State the join and any buffer or contribution rule;
   do not infer that amenities cause the observed conditions.
7. Compare the final reviewed hubs and context profiles with Q2 job-center
   evidence. Report overlap, separation, and descriptive relationships without
   treating jobs as a target amenity or a resident-access result.

## Inputs and readiness

| Input | V1 role | Audit result |
|---|---|---|
| Richmond and Jacksonville Overture Places runs | POI evidence | Both runs are source-faithful, classified, and tract-assigned. |
| Governed POI taxonomy | Category/subcategory and basket input | 96.7% of Richmond and 96.2% of Jacksonville retained places are mapped across 22 categories and 117 subcategories. |
| POI geography assignment | Tract context join | Every retained POI in both runs is tract- and county-assigned by point-in-polygon. Provider ZIP is not a ZCTA assignment. |
| ACS-derived tract context | Density and living-standard interpretation | Documented as available; the live serving interface and vintages must be verified when the notebook is built. |
| Infrastructure candidate runs | Map and descriptive context | Available for both pilots but not routable or a barrier product. |
| Q2 job-center outputs | Employment comparison | Optional comparison input; not a gate for the POI workbench. |

The POI artifacts support a two-market pilot, not national scale-out. Their
consumer-serving mart/interface status—especially the Jacksonville portability
check—must be confirmed before this becomes a reusable cross-analysis service.

## Minimum outputs

- map-ready POI inventory with category and basket filters;
- basket catalog and category-coverage report for both pilot markets;
- reviewed spatial amenity-hub inventory, geometry, and POI membership table;
- amenity-environment typology table based on cluster composition;
- cluster profile views, including category mix, diversity, infrastructure
  context, and explicit source-coverage flags;
- tract context matrix and descriptive cluster-context comparisons;
- Q2 job-center comparison view; and
- a method record with cluster parameters, sensitivity versions, reviewer,
  date, limitations, and `unavailable` results where coverage is inadequate.

## Guardrails

- POI counts can describe amenity composition and concentration; alone, they do
  not establish resident access, livability, or quality.
- Do not call V1 a 15-minute-access, walkability, travel-time, or barrier
  result.
- Do not make tract context the cluster-selection input unless a later method
  explicitly declares and justifies that choice.
- Do not rewrite POI taxonomy, provenance, identity, or assignment locally.
- Keep geographic amenity hubs separate from noncontiguous composition-based
  typologies.
- Treat unclassified POIs, sparse categories, missing context, and incomplete
  source coverage as visible result states, not zeros.
- Do not scale nationally before the basket, cluster method, and two-market
  review are approved.

## Open decisions for the pilot

- the governed categories/subcategories in broad livability and
  errands/essentials baskets;
- the direct point-pattern candidate methods and review thresholds for hubs;
- cluster geometry and tract-context association rule;
- context-field vintages and primary living-standard measures;
- typology features and number/selection of types; and
- criteria for promoting a pilot POI interface and considering national scope.

## References

- [EXPLANATION_Q4_AUDIT.md](EXPLANATION_Q4_AUDIT.md)
- [EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md](EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md)
- [POI Engine Contract](../../../engines/poi/CONTRACT.md)
- [Infrastructure Engine Contract](../../../engines/infrastructure/CONTRACT.md)
