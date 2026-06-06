# EDA 01 Summary

## What this checked

Whether the US and regional vacancy-rate series are complete enough to support
a five-line comparison chart.

## Takeaways

- Coverage is complete for this insight: the `us` row and all `4` Census
  regions have full annual series from `2012` through `2024`.
- Each geography has `13` rows and `0` null, NaN, or infinite
  `vacancy_rate` values.
- The regional labels in the source table are `Midwest Region`,
  `Northeast Region`, `South Region`, and `West Region`.

## Why it matters for this insight

- We can build a clean regional trend chart without any gap-filling or label
  reconstruction.
- If we want shorter legend labels in production SQL, that should be a display
  choice rather than a data-quality workaround.
