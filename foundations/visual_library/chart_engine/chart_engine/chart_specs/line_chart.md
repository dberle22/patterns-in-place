---
chart_type: line_chart
backend: altair
required_fields: [period, value, series]
optional_fields: [subtitle]
column_mapping: {}
default_benchmark: national_median
---
# Line Chart

**Use for:** trend questions — one or more series over time, e.g. metro
vs. national.

**Required fields**
- `period` — x-axis (year or date)
- `value` — the metric
- `series` — the line grouping (e.g. "Jacksonville" vs "US National")

**Optional fields**
- `subtitle`

**Notes:** the first distinct value in `series` (by row order) is drawn
in the theme's primary color; every other series uses the benchmark
color. Designed for 2–3 series max — more than that, use small multiples
instead.
