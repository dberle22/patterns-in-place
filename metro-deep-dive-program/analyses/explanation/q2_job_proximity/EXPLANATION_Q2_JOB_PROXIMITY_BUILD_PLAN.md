# Explanation Q2 — Job Proximity Build Plan

**Status:** Epic 1 complete; V0 method definition is next

**This build gates Q3, Q4, and Q6.** Epic 2's output is consumed by three other
analyses, so it deserves more care than a first notebook usually gets.

## How this plan works

**Epic 1 is an audit, and it comes first.** Its evidence narrows the immediate
build to a Richmond-first physical-proximity V0. The shared access method,
affordability match, and national calibration remain later decisions.

## Epic 1 — Audit the Inputs and the Existing Job-Center Work

- [x] Confirm LODES WAC/RAC grain, vintage, and coverage. Record plainly whether
  more than one year exists.
- [x] Extract the existing job-center method from the Industry explorer's D3
  work: what defines a center today, what threshold or floor it uses, and where
  that constant came from.
- [x] Separate the reusable method from Streamlit and app-shaped assumptions.
- [x] Confirm tract geometry availability and distance-safe spatial operations,
  including projection handling.
- [x] Confirm which ACS tract fields are populated for both dependent variables
  — cost and units — and for income and burden.
- [x] Confirm OEWS grain and how it can be related to tract evidence without
  implying tract-level precision.
- [x] Confirm whether any managed tract-grain price series exists.
- [x] Review what Q1 produced and decide what to reuse.
- [x] State plainly whether one year of LODES is sufficient for a defensible
  center definition.

**Done when:** we know what a center can honestly be built from, what prior art
exists, and what the two dependent variables actually support. The spec is
rewritten against those findings.

Record the audit in [EXPLANATION_Q2_AUDIT.md](EXPLANATION_Q2_AUDIT.md).

**Completed conclusion:** V0 is feasible as a Richmond-first, current-snapshot
physical-proximity study. It does not yet establish a 15-minute access method
or a household-to-worker affordability mismatch.

## Epic 2 — Define the V0 Proximity Method

*Provisional. Rewrite after Epic 1.* **This is the epic that matters.**

- [ ] Define what a job center is: the construction rule, the threshold, and the
  minimum a center must satisfy.
- [ ] Define the V0 reach measure. Do not name it a 15-minute definition unless
  a routed travel-time input is added and audited.
- [ ] Define the origin point for tracts and the treatment of multiple centers.
- [ ] Record the candidate rule, selected rule, exclusions, and Haversine
  calculation in a method note that the notebook displays.
- [ ] State which V0 choices are provisional and what evidence a shared method
  would need before later analyses adopt it.
- [ ] Sanity-check the definition against a second center construction on paper
  before any consumer builds on it.

**Done when:** V0 has an inspectable center and proximity construction, without
claiming to be the shared 15-minute definition.

## Epic 3 — Build the Gradient

*Provisional. Rewrite after Epic 1.*

- [ ] Build the center inventory and selected-market center map.
- [ ] Calculate straight-line distance from residential tracts to centers.
- [ ] Build the binned distance curve for both dependent variables.
- [ ] Estimate the gradient with regression; report coverage and residuals.
- [ ] Add the tract residual map.

**Done when:** the gradient is visible, its model is inspectable, and its
residuals are mapped rather than hidden.

## Epic 4 — Add Affordability (post-V0)

*Provisional. Rewrite after Epic 1.*

- [ ] Add the job-center earnings profile from LODES earnings bands.
- [ ] Add tract income and housing burden.
- [ ] Add OEWS as labeled CBSA-grain context.
- [ ] Define a household-versus-worker comparison standard before calculating
  any affordability mismatch.
- [ ] Build a mismatch distribution or residence-versus-workplace comparison
  only if that standard supports it.

**Done when:** the affordability read is present without blending the three wage
and income concepts or claiming a worker-household bridge that has not been
defined.

## Epic 5 — National Calibration (post-V0)

*Provisional. Rewrite after Epic 1.*

- [ ] Run the method nationally to compare gradient shape and strength.
- [ ] Add sensitivity to center selection, price source, and normalization.
- [ ] Confirm the method produces a defensible `no clear signal` where it should.

**Done when:** the national run has tested the method rather than merely
producing a ranking.

## Epic 6 — Hand Off the Spine

*Provisional. Rewrite after Epic 1.*

- [ ] Publish the access definition in a form Q3, Q4, and Q6 can consume.
- [ ] Record which parts are fixed and which are variable.
- [ ] Decide whether the center surface should be promoted or stay analysis-local.
- [ ] Note what a routed network method would need to beat.

**Done when:** the next analysis can start without reverse-engineering this
notebook.

## What not to do

- do not let the access definition live only in notebook code
- do not infer travel or commuting from straight-line distance
- do not blend household income, job earnings, and occupational wages
- do not build two notebooks for the two dependent variables
