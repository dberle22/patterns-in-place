# Heatmap Table

## Visual Overview

**What it's for:**
- Summarize a large amount of information in a scan-friendly matrix.

**Questions it answers:**
- Which geographies look strong or weak across many KPIs?
- Which metrics stand out for a given geography?
- How do metrics evolve through time in one compact view?

**Best when:**
- The goal is shortlist, scan, or appendix-style diagnosis.

**Not ideal when:**
- Exact numeric values are the main takeaway.

---

## Variants

- Geo x Metric
- Geo x Year
- Metric x Year
- Percentile or rank heatmap
- Clustered heatmap

---

## Required Data Contract

**Base grain:**
- One row per geography per period per metric.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `metric_id`
- `metric_label`
- `metric_value`
- `source`
- `vintage`

**Optional fields (recommended):**
- `time_window`
- `period`
- `metric_group`
- `normalized_value`
- `direction`
- `group`
- `highlight_flag`
- `note`

---

## Filters and Assumptions

- Use a clear normalization universe.
- Keep missing data explicit.
- Limit rows and columns to a readable set.

---

## Pre-processing Required

- Compute the displayed statistic, usually percentile.
- Apply polarity for multi-metric score views.
- Choose row and column ordering.

---

## Visual Specs

**Core encodings:**
- Tile position = row and column entities
- Fill = normalized or raw value

**Hard requirements:**
- Title states the matrix shape and universe.
- Subtitle states year range or time window plus normalization method.
- Legend explains the fill statistic.
- Missing data is clearly distinct.
- Source/vintage is included.

**Optional add-ons:**
- Cell labels
- Group headers
- Highlight rows
- Marginal summaries

---

## Interpretation and QA Notes

**How to read it:**
- Scan across rows for profile and down columns for comparison.

**Common pitfalls:**
- Incomparable raw metrics
- Unclear polarity
- Overcrowding

**Quick QA checks:**
- Row/column counts are expected.
- Polarity is applied consistently.
- Missing cells are not confused with low values.

---

## Example Question Bank

- Across a shortlist, which geographies are consistently strong across growth and affordability guardrails?
- For counties in the target CBSA, which dimensions are strongest versus weakest?
- For selected peer CBSAs, what does the full KPI profile look like in one matrix?
- For rent burden, which ZCTAs show persistent stress across years?
- Which metrics improved most in the target CBSA over time?
