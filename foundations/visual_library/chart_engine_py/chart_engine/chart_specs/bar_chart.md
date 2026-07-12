---
chart_type: bar_chart
backend: altair
required_fields:
- entity
- value
optional_fields:
- subtitle
column_mapping: {}
default_benchmark: null
---
# Bar Charts

Generated from `visual_library/charts/bar/bar_spec.md`.

Backend: `altair`. Required fields: `entity, value`.

## Source Spec

## Visual Overview

**What it's for:**
- Compare magnitudes across geographies, categories, or time windows with fast ranking readability.

**Questions it answers:**
- Who is highest or lowest?
- How big are the gaps?
- How does a target geography rank against peers?

**Best when:**
- One snapshot or one growth window is the story.

**Not ideal when:**
- The story is continuous change over time or a two-metric relationship.

---

## Variants

- Ranked horizontal bar
- Grouped bar
- Stacked and 100% stacked bar
- Diverging bar
- Highlighted peer comparison

## Implementation Defaults (Current)

- Primary reference implementation: ranked horizontal bars with direct value labels.
- First canonical test cases:
  - national CBSA ranking for `income_pc_growth_5yr`
  - within-target county ranking for `rent_to_income`
- Current gold-layer sources:
  - `gold.economics_income_wide`
  - `gold.affordability_wide`
- Deferred for a later pass:
  - highlighted target-versus-peer ranking
  - diverging benchmark delta bars
  - grouped/stacked composition behavior

---

## Required Data Contract

**Base grain:**
- One row per category per metric per time window.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `time_window`
- `metric_id`
- `metric_label`
- `metric_value`
- `source`
- `vintage`

**Optional fields (recommended):**
- `rank`
- `group`
- `series`
- `share_value`
- `highlight_flag`
- `benchmark_value`
- `note`

---

## Filters and Assumptions

- Default to sorted bars with a clear filter scope.
- Use Top/Bottom N for larger universes.
- Keep grouped series to a small set.

---

## Pre-processing Required

- Rank after filtering.
- Compute `share_value` for composition variants.
- Compute benchmark deltas for diverging variants.

---

## Visual Specs

**Core encodings:**
- Axis category = `geo_name`
- Bar length = `metric_value`
- Color = `series` or `highlight_flag`

**Hard requirements:**
- Title includes metric and scope.
- Subtitle includes time window and filter set.
- Sorting logic is explicit.
- Units and source/vintage are shown.

**Optional add-ons:**
- Data labels
- Benchmark reference
- Highlighted target bars

---

## Interpretation and QA Notes

**How to read it:**
- Compare bar lengths for rank and gap size.

**Common pitfalls:**
- Too many categories
- Inconsistent sort logic
- Mixing incomparable units

**Quick QA checks:**
- Sort order matches the stated rule.
- Top/Bottom truncation is disclosed.
- Shares sum correctly when used.

---

## Example Question Bank

- What are the top 25 CBSAs by 5-year median income growth?
- Which counties in this CBSA have the highest rent-to-income ratio?
- How does the selected metro rank on affordability vs its peer set?
- Which ZCTAs have the highest home value-to-income ratio within a target CBSA?
- Which states diverge most from the national benchmark on real per-capita income?

## Question Coverage

Generated from `visual_library/charts/bar/question_coverage.md`.

# Bar Question Coverage

## Canonical Test Cases
- `bar_top_growth_cbsas`: top-ranked CBSA growth comparison.
- `bar_county_affordability`: county rent-to-income ranking within a target metro.
- `bar_target_vs_peers`: highlighted target metro rank against peer set.
- `bar_state_benchmark_delta`: diverging benchmark comparison for states.

## Source Question Mapping
- Top 25 CBSAs by 5-year median income growth -> `bar_top_growth_cbsas`
- Counties with the highest rent-to-income ratio -> `bar_county_affordability`
- Selected metro rank on affordability vs peers -> `bar_target_vs_peers`
- ZCTAs with highest home value-to-income ratio -> `bar_county_affordability` with ZCTA filter
- States with the largest divergence from the national benchmark -> `bar_state_benchmark_delta`

## Current Implementation Status
- Implemented first: `bar_top_growth_cbsas`
- Implemented first: `bar_county_affordability`
- Deferred: `bar_target_vs_peers`
- Deferred: `bar_state_benchmark_delta`

