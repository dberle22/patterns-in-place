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

## Source Spec

## Visual Overview

**What it's for:**
- Show the density shape of a high-volume two-metric relationship without overplotting.

**Questions it answers:**
- Where do most observations sit?
- Are there dense clusters or sparse outliers?
- How does the relationship structure differ across groups?

**Best when:**
- Hundreds to thousands of points need summarizing.

**Not ideal when:**
- Individual geography labels are the story.

---

## Variants

- Hexbin
- 2D rectangular binning
- Weighted density
- Faceted density
- Hybrid density plus highlighted points

---

## Required Data Contract

**Base grain:**
- One observation per row per time window.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `time_window`
- `x_value`
- `y_value`
- `x_label`
- `y_label`
- `source`
- `vintage`

**Optional fields (recommended):**
- `group`
- `weight_value`
- `highlight_flag`
- `note`

---

## Filters and Assumptions

- Default to one time window per view.
- Decide and disclose outlier handling.
- Do not mix incompatible geography levels.

---

## Pre-processing Required

- Drop or flag missing X/Y values.
- Validate weights when used.
- Document transforms such as log scaling.

---

## Visual Specs

**Core encodings:**
- X-axis = `x_value`
- Y-axis = `y_value`
- Fill color = bin count or weighted sum

**Hard requirements:**
- Subtitle states binning method and statistic.
- Legend explains count vs weighted mass.
- Axis labels include units.
- Source/vintage is included.

**Optional add-ons:**
- Highlight overlays
- Reference lines
- Facets by group

---

## Interpretation and QA Notes

**How to read it:**
- More intense bins represent more observations or more weighted mass.

**Common pitfalls:**
- Bin size too coarse or too noisy
- Undisclosed log scaling
- Confusing density with desirability

**Quick QA checks:**
- Legend matches the statistic shown.
- Bin resolution is readable.
- Filters and weights match the subtitle.

---

## Example Question Bank

- Across all ZCTAs, where do most neighborhoods sit on income vs rent burden?
- Are there distinct clusters with both high growth and high rent burden?
- In a target CBSA, what is the density pattern of home value-to-income vs rent-to-income?
- How does affordability density differ across regions?
- If weighted by population, where do most people fall on the tradeoff curve?

## Question Coverage

Generated from `visual_library/charts/hexbin/question_coverage.md`.

# Hexbin Question Coverage

## Canonical Test Cases
- `hexbin_affordability_density`
- `hexbin_growth_vs_burden_clusters`
- `hexbin_target_cbsa_tradeoff_shape`
- `hexbin_regional_density_compare`
- `hexbin_population_weighted_tradeoff`

## Source Question Mapping
- Where most neighborhoods sit on income vs rent burden -> `hexbin_affordability_density`
- Distinct clusters of high growth and high rent burden -> `hexbin_growth_vs_burden_clusters`
- Density of home value-to-income vs rent-to-income in target CBSA -> `hexbin_target_cbsa_tradeoff_shape`
- Density differences across regions or CBSA types -> `hexbin_regional_density_compare`
- Population-weighted affordability tradeoff -> `hexbin_population_weighted_tradeoff`

