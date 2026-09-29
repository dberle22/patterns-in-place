# Thematic A3 — Moving Toward Harm Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Is population and housing growth increasingly concentrated in metros and
neighborhoods with higher natural-hazard exposure?

The analysis should connect environment/risk to population and built-environment
change while preserving the difference between hazard exposure, vulnerability,
expected loss, realized disasters, and migration flows.

**Themes crossed:** Environment & Risk × People & Movement × Housing &
Affordability.

## 2. Provisional claim and alternatives

**Claim direction to review:** Recent population and housing growth is
disproportionately occurring in metros with higher hazard exposure, but the
pattern varies by hazard type and reflects regional demand and housing supply
as well as risk.

The claim is weakened if growth is unrelated to or lower in high-risk metros,
if results are driven by a few large Sun Belt markets, or if the relationship
does not survive source-vintage and population-weighting choices.

Net population or housing growth does not establish that particular households
moved from lower-risk to higher-risk places.

## 3. Analytical unit and universe

- National unit: CBSA, with growth measured over a declared historical window
  and risk measured from a declared FEMA release.
- Hazard detail: composite risk plus reviewed hazard-specific measures.
- Market unit: selected CBSA with county and tract growth/risk overlap where
  geography and vintage contracts permit.
- Flow analysis is optional later work and requires origin-destination data.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. define risk, exposure, vulnerability, resilience, and growth separately
2. show the national distributions and geographic concentration of each
3. compare population growth, housing-unit growth, and permitting without
   treating them as interchangeable
4. test composite and hazard-specific relationships
5. test population weighting, region, size cohort, and influential-market
   sensitivity
6. show whether the conclusion changes when growth levels and rates are used
7. identify market cases without claiming household-level migration paths

### Parameterized market notebook

The market notebook should:

- place the selected CBSA in the national hazard/growth result
- compare nation, division, and peers
- show which hazards drive the market’s profile
- map tract or county growth against governed hazard measures when valid
- distinguish existing exposure from where recent development occurred
- provide standard deep dives for high-growth/high-risk, high-growth/lower-risk,
  slow-growth/high-risk, and mixed cases
- state when the market has no distinctive overlap pattern

## 5. Current repository assets

- `gold.environment_wide` with EPA, EJScreen, FEMA composite, vulnerability,
  resilience, and hazard-specific measures
- `silver.fema_nri` at tract, county, and CBSA grains for the current release
- 2012–2024 population and housing panels
- housing permits at supported grains
- Geography temporal and display interfaces
- Q3 Where Growth Lands planning as related future method work
- Benchmarking, Peers, and Time-Series context

## 6. Audit findings to verify

- FEMA promoted measures are a current release rather than a recurring
  year-by-year hazard panel.
- Growth periods precede or overlap that snapshot and need explicit temporal
  interpretation.
- FEMA risk, expected annual loss, social vulnerability, and resilience answer
  different questions.
- Tract growth may require temporal harmonization; non-additive risk scores must
  not be allocated as counts.
- Regional sorting and large-market influence could dominate a national result.
- The original “moving” language is stronger than net growth evidence alone.

## 7. Provisional outputs

- national coverage/vintage and metric-contract tables
- composite and hazard-specific growth/risk views
- region, size, and weighting sensitivity tables
- selected-market hazard profile and growth-overlap maps/tables
- finding ledger with explicit inference limits

## 8. Decisions Epic 1 must prepare

- primary risk concept and hazard measures
- growth measures and time windows
- weighting and stable comparison universe
- role of permits versus realized stock/population growth
- treatment of region, size, and influential markets
- tract temporal-harmonization requirement
- language rule for “moving,” “growth,” “risk,” and “harm”
- whether flow data is necessary for any retained claim

## 9. Non-goals

- claiming observed disasters or damages from risk scores alone
- inferring household migration paths from net population change
- combining hazard scores into an undocumented universal danger index
- allocating non-additive risk measures across boundaries
- making issue-specific resilience or investment recommendations

