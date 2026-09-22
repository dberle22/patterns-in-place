# Thematic A7 — Who Is Squeezed Spec

**Status:** Provisional; revise after Epic 1 audit

**Updated:** 2026-09-20

**Family plan:** [THEMATIC_ANALYSES_PLAN.md](../THEMATIC_ANALYSES_PLAN.md)

## 1. Question and purpose

Where do housing price levels and household cost burdens diverge, which groups
are most affected, and how do local incomes and wages help explain the gap?

The analysis should prevent “expensive,” “unaffordable,” and “burdened” from
being used as synonyms. It should show why a high-cost/high-income market and a
lower-cost/low-income market can create different forms of housing pressure.

**Themes crossed:** Housing & Affordability × Industry & Labor.

## 2. Provisional claim and alternatives

**Claim direction to review:** Housing pressure is not captured by price alone;
some lower-price metros show high burden because local incomes and wages are
low, while some high-price metros show different burden patterns across tenure
and income groups.

The claim is weakened if price, burden, and income measures mostly rank metros
the same way or if subgroup coverage cannot support the promised “who” analysis.

## 3. Analytical unit and universe

- National unit: CBSA for broad price, burden, income, and wage comparisons.
- Household-distribution detail: income band, tenure, and burden severity where
  governed CHAS or ACS fields support it.
- Market unit: selected CBSA with county, Place, tract, or ZCTA context only at
  each measure’s valid native grain.
- Time: recurring ACS/FHFA context plus source-specific CHAS snapshots; no
  false common year should be imposed.

## 4. Notebook contracts

### National notebook

The national notebook should:

1. define price level, market-entry cost, renter burden, owner context, income,
   and wages separately
2. show how metro rankings change across those concepts
3. identify meaningful divergence patterns or a typology if stable
4. examine income-band and tenure evidence when coverage supports “who” claims
5. test region, tenure mix, household composition, and source-year sensitivity
6. distinguish household income from worker wages
7. identify market cases and counterexamples from component evidence

### Parameterized market notebook

The market notebook should:

- place the selected CBSA on each reviewed affordability dimension
- compare nation, division, and peers
- show renter burden, severe burden, home-value/income, rent/income, income, and
  wage context without blending denominators
- expose subgroup evidence where available
- show valid tract, Place, and ZCTA context with source and overlap caveats
- provide standard deep dives for high-price/high-income, lower-price/high-
  burden, broad stress, and mixed cases
- retain a no-distinctive-divergence result

## 5. Current repository assets

- Explanation Q1 mart, national and market notebooks, metric contract, and
  affordability-method corrections
- `gold.housing_core_wide`, `gold.housing_market_wide`, and
  `gold.affordability_wide`
- `gold.economics_income_wide`, QCEW wages, OEWS wages, and QWI earnings
- CHAS burden fields at supported grains
- Geography, Benchmarking, Peers, and Time-Series context
- Housing publisher workbenches as non-authoritative prior art

## 6. Audit findings to verify

- Q1 already documents critical distinctions between renter burden, median-rent
  price proxies, existing-owner costs, and market-entry measures.
- Household income and worker/occupation wages have different populations and
  cannot be substituted.
- CHAS and recurring ACS measures have different vintages and detail.
- “Who” may require income band and tenure; metro averages alone cannot answer
  it.
- Price-to-income ratios, burden shares, and residual typologies need component
  transparency.
- ZCTA prices, Place permits, and tract burden are contextual lenses rather
  than one nested partition of the CBSA.

## 7. Provisional outputs

- affordability metric contract and coverage table
- national price/burden/income/wage distributions and divergence views
- subgroup tables where supported
- stable typology or component-led cases, depending on audit results
- selected-market component, subgroup, comparison, and spatial context tables
- finding ledger with denominator and vintage caveats

## 8. Decisions Epic 1 must prepare

- primary meaning of “squeezed” and whether more than one concept remains
- population behind “who”: renter households, owner households, workers,
  income bands, or a declared combination
- primary burden, price, income, and wage measures
- source-year and inflation rules
- typology versus component-led narrative
- missing-data and subgroup-coverage rules
- valid sub-CBSA views
- relationship to Q1 and A2 without duplicating either

## 9. Non-goals

- treating all-household income as a renter-income denominator without labeling
- combining renter and owner measures into one opaque score
- inferring household experience from sector-average wages alone
- recreating Q1’s supply/demand classification
- recommending market policy from descriptive typology alone

