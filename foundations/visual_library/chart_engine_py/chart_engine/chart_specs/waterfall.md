---
chart_type: waterfall
backend: altair
required_fields:
- geo_level
- geo_id
- geo_name
- time_window
- total_label
- component_id
- component_label
- component_value
- source
- vintage
optional_fields:
- start_period
- end_period
- component_delta
- unit_label
- component_group
- benchmark_label
- highlight_flag
- sort_order
- note
column_mapping: {}
default_benchmark: null
---
# Waterfall Chart

Generated from `visual_library/charts/waterfall/waterfall_spec.md`.

Backend: `altair`. Required fields: `geo_level, geo_id, geo_name, time_window, total_label, component_id, component_label, component_value, source, vintage`.

## Source Spec

## Visual Overview

**What it's for:**
- Explain how a total level or total change is built from additive components.

**Questions it answers:**
- What components drive the total?
- Which pieces contribute most to growth or decline?
- What offsets what?

**Best when:**
- A clean additive breakdown exists.

**Not ideal when:**
- Components overlap or the story requires many time points.

---

## Variants

- Level decomposition
- Change decomposition
- Benchmark comparison
- Percent-contribution waterfall
- Grouped waterfall

---

## Required Data Contract

**Base grain:**
- One row per component per geography per snapshot or change window.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `time_window`
- `total_label`
- `component_id`
- `component_label`
- `component_value`
- `source`
- `vintage`

**Optional fields (recommended):**
- `start_period`
- `end_period`
- `component_delta`
- `unit_label`
- `component_group`
- `benchmark_label`
- `highlight_flag`
- `sort_order`
- `note`

---

## Filters and Assumptions

- Components must add to the total or total change.
- The component list must be stable and explainable.
- Keep component count manageable.

---

## Pre-processing Required

- Compute component deltas for change views.
- Set a canonical ordering.
- Optionally roll tiny components into `Other`.

---

## Visual Specs

**Core encodings:**
- X-axis = ordered components
- Y-axis = running total position
- Bar sign = positive or negative contribution

**Hard requirements:**
- Title states what is being decomposed.
- Subtitle states units and window.
- Start and end totals are clear.
- Source/vintage is included.

**Optional add-ons:**
- Component labels
- Group separators
- Benchmark side-by-side comparison

---

## Interpretation and QA Notes

**How to read it:**
- Each component adds or subtracts from the running total.

**Common pitfalls:**
- Non-additive components
- Double counting
- Too many tiny parts

**Quick QA checks:**
- Components sum to the total within tolerance.
- Units are consistent.
- Any `Other` rollup is documented.

---

## Example Question Bank

- What drove the change in personal income from 2013 to 2023 in the target CBSA?
- How does the income component mix differ from a benchmark?
- What components explain GDP change by sector?
- For housing stock change, what share came from 1-unit vs multi-unit additions?
- Which components offset growth in the last 5 years?

## Question Coverage

Generated from `visual_library/charts/waterfall/question_coverage.md`.

# Waterfall Question Coverage

## Canonical Test Cases
- `waterfall_income_change_drivers`
- `waterfall_income_mix_compare`
- `waterfall_gdp_sector_change`
- `waterfall_housing_stock_components`
- `waterfall_negative_offsets`

## Source Question Mapping
- Drivers of income change -> `waterfall_income_change_drivers`
- Income component mix versus benchmark -> `waterfall_income_mix_compare`
- GDP change by sector -> `waterfall_gdp_sector_change`
- Housing stock change by unit type -> `waterfall_housing_stock_components`
- Negative drivers offsetting growth -> `waterfall_negative_offsets`

