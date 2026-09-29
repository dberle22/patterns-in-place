# Thematic A4 — Remote Work Rewired Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Did the remote-work shift durably change where people live, how they commute,
where jobs concentrate, and how housing markets behave across metros?

The analysis must turn “rewired” into testable dimensions instead of treating
WFH share, residence patterns, workplace geography, and housing prices as one
phenomenon.

**Themes crossed:** Work Geography × Housing & Affordability × Industry &
Labor.

## 2. Provisional claim and alternatives

**Claim direction to review:** Metros with larger and more persistent increases
in working from home experienced different housing and commuting trajectories,
but current data may support residential and commute-mode change more strongly
than workplace-geography change.

The claim is weakened if WFH changes largely reverted, if housing relationships
vanish after pre-existing industry and demand differences are considered, or
if “rewiring” cannot be distinguished from broader pandemic-era regional
sorting.

## 3. Analytical unit and universe

- National unit: CBSA × year for recurring ACS WFH, commute, housing,
  demographic, and industry measures.
- Candidate period: pre-shift, disruption, and post-shift windows within
  2012–2024, to be audited for ACS comparability.
- Current workplace geography: tract and CBSA 2023 LODES WAC/RAC.
- Market unit: selected CBSA over time, with tract evidence where recurring ACS
  measures and current LODES answer clearly separated questions.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. define persistence and the dimensions of rewiring
2. establish pre-period WFH, industry, housing, and commute baselines
3. compare WFH shifts with housing-price/rent, population, and commute changes
4. distinguish level differences from change relationships
5. test industry composition, size, region, and pretrend alternatives
6. state which workplace-geography claims remain blocked by history or OD data
7. identify national archetypes only if the evidence separates them cleanly

### Parameterized market notebook

The market notebook should:

- show the selected CBSA’s WFH and commute-mode path against national,
  division, and peers
- compare housing, population, and industry context over aligned periods
- show current tract workplace/residence structure as a snapshot, not a
  before/after claim
- identify where WFH is locally concentrated when tract ACS coverage permits
- offer standard paths for persistent-high, surge-and-revert, low-change, and
  mixed markets
- preserve a no-clear-rewiring conclusion

## 5. Current repository assets

- 2012–2024 `pct_commute_wfh` and related commute measures in
  `gold.transport_built_form_wide`
- recurring population, housing, income, and broad industry panels
- 2023 LODES WAC/RAC at tract and CBSA grains
- current job-center work from Industry D3 and Explanation Q2
- Geography, Benchmarking, Peers, and Time-Series surfaces
- Regional Role and Q6 plans for future flow/polycentricity context

## 6. Audit findings to verify

- ACS WFH is residence-based commute-mode evidence, not employer-location or
  job-flow evidence.
- Current managed LODES is a 2023 snapshot; it cannot show how employment
  centers changed through the remote-work shift.
- LODES OD is not available, so commute-shed claims are out of scope.
- Pandemic-period ACS comparability and survey-year treatment need explicit
  review.
- Housing and population changes have many coincident causes; simple WFH
  correlations are not causal.
- The audit may need to narrow the question to durable WFH-associated change
  unless historical workplace inputs are added.

## 7. Provisional outputs

- WFH/commute persistence and coverage tables
- national WFH-change trajectories and cohort views
- housing/population/industry relationship and sensitivity views
- selected-market aligned timeline and current geography snapshot
- finding ledger with supported and blocked rewiring dimensions

## 8. Decisions Epic 1 must prepare

- operational definition of persistent remote-work change
- pre, disruption, and post windows
- which dimensions qualify as “rewiring”
- treatment of pandemic ACS years and source comparability
- primary housing and population outcomes
- industry-composition controls or comparison cohorts
- whether historical LODES or OD is a blocker or a later extension
- valid tract-level market views

## 9. Non-goals

- inferring origin-destination commute flows from WAC/RAC totals
- claiming employment-center change from a one-year LODES snapshot
- attributing housing prices solely to remote work
- defining remote-work eligibility from memory or undocumented occupation rules
- building a full commute-shed engine

