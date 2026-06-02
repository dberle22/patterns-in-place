# Bivariate Choropleth

## Visual Overview

**What it's for:**
- Show where two conditions overlap spatially using a bivariate color grid.

**Questions it answers:**
- Where are places high on both metrics?
- Where are tradeoff quadrants?
- Where do risk factors co-locate?

**Best when:**
- Two linked metrics need to be read together on a map.

**Not ideal when:**
- Precise values or more than two metrics matter most.

---

## Variants

- 3x3 quantile bivariate map
- 4x4 bivariate map
- Threshold-based bivariate map
- Benchmark-relative bivariate map
- Faceted bivariate map

---

## Required Data Contract

**Base grain:**
- One row per geography per time window plus geometry.

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
- `geometry`
- `x_bin`
- `y_bin`
- `bivar_class`
- `highlight_flag`
- `group`
- `note`

---

## Filters and Assumptions

- Use one geography level and one time window per map.
- State the binning universe explicitly.
- Missing values must be visible.

---

## Pre-processing Required

- Choose the binning method.
- Compute `x_bin`, `y_bin`, and `bivar_class`.
- Check bin balance and document skew if needed.

---

## Visual Specs

**Core encodings:**
- Fill = `bivar_class`
- Geometry = polygons for the chosen geography

**Hard requirements:**
- Title names both metrics.
- Subtitle names the binning method and universe.
- Bivariate legend is a clear 2D key.
- Missing data is labeled.
- Source/vintage is included.

**Optional add-ons:**
- Highlight outlines
- Cluster callouts
- Companion precision chart

---

## Interpretation and QA Notes

**How to read it:**
- Focus on high-high, low-low, and the two tradeoff quadrants.

**Common pitfalls:**
- Legend confusion
- Too many bins
- Wrong comparison universe

**Quick QA checks:**
- Bin counts are reasonable.
- Legend orientation matches labels.
- Palette is consistent across uses.

---

## Example Question Bank

- Where are counties that are high growth and still relatively affordable?
- Where are ZCTAs that combine high rent burden with low income?
- Within the target CBSA, where do two local stress factors overlap?
- Across CBSAs, which regions show the strongest overlap of economic strength and affordability?
- How does the overlap pattern change across growth windows?
