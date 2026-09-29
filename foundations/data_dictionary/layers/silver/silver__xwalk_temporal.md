# Data Dictionary: silver.xwalk_temporal

2010 Census tract to 2020 Census tract temporal restatement relationship. One
row per source tract, target tract, and basis.

- Land-area edges use the Census national tract relationship file.
- Population and housing-unit edges apportion 2010 PL 94-171 block counts by
  Census 2010-to-2020 block-intersection land area.
- `change_type` exposes `unchanged`, `split`, or `redrawn`; use it in consumer
  disclosure rather than presenting boundary change as ordinary growth.
- `quality_flag`, denominators, and weight sums preserve incomplete or
  zero-denominator cases.
