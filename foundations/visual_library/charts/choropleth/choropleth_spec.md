# Choropleth Maps

## Visual Overview

**What it's for:**
- Show one metric across space to reveal clusters, gradients, and geographic exceptions.

**Questions it answers:**
- Where is a metric high or low?
- Are there meaningful spatial clusters?
- How does a target geography compare to surrounding areas?

**Best when:**
- One metric and one geography layer are the story.

**Not ideal when:**
- Exact rank differences matter more than spatial pattern.

---

## Variants

- Standard choropleth
- Highlighted choropleth
- Binned choropleth
- Diverging choropleth
- Small-multiple map

---

## Required Data Contract

**Base grain:**
- One row per geography per time window plus joinable geometry.

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `time_window`
- `metric_value`
- `metric_label`
- `source`
- `vintage`

**Optional fields (recommended):**
- `geometry`
- `bin`
- `benchmark_value`
- `highlight_flag`
- `group`
- `note`

---

## Filters and Assumptions

- Use one geography layer per map.
- Keep one time window per panel unless faceting.
- Missing geometries and missing data must be explicit.
- For national comparison maps, default to the contiguous 48 states plus DC unless the analytical question explicitly requires a broader footprint.

---

## Pre-processing Required

- Join data to geometry.
- Compute bins or benchmark deltas when relevant.
- Decide and document the missing-data policy.
- Choose a composition preset intentionally:
- `national_compact` for single-panel contiguous-US review maps
- `facet_national` for shared-extent multi-panel national comparisons
- `local_focus` for metro/submetro maps fit tightly to the study area

---

## Visual Specs

**Core encodings:**
- Fill color = `metric_value` or `bin`
- Geometry = polygon layer for the chosen geography

**Hard requirements:**
- Title and subtitle identify geography and time window.
- Legend explains units or binning.
- Missing data is labeled.
- Source/vintage is included.
- Subtitle wrapping should be handled in shared map defaults rather than ad hoc line breaks in chart runners.
- Diverging benchmark maps should default to the shared stronger diverging palette unless a domain-specific override is justified.

**Optional add-ons:**
- Highlight outline
- Context boundaries
- Limited labels
- Inset zoom
- Shared base context layers such as US outline and state outlines should be available as toggles, especially for national CBSA and county maps.

---

## Interpretation and QA Notes

**How to read it:**
- Look for clusters, corridors, and isolated outliers.

**Common pitfalls:**
- Area bias
- Washed-out scales from outliers
- Geometry join failures

**Quick QA checks:**
- Join success rate looks plausible.
- Subtitle matches the filtered time window.
- No-data areas are intentional.

---

## Example Question Bank

- Where are the clusters of high rent burden, and how do they align with income levels?
- Which counties show the strongest 10-year population growth?
- Within a CBSA, which ZCTAs are affordability outliers?
- Which metros are above or below a national benchmark?
- How do spatial patterns differ between growth windows?
