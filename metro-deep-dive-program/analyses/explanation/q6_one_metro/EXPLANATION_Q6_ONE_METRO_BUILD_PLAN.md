# Explanation Q6 — One Metro? Build Plan

**Status:** Complete. The Q6 workbench provides the Place hierarchy,
materiality-sensitive anchor read, and separately labeled OD, POI, and
Infrastructure relationship context.

**Depends on Q2 (E3)** for its reviewed physical-proximity surface and on
Geography for Census Place relationships. OD, POI, and Infrastructure become
relationship evidence as their Place-grain interfaces are available.

## How this plan works

**All epics are complete.** The workbench is ready for analyst/issue review;
its result remains explicit about materiality sensitivity rather than forcing a
single anchor conclusion.

**Geometry foundation:** Geography now publishes national 2024
`geo.places_analysis` for direct point assignment and line/polygon overlap.
This unblocks the spatial boundary dependency. POI now publishes direct point
assignments and Infrastructure publishes retained-feature overlap evidence.

## Epic 1 — Audit Flow Data and Center Inputs

- [x] Confirm that OMB 2023 Central/Outlying county status already exists in
  `silver.xwalk_cbsa_county`; Q6 reports it rather than recreating it.
- [x] Scope the next OD extension—Place-to-Place flows—as shared Foundations
  work in `LODES_OD_INGEST_AGENT_SCOPE.md`.
- [x] Materialize the national available-state county-home to county-work LODES
  OD surface with coverage metadata; it is county context, not an anchor rule.
- [x] Confirm 2023 LODES WAC/RAC grain and availability for structural context.
- [x] Confirm 2023 OMB CBSA-county membership and its existing provider flag.
- [x] Select Census Places as the candidate anchor-city unit; use Place
  allocation/relationship evidence rather than display geometry.
- [x] Record Q2's adopted V0 as physical proximity, not access.
- [x] Confirm that Regional Role has a reusable contract but no completed
  output surface; Q6 does not wait on it.
- [x] Confirm that Census Place hierarchy and anchor-city analysis are Q6's
  primary build; OD is a later Place-relationship input, not a county-status
  gate.

**Done when:** the Place hierarchy is separated from sourced county context,
and each later relationship layer has a named interface dependency.

Findings are recorded in `EXPLANATION_Q6_AUDIT.md`.

## Epic 2 — Build the Census Place Hierarchy

- [x] Build the OMB county-status context table.
- [x] Build Census Place profile and ranking views for population, income,
  housing, and allocated workplace-job context.
- [x] State direct-versus-allocated provenance beside every Place metric.
- [x] Build the employment-center context and Place association view.
- [x] Implement notebook sections 1–4 of the visual contract: orientation,
  coverage, complete Place hierarchy, and Place-role comparison.

**Completed implementation:** named read-only queries in `sql/` load the
profile, county context, allocation provenance, and Q2 Place-component context;
`EXPLANATION_Q6_NOTEBOOK.py` is the read-only workbench.

**Done when:** an analyst can compare every covered Place without confusing
administrative Place identity, allocated measures, and functional relationships.

## Epic 3 — Build the Anchor-City Read

- [x] Start with the full covered Census Place inventory, not only title-named
  or principal cities.
- [x] Associate Census Place candidates with Q2 reviewed job-center components
  using a declared Geography relationship or allocation rule.
- [x] Build the candidate anchor-city inventory with Place-profile and
  physical-proximity evidence.
- [x] Apply the anchor-classification matrix and center-version sensitivity.
- [x] Implement the orientation map, candidate-evidence table, decision matrix,
  and candidate-findings handoff defined in notebook sections 5, 6, and 8.
- [x] Keep POI and Infrastructure evidence out of the anchor decision; use
  their direct Place-grain interfaces only as separately labeled context.

**Completed implementation:** component association is the largest
population-weighted allocation of a reviewed Q2 center component's tract jobs.
The candidate inventory retains every Place; the provisional 5,000-resident and
1%-of-CBSA materiality rule and all three Q2 distance versions are visible for
Epic 5 review. Richmond returns `mixed`: three initial candidates have distinct
reviewed components, but the higher materiality sensitivity leaves one. This is
not a composite score.

**Done when:** the polycentricity question has a Place-based, reviewable
classification grounded in Q2 physical proximity, with sensitivity visible.

## Epic 4 — Add Place Relationship Evidence

- [x] Specify and publish a Place-to-Place OD relationship surface from the
  block-native source/crosswalk path; the current county OD table cannot be
  disaggregated to Places.
- [x] Add direct POI-to-Place context from `mart_poi.poi_geography_assignment`;
  it is a direct point assignment and retains `no_census_place` separately.
- [x] Add Infrastructure-to-Place physical context from the retained-feature
  overlap interface; keep line length and surface area separate and do not use
  either as an anchor score, barrier finding, or access measure.
- [x] Test whether these layers corroborate or complicate the anchor read.
- [x] Use an OD matrix or ranked connection table before any flow map, and keep
  relationship layers separate from the anchor decision table.

**Completed implementation:** Q6 reads directional `JT00` Place OD links from
`silver.lehd_lodes_od_place`, retaining endpoint status and source coverage;
`JT02` remains separate because it is a subset. The workbench also reads direct
POI assignments and retained-feature Infrastructure overlap summaries. The
three layers are context only and never enter the anchor decision matrix.

**Done when:** relationship layers deepen the Place analysis without becoming a
hidden composite anchor score.

## Epic 5 — Review

- [x] Test on a metro known to be polycentric and one known to be monocentric.
- [x] Report findings about Q2 physical-proximity evidence back to Q2.
- [x] Record what the A5 "How many downtowns?" theme can reuse.

**Completed review:** [EXPLANATION_Q6_EPIC5_REVIEW.md](EXPLANATION_Q6_EPIC5_REVIEW.md)
tests Richmond (`mixed` under materiality sensitivity) and Harrisonburg (`one
supported anchor` across the tested rules), records Q2's physical-proximity
lesson, and bounds A5 reuse to transparent candidate/component evidence.

**Done when:** the method distinguishes real cases and its reusable parts are
documented.

## What not to do

- do not derive a competing county Central/Outlying classification
- do not use an allocated metric as if it were a direct Census Place estimate
- do not call physical proximity access, travel time, or a 15-minute result
