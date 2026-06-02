# Boxplot

## Visual Overview

**What it's for:**
- Compare the distribution, spread, median, and outliers of one metric across groups.
- Show where a selected geography sits relative to its peer distribution.

**Questions it answers:**
- How does a metric vary across groups?
- Which groups have higher medians or wider spread?
- Are there long tails or extreme outliers?
- Is the target geography typical or unusual within the distribution?

**Best when:**
- The story is about distribution shape rather than exact rank.
- The sample size within each group is large enough to make quartiles meaningful.

**Not ideal when:**
- Exact entity-by-entity values matter more than spread.
- Groups have very small sample sizes.
- The full density shape is the main story; use violin or ECDF instead.

---

## Variants

- Grouped boxplot
- Horizontal grouped boxplot
- Boxplot plus highlighted point
- Boxplot plus jittered observations
- Faceted boxplot for a small set of metrics or time windows
- Violin plus box overlay, later, when distribution shape matters

---

## Required Data Contract

**Base grain:**
- One row per geography per snapshot or time window for one metric.

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

**Optional fields:**
- `group`
- `highlight_flag`
- `label_flag`
- `weight_value`
- `benchmark_value`
- `note`

---

## Filters and Assumptions

- Default to one `geo_level`, one `metric_id`, and one `time_window` per chart unless faceting.
- The grouping universe must be clear in the title or subtitle.
- Missing metric values are dropped during prep by default and the dropped count should be available for captions.
- Boxplot whiskers use the standard 1.5 IQR rule unless a chart-specific note says otherwise.
- Display clipping or winsorization is allowed only when documented as display-only.

---

## Pre-processing Required

- Coerce `metric_value`, `benchmark_value`, and `weight_value` to numeric when present.
- Coerce `highlight_flag` and `label_flag` to logical.
- Filter to the requested question, metric, time window, geography, and group set.
- Compute group sample sizes and medians for ordering and subtitle/caption notes.
- Add a stable `box_group` field that falls back to `"All observations"` when no group is supplied.
- Optionally order groups by median value.

---

## Visual Specs

**Core encodings:**
- Category axis = `box_group`
- Value axis = `metric_value`
- Box = median, IQR, and 1.5 IQR whiskers
- Color or point overlay = highlight geography when provided

**Hard requirements:**
- Title identifies the metric, universe, and geography level.
- Subtitle identifies the time window, grouping dimension, and any transform or clipping rule.
- Value axis labels include units.
- Source and vintage appear in the caption.
- Highlight points are labeled when the chart is being used narratively.
- Group ordering should be stated when it is not alphabetical.

**Optional add-ons:**
- Jittered observations for small or medium sample sizes.
- Benchmark/reference line for a national or peer median.
- Facets by `metric_label` or `time_window`.
- Horizontal orientation when group labels are long or group count is high.

---

## Interpretation and QA Notes

**How to read it:**
- The line inside each box is the median; the box is the middle 50%; whiskers show the typical range; points beyond whiskers are outliers.
- Compare medians and spreads across groups before focusing on individual outliers.

**Common pitfalls:**
- Over-interpreting individual outliers.
- Comparing groups with very different sample sizes without noting it.
- Mixing geography levels or time windows.
- Hiding skewed distributions through aggressive clipping.

**Quick QA checks:**
- Universe and grouping match the subtitle.
- Units and formatting are correct.
- Highlight point matches the intended geography.
- Missing-value handling is explicit.
- Faceted charts preserve comparable axes unless intentionally overridden.

---

## Example Question Bank

- How does rent burden vary across regions, and where does the target CBSA fall?
- For counties in the target CBSA, what is the distribution of median rent-to-income?
- Within the target CBSA, do ZCTAs show a long tail of high commute intensity?
- Are Sweet Spot markets outliers on affordability relative to all CBSAs?
- How does the distribution of income growth differ by CBSA type?
