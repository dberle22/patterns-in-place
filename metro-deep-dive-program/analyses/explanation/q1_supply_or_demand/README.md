# Q1 — Supply or Demand

**Build order:** E2

**Status:** Epic 1 audit complete; Q1 component mart design is next.

**Question:** Where housing is relatively inexpensive, does the evidence point to
abundant supply, weak demand, or a mixed condition?

Purpose:

- build separate supply and demand component families before any combined
  classification
- classify submarkets as supply-supported affordability, weak-demand
  affordability, pressure/shortage, or mixed
- produce a reusable housing component cut for later analyses

**Primary analytical unit:** tract for housing stock and resident conditions,
with Place/county permit evidence and ZCTA/county price trends kept as separate,
labeled lenses. Historical tract counts can use the Geography layer's
2010-to-2020 harmonization; medians and ratios remain vintage-labeled.

**National posture:** **national analysis** — the one analysis in this family
where the national run is itself a result worth reading. Housing genuinely
nationalizes. Build the national analysis first, then move into market-specific
work.

## First task: define `inexpensive`

Start with annualized median gross rent divided by local median household income:
the `30%` threshold identifies inexpensive housing and `50%` is the stress-test
threshold. Owner costs with and without a mortgage are parallel context.

## Main outputs under consideration

- relative cost distributions (box plots or similar)
- a supply-versus-demand formula producing an **overheating index** score
- quadrant scatter graphs of key variable relationships, at both submarket and
  CBSA level
- maps of submarket metrics, highlighting both cheap and expensive areas
- classifications of tracts and ZIP codes

Work broad-to-narrow: establish broad market signals first, then go submarket
with supply-versus-demand scores and their relationship to cost.

Alongside Q2, this is the family's best opportunity to build regression practice.

## Guardrails

- do not assign county or Place permits to tracts
- do not combine price level and appreciation into one unlabeled housing-price
  measure

## Open decisions for the spec

- the operational meaning of `inexpensive` as a cost-to-wage function
- submarket unit
- component definitions and weights
- the overheating index formula
- time windows and minimum coverage
- multi-grain combination rule
- no-signal rule

See [EXPLANATION_Q1_SUPPLY_OR_DEMAND_SPEC.md](EXPLANATION_Q1_SUPPLY_OR_DEMAND_SPEC.md) for the
analysis boundary and inputs,
[EXPLANATION_Q1_SUPPLY_OR_DEMAND_BUILD_PLAN.md](EXPLANATION_Q1_SUPPLY_OR_DEMAND_BUILD_PLAN.md) for
the epic sequence, and [EXPLANATION_Q1_AUDIT.md](EXPLANATION_Q1_AUDIT.md) for
the completed evidence review.

Section 5.3 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
