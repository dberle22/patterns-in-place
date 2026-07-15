---
chart_type: scatter
backend: altair
required_fields:
- geo_level
- geo_id
- geo_name
- time_window
- x_value
- y_value
- x_label
- y_label
optional_fields:
- source
- vintage
- group
- size_value
- label_flag
- note
column_mapping: {}
default_benchmark: null
---
# Scatter Plots

Generated from `visual_library/charts/scatter/scatter_spec.md`.

Backend: `altair`. Required fields: `geo_level, geo_id, geo_name, time_window, x_value, y_value, x_label, y_label`.

## Source Spec

## Visual Overview

**What it’s for:**
Compare two metrics across geographies to spot outliers, tradeoffs, and peer clusters.

**Questions it answers:**

- Which markets are strong on both metrics?
- Which are weirdly high/low relative to the trend?
- Where are the tradeoffs?

**Best when:**

- Single-year snapshots or growth-window snapshots across CBSAs/counties/ZCTAs.

**Not ideal when:**

- Very high point counts without density handling (e.g., thousands of ZCTAs).
- When a third variable is the real story.

## Variants

- Standard scatter: best default relationship + outlier scan.
- Quadrant scatter (median lines): best for four-box narratives (strong/weak/tradeoff).
- Bubble scatter: encode importance (population, housing units).
- Hexbin/density scatter: for ZCTA-heavy views (reduce overplotting).
- Faceted scatter: compare relationship by region/division/time window.

## Implementation Defaults (Current)

- Primary reference implementation: National CBSA scatter with labels, bubble size, and reference line.
- Keep size encoding in the base implementation.
- Support two optional highlight modes:
  - Label overlay for selected subset.
  - Color-highlighted subset points.
- Include optional trend/reference line pattern.
- Keep density/hexbin as a separate variant, not the default scatter mode.

## Required Data Contract

**Base grain:**

- 1 row per geo per snapshot/time_window.

**Required fields:**

- `geo_level`
- `geo_id`
- `geo_name`
- `time_window`
- `x_value`
- `y_value`
- `x_label`
- `y_label`

**Optional fields:**

- `source`
- `vintage`
- `group` (region/division/type)
- `size_value`
- `label_flag`
- `note`

## Filters and Assumptions

- Filter to one `time_window` unless faceting.
- Do not mix `geo_levels` unless explicitly comparing.

## Pre-processing Required

- Drop/flag missing `x_value` and `y_value`.
- Define growth metrics clearly.
- Document log transform/winsorization if used.

## Visual Specs

**Core encodings:**
- X-axis = `x_value`
- Y-axis = `y_value`
- Color = `group` (optional)
- Size = `size_value` (bubble variant)
- Labels = `label_flag` (optional)

**Hard requirements:**

- Title + subtitle include `geo_level` + `time_window`.
- Axis labels include units.
- Consistent number formatting (per Standards).

**Optional add-ons:**

- Source + vintage footnote.
- Quadrant lines.
- Benchmark point.
- Trend line + correlation.
- Auto-label top/bottom outliers.
- Highlight selected geos.
- Facets.

## Interpretation and QA Notes

**How to read it:**

- Upper-right: strong on both metrics.
- Lower-left: weak on both metrics.
- Other quadrants show tradeoffs.
- Outliers should prompt investigation.

**Common pitfalls:**

- Overplotting (use density).
- Spurious correlation (check per-capita vs totals).
- Scale issues (declare log transforms).

**Quick QA checks:**

- Units are correct.
- Intended `time_window` is applied.
- Missing values handled intentionally.
- Outliers validated against raw/source data.

## Example Question Bank

- Which CBSAs have high income growth but comparatively low rent burden?
- Which counties have unusually high home values relative to incomes?
- Which ZCTAs are outliers within a given CBSA on rent vs income?

## Question Coverage

Generated from `visual_library/charts/scatter/question_coverage.md`.

# Scatter Question Coverage

## Canonical Test Cases
- `scatter_q1_cbsa_income_growth_vs_rent_burden`: CBSA growth versus affordability tradeoff.
- `scatter_q2_county_home_value_vs_income`: county valuation outlier scan.
- `scatter_q3_zcta_rent_vs_income_outliers`: within-CBSA neighborhood outlier scan.

## Source Question Mapping
- "Which CBSAs have high income growth but comparatively low rent burden?" -> `scatter_q1_cbsa_income_growth_vs_rent_burden`
- "Which counties have unusually high home values relative to incomes?" -> `scatter_q2_county_home_value_vs_income`
- "Which ZCTAs are outliers within a given CBSA on rent vs income?" -> `scatter_q3_zcta_rent_vs_income_outliers`

