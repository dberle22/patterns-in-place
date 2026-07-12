---
chart_type: bump_chart
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
- rank
- group
- highlight_flag
- peer_flag
- note
column_mapping: {}
default_benchmark: null
---
# Bump Chart

Generated from `visual_library/charts/bump_chart/bump_chart_spec.md`.

Backend: `altair`. Required fields: `geo_level, geo_id, geo_name, period, metric_id, metric_label, metric_value, source, vintage`.

## Source Spec

## Visual Overview

**What it's for:**
- Track rank movement over time and show who moves up, down, or stays stable.

**Questions it answers:**
- Which places jumped in rank?
- Which fell?
- Are leaders stable or rotating?

**Best when:**
- Rank narrative across 3-10 periods is the story.

**Not ideal when:**
- Magnitude matters more than ordering.

---

## Variants

- Fixed top-N bump chart
- Peer-set bump chart
- Rolling top-N bump chart
- Highlighted bump chart
- Faceted bump chart

---

## Required Data Contract

**Base grain:**
- One row per geography per period per metric.

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
- `rank`
- `group`
- `highlight_flag`
- `peer_flag`
- `note`

---

## Filters and Assumptions

- One geography level and one metric per chart.
- The entity universe must be defined and stable.
- Tie handling must be consistent.

---

## Pre-processing Required

- Compute rank per period.
- Invert the rank axis so 1 is visually highest.
- Decide whether the entity set is fixed or rolling.

---

## Visual Specs

**Core encodings:**
- X-axis = `period`
- Y-axis = `rank`
- Line = one entity over time

**Hard requirements:**
- Subtitle states rank method and entity selection rule.
- Endpoint labels are readable for the highlighted subset.
- Source/vintage is included.

**Optional add-ons:**
- Rank change annotations
- Facets by cohort
- Background bands for top zones

---

## Interpretation and QA Notes

**How to read it:**
- Lines moving upward indicate improving rank.

**Common pitfalls:**
- Unstated entity-universe changes
- Inconsistent ties
- Too many lines

**Quick QA checks:**
- Ranks are computed correctly each period.
- Y-axis is reversed.
- Missing periods are handled intentionally.

---

## Example Question Bank

- Which CBSAs moved into the top 10 for 5-year population growth?
- Did the target CBSA improve in affordability rank since 2018?
- Are the top performers stable or rotating?
- Which counties within the CBSA rose fastest in rent burden rank?
- How did Sweet Spot markets shift in overheating risk rank?

## Question Coverage

Generated from `visual_library/charts/bump_chart/question_coverage.md`.

# Bump Chart Question Coverage

## Canonical Test Cases
- `bump_top10_growth`
- `bump_target_affordability_rank`
- `bump_top_performer_stability`
- `bump_county_rent_burden_rank`
- `bump_sweet_spot_overheating`

## Source Question Mapping
- CBSAs moving into the top 10 for growth -> `bump_top10_growth`
- Target CBSA affordability rank since 2018 -> `bump_target_affordability_rank`
- Stability or churn in top performers -> `bump_top_performer_stability`
- Counties rising in rent burden rank -> `bump_county_rent_burden_rank`
- Sweet Spot overheating rank shifts -> `bump_sweet_spot_overheating`

