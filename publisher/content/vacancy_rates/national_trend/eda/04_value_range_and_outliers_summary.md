# EDA 04 Summary

## What this checked

The overall range of vacancy rates by geography, plus a quick outlier scan for
county and CBSA values.

## Key findings

- The US series is tightly bounded: `10.1%` to `12.5%` across 2012-2024.
- Regions run from `8.5%` to `14.5%`; divisions from `7.8%` to `15.9%`; states
  from `7.0%` to `24.7%`.
- CBSA values are much wider: `3.0%` to `70.3%`.
- County values are wider still: `1.7%` to `88.3%`.
- The most extreme county outliers include places like Daggett County, Utah and
  Hamilton County, New York, both with very small housing-unit counts and very
  high vacancy rates.

## Takeaways

- Extreme vacancy rates at sub-state geographies are real in the table, but they
  behave like niche-market or second-home outliers rather than useful context
  for a national headline chart.
- The US series is stable and interpretable, which supports using it as the
  anchor for the first post in the topic.

## Why it matters for this insight

- This reinforces the topic note that vacation and rural markets can dominate
  high-vacancy rankings at smaller geographies.
- For `national_trend`, the cleanest story is still the US line alone, with
  metro and state variation saved for later insights.
