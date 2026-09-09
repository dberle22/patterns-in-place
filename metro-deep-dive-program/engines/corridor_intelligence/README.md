# Corridor Intelligence Engine

**Status:** Paused after prototype calibration (2026-09-09). Epics 1–4 and the
Jacksonville/Richmond pilot runs remain documented artifacts, not a product
approved for publication or downstream use.

## Direction change

The pilot showed that a same-zone grouping model can produce reproducible
structural candidates, but not that those candidates are the right local
geography for analysis. Do not treat candidate counts as neighborhood counts,
publish them as a market-wide overlay, or continue to Epic 7.

The next priority is a governed local-neighborhood mapping layer: sourced,
vintaged local identifiers and geometry where available, with explicit
tract/ZCTA relationships. Tract and ZCTA taxonomies remain the analytical
backbone. Corridor exploration moves into Internal Structure as an optional,
question-led analysis using neighborhoods, tract types, POIs, Infrastructure,
and employment/activity evidence; it does not create canonical corridor
boundaries by default.

The Corridor Intelligence Engine turns national Phase 7 tract zone types into
reproducible structural candidates within one metro at a time. It is the
grouping layer between the Intelligence Framework's tract classifications and
a dedicated corridor/district section inside the broader Internal Structure
market-anatomy analysis.

Start with:

- [Contract](CONTRACT.md)
- [Build plan](CORRIDOR_INTELLIGENCE_ENGINE_BUILD_PLAN.md)
- [Input declaration](inputs/corridor_inputs_v1.yml)
- [DuckDB output contract](outputs/corridor_duckdb_contract_v1.yml)
- [Method-review notebook](CORRIDOR_INTELLIGENCE_REVIEW_NOTEBOOK.py)
- [Calibration and portability review](CALIBRATION_AND_PORTABILITY_REVIEW.md)
- [Internal Structure spec](../../analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_SPEC.md)

## Purpose

The engine answers two related questions:

1. Which nearby tracts with the same Phase 7 zone type form a coherent
   structural area within this CBSA?
2. Is that area best understood as a corridor organized around a spine, or as
   a compact district?

It does not decide which candidates are interesting, investable, or ready to
feature. Those are downstream analytical and editorial decisions.

## Core model

- Each market run evaluates every represented Phase 7 zone type using one
  shared, versioned method.
- Same-zone tracts establish each candidate's core and primary zone type.
- Geography limits the search to plausible adjacent or nearby tracts.
- Infrastructure can strengthen, weaken, or block a connection when Corridor
  Intelligence has assigned an explicit role to the governed source feature.
- Aggregated POI category counts and rates can refine borderline connections,
  but POIs cannot create a candidate or justify a bridge tract by themselves.
- A small number of different-type tracts may join as flagged bridge members
  when they connect core sections and pass conservative structural and
  infrastructure checks.
- Resulting candidates are classified as `corridor`, `district`, or
  `unclassified` during review.

Zone types remain national tract labels. Corridors and districts are
within-market forms built from those tracts; neither is a neighborhood name or
an opportunity conclusion.

## Execution model

The first implementation will be a reusable Python package and command-line
runner. One invocation processes one market and all of its represented zone
types. A later batch wrapper can call the same runner for many markets.

Canonical versioned outputs will be stored in DuckDB. Maps and flat-file
exports are review artifacts rather than the source of truth.

## Input preflight

The command below checks one declared market, then writes the Epic 2
same-zone graph variants and DBSCAN challenger as review artifacts.

```bash
python3 metro-deep-dive-program/engines/corridor_intelligence/run_corridor_intelligence.py \
  --market jacksonville_fl \
  --db-path "$DB_PATH"
```

Add `--preflight-only` to inspect inputs without writing artifacts.

## Method review

Open the read-only Marimo notebook after at least one review artifact exists:

```bash
.venv-marimo/bin/python -m marimo edit \
  metro-deep-dive-program/engines/corridor_intelligence/CORRIDOR_INTELLIGENCE_REVIEW_NOTEBOOK.py
```

It discovers completed run manifests and does not write DuckDB or modify
candidate membership.

Run this from the repository root. The project `.venv-marimo` environment is
the notebook kernel and includes its geospatial dependencies, including
`geopandas`; a globally installed `marimo` command may use a different Python
environment and fail on the first import.

### Review workflow

1. Select the shared parameter profile to review; start with
   `physical_evidence_v1__baseline_graph_v1`, not a sensitivity profile.
2. Read the provenance table before interpreting a map. Confirm the Phase 7,
   geometry, Infrastructure, and POI run IDs match the review question.
3. Start with **Candidate inventory** and **Candidate map**. Filter by zone
   type and form, select a candidate, and judge its tract footprint, spatial
   form, and apparent coherence.
4. Use **Method stage** to compare how many candidate zones and forms the
   strict/bounded no-POI baselines, DBSCAN challenger, and physical/place
   result produce.
5. Open the diagnostic trace only when a candidate boundary is questionable.
   A bridge requires its own trace record; a POI-only decision is a defect.
6. Use the Jacksonville–Richmond table only for the same selected parameter
   profile. A difference is review evidence, not permission to tune one market.
7. Download membership or edge evidence only when sharing a review finding.
   Report a questionable result as a method or parameter issue; do not edit
   tract membership.

The six completed runs and their initial like-for-like counts are recorded in
[the calibration and portability review](CALIBRATION_AND_PORTABILITY_REVIEW.md).
That document also names the decision required after notebook review.

## Ownership

- The Intelligence Framework owns Phase 7 tract assignments and structural
  fields.
- Geography owns boundaries, tract geometry, vintages, and spatial-operation
  conventions.
- POI and Infrastructure own source-faithful records, mappings, geometry, and
  provenance.
- Corridor Intelligence owns how those governed inputs contribute to tract
  relationships, bridge membership, candidate form, systematic
  IDs, and grouping QA.
- Internal Structure consumes and explores the results in one section without
  using them as the master description of the market or rewriting them.
- Opportunity analyses and issues own selection, scoring, editorial names,
  narrative, and publication decisions.

## First validation markets

Jacksonville, FL (`27260`) is the calibration market because it is the planned
Act 4 debut and has an existing parcel follow-through path. Richmond, VA
(`40060`) is the second-market validation and tests whether the same method
survives a 17-county metro with more urban-to-rural variation.

Neither market receives hand-edited membership. Any retained override must be
explicit, versioned, and justified.

## Prototype preservation

Preserve the inputs, code, and Jacksonville/Richmond run artifacts for later
method reference. Do not promote these artifacts to `foundations/`, materialize
them as a canonical mart, or add a consumer until a future decision reopens
the engine with a stable use case.
