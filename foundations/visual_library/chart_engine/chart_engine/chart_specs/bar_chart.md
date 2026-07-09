---
chart_type: bar_chart
backend: altair
required_fields: [entity, value]
optional_fields: [subtitle]
column_mapping: {}
default_benchmark: null
---
# Bar Chart

**Use for:** ranking questions — "top N metros by X."

**Required fields**
- `entity` — the thing being ranked (e.g. CBSA name)
- `value` — the metric being ranked on

**Optional fields**
- `subtitle` — shown under the chart title

**Notes:** sorted descending by `value` automatically. Keep to 15–20
entities max before it stops being legible as a horizontal bar.
