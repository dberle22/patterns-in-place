---
status: in_progress
scope: reusable physical infrastructure engine
planning_home: metro-deep-dive-program/engines/infrastructure
promotion_target: foundations after the interface proves reusable
last_updated: 2026-09-08
---

# Infrastructure Engine Build Plan

## Goal

Build a reusable system for acquiring, normalizing, and serving the physical
infrastructure that shapes how a metro functions. The initial scope is the
line and polygon features already explored in Richmond and Jacksonville:

- roads and highways;
- rail;
- waterways and water bodies;
- airports and ports as physical footprints; and
- selected logistics or industrial features when source quality supports them.

The engine provides governed infrastructure geometry and diagnostics. It does
not decide whether a feature is a barrier, calculate a catchment, or identify a
corridor.

## Architecture boundary

### What the engine owns

| Capability | Responsibility |
|---|---|
| Source acquisition | Obtain a reproducible extract for a declared release and study area |
| Feature normalization | Translate source tags into a small, documented infrastructure vocabulary while retaining raw tags |
| Geometry preparation | Preserve geometry type, repair or reject invalid geometry, clip to the study area, and provide analytical and lightweight representations when needed |
| Provenance | Record source, provider, release or extract date, query, study boundary, and transformation history |
| Serving and QA | Expose reusable features plus coverage, validity, and classification diagnostics |

The first contract should describe stable feature objects rather than promise a
complete transportation-network model.

### What stays outside

- The Geography Engine owns administrative and statistical boundaries,
  geography identities, vintages, crosswalks, and shared spatial conventions.
- The POI Engine owns place-like point records and their taxonomy. An airport
  POI anchor and an airport footprint can coexist without being forced into one
  record.
- Catchment and accessibility analyses decide how infrastructure affects
  practical reach.
- Barrier handling is an analytical interpretation of infrastructure, not a
  source classification produced here.
- Corridor Intelligence will combine Intelligence Framework zones with
  proximity and optional infrastructure, POI, and trajectory evidence.
- Parcel screening remains downstream and conditional.

## Source roles

OSM is the proven first source for geometry-first features in the existing
pilots. The engine should preserve that useful source-role distinction:

| Real-world object | Default representation |
|---|---|
| Road, highway, rail, or water network | Infrastructure line or polygon |
| Airport, port, campus, or industrial site footprint | Infrastructure polygon when the mapped geometry is useful |
| Named amenity or establishment anchor | POI record |

Official or specialist sources can be added where they materially improve a
consumer, but the first plan does not select a national source stack for every
infrastructure family.

## Methods

### Reproducible extraction

Prefer provider-backed or downloadable extracts that can be cached and parsed
locally over fragile repeated live queries for metro-scale builds. Derive the
study boundary from the Geography Engine, use a bounding box when required for
acquisition, and clip the normalized analytical layer to the governed market
footprint when over-capture matters.

### Source-faithful normalization

Keep raw OSM or provider tags beside a small governed `feature_group` and
`feature_type`. Initial mappings should cover only features a consumer needs.
The routine core water network is rivers and canals, with river/riverbank
polygons when the source supplies them. Lakes, reservoirs, estuaries, coastal
water, and other major water bodies are conditional context selected by a
named analysis; ponds, basins, wastewater surfaces, tanks, and untyped water
surfaces remain source-side by default.
Warehouse, logistics, industrial, airport, and port mappings should remain
reviewable because the Richmond pilot found enough records to investigate but
not enough evidence to treat every rule as settled.

### Geometry handling

Carry source geometry type and CRS, transform to an appropriate projected CRS
for distance or area work, and validate geometry before serving it. Avoid
turning line or polygon infrastructure into POIs merely to fit a common table.
Any simplified display products should remain derived from the analytical
geometry.

### Resolution and generalization policy

Retain valid, identity-complete source features in the analytical layer; a
market-wide minimum-area rule must not silently remove small water bodies that
may matter to a named analysis. Water needs a `linear` versus `surface` form
and source-supported type before consumers use it. A map or other
scale-specific consumer may request a derived display layer with a documented
minimum size, simplification, or dissolve rule. That derivative must retain
its source-run, rule, scale, and contributing-feature lineage; it never
replaces source features or pre-decides barrier behavior. Open park space is a
separate future family, not an unreviewed extension of the water mapping.
Never run an unbounded market-wide dissolve of raw geometries. Validate first,
then partition any requested dissolve by feature type and bounded spatial unit;
record failures rather than allowing a geometry-engine crash to terminate a
run.

### Network readiness

Preserve identifiers and topology-relevant attributes that could support a
future routable network, but do not build graph topology, travel times, or
universal impedance assumptions until Q2 or another consumer requires them.

### Coverage and quality review

Each build should report:

- source and extract coverage relative to the study area;
- feature counts by group, type, and geometry;
- invalid, empty, repaired, and rejected geometries;
- unmapped source tags and likely classification false positives;
- duplicated or overlapping features where they affect use; and
- lightweight maps or samples for qualitative inspection.

## Candidate data products

Names are logical contract products; physical table and schema names remain
provisional.

| Product | Grain | Purpose |
|---|---|---|
| Source extract and manifest | source run | Reproducible provider, release, boundary, query, and row-count record |
| Normalized infrastructure feature | source feature | Common geometry, governed feature type, raw tags, and provenance |
| Feature mapping | source tag rule | Explicit mapping from source tags to the governed vocabulary |
| Study-area infrastructure layer | market × source feature | Clipped, validated analytical features for consumers |
| Display/generalization derivative | market × source feature or derived component | Optional scale-specific filtering, simplification, or dissolve for maps; retains rule and source-feature lineage |
| QA and coverage views | run × feature group | Review surfaces for coverage, geometry validity, and mapping quality |

## Task list by epic

### 1. Audit and contract

- [x] Inventory the Richmond and Jacksonville `osmextract`, PBF, normalized
  parquet, manifest, and downstream code paths.
- [x] Separate proven extraction behavior from exploratory feature mappings.
- [x] Define the minimum normalized line and polygon fields, provenance, and
  rejected-feature behavior.
- [x] Define the interface with Geography for boundaries, CRS, and clipping.
- [x] Record topology, routing, and barrier questions as deferred extensions.

### 2. Make extraction reproducible

- [x] Choose the smallest reliable cached-extract path for the first two
  markets based on the existing provider and PBF evidence.
- [x] Parameterize the build by market, boundary, source, and extract date or
  release.
- [x] Keep the first reproducible path market-scoped; defer a national network
  pull until a named all-market analysis needs it and the two-market contract
  has proven reusable.
- [x] Preserve a durable source feature and geometry identity for every
  line or polygon before it can enter the serving layer; retain the existing
  identity-incomplete polygons only as rejected audit records.
- [x] Write one manifest per run with query and layer counts.
- [x] Record the source asset checksum or an explicit unavailable status beside
  its release or dated snapshot.
- [x] Clip to the governed market footprint when provider coverage extends
  beyond it.
- [x] Record source-to-clipped counts and area by geometry family and water
  type so provider over-capture and fine-grained feature density are separate
  diagnostics.
- [x] Confirm rerun behavior before widening the extraction pattern.

### 3. Normalize infrastructure features

- [ ] Implement the initial roads/highways, rail, and `water_network`
  mappings needed by current consumers.
- [ ] Apply the same core `water_network` selectors to Richmond and
  Jacksonville before comparing their coverage; do not make the broad
  water-surface selector a routine consumer output.
- [ ] Keep `water_network` linear and surface forms distinct, covering rivers,
  canals, and source-supported riverbank/river surfaces; leave other water
  types source-side or conditional context until a named analysis selects them.
- [ ] Preserve raw tags and source geometry alongside governed feature groups.
- [ ] Keep airport, port, warehouse/logistics, and industrial mappings
  exploratory until reviewed.
- [ ] Avoid cross-source conflation with POI anchors.
- [ ] Document unmapped and ambiguous tag handling.

### 4. Validate and serve geometry

- [ ] Validate CRS, geometry type, emptiness, and geometry validity.
- [ ] Define when invalid geometry is repaired versus rejected.
- [ ] Produce feature-count, coverage, and unmapped-tag summaries.
- [ ] Create lightweight review maps for Richmond and Jacksonville.
- [ ] Profile water count, area, vertex complexity, type, and scale-specific
  display burden before selecting a display derivative.
- [ ] Add a documented size filter, simplification, or dissolve derivative
  only when a consumer demonstrates a need; preserve feature lineage and do
  not apply it to the analytical layer.
- [ ] Require geometry validation and bounded, partitioned execution before
  any dissolve; a failed geometry operation must produce a QA outcome rather
  than crash a market build.

### 5. Support initial consumers

- [ ] Supply Q4 with only the infrastructure context required by its first
  method, if any.
- [ ] Expose road/network-ready attributes for a future Q2 experiment without
  implementing routing in advance.
- [ ] Make normalized layers available to future catchment, barrier, and
  Corridor Intelligence work without embedding those methods here.
- [ ] Record which interfaces consumers use unchanged.

### 6. Widen and promote

- [ ] Run the same contract for Richmond and Jacksonville.
- [ ] Add additional markets or infrastructure families only when routed
  analyses call for them.
- [ ] Open a national road, rail, or water-network extraction only when a
  named all-market analysis needs it and the two-market interface is reused
  unchanged.
- [ ] Reconcile with official or specialist sources only where comparison
  shows a meaningful gain.
- [ ] Promote stable code or tables to `foundations/` when the program's reuse
  rule is met.
- [ ] Update the engine contract, limitations, and program planning documents
  as decisions are made.

## First implementation slice

Use Virginia and Florida to turn the existing OSM work into one reusable path:

1. audit the successful `osmextract` outputs and the incomplete or alternate
   PBF paths;
2. define a minimal normalized contract for roads/highways, rail, and the
   river/canal `water_network`;
3. parameterize extraction and market clipping;
4. retain the existing airport, port, and logistics layers as review-only;
5. run geometry and tag QA for Richmond and Jacksonville; and
6. expose the validated layers without adding routing, barrier, or corridor
   logic.

## Decisions deferred until build

- The long-term extract provider and national partition strategy.
- Exact managed table and schema names.
- Which exploratory infrastructure families graduate into the core contract.
- Whether routing requires a widened network contract or a separate network
  component.
- How official transportation or hydrography sources should reconcile with
  OSM.
- Display simplification rules and scales.

## Completion criteria

- A market infrastructure extract can be rebuilt from declared configuration.
- Every normalized feature retains source tags, geometry, and run provenance.
- Core geometry validity, CRS, boundary, and coverage checks pass.
- Roads/highways, rail, and the river/canal `water_network` use the same
  interface in Richmond and Jacksonville.
- Consumers can identify infrastructure features without inheriting source-
  specific parsing logic.
- No output claims that a feature is a barrier, a route, or a corridor.
