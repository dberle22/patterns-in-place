# Thematic A9 — Converging or Diverging Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Are U.S. metros becoming more alike or sorting farther apart on education, age,
income, population change, and related economic structure?

The analysis should distinguish movement in the national distribution from one
market moving relative to its peers. It should not compress unlike measures
into one divergence score unless the audit demonstrates that such a score adds
meaning.

**Themes crossed:** People & Movement × Industry & Labor × Housing &
Affordability.

## 2. Provisional claim and alternatives

**Claim direction to review:** Metros are diverging on some human-capital and
income dimensions even while converging on others; the pattern reflects both
between-region sorting and different trajectories among initially similar
markets.

The claim is weakened if national dispersion is broadly stable, if nominal
dollar growth creates the apparent separation, or if results change materially
with the CBSA cohort, population weights, or start/end years.

## 3. Analytical unit and universe

- National unit: CBSA × year for a reviewed metric set.
- Candidate panel: recurring 2012–2024 Gold measures, with source-specific
  availability and a stable cohort declared.
- National objects: metric distributions over time and conditional movement
  from initial position.
- Market unit: selected CBSA trajectory relative to nation, division, and a
  fixed or clearly time-indexed Act 1 peer set.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. define convergence and divergence before choosing statistics
2. show each metric’s distribution and coverage over time
3. distinguish dispersion change from rank mobility and conditional catch-up
4. handle nominal/real and level/rate differences explicitly
5. test stable cohort, population weighting, period, region, and outlier
   sensitivity
6. examine whether initially similar metros are separating
7. report mixed metric-family results instead of forcing one verdict

### Parameterized market notebook

The market notebook should:

- show the selected CBSA’s level, percentile, and change for reviewed metrics
- compare nation, division, and peers over aligned periods
- distinguish the market moving from the comparison distribution moving
- show which metrics drive convergence toward or divergence from peers
- preserve ordinary/no-standout trajectories
- provide standard deep dives for convergence, upward divergence, downward
  divergence, cross-metric splitting, and stability

## 5. Current repository assets

- recurring 2012–2024 population, education, age, income, housing, migration,
  commuting, and industry Gold panels
- Time-Series engine’s 50-metric 2018–2023 stable 396-CBSA panel
- Position Trajectory and Peers notebooks/contracts
- Benchmarking comparison sets
- Intelligence Framework cross-frame and peer outputs

## 6. Audit findings to verify

- The Time-Series engine measures market trajectory and salience; it does not
  answer national convergence by itself.
- Its stable 396-CBSA cohort and 2018–2023 period are useful prior art but may
  be too short or narrow for A9.
- Nominal income, real purchasing power, shares, ages, and growth rates require
  different transformations.
- Changing CBSA coverage can create artificial dispersion changes.
- Current peer membership may use endpoint characteristics, creating look-ahead
  risk in a historical comparison.
- National dispersion, within-region dispersion, rank mobility, and beta-style
  catch-up are distinct concepts.

## 7. Provisional outputs

- metric/cohort contract and coverage table
- national dispersion paths by metric family
- rank-mobility and conditional-convergence views where appropriate
- region, period, weighting, and cohort sensitivities
- selected-market relative trajectory and driver table
- finding ledger with mixed results preserved

## 8. Decisions Epic 1 must prepare

- primary definitions of convergence/divergence
- narrow metric set and family organization
- stable universe and population threshold
- period and endpoint rules
- nominal/real and transformation rules
- weighting and regional decomposition
- historical peer-set treatment
- whether any cross-metric summary is justified

## 9. Non-goals

- rebuilding the Time-Series engine inside the notebook
- treating `no_standout_trend` as missing analysis
- using endpoint peers as if they were historically fixed without disclosure
- combining incomparable units into an opaque divergence index
- claiming individual household sorting from metro aggregates alone

