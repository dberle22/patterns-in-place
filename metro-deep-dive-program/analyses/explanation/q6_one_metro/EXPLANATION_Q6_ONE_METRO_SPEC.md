# Explanation Q6 — One Metro? Spec

**Status:** V1 contract aligned after Epic 1 audit; implementation not started

**Build order:** E7 — applies Q2's physical-proximity method to Census Place
anchor candidates

**Primary surface:** `EXPLANATION_Q6_NOTEBOOK.py` (not yet written)

**Default market:** Richmond, VA (`40060`)

**Initial method:** `q6_one_metro_v1`

**Dependencies:** LODES WAC/RAC, Q2's reviewed job-center/proximity surface,
and Geography's Census Place relationships. LODES OD is required for the
county-integration half.

## How to read this spec

**Epic 1 is complete.** This V1 contract reflects its findings. Later epics may
refine thresholds after market review, but must retain the audit's evidence and
method boundaries.

## Goal

Identify the Census Places that anchor a CBSA, describe the distinct roles its
Places play, and determine whether the market has one anchor or several.

## Primary question and sourced context

The primary question is: **Which Census Places anchor this CBSA, and how do the
other Places relate to those anchors?**

The OMB 2023 CBSA-to-county crosswalk already classifies each member county as
Central or Outlying. Q6 reports that official designation as county context; it
does not reconstruct or challenge the federal metro delineation. OD flows may
later describe Place relationships, but they are not a gate for reporting the
official county status.

## How the second question is answered

Start with every governed Census Place in the CBSA and build a comparable Place
profile: population, income, housing, allocated workplace-job context, and
relative scale within the metro. Associate candidate anchors with Q2's reviewed
job-center components. Q6 adopts Q2's V0 centroid-to-centroid Haversine distance
unchanged: it is physical proximity, not access, travel time, commuting
behavior, or a 15-minute-city measure.

OD flows, infrastructure, and POIs explain relationships and daily activity
after their Place-grain interfaces are available. They are evidence layers, not
a substitute for the Place hierarchy.

This makes Q6 a further test of the shared physical-proximity spine, against a
Place-based center construction.

## National posture: national method, local application

Prototype one consistent Place-hierarchy method nationally, then explain the
selected market locally.

## Preliminary read of what exists

**Confirmed by Epic 1.**

| Observation | Why it matters | What Epic 1 must settle |
|---|---|---|
| Official county status | `silver.xwalk_cbsa_county` is an OMB 2023 crosswalk with `county_flag` | Report Central/Outlying as sourced context; do not derive a competing classification |
| Census Place profile | `gold.population_demographics` has direct 2024 Place rows; Geography has Place identity and tract-to-Place allocation edges | Build a Place hierarchy from named, comparable Place measures; label allocated measures |
| Census Place identity and tract-to-Place allocation edges exist | Places can be the anchor-city unit without treating a tract as a city | Record the reviewed Place-to-component association rule |
| Q2 publishes 2023 WAC candidate, cluster, and proximity surfaces | The anchor-city half can adopt physical proximity now | Retain the Q2 center-version sensitivity; do not call it access |

The Place hierarchy and anchor-city analysis are buildable now from governed
Place and Q2 surfaces. OD is a later relationship input, not a county-status
gate. Direct POI-to-Place and Infrastructure-to-Place interfaces remain
dependencies rather than candidates for approximation.

## Inputs

| Input | Role |
|---|---|
| Regional Role source and interpretation contract | Regional context; no completed output surface is required for V1 |
| Direct ACS Place measures | Population, income, housing, and other Place profile measures |
| Tract LODES WAC/RAC with Place allocation edges | Allocated workplace-job context, labeled as such |
| Q2 reviewed job-center and physical-proximity surface | Supporting evidence for the anchor-city read |
| Census Place identity and tract-to-Place allocation edges | Candidate-anchor inventory and component association |
| OD flows | Later Place-to-Place work relationship evidence |
| Direct POI-to-Place and Infrastructure-to-Place interfaces | Later activity and connection context; not yet published |
| Phase 7 / Internal Structure context | Polycentric form description |

## V0 method

Report the OMB 2023 Central/Outlying county designation as context. Rank and
profile every covered Census Place within the selected CBSA using separately
labeled levels and shares, not a composite score. Candidate anchors are then
reviewed against population and income context, allocated workplace-job evidence,
and association with distinct Q2 job-center components.

Treat OD flows, infrastructure, and POIs as relationship evidence: OD can show
Place-to-Place work connections; infrastructure can describe connection and
barrier context; POIs can describe activity concentration once direct
point-to-Place assignment exists. None determines anchor status alone.

## Minimum outputs

OMB county-status context table; Census Place hierarchy and profile table;
Place ranking views for population, income, housing, and allocated workplace
jobs; employment-center map; candidate-anchor inventory with physical-proximity
evidence; Place relationship views as OD, infrastructure, and POI interfaces
become available; and an anchor result (`one supported anchor`, `multiple
supported anchors`, `mixed`, or `insufficient structure evidence`).

## Guardrails

- do not infer Place commuting relationships from WAC/RAC without OD
- do not turn the OMB county designation into a Q6-derived score
- do not describe Q2 physical proximity as access or a 15-minute measure

## Open decisions

- minimum materiality rule for entering the Census Place candidate inventory
- Place metric contract, including which measures are direct versus allocated
- OD Place-to-Place flow contract and coverage treatment
- direct POI-to-Place and Infrastructure-to-Place interfaces

## References

- Section 5.2 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md](EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md)
- [Epic 1 audit](EXPLANATION_Q6_AUDIT.md)
