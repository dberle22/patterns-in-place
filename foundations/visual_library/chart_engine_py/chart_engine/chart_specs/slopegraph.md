---
chart_type: slopegraph
backend: altair
required_fields:
- geo_level
- geo_id
- geo_name
- period
- metric_id
- metric_label
- metric_value
- source
- vintage
optional_fields:
- group
- highlight_flag
- benchmark_label
- rank
- note
column_mapping: {}
default_benchmark: null
---
# Slopegraph

Generated from `visual_library/charts/slopegraph/slopegraph_spec.md`.

Backend: `altair`. Required fields: `geo_level, geo_id, geo_name, period, metric_id, metric_label, metric_value, source, vintage`.

## Source Spec

## Visual Overview

**What it's for:**
- Compare values across exactly two periods and emphasize change direction and size.

**Questions it answers:**
- Who improved or declined the most?
- Did ordering shift?
- How large is the gap between start and end?

**Best when:**
- Two periods and a moderate number of entities are in scope.

**Not ideal when:**
- Full time-series dynamics or a very large entity set matter.

---

## Variants

- Geo change slopegraph
- Rank slopegraph
- Indexed slopegraph
- Benchmark slopegraph
- Grouped slopegraph

---

## Required Data Contract

**Base grain:**
- One row per entity per period, with exactly two periods per chart.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `period`
- `metric_id`
- `metric_label`
- `metric_value`
- `source`
- `vintage`

**Optional fields (recommended):**
- `group`
- `highlight_flag`
- `benchmark_label`
- `rank`
- `note`

---

## Filters and Assumptions

- Exactly two periods.
- One geography level and one metric per chart.
- Entity universe must be stated.

---

## Pre-processing Required

- Select start and end periods.
- Decide ordering logic.
- Optionally compute delta or indexed values.

---

## Visual Specs

**Core encodings:**
- X-axis = start/end period
- Y-axis = value or rank
- Line = entity

**Hard requirements:**
- Subtitle states the two periods and any transform.
- Units are explicit.
- Label strategy is readable.
- Source/vintage is included.

**Optional add-ons:**
- End labels
- Delta annotations
- Benchmark line

---

## Interpretation and QA Notes

**How to read it:**
- Steeper slope means bigger change.

**Common pitfalls:**
- More than two periods
- Hidden missing endpoints
- Ambiguous ordering

**Quick QA checks:**
- Exactly two periods are present.
- Entity count matches the intended filter.
- Missing handling is documented.

---

## Example Question Bank

- Which CBSAs saw the largest change in real per capita income between 2013 and 2023?
- How did rent burden change from 2018 to 2023 for counties within the target CBSA?
- Did affordability improve or worsen pre vs post 2020 for a peer set?
- Which ZCTAs moved most on home value-to-income between two periods?
- How did the target CBSA shift relative to its region benchmark?

## Question Coverage

Generated from `visual_library/charts/slopegraph/question_coverage.md`.

# Slopegraph Question Coverage

## Canonical Test Cases
- `slope_income_change_cbsas`
- `slope_county_rent_burden`
- `slope_peer_affordability_shift`
- `slope_zcta_value_to_income_change`
- `slope_target_vs_region`

## Source Question Mapping
- Largest CBSA change in real per-capita income -> `slope_income_change_cbsas`
- County rent burden change within target CBSA -> `slope_county_rent_burden`
- Pre/post 2020 peer affordability shift -> `slope_peer_affordability_shift`
- ZCTA home value-to-income movement -> `slope_zcta_value_to_income_change`
- Target CBSA versus region benchmark -> `slope_target_vs_region`

