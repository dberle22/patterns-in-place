---
chart_type: highlight_context_map
backend: matplotlib
required_fields:
- geo_level
- geo_id
- geo_name
- time_window
- source
- vintage
- highlight_flag
optional_fields:
- metric_value
- metric_label
- geometry
- context_group
- neighbor_flag
- bin
- note
column_mapping: {}
default_benchmark: null
---
# Highlight + Context Map

Generated from `visual_library/charts/highlight_context_map/highlight_context_map_spec.md`.

Backend: `matplotlib`. Required fields: `geo_level, geo_id, geo_name, time_window, source, vintage, highlight_flag`.

## Source Spec

## Visual Overview

**What it's for:**
- Put a selected geography in focus while preserving the surrounding map context.

**Questions it answers:**
- Where is the target?
- What surrounds it?
- Is it an outlier relative to nearby geographies?

**Best when:**
- The narrative needs a focal market map rather than a full analytical choropleth.

**Not ideal when:**
- Many highlighted targets need comparison at once.

---

## Variants

- Single highlight
- Highlight plus neighbor ring
- Highlight on choropleth
- Inset zoom
- Shortlist highlight map

---

## Required Data Contract

**Base grain:**
- One row per geography per time window plus geometry.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `time_window`
- `source`
- `vintage`
- `highlight_flag`

**Optional fields (recommended):**
- `metric_value`
- `metric_label`
- `geometry`
- `context_group`
- `neighbor_flag`
- `bin`
- `note`

---

## Filters and Assumptions

- Use one geography level per panel.
- Make highlight selection explicit.
- Treat missing joins as blocking QA issues.

---

## Pre-processing Required

- Define the highlight set.
- Compute neighbor ring or context set when needed.
- Join geometry and optional background metric.

---

## Visual Specs

**Core encodings:**
- Highlight style = selected geography
- Context style = muted surrounding geography
- Optional background = choropleth fill

**Hard requirements:**
- Title names the highlighted geography.
- Subtitle explains the context shown.
- Legend distinguishes highlight from background encoding.
- Source/vintage is included.

**Optional add-ons:**
- Inset zoom
- Labels for the target and key neighbors
- Context callout box

---

## Interpretation and QA Notes

**How to read it:**
- The highlight shows where to look; the context shows how it sits in place.

**Common pitfalls:**
- Over-layered styling
- Ghost geometries from join failures
- Context extent that is too broad or too narrow

**Quick QA checks:**
- Highlight IDs are correct.
- Join rate is high.
- Extent matches the subtitle.

---

## Example Question Bank

- Where is the target CBSA and what surrounds it?
- Which ZCTAs are affordability outliers within the target CBSA?
- Are neighboring counties experiencing similar growth?
- How does the target compare to adjacent counties on rent burden?
- Which shortlisted markets cluster geographically?

## Question Coverage

Generated from `visual_library/charts/highlight_context_map/question_coverage.md`.

# Highlight + Context Map Question Coverage

## Canonical Test Cases
- `highlight_target_locator`
- `highlight_zcta_outliers`
- `highlight_neighbor_growth`
- `highlight_adjacent_rent_burden`
- `highlight_shortlist_geography`

## Source Question Mapping
- Where is the target CBSA and what surrounds it -> `highlight_target_locator`
- ZCTA affordability outliers in target CBSA -> `highlight_zcta_outliers`
- Neighbor counties with similar growth -> `highlight_neighbor_growth`
- Adjacent county rent burden comparison -> `highlight_adjacent_rent_burden`
- Sweet Spot clustering versus isolation -> `highlight_shortlist_geography`

