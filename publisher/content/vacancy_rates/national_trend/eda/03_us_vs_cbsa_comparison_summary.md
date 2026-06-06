# EDA 03 Summary

## What this checked

Whether adding a second "US metro average" line would deepen the story or muddy
it.

## Key numbers

- In 2024:
  `us = 10.1%`, `cbsa weighted = 9.4%`, `cbsa median = 11.3%`,
  `cbsa unweighted average = 13.0%`.
- In 2019:
  `us = 12.1%`, `cbsa weighted = 11.3%`, `cbsa median = 13.4%`,
  `cbsa unweighted average = 15.3%`.
- The unweighted CBSA average is above the US series in every year.
- The weighted CBSA rate is below the US series in every year.

## Takeaways

- "US average" and "US metro average" are not apples-to-apples series.
- The unweighted CBSA average is heavily influenced by smaller metros and sits
  roughly 2.9pp above the national figure in 2024.
- The weighted CBSA rollup is closer in concept to the national market, but it
  still runs lower because it excludes non-CBSA areas and uses a different
  population frame.
- All CBSA variants decline after 2019, so the direction matches the national
  story even though the levels differ.

## Recommendation

- Keep the final chart focused on the clean `geo_level = 'us'` line.
- If we want a second national comparison later, regional trends are a cleaner
  follow-on than an ad hoc metro-average benchmark.
