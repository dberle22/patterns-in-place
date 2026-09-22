# Explanation Q2 — Job Proximity Build Plan (Superseded Snapshot)

**Status at supersession:** Epic 2 implementation complete; national-pattern
review was next.

**Why this file remains:** This preserves the pre-revision Q2 build history and
its completed work. The active plan is
[EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN.md](EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN.md).
It adopts the later three-notebook architecture: national job concentration,
market job-center method selection, and analytical job-center outcomes.

## How the previous plan worked

**Epic 1 was an audit, and came first.** Its evidence supported a national
employment-concentration exploration followed by local geographic review. The
shared access method, affordability match, worker origins, and national
proximity calibration remained later decisions.

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

**Completed conclusion:** V0 is feasible as a Richmond-first, current-snapshot
physical-proximity study. It does not yet establish a 15-minute access method
or a household-to-worker affordability mismatch.

## Epic 2 — Explore National Employment Concentration

This established the empirical frame before any local center or district rule
was considered.

- [x] Create `EXPLANATION_Q2_JOB_CONCENTRATION_NOTEBOOK.py`, using named
  read-only queries over the 2023 WAC/RAC tract surface.
- [x] State the eligible-CBSA rule, WAC coverage exclusions, and all
  denominator rules before substantive national views.
- [x] Rank tracts by workplace jobs within each CBSA and produce cumulative
  job-share (Pareto) curves for selected and contrasting markets plus a pooled
  eligible-CBSA tract reference curve.
- [x] Calculate, for every eligible CBSA, the tract share required to reach 50%
  and 80% of workplace jobs, plus the job share held by the top 20% of tracts.
- [x] Show national distributions of those concentration measures with explicit
  tract and job-count denominators.
- [x] Show distributions and scatters for total jobs, jobs per square mile, and
  jobs-to-resident-workers; add raw and log-scale distributions/boxplots and
  keep a visible job-mass screen on ratio views.
- [x] Compare tract job share and resident-worker share without treating job
  share as an independent metric or assuming jobs and workers have equal totals.
- [x] Identify contrasting market patterns for local geographic review without
  publishing a market ranking or selecting a center rule.
- [x] Add an inspectable national top-tract table with metro identifiers and
  each tract's primary employment-geography measures.

**Done when:** the national notebook makes the concentration patterns and their
limitations visible enough to inform—not determine—the local method review. No
construction is promoted to the shared access spine in this epic.

**Implementation complete:** the notebook uses named, read-only national
readers and has run end-to-end in the Marimo environment. Review the observed
patterns before changing the market notebook or beginning the local method
review.

## Epic 3 — Explore Market Employment Geography

The current Richmond notebook was an unreviewed prototype for this epic, not a
selected method.

- [ ] Rework `EXPLANATION_Q2_PROXIMITY_METHOD_NOTEBOOK.py` to begin with the
  selected market's national concentration context.
- [ ] Retain interactive tract maps for total jobs, CBSA workplace-job share,
  job density, and jobs-to-resident-workers. Treat density as a contextual
  diagnostic rather than an end-all measure; standardize the future market
  selector on readable CBSA name plus code while retaining the code as the
  query value.
- [ ] Add the tract job-share versus resident-worker-share comparison with
  explicit denominator and small-denominator safeguards.
- [ ] Map and compare absolute job floors, within-market percentiles, density,
  contiguous qualifying-tract clusters, and jobs-to-workers context.
- [ ] Keep candidate flags independent. For the current prototype, seed
  contiguous components from absolute-job-floor tracts only and group touching
  polygons; label components with two or more tracts as candidate districts,
  never automatic zones or corridors. Any later composite seed predicate or
  nearby-tract distance merge requires explicit review.
- [ ] Display every candidate's parameters, inventory, overlap, and exclusions.
- [ ] Add descriptive comparisons between job measures and declared observed
  tract KPIs; do not silently create zones or a composite score.
- [ ] End with an explicit reviewer decision record for the center or district
  rule, parameters, origin point, and multiple-center treatment. It remains
  blank until review; the notebook must not select a rule itself.

**Done when:** a reviewer can connect a market's maps to its national pattern,
then explicitly choose, reject, or request another local construction. Adjacent
tracts are candidate districts, not automatically zones or corridors.

## Epic 4 — Build the V0 Evidence Notebook

- [ ] Create `EXPLANATION_Q2_NOTEBOOK.py`, parameterized by CBSA and with a
  concise reviewed-rule, parameter, and guardrail summary at the top.
- [ ] Require an explicit reviewed rule before calculating the evidence surface;
  halt with a clear message if one has not been recorded.
- [ ] Build the center inventory and selected-market center map from that rule.
- [ ] Calculate straight-line distance from residential tracts to centers.
- [ ] Build the binned distance curve for both dependent variables.
- [ ] Estimate the gradient with regression; report coverage and residuals.
- [ ] Add the tract residual map.

**Done when:** the gradient is visible, its model is inspectable, and its
residuals are mapped rather than hidden. The notebook makes no claim beyond the
reviewed V0 physical-proximity rule.

## Epic 5 — Add Affordability (post-V0)

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

## Epic 6 — National Proximity Calibration (post-V0)

- [ ] Run the method nationally to compare gradient shape and strength.
- [ ] Add sensitivity to center selection, price source, and normalization.
- [ ] Confirm the method produces a defensible `no clear signal` where it should.

**Done when:** the national run has tested the method rather than merely
producing a ranking.

## Epic 7 — Hand Off the Spine

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
- do not infer worker origins from RAC; that requires LODES OD
