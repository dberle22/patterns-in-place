# EDA 01 Summary

## What this checked

Whether 2024 CBSA vacancy data is complete enough to rank, and how much the
distribution changes once we apply a "major metro" population cutoff.

## Takeaways

- 2024 CBSA coverage is complete for this use case: there are `935` CBSA rows
  with no null, NaN, or infinite `vacancy_rate` values, and no null `hu_total`
  or `pop_total` values after joining population.
- The CBSA universe is very broad without a filter, ranging from `12,616`
  people to `19.8M`, which mixes true large metros with very small vacation and
  retirement markets.
- A `250k+` cutoff leaves `197` metros. That is a healthy ranking set and
  materially changes the distribution:
  all CBSAs have a `13.0%` average vacancy rate and `58.3%` max, while the
  `250k+` set has a `9.5%` average vacancy rate and `33.4%` max.
- Tightening the filter further to `500k+` leaves `110` metros with an `8.4%`
  average, and `1M+` leaves `56` metros with a `7.8%` average.

## Why it matters for this insight

- The question brief's `250k+` threshold is a good editorial choice: it removes
  the most distorted small-market outliers while still leaving nearly 200 large
  enough metros to rank.
- Using all CBSAs would overstate how loose metro housing markets are because
  the highest-vacancy places are disproportionately small seasonal markets.
