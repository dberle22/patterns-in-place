---
chart_type: strength_strip
backend: altair
required_fields:
- geo_level
- geo_id
- geo_name
- time_window
- metric_id
- metric_label
- metric_value
- source
- vintage
optional_fields:
- metric_group
- direction
- normalized_value
- benchmark_label
- highlight_flag
- note
column_mapping: {}
default_benchmark: null
---
# Strength Strip / Scorecard Bars

Generated from `visual_library/charts/strength_strip/strength_strip_spec.md`.

Backend: `altair`. Required fields: `geo_level, geo_id, geo_name, time_window, metric_id, metric_label, metric_value, source, vintage`.
