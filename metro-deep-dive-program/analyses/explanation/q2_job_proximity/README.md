# Q2 — Job Proximity, Housing, and Affordability

**Build order:** E3 — **gates E5 (Q4), E6 (Q3), and E7 (Q6)**

**Status:** Epic 2 implementation complete; national-pattern review is next.

**Question:** What does proximity to the market's major employment centers cost
in housing value or rent, and can households with local incomes afford to live
there?

Purpose:

- establish how workplace jobs concentrate across tracts nationally before
  choosing any local center or district rule
- explore and review local candidate job-center and district constructions only
  after the national pattern is visible
- estimate the price/rent gradient against distance, with coverage and residuals
- compare tract housing cost and resident income against the earnings profile of
  nearby job centers

**Primary analytical unit:** tract for job centers, housing level, and income.
ZCTA supports market-price trends when its distinct grain stays visible. CBSA
occupational wages are context, not tract-level precision.

**National posture:** national employment-concentration discovery first;
Richmond-first geographic interpretation second. National proximity calibration
comes only after a reviewed V0 rule has been tested locally.

## This analysis carries the shared access spine

Its most important early output is not the gradient. It is a national account
of workplace-job concentration and a reviewable set of local candidate
constructions that can eventually support a reusable operational definition —
what a center is, how reach is measured, what counts as access.

**Do not specify that definition before exploration.** The first notebook
profiles national tract concentration; the second maps raw local job geography
and competing candidate constructions. A reviewer then explicitly selects or
rejects a V0 rule. Nothing is promoted to later analyses during that review.

## Merged analysis

This absorbs what was previously **Q5, "Afford to Live Near Jobs."** The two ran
on identical inputs and outputs and differed only in dependent variable —
housing units versus housing cost. They are one analysis with two dependent
variables. Two separate publication hooks remain available, but that is an
issue-layer decision, not a reason to build two notebooks.

## V0 method, in order

1. **Measure national tract concentration.** Build within-market Pareto curves
   and 50%/80% concentration cutoffs from workplace jobs.
2. **Profile the tract metrics.** Inspect total jobs, density, and
   jobs-to-resident-workers without collapsing them into one score.
3. **Explore local employment geography.** Map candidate tracts and adjacent
   districts in a selected market before selecting a construction.
4. **Build tract gradients by physical proximity**, network effects second.
5. **Measure housing outcomes and affordability context** across the reviewed
   proximity gradient, with coverage and residuals visible.

Keep household income, individual job earnings, and occupational wages separate.
Any modeled bridge between them must be explicit.

Start with straight-line distance. Network distance or travel time is a later
challenger, tested once for the whole family rather than per question.
Infrastructure may explain a visible anomaly but is not a routing network under
its current contract.

## Open decisions for the spec

- concentration measures and eligible-market rules for the national analysis
- center/district construction rule and the evidence required before a
  15-minute method can be defined
- treatment of multiple centers; origin point for tracts
- distance bins and model form
- housing measure, controls, minimum observations
- whether gradients are descriptive or adjusted
- affordability standard; household-versus-worker unit
- worker-origin analysis after LODES OD is available; RAC alone is insufficient
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
