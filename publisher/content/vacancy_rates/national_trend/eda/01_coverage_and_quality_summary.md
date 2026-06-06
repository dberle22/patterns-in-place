# EDA 01 Summary

## What this checked

Coverage by geography and year, plus whether `vacancy_rate` is clean enough to
use directly for the national trend.

## Takeaways

- `vacancy_rate` exists from 2012 through 2024 for every benchmark geography we
  care about here: `us`, `region`, `division`, `state`, and `cbsa`.
- The national series is complete: 13 US rows for 2012-2024, with no null, NaN,
  or infinite values.
- Region, division, state, county, and CBSA rows are also fully finite for
  `vacancy_rate`.
- Non-finite values only show up at smaller geographies:
  11,514 tract rows, 7,729 ZCTA rows, and 2,903 place rows are `NaN`.

## Why it matters for this insight

- The national trend post can safely use `geo_level = 'us'` with no cleaning
  step beyond converting the decimal to percent.
- Smaller-geography noise is a reminder not to use tract, ZCTA, or place values
  for this national headline EDA.
