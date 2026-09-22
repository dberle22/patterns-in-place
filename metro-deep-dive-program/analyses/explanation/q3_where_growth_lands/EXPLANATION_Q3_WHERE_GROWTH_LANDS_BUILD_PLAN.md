# Explanation Q3 — Where Growth Lands Build Plan

**Status:** Epic 1 complete — pending method alignment before Epic 2

**Depends on** its own tract-harmonization slice and a Geography-owned
Place-to-CBSA membership interface. Q2's reviewed job-center physical-proximity
surface is an optional explanatory input; it is not an access dependency.

## How this plan works

**Epic 1 is an audit, and it comes first.** Epics 2–5 are written from
expectation rather than evidence and should be rewritten once the audit reports.

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

**Done when:** we know whether harmonization is reuse or construction, and the
classification inputs are confirmed. The spec is rewritten against those
findings.

Audit findings are recorded in `EXPLANATION_Q3_AUDIT.md`. The later epics remain
provisional until the growth-location output structure is aligned.

## Geography dependency — Build Place-to-CBSA membership

This is a Geography-engine epic, not Q3 notebook logic. Census Places are not
an exact administrative child of a CBSA: a Place can span counties and CBSA
boundaries, while unincorporated metro growth has no Place row. The engine must
publish a typed, inspectable relationship before Q3 uses Places as a metro lens.

- [ ] Build a 2020-vintage `Place × CBSA` relationship from governed block
  membership, current county-to-CBSA membership, and the existing block-level
  population, housing-unit, and land-area numerators.
- [ ] Publish one row per Place, CBSA, and explicit weight basis with source and
  target denominators, Place share in the CBSA, CBSA share in the Place,
  coverage/quality flags, and boundary vintages.
- [ ] Publish a declared primary-CBSA association for each Place, determined
  from the largest 2020 population share, while retaining all split memberships
  rather than treating the primary association as exact containment.
- [ ] Document how direct Place measures may be used: whole-Place values are
  valid for wholly associated Places; split-Place measures require an explicit
  allocation method or a whole-Place caveat.
- [ ] Add national structural checks and Richmond/one split-Place smoke tests.

**Done when:** Q3 can select all Places associated with a CBSA, distinguish
wholly associated from split Places, retain unincorporated geography outside the
Place lens, and never represent the relationship as exact containment.

## Epic 2 — Harmonize the tract panel and declare growth horizons

*Provisional. Rewrite after Epic 1.*

- [ ] Declare the target tract vintage and comparison years.
- [ ] Restate population and housing-unit counts onto that vintage.
- [ ] Produce harmonization QA showing allocation error and low-confidence
  tracts.
- [ ] Decide how to treat tracts that cannot be harmonized cleanly.
- [ ] Calculate 1-, 3-, 5-, and 10-year population and housing-unit change;
  label 1- and 3-year ACS 5-year-release comparisons as descriptive signals,
  not independent annual growth estimates.
- [ ] Define the initial reliability posture: 5- and 10-year results are the
  interpretive core; short-horizon results remain watchlist evidence pending a
  Q3-scoped MOE review.

**Done when:** a comparable tract panel exists and its error is visible rather
than assumed away, with all four horizons labeled for their evidentiary role.

## Epic 3 — Locate and summarize growth

*Provisional. Rewrite after Epic 1.*

- [ ] Build the metro growth ledger for population and housing units, by each
  declared horizon.
- [ ] Build harmonized tract, county, and governed Place location lenses;
  retain unincorporated and split/ambiguous Place geography explicitly.
- [ ] Define growth, decline, no-material-change, and insufficient-confidence
  statuses without forcing an infill/greenfield label.
- [ ] Identify concentration, dispersion, outlying-county, and named-Place
  patterns from the observed growth evidence.

**Done when:** the location of growth is measured reproducibly at its native
grain and does not depend on a site-development classification.

## Epic 4 — Build the growth-location read

*Provisional. Rewrite after Epic 1.*

- [ ] Build the national growth-location coverage/distribution for method
  calibration, not as a metro ranking.
- [ ] Build the CBSA summary, selected-market tract map, county table, and
  Place table for all four horizons.
- [ ] Build the population-versus-housing-unit change table and a concentration
  versus dispersion read.
- [ ] Optionally read growth against Q2's physical job-center proximity surface,
  preserving its distance-only label.
- [ ] Add permit context at its own grain, clearly labeled.

**Done when:** the growth geography is inspectable across tracts, counties, and
Places; permit and job-proximity context remain separate explanatory lenses.

## Epic 5 — Review

*Provisional. Rewrite after Epic 1.*

- [ ] Test sensitivity to material-growth statuses and the selected horizons.
- [ ] Confirm residual, unincorporated, and split-Place groups are visible and
  explicable.
- [ ] Decide whether the observed patterns support an issue-layer
  infill/greenfield interpretation; do not promote it into the Q3 method.
- [ ] Determine whether a Q3-scoped ACS MOE check is needed before publishing
  short-horizon tract findings.
- [ ] Decide what the harmonization work should become for other analyses.

**Done when:** the method is stable and the harmonization asset's future is
decided.

## What not to do

- do not assign county or Place permits to tracts
- do not make infill or greenfield a Q3 classification
- do not bury harmonization error
- do not call Q2 physical proximity access or travel time
