# Q2 — Job Proximity, Housing, and Affordability

**Build order:** E3 — **gates E5 (Q4), E6 (Q3), and E7 (Q6)**

**Status:** Epic 1 audit complete; V0 method definition is next.

**Question:** What does proximity to the market's major employment centers cost
in housing value or rent, and can households with local incomes afford to live
there?

Purpose:

- establish the reusable definition of a job center
- establish the operational 15-minute-city definition the rest of the family
  re-runs
- estimate the price/rent gradient against distance, with coverage and residuals
- compare tract housing cost and resident income against the earnings profile of
  nearby job centers

**Primary analytical unit:** tract for job centers, housing level, and income.
ZCTA supports market-price trends when its distinct grain stays visible. CBSA
occupational wages are context, not tract-level precision.

**National posture:** national method, local application. The national run tests
and calibrates the method rather than being the finding.

## This analysis carries the shared access spine

Its most important output is not the gradient. It is the reusable operational
definition — what a center is, how reach is measured, what counts as access —
that Q3, Q4, Q6, and Catchment re-run with different center inputs.

**Specify that definition to be adopted without reinterpretation.** A loose
definition here gets expensive to unwind after three other analyses have consumed
it. This is the one deliberate exception to the promotion rule: five consumers
are known before any is written, so the method is specified once here rather than
discovered on the third notebook.

## Merged analysis

This absorbs what was previously **Q5, "Afford to Live Near Jobs."** The two ran
on identical inputs and outputs and differed only in dependent variable —
housing units versus housing cost. They are one analysis with two dependent
variables. Two separate publication hooks remain available, but that is an
issue-layer decision, not a reason to build two notebooks.

## V0 method, in order

1. **Define job centers.** Required, not optional — four later analyses depend on
   it.
2. **Build tract gradients by physical proximity first**, network effects second.
3. **Measure what varies across the gradient** — housing cost, housing units, and
   simple counts like how many people live there.
4. **Estimate the relationship** with regression, for both cost and units,
   reporting coverage and residuals.
5. **Layer in affordability** by comparing tract housing cost and resident income
   against the earnings profile of nearby job centers.

Keep household income, individual job earnings, and occupational wages separate.
Any modeled bridge between them must be explicit.

Start with straight-line distance. Network distance or travel time is a later
challenger, tested once for the whole family rather than per question.
Infrastructure may explain a visible anomaly but is not a routing network under
its current contract.

## Open decisions for the spec

- center construction rule and the evidence required before a 15-minute method
  can be defined
- treatment of multiple centers; origin point for tracts
- distance bins and model form
- housing measure, controls, minimum observations
- whether gradients are descriptive or adjusted
- affordability standard; household-versus-worker unit
- wage source hierarchy; tenure treatment; time alignment

See [EXPLANATION_Q2_JOB_PROXIMITY_SPEC.md](EXPLANATION_Q2_JOB_PROXIMITY_SPEC.md) for the
V0 analysis boundary, minimum outputs, and Marimo outline;
[EXPLANATION_Q2_AUDIT.md](EXPLANATION_Q2_AUDIT.md) for the completed input
review; and
[EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN.md](EXPLANATION_Q2_JOB_PROXIMITY_BUILD_PLAN.md) for
the epic sequence.

Sections 5.4 and 2.5 of
[EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md) hold the
family-level framing and the shared-spine rule.
