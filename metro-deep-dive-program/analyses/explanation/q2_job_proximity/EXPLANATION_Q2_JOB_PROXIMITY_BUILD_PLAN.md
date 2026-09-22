# Explanation Q2 — Job-Center and Proximity Method Build Plan

**Status:** Epic 3 initial analytical outcomes notebook complete; ready for
review in Richmond before any second-market calibration.

**History:** The completed and superseded epic sequence is preserved in
[EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN_PREVIOUS.md](EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN_PREVIOUS.md).

## Build sequence

Q2 owns a job-center method and its first housing/cost outcomes analysis. Build
in this order:

1. review national job concentration to understand the first center surface;
2. select a reviewed job-center rule in a market-specific workbench;
3. build one market-specific analytical notebook for housing, cost, and
   affordability outcomes; and
4. let Q3, Q4, and Q6 later reuse the reviewed proximity surface for their own
   questions.

Do not build national comparison notebooks for every job-center outcome before
local runs establish that the method is worth calibrating nationally.

## Completed foundation

- [x] Audit WAC/RAC, geometry, Q1 housing fields, OEWS, and price-series limits.
- [x] Establish V0 as physical proximity, not routed 15-minute access or a
  household-worker affordability method.
- [x] Build `EXPLANATION_Q2_JOB_CONCENTRATION_NOTEBOOK.py` over named,
  read-only 2023 WAC/RAC queries.
- [x] Implement national WAC coverage, concentration, distribution, ratio, and
  top-tract outputs.

## Epic 1 — Review national job concentration

- [x] Review coverage, exclusions, eligible-CBSA rules, and the 2023 snapshot
  limitation in `EXPLANATION_Q2_JOB_CONCENTRATION_NOTEBOOK.py`.
- [x] Review Pareto curves, 50%/80% cutoffs, top-20%-tract job share, and
  employment-geography metric behavior.
- [x] Identify contrasting markets for method testing; do not rank markets or
  promote a threshold from the national distributions.
- [x] Record Richmond's national concentration context for the
  market method notebook.

**Done when:** national patterns inform the local review without selecting its
job-center rule.

**Completed review:** [EXPLANATION_Q2_NATIONAL_CONCENTRATION_REVIEW.md](EXPLANATION_Q2_NATIONAL_CONCENTRATION_REVIEW.md)
records the cohort, Richmond context, two-signal exploratory screen, and
recommended contrast sequence. The 1% market-job-share, 1.5 jobs-to-workers,
and 2,500-job settings remain sensitivities, not an adopted rule.

## Epic 2 — Complete the market job-center method workbench

- [x] Rework `EXPLANATION_Q2_PROXIMITY_METHOD_NOTEBOOK.py` to begin with the
  selected market's national concentration context.
- [x] Retain full tract maps for workplace jobs, CBSA job share, job density,
  and jobs-to-resident-workers before any display filter.
- [x] Make tract market-job share and jobs-to-workers the primary, independent
  candidate signals. Retain an absolute-job floor as a required guardrail;
  retain density and contiguous clusters as contextual/exploratory views.
- [x] Show every rule's parameters, inventory, overlap, exclusions, and visible
  fragmentation. Do not create a composite score or automatic center choice.
- [x] Define a reviewed job-center record outside notebook state: version,
  selected/rejected rule, selected tracts/districts, center origins,
  nearest/multiple-center treatment, sensitivities, reviewer, and date.
- [x] Publish named national candidate and tract-level proximity surfaces for
  strict-core, recommended core-plus-one-hop, and no-share-sensitivity versions.

**Done when:** a reviewer can select or reject a transparent job-center method,
and another notebook can consume the resulting proximity surface without
recreating center selection.

**Completed publication:** the workbench and
[EXPLANATION_Q2_JOB_CENTER_METHOD_RECORD.md](EXPLANATION_Q2_JOB_CENTER_METHOD_RECORD.md)
are paired with the national `mart_explanation_q2` candidate, cluster,
proximity, and method-catalog tables. Per-market reviewer approval still
governs which version is primary in an outcomes read; it does not block reuse
of the published sensitivity surfaces.

## Epic 3 — Build the analytical job-center outcomes notebook

- [x] Create `EXPLANATION_Q2_JOB_CENTER_OUTCOMES_NOTEBOOK.py`, parameterized
  by CBSA and a reviewed job-center record.
- [x] Read the reviewed tract-level proximity surface and Q1's 2024 tract
  housing surface through named queries; do not recreate job-center selection
  or Q1 transformations in notebook cells.
- [x] Show the reviewed method, center inventory/map, national job context, and
  outcome-specific coverage before analytical results.
- [x] Build binned distance curves for median gross rent, median home value,
  and housing units; retain household income, rent-to-income, and rent burden
  as separately labeled affordability context.
- [x] Fit disclosed descriptive models, show a primary-cost residual map, and
  state a no-clear-signal result where warranted.
- [x] Keep household income, LODES earnings bands, and OEWS wage context
  separate; do not claim a household-worker affordability match.
- [x] Keep center-selection controls out of this notebook and halt if the
  job-center method has not been reviewed.

**Done when:** one analytical market notebook produces a reviewable job-center
housing/cost result without mixing method selection and conclusion.

**Completed implementation:** the new notebook reads the published Q2 mart
through outcome-specific queries, defaults to Richmond's reviewed
`recommended_core_one_hop` version, and retains strict-core/no-share as visible
sensitivity views. It explicitly stops a selected version with no centers;
Marimo static and full execution checks passed against the local mart.

## Epic 4 — Hand off to later thematic notebooks

- [ ] Document the reviewed job-center proximity surface so Q3 can analyze
  growth, Q4 can contextualize daily-needs access, and Q6 can assess
  multi-anchor structure without recreating job-center selection.
- [ ] Require each consumer to declare its outcome grain, time treatment,
  controls, and interpretation independently.
- [ ] Defer a broader market synthesis until multiple reviewed theme results
  exist; it is not another Q2 notebook now.

## Epic 5 — National calibration and access promotion, only if earned

- [ ] Run the reviewed job-center method and one thematic comparison in a
  second contrasting market.
- [ ] Open a national job-center-versus-outcome calibration notebook only when
  the local method and outcome definition survive those runs.
- [ ] Test sensitivity and `no clear signal` behavior rather than producing a
  national market ranking.
- [ ] Evaluate a routed travel-time challenger once for the family before
  promoting a 15-minute-access definition.

## Guardrails

- Do not use housing, cost, income, burden, or growth to select job centers.
- Do not build duplicate national notebooks when Q1 already owns the national
  housing/cost question.
- Do not infer travel, commuting, worker origins, or 15-minute access from
  Haversine distance or RAC.
- Do not blend household income, LODES earnings bands, and OEWS wages.
- Do not run parallel DuckDB materializations for needed upstream data work.
