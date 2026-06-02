# Line Graphs

## Visual Overview

**What it’s for:**  
Show how a metric changes over time and make the “shape of change” obvious (trend, cycles, breaks, acceleration).

**Questions it answers:**
- Is the metric rising or falling?
- When did it change direction?
- How does one geography compare to peers over time?
- How do different metrics move together?

**Best when:**
- Annual series (common for your KPIs), especially with single geographies, small peer sets, or indexed comparisons.

**Not ideal when:**
- Too many lines (“spaghetti”).
- Highly volatile small-geo series without smoothing/aggregation.
- When the point is rank rather than trajectory.

---

## Variants

- **Single-series line:** best for telling one place’s story over time.
- **Multi-series comparison (small N):** best for “selected metro vs peers.”
- **Indexed line (base year = 100):** best for comparing growth trajectories across places with different starting levels.
- **Small multiples (faceted lines):** best when you need many geographies but still want readability.
- **Rolling/Smoothed line:** best for noisy series (more common at small geos or monthly data).
- **Dual-metric overlay (use sparingly):** best when two metrics share units or are normalized/indexed (avoid dual axes).

---

## Required Data Contract

**Base grain:**  
1 row per geo per time period per metric (long/tidy preferred for flexibility).

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `period` (e.g., year as integer; could be date if monthly/quarterly later)
- `metric_id` (stable key)
- `metric_label`
- `metric_value` (numeric)
- `source`
- `vintage`

**Optional fields (recommended):**
- `time_window` (examples: `level`, `indexed`, `rolling_3yr`)
- `group` (Region / Division / CBSA Type / State)
- `highlight_flag` (TRUE/FALSE for selected geos)
- `benchmark_value` (for benchmark line, or include a benchmark geo as a series)
- `index_base_period` (e.g., 2013, if using indexed lines)
- `note` (data breaks, definitional changes)

---

## Filters and Assumptions

Default for readability:
- one metric at a time, and
- a controlled set of geographies (single geo, highlight + peers, or facets).

Additional rules:
- When mixing different `geo_level`, do it only intentionally (usually avoid).
- Handle missing periods explicitly (gaps should be visible unless imputed and documented).

---

## Pre-processing Required (by variant)

- **Indexed line:**  
  Compute `index_value = metric_value / metric_value[base_period] * 100` per geo (guard against missing/zero base).

- **Rolling/smoothed:**  
  Define window and method (rolling mean, rolling CAGR, LOESS); document in subtitle.

- **Growth windows (5–10y):**  
  Prefer a separate chart type (bar/ranking), unless you’re plotting growth rates by year.

---

## Visual Specs

**Core encodings:**
- X-axis = `period`
- Y-axis = `metric_value` (or `index_value`)
- Color = `geo_name` (small N) or `highlight_flag` (highlight vs muted peers)
- Facet = optional (`group`, `geo_name`, or `metric_id` depending on variant)

**Hard requirements:**
- **Title:** metric + geography context  
  Example: “Real Per Capita Income: Raleigh-Cary vs Peers”
- **Subtitle:** period range + transform (indexed base year, rolling window)
- **Axis labels:** include units (%, $, index) and note if inflation-adjusted/indexed
- **Legend rules:** keep readable; if too many series, switch to small multiples
- **Source + vintage** footnote
- Use library font + number formatting (per Standards)

**Optional add-ons:**
- Benchmark line (national average, peer average, target)
- Reference markers (vertical lines for policy change, recession band, etc., if relevant)
- End labels (label lines at the right edge instead of a legend, if supported later)
- Annotations for notable inflection points
- Confidence bands (rare for your use cases, but possible for survey estimates)

---

## Interpretation and QA Notes

**How to read it:**
- Prioritize slope and inflection points over single-year noise.
- Use indexed lines to compare “pace” rather than “level.”

**Common pitfalls:**
- Spaghetti lines: too many geos without faceting/highlight strategy.
- Changing definitions: breaks in series can look like real change; annotate if known.
- Misleading scaling: truncated y-axes can exaggerate differences; be intentional.
- Missing years: silent interpolation hides real gaps; show gaps unless documented.

**Quick QA checks (visual-level):**
- Period range matches what’s stated in subtitle.
- Transform (indexed/rolling) is applied correctly and labeled.
- Missing periods are handled intentionally (gaps or documented imputation).
- Units and formatting are correct (%, $, index base).
- If comparing multiple geos: confirm consistent metric definition across geos.

---

## Example Question Bank

- How has median income changed over the past decade in this CBSA vs its peers?
- Did population growth accelerate after 2018, or was it steady?
- Are housing costs rising faster than incomes over time (indexed comparison)?
- Which counties in this CBSA are diverging in growth trajectories? (small multiples)
- How did the “Sweet Spot” metros behave through 2020–2023 relative to the broader set?
