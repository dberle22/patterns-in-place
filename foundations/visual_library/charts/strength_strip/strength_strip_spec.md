# Strength Strip / Scorecard Bars

## Visual Overview

**What it's for:**
- Provide a compact profile of strengths and weaknesses across a stable KPI set.

**Questions it answers:**
- Where is a market relatively strong or weak?
- Which KPI dimensions drive a high or low composite story?
- How does a target compare with a small peer set?

**Best when:**
- A normalized multi-KPI market profile is needed for one to three geographies.

**Not ideal when:**
- Many geographies need side-by-side comparison.

---

## Variants

- Single-geo profile
- Selected versus peers
- Category-grouped strip
- Delta strip versus benchmark
- Rank or percentile strip

---

## Required Data Contract

**Base grain:**
- One row per geography per metric per time window.

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
- `metric_group`
- `direction`
- `normalized_value`
- `benchmark_label`
- `highlight_flag`
- `note`

---

## Filters and Assumptions

- Use a fixed canonical KPI list.
- Normalize within an explicitly stated universe.
- Keep missing metrics visible rather than dropping them.

---

## Pre-processing Required

- Compute percentiles or another stated normalization method.
- Apply polarity so "better" always goes right.
- Compute benchmark deltas when needed.

---

## Visual Specs

**Core encodings:**
- Y-axis = `metric_label`
- X-axis = `normalized_value`
- Color = `geo_name` or `highlight_flag`

**Hard requirements:**
- Title/subtitle identify geography, time window, and normalization universe.
- Directionality is consistent across metrics.
- Scale labeling is explicit.
- Source/vintage is included.

**Optional add-ons:**
- Benchmark marker
- KPI group headers
- End labels

---

## Interpretation and QA Notes

**How to read it:**
- Read each row as relative standing on a metric after normalization.

**Common pitfalls:**
- Missing polarity inversion
- Wrong normalization universe
- Too many geographies

**Quick QA checks:**
- Polarity is correct.
- Metric list is canonical.
- Missing values are explicit.

---

## Example Question Bank

- What is this CBSA's KPI profile across major categories?
- Which dimensions are strengths or weaknesses versus peers?
- Which KPIs are dragging down a composite score?
- How does the profile differ between level and growth windows?
- Which county in a CBSA has the strongest overall profile?
