# Explanation Q3 — Where Growth Lands Build Plan

**Status:** Epic 1 not started

**Depends on Q2 (E3)** for the access method, and on its own harmonization
slice, which is the larger dependency.

## How this plan works

**Epic 1 is an audit, and it comes first.** Epics 2–5 are written from
expectation rather than evidence and should be rewritten once the audit reports.

## Epic 1 — Audit Harmonization and Growth Inputs

- [ ] Audit the temporal crosswalk: which vintages it covers, its weight basis,
  its change types, and its quality flags.
- [ ] Determine whether the existing crosswalk is sufficient for restating
  population and housing counts, or whether Q3 must build its own harmonization.
- [ ] Confirm tract population and housing-unit field coverage across the full
  comparison window.
- [ ] Confirm the permit coverage pattern by grain; record plainly that tract
  permits do not exist if that holds.
- [ ] Identify which fields best express prior density and built condition.
- [ ] Read Q2's access definition and record what Q3 will adopt and what it must
  vary.
- [ ] State plainly whether harmonization is a solved problem here or a genuine
  build.

**Done when:** we know whether harmonization is reuse or construction, and the
classification inputs are confirmed. The spec is rewritten against those
findings.

Record the audit in `EXPLANATION_Q3_AUDIT.md`.

## Epic 2 — Harmonize the Tract Panel

*Provisional. Rewrite after Epic 1.*

- [ ] Declare the target tract vintage and comparison years.
- [ ] Restate population and housing-unit counts onto that vintage.
- [ ] Produce harmonization QA showing allocation error and low-confidence
  tracts.
- [ ] Decide how to treat tracts that cannot be harmonized cleanly.

**Done when:** a comparable tract panel exists and its error is visible rather
than assumed away.

## Epic 3 — Define Infill and Greenfield

*Provisional. Rewrite after Epic 1.*

- [ ] Define the developed-footprint baseline as a measured condition.
- [ ] Define infill, greenfield, and outer-center rules.
- [ ] Define the growth floor and the negative/no-growth classes.
- [ ] Test the rules against tracts with known character in one market.

**Done when:** the classes are measured, reproducible, and survive a manual
sanity check.

## Epic 4 — Build the Classification and Read It Against Access

*Provisional. Rewrite after Epic 1.*

- [ ] Build the national growth-location distribution.
- [ ] Build the CBSA summary and selected-market classification map.
- [ ] Build the population-versus-unit change table.
- [ ] Read growth against Q2's access surfaces: new 15-minute areas, and whether
  growth lands inside or outside them.
- [ ] Add permit context at its own grain, clearly labeled.

**Done when:** the classification is inspectable and the access relationship is
visible.

## Epic 5 — Review

*Provisional. Rewrite after Epic 1.*

- [ ] Test sensitivity to the growth floor and footprint baseline.
- [ ] Confirm the residual group is small and explicable.
- [ ] Report findings about the shared access method back to Q2.
- [ ] Decide what the harmonization work should become for other analyses.

**Done when:** the method is stable and the harmonization asset's future is
decided.

## What not to do

- do not assign county or Place permits to tracts
- do not infer infill or greenfield from map appearance
- do not bury harmonization error
- do not silently diverge from Q2's access definition
