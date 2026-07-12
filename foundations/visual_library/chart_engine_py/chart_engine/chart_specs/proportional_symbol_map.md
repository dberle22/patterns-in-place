---
chart_type: proportional_symbol_map
backend: matplotlib
required_fields:
- geo_level
- geo_id
- geo_name
- time_window
- size_value
- size_label
- source
- vintage
optional_fields:
- geometry
- lon
- lat
- color_group
- highlight_flag
- label_flag
- note
column_mapping: {}
default_benchmark: null
---
# Proportional Symbol Map

Generated from `visual_library/charts/proportional_symbol_map/proportional_symbol_map_spec.md`.

Backend: `matplotlib`. Required fields: `geo_level, geo_id, geo_name, time_window, size_value, size_label, source, vintage`.

## Source Spec

## Visual Overview

**What it's for:**
- Map totals with symbol size so concentration and hierarchy are visible without polygon area bias.

**Questions it answers:**
- Where are the biggest totals?
- How concentrated is activity?
- Where are the secondary nodes?

**Best when:**
- The mapped metric is a total such as population, housing units, jobs, permits, or parcels.

**Not ideal when:**
- The mapped metric is already a size-controlled rate.

---

## Variants

- Pure bubble map
- Bubble plus color group
- Bubble over choropleth
- Top-N-only bubble map
- Bubble plus highlight

---

## Required Data Contract

**Base grain:**
- One row per geography or point entity per time window.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `time_window`
- `size_value`
- `size_label`
- `source`
- `vintage`

**Optional fields (recommended):**
- `geometry`
- `lon`
- `lat`
- `color_group`
- `highlight_flag`
- `label_flag`
- `note`

---

## Filters and Assumptions

- Use one geography level per map.
- Default to one time window.
- Make decluttering rules explicit.

---

## Pre-processing Required

- Choose symbol scaling, usually square-root radius.
- Derive centroids or explicit coordinates.
- Apply Top N or other clutter management when necessary.

---

## Visual Specs

**Core encodings:**
- Position = `lon`/`lat` or derived centroid
- Size = `size_value`
- Optional color = `color_group` or `highlight_flag`

**Hard requirements:**
- Subtitle says bubbles represent totals and notes any Top N filter.
- Size legend shows scale and units.
- Source/vintage is included.

**Optional add-ons:**
- Labels for top bubbles
- Light context boundaries
- Highlight styling
- Insets for dense regions

---

## Interpretation and QA Notes

**How to read it:**
- Larger bubbles indicate larger totals and more concentration.

**Common pitfalls:**
- Overlap hiding values
- Misleading size scaling
- Using bubbles for rates

**Quick QA checks:**
- Symbol scale looks sensible.
- Coordinates are correct.
- Filtering rules match the subtitle.

---

## Example Question Bank

- Where are population and housing units most concentrated?
- Which counties account for the majority of new permits?
- Within a CBSA, where are the largest ZCTAs by population?
- Where are the largest retail parcel clusters?
- How concentrated are jobs or establishments across counties?

## Question Coverage

Generated from `visual_library/charts/proportional_symbol_map/question_coverage.md`.

# Proportional Symbol Map Question Coverage

## Canonical Test Cases
- `bubble_population_concentration`
- `bubble_permit_majority_counties`
- `bubble_largest_zctas_in_cbsa`
- `bubble_retail_parcel_clusters`
- `bubble_jobs_concentration`

## Source Question Mapping
- Population and housing concentration -> `bubble_population_concentration`
- Counties driving most new permits -> `bubble_permit_majority_counties`
- Largest ZCTAs by population in a CBSA -> `bubble_largest_zctas_in_cbsa`
- Largest retail parcel clusters -> `bubble_retail_parcel_clusters`
- Jobs or establishment concentration across counties -> `bubble_jobs_concentration`

