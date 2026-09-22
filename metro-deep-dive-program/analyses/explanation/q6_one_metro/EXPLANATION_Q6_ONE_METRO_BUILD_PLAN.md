# Explanation Q6 — One Metro? Build Plan

**Status:** Epic 1 audit complete; Census Place hierarchy is the primary build

**Depends on Q2 (E3)** for its reviewed physical-proximity surface and on
Geography for Census Place relationships. OD, POI, and Infrastructure become
relationship evidence as their Place-grain interfaces are available.

## How this plan works

**Epic 1 is an audit, and it comes first.** Epics 2–5 are written from
expectation rather than evidence and should be rewritten once the audit reports.

## Epic 1 — Audit Flow Data and Center Inputs

- [x] Confirm that OMB 2023 Central/Outlying county status already exists in
  `silver.xwalk_cbsa_county`; Q6 reports it rather than recreating it.
- [x] Scope OD ingestion as shared Foundations work in
  `LODES_OD_INGEST_AGENT_SCOPE.md`.
- [x] Materialize the national available-state county-home to county-work LODES
  OD surface with coverage metadata; Q6 remains responsible for its own
  classification rule.
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

*Provisional. Rewrite after Epic 1.*

- [ ] Build the OMB county-status context table.
- [ ] Build Census Place profile and ranking views for population, income,
  housing, and allocated workplace-job context.
- [ ] State direct-versus-allocated provenance beside every Place metric.
- [ ] Build the employment-center context and Place association view.

**Done when:** an analyst can compare every covered Place without confusing
administrative Place identity, allocated measures, and functional relationships.

## Epic 3 — Build the Anchor-City Read

*Provisional. Rewrite after Epic 1.*

- [ ] Start with the full covered Census Place inventory, not only title-named
  or principal cities.
- [ ] Associate Census Place candidates with Q2 reviewed job-center components
  using a declared Geography relationship or allocation rule.
- [ ] Build the candidate anchor-city inventory with Place-profile and
  physical-proximity evidence.
- [ ] Apply the anchor-classification matrix and center-version sensitivity.
- [ ] Add amenity clusters only when Q4 supplies them as corroboration.

**Done when:** the polycentricity question has a Place-based, reviewable
classification grounded in Q2 physical proximity, with sensitivity visible.

## Epic 4 — Add Place Relationship Evidence

*Provisional. Expand as Place-grain interfaces become available.*

- [ ] Build Place-to-Place OD relationship views when the shared OD contract is
  available, retaining cross-CBSA flows and coverage context.
- [ ] Add direct POI-to-Place and Infrastructure-to-Place context when
  Geography publishes those interfaces.
- [ ] Test whether these layers corroborate or complicate the anchor read.

**Done when:** relationship layers deepen the Place analysis without becoming a
hidden composite anchor score.

## Epic 5 — Review

*Provisional. Rewrite after Epic 1.*

- [ ] Test on a metro known to be polycentric and one known to be monocentric.
- [ ] Report findings about Q2 physical-proximity evidence back to Q2.
- [ ] Record what the A5 "How many downtowns?" theme can reuse.

**Done when:** the method distinguishes real cases and its reusable parts are
documented.

## What not to do

- do not derive a competing county Central/Outlying classification
- do not use an allocated metric as if it were a direct Census Place estimate
- do not call physical proximity access, travel time, or a 15-minute result
