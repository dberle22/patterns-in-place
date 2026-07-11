---
chart_type: age_pyramid
backend: altair
required_fields:
- geo_level
- geo_id
- geo_name
- period
- age_bin
- sex
- pop_value
- source
- vintage
optional_fields:
- pop_total
- pop_share
- benchmark_label
- highlight_flag
- note
column_mapping: {}
default_benchmark: null
---
# Age Pyramid

Generated from `visual_library/charts/age_pyramid/age_pyramid_spec.md`.

Backend: `altair`. Required fields: `geo_level, geo_id, geo_name, period, age_bin, sex, pop_value, source, vintage`.
