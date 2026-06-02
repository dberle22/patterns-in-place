# Age Pyramid

## Visual Overview

**What it's for:**
- Show age structure by sex and quickly surface whether a place skews young, family-oriented, or older.

**Questions it answers:**
- Is the place aging or young?
- Is there a family formation bulge?
- How does the demographic structure compare with a benchmark?

**Best when:**
- A demographic profile or benchmark comparison is the story.

**Not ideal when:**
- Many geographies must be compared at once with precise values.

---

## Variants

- Single-geo pyramid
- Percent-of-total pyramid
- Geo versus benchmark
- Small-multiple pyramids
- Simplified age-band pyramid

---

## Required Data Contract

**Base grain:**
- One row per geography per age bin per sex per period.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `period`
- `age_bin`
- `sex`
- `pop_value`
- `source`
- `vintage`

**Optional fields (recommended):**
- `pop_total`
- `pop_share`
- `benchmark_label`
- `highlight_flag`
- `note`

---

## Filters and Assumptions

- Use one period per chart.
- Keep age bins consistent across all pyramids.
- Prefer percent-of-total for cross-geo comparison.

---

## Pre-processing Required

- Standardize age bins.
- Compute `pop_share` where needed.
- Apply a consistent sign convention for sex splits.

---

## Visual Specs

**Core encodings:**
- Y-axis = `age_bin`
- X-axis = `pop_share` or `pop_value`
- Fill = `sex`

**Hard requirements:**
- Title/subtitle identify geography, benchmark, and period.
- Signed axis is labeled clearly when using mirrored values.
- Legend for sex and benchmark is readable.
- Source/vintage is included.

**Optional add-ons:**
- Symmetric axis limits
- Bulge annotations
- Companion summary metrics

---

## Interpretation and QA Notes

**How to read it:**
- Wider bars indicate a larger share in that age-sex segment.

**Common pitfalls:**
- Using counts for cross-geo comparison
- Inconsistent age bins
- Unsymmetrical axes

**Quick QA checks:**
- Age bins cover the full population.
- Percent shares sum correctly.
- Benchmark uses the same binning and period.

---

## Example Question Bank

- Does this CBSA skew younger or older than the national benchmark?
- Which counties within the CBSA have the strongest family formation profile?
- Is the metro aging faster than peers?
- Do target ZCTAs show a retiree concentration?
- How do age-structure differences align with housing demand signals?
