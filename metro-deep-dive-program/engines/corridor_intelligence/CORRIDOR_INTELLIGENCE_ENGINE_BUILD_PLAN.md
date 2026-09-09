---
status: paused
scope: reproducible within-market corridors and districts
planning_home: metro-deep-dive-program/engines/corridor_intelligence
first_consumer: metro-deep-dive-program/analyses/position/internal_structure
promotion_target: foundations after two unchanged consumer uses
last_updated: 2026-09-09
---

# Corridor Intelligence Engine Build Plan

> **Paused 2026-09-09 — architecture decision:** the Jacksonville and Richmond
> pilot demonstrated reproducible grouping, but not a stable local-geography
> product. Preserve Epics 1–6 as a prototype. Do not start Epic 7 or promote
> outputs. The program will prioritize governed local-neighborhood mappings and
> broader Internal Structure analyses; corridor work becomes a question-led
> analysis rather than a canonical engine output.

## Goal

Build a reusable engine that applies one shared method market by market to
organize Phase 7 tracts into reproducible structural candidates. Same-zone
tracts form the core; Geography, Infrastructure, and cautiously weighted POI
composition help determine coherent membership; limited bridge tracts may join
under explicit rules. Each result is described as a corridor, district, or
unclassified candidate.

The engine makes one corridor/district layer of a metro's internal structure
inspectable. It does not replace the broader Place, zone, POI, employment-center,
or Infrastructure review; select opportunities; screen parcels; or create
editorial neighborhoods.

## Agreed approach

- Phase 7 remains the national structural base and is not rerun here.
- One market run processes every represented zone type using shared rules.
- Same-zone tracts form candidate cores.
- Infrastructure is membership evidence under explicit Corridor-specific
  roles; the Infrastructure Engine remains source-faithful.
- Aggregate POI counts, rates, and composition are softer membership evidence.
  No individual POI creates or breaks a candidate.
- Different-type bridge tracts are allowed only as a conservative, visible
  refinement of a same-zone baseline.
- Corridor and district are two spatial forms of one candidate object.
- Membership, inputs, parameters, and candidate IDs are reproducible and
  versioned. Manual tract edits are prohibited.
- Selection, scoring, editorial naming, and publication remain downstream.

## Execution architecture

Implement a small Python package with one market-parameterized command-line
entry point. One invocation reads the declared DuckDB and engine inputs,
processes all represented zone types for the market, validates the result, and
publishes one versioned run to DuckDB.

A batch runner can later call the same market entry point across many CBSAs.
Review maps and flat-file exports are optional QA artifacts, not canonical
inputs for downstream analyses.

Add a Marimo review notebook alongside the package so we can inspect how the
method behaves while it is being built. The notebook must call shared engine
logic or read versioned run artifacts; it must not become a second grouping
implementation or write manual corrections to canonical outputs.

## Method starting point

Use an explainable neighborhood graph as the leading method:

1. Treat tracts as nodes and evaluate only adjacent or bounded-nearby
   relationships.
2. Establish the same-zone-only core using Phase 7 similarity and Geography.
3. Add explicit Infrastructure continuity, separation, and anchor evidence.
4. Use eligible aggregate POI composition to refine borderline relationships.
5. Test conservative bridge tracts without changing their original zone type.
6. Group qualifying relationships and classify each candidate's spatial form.

Phase 7 Stage 2's hybrid DBSCAN proposal remains an important comparison
method. The Jacksonville pilot should retain it only if it materially and
repeatably outperforms the simpler graph approach without sacrificing
explainability or portability.

Exact thresholds and feature weights are intentionally deferred to pilot
calibration. The goal is one shared scaling rule, not a hand-tuned map for each
market.

## Candidate forms

| Form | Working rule |
|---|---|
| `corridor` | Linear or branched structure with meaningful alignment to a shared infrastructure spine or connected sequence |
| `district` | Compact contiguous or near-contiguous structure without one dominant spine |
| `unclassified` | Valid grouping whose form does not pass either rule confidently during review |

Form is an engine diagnostic, not an editorial neighborhood label.

## Implementation epics

### Epic 1 — Lock inputs and interfaces

- [x] Record the exact Phase 7 build and tract fields used.
- [x] Lock the existing market-scoped tract geometry input for Florida and
  Virginia, with its legacy-vintage status retained as run provenance.
- [x] Define the narrow Infrastructure feature set and Corridor-specific feature
  roles.
- [x] Define the eligible aggregate POI categories and minimum coverage rules.
- [x] Finalize the Python entry point and logical DuckDB output contract.

#### Epic 1 implementation note (2026-09-08)

`inputs/corridor_inputs_v1.yml` is the executable input declaration. Its
preflight command verifies Phase 7 identity and fields, pilot-market coverage,
and exact geometry coverage before any grouping code can run. The July 2026
Phase 7 build has a one-to-one, non-null match in the existing
`geo.tracts_all_us` geometry table for all 340 Jacksonville and 332 Richmond
tracts. That table remains explicitly recorded as
`legacy_cartographic_tract_geometry_v1` with `unknown_legacy_vintage`; its
provenance is not inferred or overwritten. A future Geography promotion to a
registered analytical table is an upgrade path, not a blocker for this first
engine build.

**Done when:** Jacksonville and Richmond have traceable, version-compatible
inputs and the engine does not have to infer any missing source or geography
decision.

### Epic 2 — Build the same-zone structural baseline

- [x] Build strict adjacency and bounded-nearby graph variants.
- [x] Use Phase 7 similarity to test whether nearby same-type tracts belong
  together.
- [x] Preserve isolated tracts and other non-members as explicit unassigned cases.
- [x] Implement the Phase 7 DBSCAN proposal as a challenger.

#### Epic 2 implementation note (2026-09-08)

`baseline_graph_v1.yml` declares the common score vector, spatial thresholds,
and DBSCAN challenger parameters. The market runner writes review artifacts
for strict adjacency, adjacency-plus-bounded-nearby, and the hybrid DBSCAN
challenger. All three retain one membership row for every Phase 7 tract and
every evaluated relationship with its acceptance result.
Jacksonville's first baseline run accounts for all 340 tracts in every
variant. The graph variants each form 45 same-zone candidates containing 246
core tracts and leave 94 explicit unassigned tracts; the uncalibrated DBSCAN
challenger forms 3 candidates containing 11 core tracts and leaves 329
unassigned. These are calibration evidence, not final corridor or district
claims. Form classification, Infrastructure, POI, and bridges remain out of
scope until Epic 3.

**Done when:** every represented Jacksonville zone type produces a complete,
explainable same-zone baseline and the leading graph method can be compared
fairly with DBSCAN.

### Epic 3 — Add physical and place evidence

- [x] Add versioned Infrastructure roles that can support or weaken tract
  connections.
- [x] Build tract-level POI category counts, rates, and composition evidence from
  the governed POI handoff.
- [x] Add POI evidence only to borderline decisions and retain a no-POI sensitivity
  result.
- [x] Add the conservative bridge-tract rule and make each bridge auditable.
- [x] Classify completed candidates as corridors, districts, or unclassified.

#### Epic 3 implementation note (2026-09-09)

The Jacksonville refinement uses the validated OSM Infrastructure source run
`osm-infrastructure-27260-snapshot-2026-08-01-0fc0cea5c456` and a newly
acquired, normalized, classified, and tract-assigned Overture POI source run
`overture-places-27260-2026-08-19-0-20260909T093431Z`. The runner records both
IDs in the run manifest. It permits Infrastructure or aggregate POI changes
only for declared geographically adjacent, same-zone borderline edges. POI
composition cannot create an edge or bridge by itself.

The first Jacksonville `physical_evidence_v1` run has 340 accounted tracts:
234 core, 25 explicit bridges, and 81 unassigned. It records 21 accepted
Infrastructure-spine refinements, 27 Infrastructure-separator rejections, and
one aggregate-POI composition refinement. Every bridge has one or more
relationship records under `conservative_bridge`; none changes the tract's
original zone type. The unreviewed diagnostic form split is 1 corridor, 14
districts, and 2 unclassified candidates. The same baseline-only variants in
the artifact provide the required no-POI comparison.

**Done when:** reviewers can trace every membership change beyond the same-zone
baseline to declared Infrastructure, POI, or bridge evidence.

### Epic 4 — Build the Marimo method-review notebook

- [x] Create `CORRIDOR_INTELLIGENCE_REVIEW_NOTEBOOK.py` as the interactive engine
  review surface, with Jacksonville as its default market.
- [x] Add controls for market, zone type, method or parameter profile, candidate
  form, and selected candidate.
- [x] Show input coverage and provenance before displaying analytical results.
- [x] Build staged maps that move from the same-zone baseline through
  Infrastructure and aggregate POI evidence, bridge decisions, and final
  corridor/district form.
- [x] Add relationship and candidate tables that explain why borderline
  connections were accepted, rejected, strengthened, or weakened.
- [x] Compare the graph method, DBSCAN challenger, no-POI baseline, and declared
  sensitivity runs side by side.
- [x] Surface tract accounting, geometry misses, fragmentation, unassigned tracts,
  bridge share, candidate size, spatial form, and rerun checks.
- [x] Allow optional review exports that retain the selected run and parameter
  lineage, while keeping DuckDB and engine artifacts read-only.
- [x] Confirm that all notebook calculations call the shared Python package rather
  than duplicating membership logic in notebook cells.

#### Epic 4 implementation note (2026-09-09)

`CORRIDOR_INTELLIGENCE_REVIEW_NOTEBOOK.py` discovers only completed run
manifests, loads their artifacts read-only, and defaults to Jacksonville's
`physical_evidence_v1` run. Its controls expose market, profile, method stage,
zone, form, and candidate selection. The staged tract map switches among the
stored strict, bounded-nearby, DBSCAN, and physical/place variants; candidate
trace tables expose the edge decision stage, physical evidence, aggregate POI
evidence, and bridge contacts. The notebook exports selected membership or
edge evidence only as in-memory downloads with run/profile lineage.

The strict and bounded variants are the stored no-POI comparison, while the
DBSCAN challenger and physical-evidence run appear in the method comparison.
No separate parameter sensitivity run exists yet; the notebook makes that
absence visible through the run inventory rather than fabricating one. It
uses the engine's shared `candidate_id()` helper for ID QA and does not carry
any grouping logic.

**Done when:** an analyst can trace a Jacksonville tract from governed inputs
through every grouping stage, compare plausible methods and parameters, and
identify a defect without editing membership in the notebook.

### Epic 5 — Calibrate in Jacksonville

- [x] Run all represented Jacksonville zone types through shared defaults.
- Review candidate size, fragmentation, bridge use, spatial form, and
  unassigned tracts.
- [x] Compare the graph method, DBSCAN challenger, and small sensitivity grid.
- Resolve problems through the shared method or an explicit parameter profile,
  never through manual tract edits.
- Lock the first method version and record known limitations.

**Done when:** Jacksonville produces coherent, reproducible candidates suitable
for Internal Structure review and the chosen method has a written rationale.

### Epic 6 — Validate in Richmond

- [x] Run Richmond through the Jacksonville method without hidden tuning.
- [x] Produce a like-for-like Jacksonville–Richmond comparison using all three
  declared shared parameter profiles.
- Test cross-county grouping, urban-to-rural tract-size variation, bridge use,
  and corridor-versus-district form.
- Revise the shared method only when the change also improves or preserves the
  Jacksonville result.
- Record any unavoidable market profile as an explicit exception.

**Done when:** one method performs defensibly in both markets and identical
inputs reproduce identical membership and IDs.

#### Epics 5–6 execution note (2026-09-09)

Physical-evidence artifacts now exist for Jacksonville and Richmond under the
default, lower-similarity, and higher-similarity profiles. All six runs passed
input, coverage, and declared-geometry checks. The shared default remains
provisional pending map and evidence-trace review in the Marimo notebook; see
`CALIBRATION_AND_PORTABILITY_REVIEW.md` for the metric comparison and review
decision.

### Epic 7 — Publish and hand off

**Status: deferred.** This work is not authorized while the prototype is
paused. A future restart requires a documented product question and evidence
that a reusable corridor entity, rather than an analysis-local overlay, is
needed.

- Publish run, membership, candidate, edge-evidence, and QA products to
  DuckDB.
- Add deterministic ID, invariant, and rerun tests.
- Provide a narrow read-only consumer interface and usage example.
- Verify Internal Structure can map and inventory both candidate forms without
  recreating membership logic.
- Update program status and record the first unchanged consumer use.

**Done when:** downstream analyses can select a versioned market run, trace its
evidence, and consume it without local grouping or source logic.

## Completion criteria

- One Python entry point runs all represented zone types for a selected market.
- Jacksonville calibrates and Richmond validates one shared, versioned method.
- Every candidate has one primary zone type and every non-core bridge is
  explicit.
- Infrastructure and POI evidence affect membership only through documented
  rules and versioned inputs.
- Every candidate is classified as corridor, district, or unclassified.
- Every eligible tract is assigned or given an explicit unassigned/excluded
  status.
- Canonical DuckDB outputs reproduce from the same inputs and configuration.
- The Marimo review notebook exposes the shared build logic, evidence stages,
  method comparisons, and QA without creating a second implementation path.
- Internal Structure consumes the engine without rewriting membership.
- Editorial names, opportunity framing, parcel screening, and issue packaging
  remain outside the engine.

## Explicit non-goals

- revising the Phase 7 national clustering model;
- building routable networks, travel times, or catchments;
- treating every road, rail line, or water feature as a universal connector or
  barrier;
- allowing POIs alone to define membership;
- opportunity or investment scoring;
- parcel screening;
- editorial naming or featured-candidate selection; and
- publication-ready maps or stat blocks.
