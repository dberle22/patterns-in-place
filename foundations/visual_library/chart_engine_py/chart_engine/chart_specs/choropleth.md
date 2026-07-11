---
chart_type: choropleth
backend: matplotlib
required_fields:
- geo_level
- geo_id
- geo_name
- time_window
- metric_value
- metric_label
- source
- vintage
optional_fields:
- geometry
- bin
- benchmark_value
- highlight_flag
- group
- note
column_mapping: {}
default_benchmark: null
---
# Choropleth Maps

Generated from `visual_library/charts/choropleth/choropleth_spec.md`.

Backend: `matplotlib`. Required fields: `geo_level, geo_id, geo_name, time_window, metric_value, metric_label, source, vintage`.
