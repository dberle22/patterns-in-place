# Explanation Q6 — One Metro? Spec

**Status:** Complete; OD, POI, and Infrastructure Place-grain relationship
context is available as separately labeled evidence.

**Build order:** E7 — applies Q2's physical-proximity method to Census Place
anchor candidates

**Primary surface:** `EXPLANATION_Q6_NOTEBOOK.py`

**Default market:** Richmond, VA (`40060`)

**Initial method:** `q6_one_metro_v1`

**Dependencies:** LODES WAC/RAC, Q2's reviewed job-center/proximity surface,
and Geography's Census Place relationships. LODES OD is required for the
county-integration half.

## How to read this spec

**The build is complete.** This V1 contract retains the audit's evidence and
method boundaries; the Epic 5 review records its materiality sensitivity.

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
gate. Infrastructure physical context is available through its governed
Place-overlap interface; POI activity context is available from direct point
assignment, not a tract allocation or address-city approximation.

## Inputs

| Input | Role |
|---|---|
| Regional Role source and interpretation contract | Regional context; no completed output surface is required for V1 |
| Direct ACS Place measures | Population, income, housing, and other Place profile measures |
| Tract LODES WAC/RAC with Place allocation edges | Allocated workplace-job context, labeled as such |
| Q2 reviewed job-center and physical-proximity surface | Supporting evidence for the anchor-city read |
| Census Place identity and tract-to-Place allocation edges | Candidate-anchor inventory and component association |
| `geo.places_analysis` | Governed 2024 Place boundary for direct POI point assignment and Infrastructure line/polygon overlap; not a substitute for those engines' published relationship surfaces |
| `silver.lehd_lodes_od_place` and coverage | Directional Place-to-Place work relationship evidence; endpoint statuses and provider coverage are required context |
| Infrastructure-to-Place overlap interface | Published physical context for retained line and polygon features; line length and surface area remain separate and do not establish access, barriers, or anchor status |
| Direct POI-to-Place interface | Published activity context from direct retained-point assignment; `no_census_place` remains a valid coverage outcome |
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

## Notebook flow and visual contract

`EXPLANATION_Q6_NOTEBOOK.py` will be a read-only analyst workbench, not an
issue-ready story or a composite ranking tool. It proceeds from complete Place
coverage to candidate-anchor evidence, so no chart can quietly promote a Place
before its source coverage and metric provenance are visible.

1. **Orientation and controls:** state the selected CBSA, source vintages,
   Q2 center version, and what is direct, allocated, or unavailable. Controls
   select a market and reviewed Q2 sensitivity version; they do not tune an
   anchor result to a preferred market.
2. **Coverage and county context:** show Place coverage, metric availability,
   allocation quality, and the sourced OMB Central/Outlying county designation.
   This separates missing evidence from a zero and county context from a Place
   role.
3. **Complete Place hierarchy:** show every covered Place in a sortable profile
   table and aligned ranked views for population, income, housing, and allocated
   workplace jobs. These show scale and role dimensions separately, not a
   summed score.
4. **Place-role comparison:** show a population-versus-allocated-jobs scatter
   with direct income in the tooltip or a companion view. It identifies
   residential, workplace-oriented, and mixed candidates for review; it does
   not itself designate an anchor.
5. **Spatial anchor context:** show an orientation map of Census Place display
   boundaries, Q2 job-center components, and candidate Places. The map explains
   the reviewed Place-to-component association; display geometry is never used
   to calculate it.
6. **Anchor decision:** show a candidate-evidence table and the classification
   matrix side by side. The table records Place profile measures, associated Q2
   component, center-version sensitivity, and decision rationale before stating
   `one supported anchor`, `multiple supported anchors`, `mixed`, or
   `insufficient structure evidence`.
7. **Relationship evidence, when available:** add a Place-to-Place OD matrix or
   ranked connection table before any flow map, then direct POI-to-Place and
   Infrastructure-to-Place context. These explain or challenge the anchor
   result; they never replace it.
8. **Handoff:** end with a small candidate-findings table that names the result,
   its evidence, material caveats, and the figures/tables available for issue
   review.

| Visual | Decision use | Interpretation boundary |
|---|---|---|
| Coverage/provenance panel | Determines whether a Place can enter comparison | Missing and allocated values are not zeros or direct estimates. |
| Place profile table and ranked bars | Establishes each Place's scale across distinct measures | Rankings remain metric-specific; no composite Place score. |
| Population × allocated-jobs scatter | Identifies contrasting Place roles for review | It is descriptive and does not establish functional integration or anchor status. |
| Place/component orientation map | Makes the reviewed spatial association inspectable | Display boundaries are not analytical membership geometry. |
| Candidate-evidence table and decision matrix | Produces the anchor classification | Q2 Haversine distance is physical proximity, not access or travel time. |
| OD matrix/ranked links and later context layers | Explains relationships after their inputs are governed | Flow, POI, or infrastructure evidence alone cannot determine an anchor. |

## Guardrails

- do not infer Place commuting relationships from WAC/RAC without OD
- do not turn the OMB county designation into a Q6-derived score
- do not describe Q2 physical proximity as access or a 15-minute measure
- do not use final issue styling or narrative selection to conceal an ambiguous
  anchor result

## Open decisions

- minimum materiality rule for entering the Census Place candidate inventory
- Place metric contract, including which measures are direct versus allocated
- OD Place-to-Place flow contract and coverage treatment

## References

- Section 5.2 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md](EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md)
- [Epic 1 audit](EXPLANATION_Q6_AUDIT.md)
