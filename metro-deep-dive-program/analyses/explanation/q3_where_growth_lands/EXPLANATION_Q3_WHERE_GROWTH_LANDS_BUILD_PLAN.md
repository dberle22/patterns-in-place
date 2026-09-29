# Explanation Q3 — Where Growth Lands Build Plan

**Status:** Epic 1 complete — Q3 method and output structure aligned

**Depends on** its own tract-harmonization slice and a Geography-owned
Place-to-CBSA membership interface. Q2's reviewed job-center physical-proximity
surface is an optional explanatory input; it is not an access dependency.

## How this plan works

**Epic 1 is complete.** The remaining epics implement the aligned growth-location
method below. The only later publication decision is whether short-horizon tract
signals need a Q3-scoped ACS-MOE check; it does not block the core method.

## Locked Q3 frame

- **Question:** Where are population and housing-unit gains or losses landing
  within a metro?
- **Primary evidence:** a 2020-vintage harmonized tract panel, summarized at
  county and governed Census Place lenses.
- **End year and horizons:** use the latest covered ACS release (currently
  2024) against 2023, 2021, 2019, and 2014 for 1-, 3-, 5-, and 10-year change.
  The 2019 and 2014 tract endpoints are restated to 2020 tracts; the 2021 and
  2023 endpoints are already on that tract vintage.
- **Interpretation:** 5- and 10-year change establish the core growth pattern;
  1- and 3-year comparisons are descriptive watchlist signals because ACS
  5-year releases overlap.
- **Non-goal:** Q3 does not classify tracts as infill or greenfield. Those may
  become issue-layer interpretations after the evidence is read.

## Notebook flow and visual contract

The notebook is a market-first research instrument. It uses one selected CBSA,
one selected horizon, and a population/housing-unit measure selector; the
default read is 10-year housing-unit change, with the 5-year view beside it.
The national run is a coverage and calibration check, not a metro ranking.

| Sequence | Notebook section | Required output | Visual / use |
|---|---|---|---|
| 1 | Method and coverage | Source vintages, selected horizon, target tract vintage, crosswalk quality, Q2/permit availability, and excluded units | Compact method/coverage table. It is the evidence boundary before any claim. |
| 2 | Metro change at a glance | Metro-level population and housing-unit change for all four horizons | Paired horizon comparison chart of annualized change, with 1- and 3-year values visually labeled as watchlist signals. This is the acceleration/deceleration read, not a tract claim. |
| 3 | Where the change lands | Harmonized tract contribution and rate fields for the selected horizon | Two aligned tract choropleths: population change and housing-unit change. Map absolute contribution by default; expose rate as a separate inspection layer so small-base percentages do not dominate. |
| 4 | How concentrated growth is | The share of positive metro change captured by the largest-growing tracts and the tract count needed to reach 50% and 80% | Cumulative concentration curve. It distinguishes dispersed growth from a small number of landing areas without inventing infill/greenfield classes. |
| 5 | County pattern | Exact county-to-CBSA population and housing-unit change | Ranked paired horizontal bars, showing absolute contribution and rate in separate views. County totals may reconcile to the CBSA ledger. |
| 6 | Census Place pattern | Direct Place population and housing-unit changes plus governed Place-to-CBSA membership flags | Ranked Place table/bar chart with whole/split/primary-association labels. It is a named-location lens, not a stack that must sum to metro change; unincorporated geography remains outside it. |
| 7 | Explanatory context | Native-grain permits and, where available, Q2 physical distance to job centers | County/Place permit context beside matching native-grain growth; optional tract scatter or binned curve of growth versus physical job-center distance. These are contextual associations, not tract permits, causation, travel, or access. |
| 8 | Finding candidates and QA | Plain-language signal status, residuals, sensitivity outcomes, and candidate claims | Compact finding table. This is the handoff to an Issue, where an infill/greenfield interpretation may be considered. |

The tract map is the primary spatial visual. County display geometry may support
an optional companion map. Place geometry is not a Q3 requirement: until a
governed Place display-geometry consumer exists, the Place lens is deliberately
a labeled table/bar chart rather than an ungoverned map.

## Epic 1 — Audit Harmonization and Growth Inputs

- [x] Audit the temporal crosswalk: which vintages it covers, its weight basis,
  its change types, and its quality flags.
- [x] Determine whether the existing crosswalk is sufficient for restating
  population and housing counts, or whether Q3 must build its own harmonization.
- [x] Confirm tract population and housing-unit field coverage across the full
  comparison window.
- [x] Confirm the permit coverage pattern by grain; record plainly that tract
  permits do not exist if that holds.
- [x] Identify which fields best express prior density and built condition.
- [x] Read Q2's access definition and record what Q3 will adopt and what it must
  vary.
- [x] State plainly whether harmonization is a solved problem here or a genuine
  build.

**Done when:** we know whether harmonization is reuse or construction and the
growth-location input contract is confirmed.

Audit findings are recorded in `EXPLANATION_Q3_AUDIT.md`.

## Geography dependency — Build Place-to-CBSA membership

This is a Geography-engine epic, not Q3 notebook logic. Census Places are not
an exact administrative child of a CBSA: a Place can span counties and CBSA
boundaries, while unincorporated metro growth has no Place row. The engine must
publish a typed, inspectable relationship before Q3 uses Places as a metro lens.

- [x] Build a 2020-vintage `Place × CBSA` relationship from governed block
  membership, current county-to-CBSA membership, and the existing block-level
  population, housing-unit, and land-area numerators.
- [x] Publish one row per Place, CBSA, and explicit weight basis with source and
  target denominators, Place share in the CBSA, CBSA share in the Place,
  coverage/quality flags, and boundary vintages.
- [x] Publish a declared primary-CBSA association for each Place, determined
  from the largest 2020 population share, while retaining all split memberships
  rather than treating the primary association as exact containment.
- [x] Document how direct Place measures may be used: whole-Place values are
  valid for wholly associated Places; split-Place measures require an explicit
  allocation method or a whole-Place caveat.
- [x] Add national structural checks and Richmond/one split-Place smoke tests.
- [x] Publish the companion 2020-vintage `Place × County` weighted-membership
  relationship on the same explicit population, housing-unit, and land-area
  bases. It is likewise not exact containment.

**Done when:** Q3 can select all Places associated with a CBSA, distinguish
wholly associated from split Places, retain unincorporated geography outside the
Place lens, and never represent the relationship as exact containment.

## Epic 2 — Harmonize the tract panel and calculate growth horizons

- [x] Build the 2020-vintage panel for 2014, 2019, 2021, 2023, and 2024;
  apply `population` weights only to population and `housing_units` weights
  only to housing-unit counts.
- [x] Restate 2014 and 2019 source tracts through `silver.xwalk_temporal` and
  retain their source ID, target ID, weight, `change_type`, and `quality_flag`.
- [x] Join 2021, 2023, and 2024 rows directly on the 2020 tract identity.
- [x] Produce harmonization QA showing allocation error and low-confidence
  tracts.
- [x] Retain tracts that cannot be harmonized cleanly as explicit
  `insufficient_confidence_or_coverage` results rather than excluding them.
- [x] Calculate 1-, 3-, 5-, and 10-year population and housing-unit change;
  label 1- and 3-year ACS 5-year-release comparisons as descriptive signals,
  not independent annual growth estimates.
- [x] Define the initial reliability posture: 5- and 10-year results are the
  interpretive core; short-horizon results remain watchlist evidence pending a
  Q3-scoped MOE review.

**Done when:** a comparable tract panel exists and its error is visible rather
than assumed away, with all four horizons labeled for their evidentiary role.

## Epic 3 — Locate and summarize growth

- [x] Build the metro growth ledger for population and housing units, by each
  declared horizon.
- [x] Build harmonized tract, county, and governed Place location lenses;
  retain unincorporated and split/ambiguous Place geography explicitly.
- [x] Define growth, decline, no-material-change, and insufficient-confidence
  statuses without forcing an infill/greenfield label.
- [x] Identify concentration, dispersion, outlying-county, and named-Place
  patterns from the observed growth evidence.

**Done when:** the location of growth is measured reproducibly at its native
grain and does not depend on a site-development classification.

## Epic 4 — Build the growth-location read

- [x] Build the national growth-location coverage/distribution for method
  calibration, not as a metro ranking.
- [x] Build the selected-market horizon comparison, aligned tract maps,
  concentration curve, county bars, and Place ranked lens specified above.
- [x] Build the population-versus-housing-unit comparison and a concentration
  versus dispersion read from the tract evidence.
- [ ] Optionally read growth against Q2's physical job-center proximity surface,
  preserving its distance-only label.
- [x] Add permit context at its own grain, clearly labeled.

**Done when:** the growth geography is inspectable across tracts, counties, and
Places; permit and job-proximity context remain separate explanatory lenses.

## Epic 5 — Review and handoff

- [ ] Test sensitivity to material-growth statuses and the selected horizons.
- [ ] Confirm residual, unincorporated, and split-Place groups are visible and
  explicable.
- [ ] Decide whether the observed patterns support an issue-layer
  infill/greenfield interpretation; do not promote it into the Q3 method.
- [ ] Determine whether a Q3-scoped ACS MOE check is needed before publishing
  short-horizon tract findings.
- [ ] Decide what the harmonization work should become for other analyses.

**Done when:** the outputs are sensitivity-reviewed, their publication limits
are explicit, and the reusable harmonization lessons are handed back to
Geography.

## What not to do

- do not assign county or Place permits to tracts
- do not make infill or greenfield a Q3 classification
- do not bury harmonization error
- do not call Q2 physical proximity access or travel time
