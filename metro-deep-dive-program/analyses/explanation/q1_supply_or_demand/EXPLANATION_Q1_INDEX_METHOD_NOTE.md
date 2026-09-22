# Q1 — Epic 5 Index Method Note

**Status:** Exploratory candidate method; no standard Q1 index has been
selected, and component-led market analysis remains required

## Working definition

Overheating is not simply high housing cost, rapid price appreciation, or weak
construction on its own. It is persistent market pressure in which demand and
price/rent momentum outpace the observed supply response, while affordability
is deteriorating or already strained.

The index should answer a narrow question: **which CBSA or county markets show
the strongest combination of pressure, weak response, and worsening ability to
pay?** It must not claim that the relationship proves causation or that every
high-cost market is overheated.

## Current use policy

Use the composite only to locate markets in the national distribution, compare
their component profiles, and prioritize deeper review while the alternatives
are tested. Do not use it as a market conclusion, a causal claim, or a
replacement for the raw component evidence.
Every market-level interpretation must inspect momentum, renter burden and
market access, demand, supply response, and relevant coverage/no-signal flags.

## Do not use a raw price-growth / unit-growth ratio

Price change is a percentage and new units are a flow/count. Dividing one by
the other produces unstable values when unit growth is near zero or negative,
and it lets small markets dominate the result.

Instead, calculate the measures separately at the same grain and period, turn
them into within-year percentile scores, and show their relationship directly:

- **Momentum:** five-year house-price appreciation and, where available,
  five-year rent appreciation.
- **Supply response:** five-year net housing-unit growth and five-year
  cumulative permitted units per starting housing unit.
- **Imbalance view:** a momentum-versus-response scatter/quadrant. High
  momentum plus low response is the direct visual expression of the proposed
  “prices rising faster than new units” idea.

## Affordability outcomes are separate from market-price proxies

Levels tell us whether housing is expensive now; changes tell us whether it is
becoming less attainable. Keep renter and owner outcomes separate:

- `pct_rent_burden_30plus_change_5yr`: change in the ACS share of renter
  households spending 30% or more of income on rent. This is the primary renter
  household-burden outcome.
- `median_rent_to_all_hh_income_proxy_change_5yr`: change in annualized median
  gross rent divided by ACS median income for all households. This is a market
  price proxy, not a renter-household burden measure and has no 30% cutoff.
- `value_to_income_5yr_change`: change in median home value divided by median
  household income.
- `owner_cost_to_income_*_5yr_change`: optional existing-owner context,
  separately for owners with and without a mortgage; not current-buyer cost.

A market with rapid price growth but stable cost-to-income may have incomes
catching up. A market with modest price growth and sharply worsening ratios can
still be a household-affordability concern. The index should retain both facts
rather than letting one erase the other.

## Candidate four-family diagnostic

Build the following component scores at CBSA and county grain only. Each score
is the mean of its available, direction-adjusted, within-year percentile inputs
and carries an input-count field.

| Family | Initial inputs | Direction |
|---|---|---|
| Momentum | FHFA five-year HPI; ACS five-year rent growth; optional Zillow rent growth | Higher = more pressure |
| Affordability deterioration | Five-year renter-burden change; five-year value-to-income change; owner-cost ratio changes as labelled context | Higher = more deterioration |
| Demand | Five-year population growth; IRS net migration through 2022 as historical context | Higher = more pressure |
| Supply constraint | Inverse five-year housing-unit growth; inverse five-year cumulative permits per starting unit; inverse vacancy rate | Higher = less response / tighter market |

The first candidate composite is the equal-weight mean of the four component
scores. Equal family weights avoid counting price movement three times through
price appreciation, current cost level, and cost-ratio change. The notebook
must show at least two alternatives: a demand/momentum emphasis and a
supply-constraint/affordability-deterioration emphasis.

## Scope and inclusion

- Publish the composite only for CBSA and county grain, where price and permit
  response are observed. Tracts remain a component-led diagnosis.
- Use a five-year window ending in the reported year. Annual permits must be
  summed across the window before normalizing by starting housing stock.
- Exclude rows missing a required family from rankings; retain them in coverage
  and component tables rather than silently averaging across fewer families.
- Use the major-CBSA (population at least 100,000) universe for the primary
  national ranking. Small-market results should remain inspectable but separate
  because percentage changes and small permit counts are more volatile.

## First evidence check

For the 2024 CBSA surface, five-year HPI, housing-stock growth, and
rent/value-to-income-change measures each cover at least 97.6% of CBSAs. The
raw price-minus-stock-growth ordering is dominated by some small, volatile
markets, confirming the need for percentile normalization and a major-market
primary universe.

Richmond's first read demonstrates the intended separation: five-year HPI grew
54.5%, housing stock grew 9.3%, and value-to-income rose 17.2%. Epic 9 should
evaluate its renter-burden change separately from the median-rent/all-household-
income price proxy rather than using either as a one-dimensional label.

## Remaining index research

Compare the equal-weight composite, its two scenario-weight variants, a
component-led diagnosis, and the momentum-versus-supply matrix against the
documented market reads. Select a standard only if it adds a stable,
interpretable orientation signal; otherwise retain component-led analysis as
the Q1 method.
