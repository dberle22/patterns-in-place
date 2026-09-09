---
status: in_progress
scope: reusable point-of-interest engine
planning_home: metro-deep-dive-program/engines/poi
promotion_target: foundations after the interface proves reusable
last_updated: 2026-09-08
---

# POI Engine Build Plan

## Goal

Build one reusable system for turning source place records into governed,
analysis-ready points of interest. The engine should provide:

- reproducible source acquisition and cache manifests;
- a common point record with source identity and provenance;
- explicit, reviewable category mappings;
- assignment to governed geographic areas; and
- coverage and quality outputs that analyses can inspect before use.

The first consumer is Q4 Daily-needs access for Richmond. The engine supplies
the classified points and diagnostics; Q4 decides which categories represent
daily needs and how access is measured.

## Architecture boundary

### What the engine owns

| Capability | Responsibility |
|---|---|
| Source acquisition | Download or query a declared POI source for a defined release and study area, then record the run in a manifest |
| Normalization | Preserve source fields while producing a consistent analytical point shape |
| Identity and lineage | Retain source identifiers, source membership, extract metadata, and duplicate diagnostics |
| Taxonomy | Map source categories into controlled analytical categories through explicit, versioned rules |
| Geographic assignment | Use the Geography Engine's boundaries and helpers to assign points to tracts and other supported areas |
| Serving and QA | Expose reusable POI records, mapping coverage, spatial coverage, and review samples |

The exact DuckDB schemas and table names should be locked with the contract,
not in this planning document.

### What stays outside

- The Geography Engine owns geographic identities, boundaries, vintages,
  crosswalks, and spatial-operation conventions.
- The Infrastructure Engine owns roads, rail, waterways, and other non-place
  line or polygon features.
- Catchment and access analyses own rings or service areas, reach measures,
  amenity baskets, and interpretation.
- Barrier handling belongs to the analysis using infrastructure as a
  constraint; a POI is not itself a barrier.
- Corridor Intelligence owns reproducible grouping and may use versioned,
  aggregate POI category counts or rates as soft membership evidence. The POI
  Engine supplies governed records and mappings but does not decide how they
  affect a structural candidate. A refreshed POI input requires a new Corridor
  Intelligence run; it never silently changes prior membership.
- Issue folders own reader-facing labels, selected categories, and narrative.

## Source lanes

Keep different kinds of place evidence distinguishable:

- **Public baseline POIs** describe the presence of amenities and institutions.
  Overture Places is the proven first national-scale candidate.
- **Official or specialist sources** may replace or supplement a category when
  they offer meaningfully better coverage or authority.
- **Curated POIs** describe editorial or personal significance. Stoop provides
  a useful model for their provenance, classification, review, and overrides,
  but curated records should not be silently merged with the public baseline.

The first build does not need a universal cross-source entity-resolution
system. Preserve source-native identities, report likely duplicates, and add
canonical merging only when a consumer demonstrates the need.

## Methods

### Source-faithful ingestion

Extract from an explicit source release and governed study-area boundary.
Retain source identifiers, raw category fields, coordinates, confidence or
quality fields when supplied, and enough metadata to reproduce the run. Use a
bounding box only as an extraction convenience; always apply the true governed
market boundary before producing market-serving records.

### Explicit taxonomy mapping

Use managed mapping rules rather than production substring matching. Preserve
the original source taxonomy beside the mapped category, mapping version,
match rule, and review status. Follow the useful Stoop pattern of separating
exploratory category profiling from approved production mappings and durable
overrides.

The engine should supply stable descriptive categories. Consumer analyses can
assemble those categories into concepts such as `daily_needs`, `anchors`, or
`competitive` without changing the underlying place record.

### Point identity and duplicates

Treat source ID plus source release as the initial durable identity. Normalize
names and coordinates for QA, flag exact and near duplicate candidates, and
preserve all source lineage. Do not assume that nearby records with similar
names are the same physical place without an explicit resolution rule.

### Geographic assignment

Call the Geography Engine for current boundary geometry and point-in-polygon
rules. At minimum, assign each usable POI to a tract and retain the boundary
vintage used. Other readable labels can be added through governed geography
relationships rather than bespoke joins inside each analysis.

### Coverage and quality review

Each build should report:

- records extracted, retained, rejected, and outside the study area;
- valid, missing, and duplicate coordinates;
- mapped, unmapped, ambiguous, and overridden categories;
- counts by source category and governed category;
- tract and market coverage; and
- sample records for high-volume, sparse, and ambiguous categories.

Counts demonstrate that an ingest ran; they do not by themselves prove that a
category is complete or suitable for an access claim.

## Candidate data products

Names remain provisional until the contract is written.

| Product | Grain | Purpose |
|---|---|---|
| Source extract and manifest | source run | Reproducible cache, release, boundary, query, and row-count record |
| Normalized POI record | source place | Common point fields with source-native identity and provenance |
| Taxonomy mapping | source category or rule | Versioned mapping, rationale, and review state |
| Classified POI record | source place | Normalized point plus governed categories and mapping evidence |
| Geography assignment | place × geography level | Boundary-vintaged tract and other supported assignments |
| QA and coverage views | run × source/category/geography | Review surfaces for completeness, ambiguity, duplicates, and spatial coverage |

## Task list by epic

### 1. Audit and contract

- [x] Inventory the Richmond and Jacksonville Overture ingests, manifests,
  category fields, and downstream consumers.
- [x] Audit the Stoop public and curated POI contracts for reusable governance
  patterns without assuming its NYC taxonomy is the MDD taxonomy.
- [x] Define the minimum normalized point fields, provenance fields, and
  rejected-record behavior.
- [x] Define the boundary between source categories, governed categories, and
  analysis-specific amenity baskets.
- [x] Record which identity, deduplication, and refresh questions remain open.

Epic 1 completed 2026-09-08. See [the contract](CONTRACT.md) for locked
interfaces and [audit notes](NOTES.md) for the legacy evidence and deferred
decisions.

### 2. Make source acquisition reproducible

- [x] Refactor the first Overture path into a market-parameterized build rather
  than separate Richmond and Jacksonville scripts.
- [x] Resolve the study area through the Geography Engine.
- [x] Preserve a source-faithful cache and write one manifest per run with a
  run ID, source release, boundary identifier and vintage, query or partition
  specification, cache location/checksum where available, and
  extract/retain/reject/outside row accounting.
- [x] Add retry, resume, or partition behavior only if the first repeatable run
  demonstrates it is needed.
- [x] Verify that rerunning the same release and boundary produces stable
  record counts or explainable differences.

Epic 2 completed 2026-09-08. The reusable Overture registry and acquisition
command are in `sources/` and `acquire_overture_places.py`; validation results
and the unavailable legacy-release note are recorded in [audit notes](NOTES.md).

### 3. Normalize identity and provenance

- [x] Build the common source-place record while retaining the raw taxonomy
  and source identifier.
- [x] Add coordinate, geometry, and market-boundary validation.
- [x] Produce exact and near-duplicate diagnostics without automatically
  merging uncertain candidates.
- [x] Preserve source release, extract time, and query or partition lineage.

Epic 3 completed 2026-09-08. `normalize_overture_places.py` produces
source-place, rejection, and duplicate-candidate artifacts beneath each
declared source run; see [audit notes](NOTES.md) for Richmond validation.

### 4. Build the taxonomy workflow

- [x] Profile the Overture fields used in the Richmond and Jacksonville pilots.
- [x] Create the first managed mappings needed by the Q4 consumer.
- [x] Store the rule and evidence behind each mapped category.
- [x] Produce unmapped and ambiguous review queues.
- [x] Add durable overrides only when manual review begins producing decisions
  that must survive reruns.

Epic 4 completed 2026-09-08. The initial exact-match registry is
`taxonomy/q4_overture_v1.yml`; `classify_overture_places.py` publishes the
classified layer and review queues without defining an analysis basket.

### 5. Assign geography and publish QA surfaces

- [x] Assign valid points to current tract and county geometry through the
  Geography Engine and retain each boundary vintage; extract postal ZIP from
  the source address as supporting resolution evidence. ZCTA point assignment
  remains blocked on a governed ZCTA geometry surface.
- [x] Add other geography labels only when a consumer needs them.
- [x] Materialize run, category, coordinate, duplicate, and geography coverage
  summaries.
- [x] Add map-ready review samples without making display artifacts canonical.
- [x] Document known source and category limitations.

Epic 5 completed 2026-09-08 for the available governed geography interface.
`assign_poi_geography.py` assigns tracts and counties by point-in-polygon and
retains source-address postal ZIP values. ZCTA geometry is a Geography Engine
dependency and is explicitly not represented as a false point assignment.

### 6. Support the first analysis

- [ ] Supply Q4 with a Richmond POI inventory and explicit category evidence.
- [ ] Keep the daily-needs basket and access calculation in the Q4 analysis.
- [ ] Use Jacksonville as a portability and regression check.
- [ ] Record which interfaces the analysis used unchanged.
- [ ] Promote stable code or tables to `foundations/` only when the program's
  reuse rule is met.

## First implementation slice

Use the existing Richmond and Jacksonville work to prove a narrow interface:

1. audit the two Overture caches and manifests;
2. parameterize the shared extraction path;
3. normalize source identity, provenance, and category fields;
4. create only the taxonomy mappings needed for Richmond Q4;
5. assign the resulting points to governed tracts; and
6. compare Richmond and Jacksonville coverage and unmapped categories.

This slice stops before calculating access, building catchments, interpreting
barriers, or detecting corridors.

## Decisions deferred until build

- Final managed table and schema names.
- Whether and when to add official category-specific sources.
- Whether cross-source canonical entity resolution is worth its cost.
- The long-term relationship between national public POIs and Stoop's curated
  place products.
- Refresh cadence and national partition strategy.
- The category basket and spatial method used by Q4.

## Completion criteria

- A market and source release can be rebuilt from a declared configuration.
- Every classified point retains source identity, provenance, and mapping
  evidence.
- Coordinates and tract assignments pass coverage and validity checks.
- Unmapped, ambiguous, and likely duplicate records remain visible for review.
- Richmond Q4 can consume the outputs without rebuilding POI ingestion or
  taxonomy logic.
- Jacksonville can use the same interface without market-specific code.
