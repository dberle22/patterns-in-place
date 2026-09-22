# Thematic A6 — Specialization Predicts Growth Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Does a metro’s initial specialization in an industry predict subsequent
employment growth in that industry, or is mean reversion more common?

This analysis should provide a disciplined national test of a common economic-
development intuition and a reusable way to inspect a selected market’s sector
trajectory.

**Themes crossed:** Industry & Labor × People & Movement.

## 2. Provisional claim and alternatives

**Claim direction to review:** Initial specialization predicts persistent
growth in some tradable or knowledge-intensive sectors but mean reversion in
others; the national average masks sector-specific patterns.

The claim is weakened if initial LQ has little out-of-period relationship with
later sector employment growth, if apparent persistence is mechanical, or if
results depend on a small number of markets or one start/end year.

## 3. Analytical unit and universe

- Native national unit: CBSA × sector × base year, followed over a declared
  horizon.
- Primary source candidate: annual QCEW fields in
  `gold.economics_industry_wide`, currently 2012–2024 at broad-sector grain.
- More detailed QCEW grain is optional only if the audit shows it is necessary
  and coverage remains suitable.
- Market unit: selected CBSA × sector over time.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. define specialization, subsequent growth, sector grain, and lag horizon
2. show LQ and growth distributions by sector
3. distinguish growth in levels, rates, and national-relative performance
4. test persistence versus mean reversion out of period
5. test start year, horizon, sector, metro size, and recession/pandemic
   sensitivity
6. distinguish within-sector results from pooled results
7. identify market-sector cases from model evidence, not only rankings

### Parameterized market notebook

The market notebook should:

- show the selected CBSA’s initial specializations and later outcomes
- compare sector paths with national, division, and peer baselines
- separate large sectors from high-LQ small sectors
- show employment, LQ, wage, and share context where available
- identify persistent strengths, emerging sectors, mean reversion, and
  inconclusive cases using the reviewed national method
- retain sector-specific coverage and source notes

## 5. Current repository assets

- 2012–2024 QCEW broad-sector employment, shares, wages, and LQs in
  `gold.economics_industry_wide`
- Industry Explorer D1 sector taxonomy, trend, specialization, and shift-share
  prior art
- Benchmarking comparison sets
- Time-Series and Peers context
- A1 industry decomposition work
- detailed QCEW Silver inputs, subject to audit if broader Gold sectors are too
  coarse

## 6. Audit findings to verify

- The Gold panel is national and recurring but aggregates to roughly twelve
  broad private-sector families.
- LQ and subsequent growth must use non-overlapping or clearly defined periods.
- Employment growth can be unstable for small base values and suppressed
  sectors.
- A high LQ can persist mechanically even while sector employment declines.
- National sector shocks and metro-wide growth need to be separated from local
  specialization effects.
- The Industry Explorer’s first-pass shift-share and LQ/growth views are useful
  prior art but not yet this national research design.

## 7. Provisional outputs

- national CBSA-sector lagged panel and coverage table
- sector-specific specialization/growth estimates and sensitivities
- persistence/mean-reversion classification only if stable
- selected-market sector trajectory and benchmark tables
- finding ledger with robust market-sector cases and counterexamples

## 8. Decisions Epic 1 must prepare

- sector taxonomy and minimum employment/coverage rules
- LQ definition/source and benchmark year
- growth outcome and horizon
- pooled versus sector-specific model role
- national-relative or shift-share alternatives
- size weighting and outlier handling
- stable cohort and shock-period treatment
- standard market deep-dive classifications

## 9. Non-goals

- treating specialization as a policy recommendation
- claiming causal growth effects from LQ alone
- hiding small-base or suppression behavior
- mixing sector taxonomies without an explicit crosswalk
- selecting only successful specialized sectors for the market story

