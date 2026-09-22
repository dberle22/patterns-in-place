---
status: epics_2_through_7_complete
scope: platform-wide geography engine
planning_home: metro-deep-dive-program/engines/geography
production_home: foundations
last_updated: 2026-09-09
---

# Geography Engine Build Plan

## Goal

Build one governed geography engine for Metro Deep Dive and the wider repo. It
should provide:

- a canonical geography dimension;
- exact, weighted, and historical crosswalks;
- analytical and display geometry down to census tract; and
- shared helpers and documentation for using geography safely.

Census tract is the lowest geometry needed by the current program. Census
blocks remain an internal tabular building block for crosswalks; block polygons
are not part of v1.

## Next priority: local-neighborhood mappings

Corridor Intelligence is paused after prototype calibration. The next
geography work is discovery and governed mapping of local neighborhoods for
analysis and orientation. This does not authorize an algorithmic neighborhood
classifier or a replacement for tract/ZCTA taxonomies.

Before a build begins, document each source's license, geography coverage,
vintage, identifier stability, geometry role, update cadence, and relationship
basis. The eventual product must preserve sourced neighborhood identities and
expose explicit tract-to-neighborhood and ZCTA-to-neighborhood overlap edges.
Internal Structure can then use local neighborhoods as a contextual overlay;
corridor questions remain analysis-local.

## Architecture

### Ownership and layers

`metro-deep-dive-program/engines/geography/` is the repository entry point for
the plan, contract, notes, and usage guidance. Canonical ETL and managed tables
should be built in `foundations/` from the start. Reusable helpers can move to
`foundations/geography/` after two consumers use the same interface unchanged.

| Layer | Responsibility |
|---|---|
| `staging` | Source-faithful Census, OMB, HUD, and geometry inputs |
| `silver` | Vintaged identities, block registry, and typed crosswalks |
| `geo` | Full analytical and simplified display geometry by geography level |
| `gold.dim_geo` | Backward-compatible current dimension for existing consumers |
| `mart_geography` | Preferred current and historical query surfaces for new work |

Keep `gold.dim_geo` in place. A new vintaged `silver.dim_geo` should become the
historical identity source, while `gold.dim_geo` continues to expose one
current row per geography. New Metro Deep Dive queries should use
`mart_geography`.

### Geography scope

V1 covers the 50 states and District of Columbia at these levels:

- US, Census region, and Census division;
- state;
- CBSA, including metropolitan and micropolitan areas;
- county and county equivalent;
- Census place;
- ZCTA; and
- census tract.

These levels do not need to live in the same physical table. School districts,
block groups, territories, parcels, and block geometry are deferred.

### Relationship types

| Type | Meaning | Example |
|---|---|---|
| Containment | Exact parent-child relationship | tract to county; county to state; county to current CBSA where assigned |
| Allocation | Many-to-many relationship with an explicit weight | tract to place; tract to ZCTA; ZIP to tract |
| Temporal | Same geography across boundary definitions | 2010 tract to 2020 tract |

The semantic catalog and Silver tables must keep these relationship types
separate. A weighted relationship must never be represented as an exact parent.

### Vintage rules

Keep three concepts distinct:

- `data_year`: when a metric was measured;
- `boundary_vintage`: which geography definition is used; and
- `source_release_year`: when the source file was released.

Use the latest approved geography for production rollups while retaining the
original geography and applied crosswalk for audit. The current tract backbone
is 2020. CBSAs should use the latest official OMB delineation supported by the
engine; as of this plan, that is July 2023.

Historical tracts should normally be restated to the current tract definition.
Historical counties should resolve to the governed current county backbone
before rolling to current CBSAs.

### Geometry

Store two governed products:

- full TIGER/Line geometry for spatial joins, intersections, and
  point-in-polygon work;
- simplified Census cartographic geometry for maps and lightweight exports.

DuckDB `geo.*` tables are canonical. Raw downloads and generated geometry
exports remain ignored by Git. Geometry stays separate from `dim_geo` and joins
by geography level, ID, and boundary vintage. Region, division, and US geometry
can be derived from state geometry.

### Sources

Use Census-authoritative inputs for the core registry:

- 2020 PL 94-171 block records;
- Census block assignment and relationship files for place and ZCTA;
- Census 2010-to-2020 tract relationships;
- TIGER/Line and cartographic boundary files;
- the latest approved OMB county-to-CBSA delineation; and
- HUD-USPS files for ZIP relationships.

Use LODES crosswalks as a reconciliation source, not the geography authority.

### ZIP and ZCTA

ZIP and ZCTA are distinct. ZCTA is the Census tabulation geography used by ACS;
USPS ZIP is a changing delivery identifier used by sources such as IRS and HUD.
ZCTA-native data uses the ZCTA identity directly. ZIP-keyed data uses the
versioned HUD-USPS allocation tables, with an explicit ratio basis; ZIP is not
a `dim_geo` member and has no geometry in this engine. The current
`silver.xwalk_zcta_*` tables contain HUD USPS ZIP relationships and should be
renamed to `silver.xwalk_zip_*`. Use temporary compatibility views while
consumers migrate. Genuine Census ZCTA relationships should enter the typed
allocation layer under unambiguous names.

### Query interface

The engine should expose a small SQL/Python interface:

- `rollup()` for exact containment;
- `allocate()` for weighted relationships with an explicit basis;
- `harmonize()` for historical-to-current geography;
- `get_geometry()` for analytical or display shapes; and
- `export_geometry()` for scoped local artifacts.

The helpers should expose relationship quality and provenance. They should not
assume every metric can be summed; rates, medians, and indices still need
metric-aware aggregation.

## Proposed managed surfaces

Exact names will be finalized during the contract task.

| Surface | Purpose |
|---|---|
| `silver.dim_geo` | Vintaged identity and name registry |
| `silver.block_registry` | Block membership and weight inputs, without block polygons |
| `silver.xwalk_containment` | Exact hierarchy edges |
| `silver.xwalk_allocation` | Weighted edges with basis and quality |
| `silver.xwalk_temporal` | Historical-to-current edges and change type |
| `geo.<level>_analysis` | Full geometry by level and vintage |
| `geo.<level>_display` | Simplified geometry by level and vintage |
| `gold.dim_geo` | Existing current serving dimension |
| `mart_geography.*` | Current/vintaged identities, typed edges, and audit views |

## Task list

### 1. Research and lock the contract

- [x] Reconcile `geo_spec.md` with this plan, including geometry scope and the
  Silver/Gold boundary.
- [x] Extend `geography_catalog.yml` with stability, boundary authority,
  vintages, legal relationships, and geometry roles.
- [x] Inventory current `gold.dim_geo`, `silver.xwalk_*`, and `geo.*` consumers.
- [x] Confirm the smallest practical Census source bundle for the block
  registry, place assignments, and ZCTA assignments.
- [x] Profile national download sizes and choose chunked ingestion patterns.
- [x] Research defensible population and housing-unit weights for 2010-to-2020
  tract harmonization; do not assume the answer in advance.
- [x] Confirm how future OMB delineations become current without overwriting
  history.
- [x] Decide the display-geometry scale needed for tract-level maps.
- [x] Write or update source contracts and finalize table names.

#### Task 1 disposition (2026-09-07)

- The governed block registry will use Census 2020 PL 94-171 counts and Census
  block assignment files, not LODES. LODES remains a reconciliation source.
- Ingestion is state-scoped and sequential. The national tract relationship
  file is only 18 MB, but block inputs are materially larger; land each state
  before building its Silver rows and never run concurrent DuckDB writers.
- The current warehouse already has nationwide current hierarchy tables and
  cartographic geometry. It lacks a block registry, vintaged identity,
  typed relationships, temporal harmonization, place/ZCTA geometry, and the
  mart. Details and source contracts are in `CONTRACT.md` and `NOTES.md`.

### 2. Correct ZIP/ZCTA semantics

- [x] Add a versioned HUD-USPS acquisition step.
- [x] Build canonical `silver.xwalk_zip_tract`, `xwalk_zip_county`, and
  `xwalk_zip_cbsa` tables.
- [x] Add temporary compatibility views for the current misnamed tables.
- [x] Migrate consumers and update the data dictionary.

### 3. Build the geography foundation

- [x] Stage the approved 2020 Census block inputs.
- [x] Build `silver.block_registry` with tract, county, state, place, and ZCTA
  membership plus approved weighting inputs.
- [x] Build vintaged `silver.dim_geo`.
- [x] Build exact containment relationships, including current
  county-to-CBSA membership.
- [x] Rebuild and reconcile `gold.dim_geo` without breaking current consumers.

#### Epics 2–3 disposition (2026-09-07)

- Materialized 8,132,968 Census 2020 block-registry rows across all 50 states
  and DC, with 34,520 Census ZCTAs supplied by the dedicated relationship file.
- `gold.dim_geo` rebuilt with its existing 88,356 current keys intact.
- Canonical HUD-USPS ZIP crosswalks are now versioned base tables; legacy
  `xwalk_zcta_*` names are compatibility views during consumer migration.

### 4. Ship the containment-first mart

This is the first part of the original mart epic. It delivers immediate value
from the completed identity and exact-containment foundation without claiming
that weighted allocation, temporal harmonization, or governed geometry already
exist.

**Validation policy:** build the interfaces and run only structural checks now:
declared keys, declared paths, row coverage, and provenance. Defer full
behavioral testing, metric-aware aggregation review, and consumer smoke tests
until a named downstream consumer adopts the operation. The first consumer is
the acceptance test for that operation; its discovered requirements then become
the reusable helper contract.

- [x] Build `mart_geography` current/vintaged identity, exact-relationship,
  ZIP-catalog, and coverage-audit views.
- [x] Implement `rollup()` for declared exact containment only.
- [x] Add SQL and Python examples for identity lookup and exact rollups.
- [x] Document the containment-only interface and its limits.

#### Epic 4 disposition (2026-09-08)

- `mart_geography` now exposes transparent, exact rollup views rather than a
  metric-aggregating function.
- The current tract-to-CBSA view carries the 2020 Census tract vintage and the
  2023 OMB CBSA vintage separately.
- Structural checks passed; consumer-specific aggregation QA remains deferred
  to the first named downstream consumer.

### 5. Govern existing geometry

The existing nationwide cartographic geometry is retained. This epic is a
refactor and governance pass, not a broad geometry reinvention.

- [x] Port `get_tiger_geos.R` to `foundations/etl/geo/` as a versioned,
  explicit-scope display-geometry build; retain the old staging path as a
  compatibility entry point.
- [x] Define the new display products with explicit role and boundary-vintage
  metadata. The on-demand build writes `geo.*_display` and leaves legacy
  `geo.states`, `geo.counties`, `geo.cbsas`, and `geo.tracts_all_us` intact.
- [ ] Add full TIGER/Line analytical geometry only where a spatial consumer
  needs it; do not duplicate current display products.
- [x] Register the existing current tract, county, and CBSA products as
  approved read-only display geometry in `mart_geography.geometry_catalog`.
  Their 2024 Census cartographic-boundary provenance and stable join keys are
  documented without a national rebuild or a consumer migration.
- [ ] Defer place, ZCTA, division, region, and US geometry until a named
  consumer requires it; derive higher-level shapes from states where needed.

#### Epic 5 disposition (2026-09-08)

- The existing cartographic-boundary logic is now owned by the geography ETL
  folder and is available for future state-scoped builds.
- It requires `GEOGRAPHY_TIGER_STATE_SCOPE` (for example, `VA,FL` or `ALL`)
  and writes new role-specific display tables only. It was not run for this
  epic, so no geometry data was rebuilt or added.

### 6. Build allocation and temporal crosswalks

Build these governed relationships and their coverage/conservation audit
surfaces now, but do not attempt exhaustive allocation or harmonization QA in
isolation. Full QA waits for the first named readability consumer (allocation)
and Q3 Where Growth Lands (harmonization), where the metric, direction, target
vintage, and interpretation risk are concrete.

- [x] Build tract/place and tract/ZCTA allocations for population, housing-unit,
  and land-area bases.
- [x] Add correctly named HUD ZIP allocation bases.
- [x] Preserve partial and zero-denominator cases in quality fields.
- [x] Build approved 2010-to-2020 tract harmonization.
- [x] Retain current county normalization for CBSA rollups in the containment
  mart; no additional county bridge was required.
- [x] Materialize coverage and conservation audits.

#### Epic 6 disposition (2026-09-08)

- `silver.xwalk_allocation` contains 826,299 2020 tract-to-Place/ZCTA edges,
  each emitted separately for population, housing units, and land area.
- `silver.xwalk_temporal` contains 373,822 2010-to-2020 tract edges. Land area
  uses the Census tract relationship file; population and housing use 2010 PL
  block counts apportioned through Census block-intersection land area.
- Audit tables retain unmatched, partial, and zero-denominator cases. There are
  6,885 tracts without a Place assignment and 338 without a ZCTA assignment;
  those are coverage facts, not dropped records.
- Structural checks passed. Full metric-level conservation and interpretation QA
  remains deferred to the first allocation and harmonization consumers.

### 7. Complete the mart, helpers, and documentation

- [x] Extend `mart_geography` with allocation, temporal, geometry-catalog, and
  audit views.
- [x] Implement narrow allocation/temporal relationship helpers and
  `get_geometry()` discovery / `export_geometry()` scoped-artifact helpers.
- [x] Add SQL and Python examples for allocation and temporal operations.
- [x] Document counts versus rates, vintage selection, ZIP versus ZCTA, and
  analytical versus display geometry.
- [x] Add Richmond and Jacksonville structural smoke queries.
- [x] Update `CONTRACT.md`, `NOTES.md`, and `USAGE.md` with the final interface
  and limitations. The pre-existing dirty `README.md` is intentionally left
  untouched.

#### Epic 7 disposition (2026-09-08)

- `mart_geography` now publishes separate allocation, temporal, coverage-audit,
  and geometry-catalog views alongside exact containment views.
- The Python helpers return relationship edges or explicitly selected display
  geometry; they never choose an aggregation for a metric.
- Richmond and Jacksonville structural smoke queries return governed
  allocation and temporal edges. Full metric-level QA remains deferred as
  agreed.

### 8. Integrate program consumers

- [ ] Move Position / Internal Structure to governed tract geometry.
- [ ] Use current county-to-CBSA rollups in Regional Role and Q6.
- [ ] Use temporal harmonization in Q3 Where Growth Lands.
- [ ] Use explicit place/ZCTA allocation in the first readability consumer.
- [ ] Promote stable helpers to `foundations/geography/` after the second
  unchanged consumer.
- [ ] Update `docs/build_sequence.md` and the classification workbook as tasks
  are completed.

### 9. Build regional-lens interfaces for Regional Role

Regional Role is the first named consumer of reusable state-adjacency and
CBSA-proximity relationships. Build these interfaces in Geography, rather than
in the analysis notebook, so Q6 and later regional comparisons consume the
same declared memberships.

- [x] Materialize approved analytical state and CBSA geometry at the current
  boundary vintage. This is the narrow geometry addition required for state
  land-boundary adjacency, CBSA centroids, and promotion of the existing
  market-scoped Infrastructure serving candidates.
- [x] Build `mart_geography.state_adjacency` as a symmetric, land-only state
  relationship. Adjacency requires a shared border line of nonzero length: a
  river boundary counts; ocean, Great Lake, and point-only contact do not.
  Carry boundary vintage, source, and method version.
- [x] Build `mart_geography.cbsa_centroids` from the approved analytical CBSA
  geometry. Declare the centroid method and retain boundary vintage and source.
- [x] Build `mart_geography.region_lens_membership` for `census_division`,
  `primary_state`, `primary_state_adjacent`, and centroid-radius lenses. Use
  `gold.dim_geo.state_fips`, whose primary-state rule is the first state named
  in the official CBSA label; do not substitute county count or population.
- [x] Store the centroid-radius parameter and calculated great-circle distance
  so Regional Role can inspect 200-, 250-, and 300-mile membership without
  recomputing geometry relationships in a notebook.
- [x] Add Richmond and one multi-state-CBSA smoke check for primary-state,
  adjacency, centroid-distance, key uniqueness, symmetry, and provenance.
- [x] Update `CONTRACT.md`, `USAGE.md`, and the data dictionary with the new
  regional-lens interface and its geometry limitations.

**Done when:** Regional Role can read all four named lens memberships from
`mart_geography` with declared source, boundary vintage, method version, and
parameters; the analytical CBSA boundary is also available to promote a
market-scoped Infrastructure context handoff.

#### Epic 9 disposition (2026-09-21)

- `geo.states_analysis` (51 state/DC rows) and `geo.cbsas_analysis` (935 rows)
  now carry full 2023 Census TIGER/Line geometry for the declared relationships.
- `mart_geography.state_adjacency` has 220 symmetric land-border edges;
  `cbsa_centroids` has 935 declared equal-area centroids; and
  `region_lens_membership` materializes all four lenses plus 200/250/300-mile
  sensitivity rows with provenance.
- Richmond lens memberships and Wheeling, WV-OH's West Virginia primary state
  passed smoke checks. Membership keys are unique and every target/lens row has
  exactly one target member.

### 10. Build Place-to-CBSA membership for Q3 Where Growth Lands

Q3 needs to identify Census Places associated with a metro without pretending
that a Place is an exact child of a CBSA. This is a reusable Geography
relationship: Places can span counties and CBSA boundaries, and unincorporated
metro geography has no Place membership.

- [ ] Build a 2020 `Place × CBSA` weighted membership relationship from the
  governed block registry's Place assignment, exact county-to-CBSA membership,
  and 2020 population, housing-unit, and land-area numerators.
- [ ] Retain both directions of share, denominators, quality/coverage flags,
  source, and Place/CBSA boundary vintages. This is an allocation/membership
  surface, never an exact containment edge.
- [ ] Publish a declared primary-CBSA association for each Place using its
  largest 2020 population share, while keeping every secondary/split membership
  available to consumers.
- [ ] Document the consumer rule: direct Place measures are whole-Place values;
  split Places need explicit allocation or a whole-Place caveat, and
  unincorporated geography must remain visible in a metro read.
- [ ] Add national cardinality/weight checks plus Richmond and a split-Place
  smoke test; expose the result through `mart_geography`.

**Done when:** a consumer can retrieve every Place associated with a CBSA,
distinguish wholly associated and split Places, and apply a declared basis
without local spatial joins or a false exact-parent claim.

## Next implementation sequence

The national ZIP and foundation builds are complete. The remaining work proceeds
in this order:

1. containment-first mart and `rollup()`;
2. govern and refactor the existing geometry products;
3. build allocation and temporal crosswalks; and
4. finish the full helper interface and integrate program consumers; and
5. build the named regional-lens interfaces for Regional Role; and
6. build Place-to-CBSA membership for Q3 Where Growth Lands.

This sequence preserves a useful mart milestone while keeping `allocate()`,
`harmonize()`, and geometry export unavailable until their required governed
inputs exist.

## Completion criteria

- Identity and geometry keys are unique at their declared vintage.
- Exact relationships satisfy their expected cardinality.
- Weighted and temporal relationships expose basis, quality, and provenance.
- Geometry coverage, CRS, and validity checks pass.
- `gold.dim_geo` remains compatible with existing consumers.
- ZIP and ZCTA are unambiguous in tables, documentation, and code.
- Richmond and Jacksonville smoke tests pass.
- At least two consumers use the same geography interface unchanged.
