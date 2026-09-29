# Thematic A2 — Building Lowers Prices Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Do metros that permit and deliver more housing subsequently experience slower
home-price and rent growth, after accounting for demand conditions?

The analysis should turn a broad housing debate into a transparent national
panel and then show how supply response and price pressure unfold in a selected
market.

**Themes crossed:** Housing & Affordability × People & Movement.

## 2. Provisional claim and alternatives

**Claim direction to review:** Greater housing production relative to market
size and demand is associated with slower subsequent price and rent growth,
with effects that vary by time horizon and initial market conditions.

The claim is weakened if the relationship disappears or reverses under
reasonable lag, cohort, demand-control, and source choices. A positive raw
relationship may reflect builders responding to demand rather than building
causing higher prices.

The title is a question, not a precommitted causal conclusion.

## 3. Analytical unit and universe

- National unit: CBSA × year, over a declared balanced or explicitly
  unbalanced panel.
- Core period candidate: 2012–2024 for ACS/permit context, with source-specific
  price and rent windows declared separately.
- Market unit: selected CBSA over time, plus county, Place, tract, or ZCTA
  context only where the measures are native and comparable.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. distinguish permits, completed stock growth, vacancy, and structure mix
2. distinguish price level, home-price growth, rent growth, and burden
3. establish the timing between supply response and later outcomes
4. show demand conditions before adjusted relationships
5. test lag/window, cohort, weighting, and influential-market sensitivity
6. avoid causal language unless the audited design supports it
7. identify market cases representing different supply/demand paths

### Parameterized market notebook

The market notebook should:

- show the selected CBSA’s supply response and price/rent path in native units
- compare nation, division, and peers
- separate permits from realized housing-stock growth
- show population/migration and vacancy context
- expose Place permit, tract housing, and ZCTA price evidence only with their
  correct coverage and overlap caveats
- provide standard deep-dive paths for responsive supply, constrained supply,
  weak demand, and ambiguous cases
- preserve a no-clear-local-conclusion result

## 5. Current repository assets

- `gold.housing_core_wide` and `gold.housing_market_wide`
- `gold.population_demographics`, `gold.migration_wide`, and income context
- the mature Explanation Q1 analysis-owned mart, national notebook, market
  notebook, metric contract, and index-method note
- Geography temporal/allocation interfaces
- Benchmarking and peer surfaces
- publisher housing workbenches as prior art, not analysis authority

## 6. Audit findings to verify

Inputs are strong, but the research design is the work:

- permits measure construction authorization, not completed supply
- stock growth is realized supply but has ACS smoothing and boundary issues
- FHFA and Zillow series have different universes and meanings
- demand drives both construction and prices, creating an endogeneity problem
- Q1 provides reusable components and semantics but does not answer A2’s
  longitudinal question
- sub-CBSA permits and prices do not share one complete common geography

## 7. Provisional outputs

- national panel coverage and metric-contract tables
- supply-response and later price/rent relationship views
- lag/window and cohort sensitivity tables
- market-path typology, only if supported
- selected-market timeline, benchmark table, and component evidence
- finding ledger with causal-language limits

## 8. Decisions Epic 1 must prepare

- primary supply measure and alternatives
- primary price and rent outcomes
- lag structure and observation window
- balanced-panel and minimum-size rules
- demand controls and interpretation boundary
- inflation treatment where dollar measures are used
- weighting and influential-market treatment
- valid sub-CBSA market views

## 9. Non-goals

- treating permits as completed units
- inferring a causal effect from one cross-sectional scatter
- creating a new broad Housing Engine in advance
- reproducing Q1’s full supply/demand diagnostic
- publishing a market-specific policy recommendation from this folder

