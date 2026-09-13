# Q1 — Epic 5 Index Method Note

**Status:** Candidate method for review — not yet adopted

## Working definition

Overheating is not simply high housing cost, rapid price appreciation, or weak
construction on its own. It is persistent market pressure in which demand and
price/rent momentum outpace the observed supply response, while affordability
is deteriorating or already strained.

The index should answer a narrow question: **which CBSA or county markets show
the strongest combination of pressure, weak response, and worsening ability to
pay?** It must not claim that the relationship proves causation or that every
high-cost market is overheated.

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

## Cost-to-income is a separate outcome family

Levels tell us whether housing is expensive now; changes tell us whether it is
becoming less attainable. Keep renter and owner outcomes separate:

- `rent_to_income_5yr_change`: change in annualized median gross rent divided
  by median household income.
- `value_to_income_5yr_change`: change in median home value divided by median
  household income.
- `owner_cost_to_income_*_5yr_change`: optional parallel owner measures,
  separately for owners with and without a mortgage.

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
| Affordability deterioration | Five-year rent-to-income change; five-year value-to-income change; owner-cost ratio changes as labeled context | Higher = more deterioration |
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
54.5%, housing stock grew 9.3%, rent-to-income rose 3.0%, and value-to-income
rose 17.2%. Its price/owner-accessibility pressure is stronger than its renter
cost-ratio deterioration, so it should not receive a one-dimensional label.

## Next Epic 5 build steps

1. Add five-year housing-stock growth, cumulative permit response, and
   renter/owner cost-ratio-change fields to the Q1 mart.
2. Build the four component scores and explicit complete-family inclusion rule.
3. Render momentum-versus-response and affordability-deterioration views.
4. Compare equal-weight and two alternative weighting schemes against the
   publisher overheating mart and known markets.
5. Decide whether the composite is useful enough to retain; component-led
   classification remains the fallback.
