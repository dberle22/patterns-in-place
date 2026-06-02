# Correlation Heatmap

## Visual Overview

**What it's for:**
- Show how KPIs move together across a defined universe and reveal redundancy or clustering.

**Questions it answers:**
- Which metrics are strongly related?
- Are we double-counting similar signals?
- Do metric families cluster together?

**Best when:**
- KPI selection and exploratory analysis are the goal.

**Not ideal when:**
- The audience needs causal interpretation or the sample size is tiny.

---

## Variants

- Spearman or Pearson matrix
- Clustered heatmap
- Faceted comparison heatmap
- Threshold-masked view

---

## Required Data Contract

**Base grain:**
- One row per geography per metric for a single analysis universe.

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
- `group`
- `include_flag`
- `weight`

---

## Filters and Assumptions

- Keep one geography level and one time window per matrix.
- Use a curated KPI set.
- State the missingness policy.

---

## Pre-processing Required

- Pivot to wide by KPI.
- Choose the correlation method.
- Optionally mask weak relationships.

---

## Visual Specs

**Core encodings:**
- X-axis = metric
- Y-axis = metric
- Fill = correlation coefficient

**Hard requirements:**
- Subtitle states method and missingness policy.
- Legend spans -1 to 1.
- Reordering method is disclosed if used.
- Source/vintage summary is included.

**Optional add-ons:**
- Cell labels
- Clustered order
- Companion table of strongest pairs

---

## Interpretation and QA Notes

**How to read it:**
- Stronger color means stronger relationship; the sign shows direction.

**Common pitfalls:**
- Treating correlation as causal
- Too many metrics
- Hidden missingness behavior

**Quick QA checks:**
- Matrix is symmetric.
- Diagonal is 1.
- The analysis universe matches the title.

---

## Example Question Bank

- Which KPIs are redundant signals?
- Do growth metrics cluster separately from level metrics?
- Is rent burden more associated with income or supply indicators?
- How does the structure differ for Sweet Spot markets?
- Within a CBSA's counties, which indicators co-move most?
