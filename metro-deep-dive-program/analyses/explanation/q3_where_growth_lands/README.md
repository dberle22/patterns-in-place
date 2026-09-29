# Q3 — Where Growth Lands

**Build order:** E6

**Status:** Geography dependency and Epics 1–4 complete; pending Epic 5 review.

**Question:** Where are population and housing-unit gains or losses landing
within a metro?

Purpose:

- restate comparable population and housing-unit counts on a declared tract
  vintage
- show concentration, county, and named-Place patterns without assigning an
  infill/greenfield class
- retain permits as native-grain context only

**Primary analytical unit:** harmonized 2020 Census tract.

**National posture:** national method, local application.

## Build and read

Run `python3 build_q3_growth_location_mart.py` to materialize the
analysis-owned `mart_explanation_q3` surfaces, then open
`EXPLANATION_Q3_NOTEBOOK.py`. The mart consumes Geography's governed temporal,
containment, and Place-membership relationships without placing ACS metrics in
the Geography mart.

The 5- and 10-year comparisons are the interpretive core. The 1- and 3-year
ACS 5-year-release comparisons are descriptive watchlist signals, not
independent annual growth estimates.

## Relationship to Q2

Q2 physical proximity is optional explanatory context. It is not an access,
travel-time, commuting, or 15-minute result, and Q3 does not need it to make
its primary growth-location read.

See [EXPLANATION_Q3_WHERE_GROWTH_LANDS_SPEC.md](EXPLANATION_Q3_WHERE_GROWTH_LANDS_SPEC.md) for the
analysis boundary and inputs, and
[EXPLANATION_Q3_WHERE_GROWTH_LANDS_BUILD_PLAN.md](EXPLANATION_Q3_WHERE_GROWTH_LANDS_BUILD_PLAN.md) for
the epic sequence.

Section 5.5 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
