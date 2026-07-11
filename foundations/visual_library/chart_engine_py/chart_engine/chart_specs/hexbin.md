---
chart_type: hexbin
backend: matplotlib
required_fields:
- geo_level
- geo_id
- geo_name
- time_window
- x_value
- y_value
- x_label
- y_label
- source
- vintage
optional_fields:
- group
- weight_value
- highlight_flag
- note
column_mapping: {}
default_benchmark: null
---
# Hexbin / 2D Binned Scatter

Generated from `visual_library/charts/hexbin/hexbin_spec.md`.

Backend: `matplotlib`. Required fields: `geo_level, geo_id, geo_name, time_window, x_value, y_value, x_label, y_label, source, vintage`.
