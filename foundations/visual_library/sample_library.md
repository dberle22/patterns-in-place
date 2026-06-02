# Visual Library

## Purpose

This document is the canonical chart catalog for the visual library. It supersedes `Visual Library.docx` as the main human-readable reference for chart families, chart-type fit, data contracts, visual specs, and example question banks.

Use this file for chart taxonomy and chart-selection guidance. Use chart-specific specs under `visual_library/charts/` for implementation details, and use `visual_style_guide_and_standards.md` for cross-chart visual rules.

## Summary

This document outlines our visual library. Our intention is to simplify our analyses by creating a library of analytical assets. The goal is to standardize our plot types and the plot add ons that make our analyses look more professional.
We will outline data structure requirements, visual elements, and example questions for each visual type. This will help us turn each visual into a standard we can reuse in our library

## Chart Families

### Daily Drivers

- Bar Charts
- Line Charts
- Scatter Plots
- Choropleth Maps
- Hexbin / 2D Binned Scatter

### Story Upgraders

- Strength Strip / Scorecard Bars
- Correlation Heatmap
- Highlight + Context Map
- Slopegraph
- Heatmap Table (geo x metric or geo x year)
- Boxplots

### Deep Dive Specialists

- Age Pyramid
- Bump Chart
- Waterfall
- Bivariate Choropleth
- Proportional Symbol Map (Bubble Map)

### Nice-to-Haves (Use Carefully)

- Flow Map (migration/commuting/trade)
- Stacked Area (composition over time)
- Ridgeline (distribution comparisons)
- ECDF (threshold / distribution comparisons)
- Hex / Grid Map (tile map)
- Point Map (markers)
- Radar Chart

## Daily Drivers

### Line Graphs

#### Visual Overview

What it’s for: Show how a metric changes over time and make the “shape of change” obvious (trend, cycles, breaks, acceleration). Questions it answers: Is the metric rising or falling? When did it change direction? How does one geography compare to peers over time? How do different metrics move together? Best when: Annual series (common for your KPIs), especially with single geographies, small peer sets, or indexed comparisons. Not ideal when: Too many lines (spaghetti), highly volatile small-geo series without smoothing/aggregation, or when the point is rank rather than trajectory.
Variants
- Single-series line: best for telling one place’s story over time.
- Multi-series comparison (small N): best for “selected metro vs peers.”
- Indexed line (base year = 100): best for comparing growth trajectories across places with different starting levels.
- Small multiples (faceted lines): best when you need many geographies but still want readability.
- Rolling/Smoothed line: best for noisy series (more common at small geos or monthly data).
- Dual-metric overlay (use sparingly): best when two metrics share units or are normalized/indexed (avoid dual axes).
#### Required Data Contract

Base grain: 1 row per geo per time period per metric (long/tidy preferred for flexibility).
Required fields:
- geo_level
- geo_id
- geo_name
- period (e.g., year as integer; could be date if monthly/quarterly later)
- time_window (optional but useful when mixing raw vs growth vs indexed; examples: level, indexed, rolling_3yr)
- metric_id (stable key)
- metric_label
- metric_value (numeric)
- source
- vintage
Optional fields (recommended):
- group (Region/Division/CBSA Type/State, if you facet or color by group)
- highlight_flag (TRUE/FALSE for selected geos)
- benchmark_value (for benchmark line, or include a benchmark geo as a series)
- index_base_period (e.g., 2013, if using indexed lines)
- note (data breaks, definitional changes)
Filters & assumptions:
- For readability, default to:
- one metric at a time, and
- a controlled set of geographies (single geo, highlight + peers, or facets).
- When mixing different geo_level, do it only intentionally (usually avoid).
- Handle missing periods explicitly (gaps should be visible unless imputed and documented).
Pre-processing required (by variant):
- Indexed line: compute index_value = metric_value / metric_value[base_period] * 100 per geo (guard against missing/zero base).
- Rolling/smoothed: define window and method (rolling mean, rolling CAGR, LOESS); document in subtitle.
- Growth windows (5–10y): prefer separate chart type (bar/ranking), unless you’re plotting growth rates by year.
#### Visual Specs

Core encodings:
- X-axis = period
- Y-axis = metric_value (or index_value)
- Color = geo_name (small N) or highlight_flag (highlight vs muted peers)
- Facet = optional (group, geo_name, or metric_id depending on variant)
Hard requirements:
- Title: metric + geography context (e.g., “Real Per Capita Income: Raleigh-Cary vs Peers”)
- Subtitle: include period range + any transform (indexed base year, rolling window)
- Axis labels: include units (%, $, index) and note if inflation-adjusted/indexed
- Legend rules: keep readable; if too many series, switch to small multiples
- Source + vintage footnote
- Use library font + number formatting (per Standards)
Optional add-ons:
- Benchmark line (national average, peer average, target)
- Reference markers (vertical lines for policy change, recession band, etc., if relevant)
- End labels (label lines at the right edge instead of a legend, if supported later)
- Annotations for notable inflection points
- Confidence bands (rare for your use cases, but possible for survey estimates)
#### Interpretation + QA Notes

How to read it:
- Prioritize slope and inflection points over single-year noise.
- Use indexed lines to compare “pace” rather than “level.”
Common pitfalls:
- Spaghetti lines: too many geos without faceting/highlight strategy.
- Changing definitions: breaks in series can look like real change; annotate if known.
- Misleading scaling: truncated y-axes can exaggerate differences; be intentional.
- Missing years: silent interpolation hides real gaps; show gaps unless documented.
Quick QA checks (visual-level):
- Period range matches what’s stated in subtitle.
- Transform (indexed/rolling) is applied correctly and labeled.
- Missing periods are handled intentionally (gaps or documented imputation).
- Units and formatting are correct (%, $, index base).
- If comparing multiple geos: confirm consistent metric definition across geos.
#### Example Question Bank

- How has median income changed over the past decade in this CBSA vs its peers?
- Did population growth accelerate after 2018, or was it steady?
- Are housing costs rising faster than incomes over time (indexed comparison)?
- Which counties in this CBSA are diverging in growth trajectories? (small multiples)
- How did the “Sweet Spot” metros behave through 2020–2023 relative to the broader set?
### Scatter Plots

#### Visual Overview

What it’s for: Compare two metrics across geographies to spot outliers, tradeoffs, and peer clusters.
Questions it answers: Which markets are strong on both metrics? Which are weirdly high/low relative to the trend? Where are the tradeoffs?
Best when: Single-year snapshots or growth-window snapshots across CBSAs/counties/ZCTAs.
Not ideal when: Very high point counts without density handling (e.g., thousands of ZCTAs) or when a third variable is the real story.
Variants
- Standard scatter: best default relationship + outlier scan
- Quadrant scatter (median lines): best for “four-box” narratives (strong/weak/tradeoff)
- Bubble scatter: encode “importance” (population, housing units)
- Hexbin/density scatter: for ZCTA-heavy views (reduce overplotting)
- Faceted scatter: compare relationship by region/division/time window

#### Required Data Contract

Base grain: 1 row per geo per snapshot/time_window
Required fields: geo_level, geo_id, geo_name, time_window, x_value, y_value, x_label, y_label
Optional fields: source, vintage, group (region/division/type), size_value, label_flag, note
Filters & assumptions: filter to one time_window unless faceting; do not mix geo_levels unless explicitly comparing.
Pre-processing required: drop/flag missing x/y; define growth metrics clearly; document log/winsor if used.
#### Visual Specs

Core encodings: x = x_value; y = y_value; color = group (optional); size = size_value (bubble variant); labels = label_flag (optional).
Hard requirements: title + subtitle include geo_level + time_window; axis labels include units; source + vintage footnote; consistent number formatting (per Standards).
Optional add-ons: quadrant lines; benchmark point; trend line + correlation; auto-label top/bottom outliers; highlight selected geos; facets.
#### Interpretation + QA Notes

How to read it: upper-right strong on both; lower-left weak on both; other quadrants show tradeoffs; outliers prompt investigation.
Common pitfalls: overplotting (use density); spurious correlation (check per-capita vs totals); scale issues (declare log).
Quick QA: units correct; intended time_window applied; missing values handled; outliers validated against raw/source.
#### Example Question Bank

- Which CBSAs have high income growth but comparatively low rent burden?
- Which counties have unusually high home values relative to incomes?
- Which ZCTAs are outliers within a given CBSA on rent vs income?


### Bar Charts

#### Visual Overview

What it’s for: Compare magnitudes across categories (geographies, groups, time windows) with high precision and fast readability. Questions it answers: Who is highest/lowest? How big are the gaps? How does a selected market rank vs peers? How does a metric break down by category? Best when: Single-year snapshots or 5–10 year growth windows across CBSA, County, ZCTA, or aggregated groups (State/Region/Division). Not ideal when: You need to show continuous change over time (use line), relationships between two metrics (use scatter), or you have too many categories without a clear sorting/filtering strategy.
Variants
- Ranked bar (horizontal): best default for ranking geographies (top/bottom N).
- Grouped bar: best for comparing 2–4 series per category (e.g., 2023 vs 2018–2023 growth).
- Stacked bar (composition): best for parts-of-whole within each geography (use cautiously).
- 100% stacked bar: best for comparing composition across geos when totals vary widely.
- Diverging bar: best for above/below benchmark or positive vs negative changes.
- Small-multiple bars: best when you need many categories but want readability by grouping (e.g., one panel per state).
- “Bar + highlight”: muted peers + highlighted selected geo(s) for narrative focus.
#### Required Data Contract

Base grain: 1 row per category per snapshot/time_window per metric (long/tidy preferred).
Required fields:
- geo_level (or category_level if not geo)
- geo_id (or category_id)
- geo_name (or category_name)
- time_window (e.g., 2023, 2013–2023 CAGR)
- metric_id
- metric_label
- metric_value (numeric)
- source
- vintage
Optional fields (recommended):
- rank (precomputed; or derive when plotting)
- group (Region/Division/CBSA Type/State; for faceting or coloring)
- series (string; for grouped/stacked bars, e.g., 2023 vs 2018–2023)
- share_value (for 100% stacked or composition)
- highlight_flag (TRUE/FALSE)
- benchmark_value (for diverging bars)
- note (data caveats)
Filters & assumptions:
- Default to sorted bars (descending unless the story needs otherwise).
- Prefer Top/Bottom N for readability at large geo counts.
- For ZCTAs: consider filtering to a CBSA or a state unless explicitly “all ZCTAs.”
Pre-processing required (by variant):
- Ranked bar: compute rank after filtering; define tie-breaking rule.
- Grouped/stacked: ensure a series field exists and is limited to a small set.
- Diverging: compute delta_value = metric_value - benchmark_value or % difference.
- 100% stacked: compute shares that sum to 1 within each category.
Visual Specs (Encoding + Elements + Add-ons)
Core encodings:
- Axis category = geo_name (or category_name)
- Bar length/height = metric_value (or delta_value, share_value)
- Color = series (grouped/stacked) or highlight_flag (highlight vs peers)
- Facet = optional (group, geo_name, time_window depending on design)
Hard requirements:
- Title: metric + scope (e.g., “Top 25 CBSAs by 10-Year Population CAGR”)
- Subtitle: include time_window + filters (e.g., “CBSAs only; n=…”)
- Sorting: must be explicit and consistent with narrative
- Axis labels: units included and formatted consistently
- Source + vintage footnote
- Use library font + number formatting (per Standards)
- If truncated (Top N): state it (“Top 25”, “Bottom 15”)
Optional add-ons:
- Data labels at bar ends (best for Top N views)
- Benchmark line / benchmark bar (e.g., US average)
- Highlight selected geo(s) with muted peers
- Reference grouping (thin separators by state/region)
- Error bars / uncertainty (rare; for survey estimates if needed)
- Callouts for notable bars (largest gap, biggest mover)
#### Interpretation + QA Notes

How to read it:
- Compare bar lengths for magnitude and gaps.
- Use ranked bars for clear ordering; use diverging bars to emphasize directionality.
Common pitfalls:
- Too many categories: unreadable labels; switch to Top/Bottom N, faceting, or filtering.
- Stacked misuse: stacked bars make cross-geo comparisons of segments hard; use 100% stacked or grouped if comparison is the goal.
- Inconsistent sorting: grouped bars must share a stable sort key (usually one series).
- Mixing units: don’t compare level and growth in the same axis without clear separation.
Quick QA checks (visual-level):
- Bars reflect intended filter set and time_window.
- Sort order matches the stated logic.
- Units and formatting are correct (%, $, index).
- If using shares: confirm totals sum to 100% per category.
- If using ranks: confirm rank computed after filters.
#### Example Question Bank

- What are the top 25 CBSAs by 5-year median income growth?
- Which counties in this CBSA have the highest rent-to-income ratio?
- How does the selected metro rank on affordability vs its peer set?
- Which ZCTAs have the highest home value-to-income ratio within a target CBSA?
- Which states have the largest divergence from the national benchmark on real per-capita income?
### Choropleth Maps

#### Visual Overview

What it’s for: Compare a single metric across geographies to reveal spatial patterns (clusters, regional gradients, hot/cold spots) and support narrative “place-based” storytelling.
Questions it answers: Where is a metric high/low? Are there geographic clusters? How does a region compare to peers? Where are exceptions (outliers) within a broader pattern?
Best when: Single-year snapshots (or a defined growth window) across CBSA, County, ZCTA, and optionally State/Region/Division summaries.
Not ideal when: You need to show precise rank differences (maps are bad at tiny deltas), the audience must compare many categories at once, or the metric is extremely noisy at small geographies (some ZCTA metrics can be jumpy).
Variants
- Standard choropleth (single metric): best default for spatial distribution in one view.
- Highlight map (selected geo + context): best for “here’s the market, here’s the surrounding story.”
- Binned choropleth (quantiles / custom bins): best when you want interpretable categories (“top 20%”, “low/med/high”).
- Diverging choropleth (above/below benchmark): best for “relative to US / state / peer average.”
- Small-multiple maps: best for comparing time windows (2013–2023 vs 2018–2023) or related metrics (income vs rent burden).
- Inset/zoom (dense areas): best for ZCTA maps where metro cores become a confetti problem.

#### Required Data Contract

Base grain: 1 row per geo per snapshot/time_window, with joinable geometry.
Required fields (data):
- geo_level (CBSA / County / ZCTA / State; plus Region/Division if used for summaries)
- geo_id (must match geometry key)
- geo_name
- time_window (e.g., 2023, 2013–2023 CAGR, 2018–2023 growth)
- metric_value (numeric)
- metric_label (string; include unit hint if useful)
- source
- vintage
Required fields (geometry):
- geo_id (same key as data)
- geometry (sf geometry column)
Optional fields (recommended):
- bin (precomputed bin label like “Q1–Q5” or “Low/Med/High”)
- benchmark_value (numeric; for diverging maps)
- highlight_flag (TRUE/FALSE; for selected geo)
- group (region/division/state; more useful for faceting than mapping)
- note (string; e.g., “suppressed due to low sample”)
Filters & assumptions:
- Filter to one time_window unless using small multiples.
- Do not mix geo_level in a single layer (CBSA and county boundaries together) unless explicitly designing an overlay map.
- Decide your missing policy: show NA as “No data” fill (do not silently drop).
Pre-processing required (by variant):
- Binned maps: compute bins from metric_value (quantiles or domain cutpoints).
- Diverging maps: compute metric_value - benchmark_value (or % difference) and store as a derived field (e.g., delta_value).
- Growth windows: ensure metric is comparable over time (same definition, inflation-adjusted if needed).
- Composition/layout: choose a composition preset intentionally. Current shared presets are `national_compact` for single-panel contiguous-US maps, `facet_national` for multi-panel national comparisons, and `local_focus` for metro/submetro maps that should fit tightly to the study area.
#### Visual Specs

Core encodings:
- Fill color = metric_value (continuous) or bin (categorical)
- Geometry = polygons for the chosen geo_level
Hard requirements:
- Title: metric + geo level (e.g., “Rent Burden by County”)
- Subtitle: include time_window + any key filters (e.g., “2018–2023 growth; contiguous US”)
- Legend: must show units or bin meaning
- Missing data treatment: explicit “No data” category / legend note
- Source + vintage footnote
- Use library font + number formatting (per Standards)
- Shared map defaults:
- subtitle wrapping should be on by default for map-family charts
- contiguous-US comparison maps should default to the contiguous 48 plus DC extent unless a broader or local scope is explicitly needed
- diverging choropleths should default to the stronger shared diverging palette unless a domain-specific override is justified
Optional add-ons:
- Outline/highlight a selected geo (highlight_flag)
- Reference boundaries (e.g., state outlines behind counties) where helpful
- Labels only for a small set: highlighted geo(s) and maybe top/bottom outliers (avoid map clutter)
- Annotations (callouts for clusters, regional gradients)
- Inset/zoom for dense metros or small geos
- Companion ranking strip beside map (optional pairing, not mandatory in template)
- Recommended composition presets:
- `national_compact`: contiguous-US national map with tighter margins and a review-friendly footprint
- `facet_national`: shared contiguous-US extent plus lean framing for small-multiple national maps
- `local_focus`: bbox-fitted local map with light padding for outlines, labels, and metro context
#### Interpretation + QA Notes

How to read it:
- Focus on patterns, not exact ranks.
- Look for clusters (adjacent high/high or low/low), transitions (gradients), and exceptions (islands).
Common pitfalls:
- Area bias: big counties dominate visually; consider pairing with a ranking chart.
- Color scaling traps: extreme outliers can wash out differences; consider bins or trimmed scales (and document it).
- Small-geo noise: ZCTAs can be volatile; consider smoothing, bins, or minimum denominator rules.
- Crosswalk/geometry mismatches: missing joins create phantom “no data” regions.
Quick QA checks (visual-level):
- Geometry join success rate looks right (no unexpected large blocks of missing).
- time_window and filters in subtitle match the dataset used.
- Metric units and legend formatting are correct.
- Missing values are intentional and labeled.
- For binned maps: bins distribute as expected (not all in one bin).
#### Example Question Bank

- Where are the clusters of high rent burden, and how do they align with income levels?
- Which counties show the strongest 10-year population growth, and are they contiguous corridors or isolated pockets?
- Within a CBSA, which ZCTAs are outliers for affordability (home value-to-income)?
- Which metros are above/below the national benchmark for real per-capita income?
- How do spatial patterns differ between 2013–2023 vs 2018–2023 growth?

### Hexbin / 2D Binned Scatter

#### Visual Overview

What it’s for: A high-volume alternative to scatter plots that shows the density of points across an X–Y plane by aggregating observations into bins. It helps you see the “shape” of relationships (clusters, gradients, dense centers) without overplotting.  Questions it answers: Where do most observations sit? Are there multiple clusters? Are there dense “hot zones” plus sparse outliers? How does density shift across peer groups or time windows?  Best when: You have hundreds to tens of thousands of points (ZCTAs, tracts, listings) and want a reliable view of relationship structure and concentration.  Not ideal when: You only have a small N (regular scatter is clearer), you need to identify specific individual geos (hexbin hides individuals), or one/both axes are categorical (use heatmap table or grouped bars instead).
#### Variants (choose your “mode” first)

- Hexbin (hexagonal bins): default; visually balanced bin adjacency and nice density perception.
- 2D binned heatmap (rectangular bins): easiest to explain; good when you want explicit bin edges.
- Weighted hexbin: bin intensity reflects a weight (population, housing units), not just count.
- Faceted hexbin: compare density patterns by group (Region/Division) or time_window.
- Hybrid (hexbin + highlighted points): hexbin for context, plus a few highlighted geos overlaid.
#### Required Data Contract

Base grain: 1 row per observation (e.g., geo, listing, tract) per snapshot/time_window.
Required fields:
- geo_level (or observation level)
- geo_id
- geo_name (optional if you won’t label individuals, but useful for overlays)
- time_window
- x_value (numeric)
- y_value (numeric)
- x_label, y_label
- source, vintage
Optional fields (recommended):
- group (Region/Division/CBSA Type/State)
- weight_value (numeric; for weighted hexbin)
- highlight_flag (TRUE/FALSE; for overlaying selected points)
- note (caveats / suppressions)
Filters & assumptions:
- Default to one time_window per view unless faceting.
- Avoid mixing geo levels unless explicitly designed.
- Decide outlier handling: either keep all points (and accept sparse bins) or trim/winsor with a documented note.
Pre-processing required:
- Drop/flag missing x_value/y_value.
- If using weights: ensure weight is non-negative and document what it represents.
- Consider log transforms for heavily skewed axes (document in subtitle).
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- X-axis = x_value
- Y-axis = y_value
- Fill color = bin statistic:
- default: count of points per bin
- weighted variant: sum(weight_value) per bin
- optional: mean of a third variable (only if clearly labeled, otherwise it becomes bivariate++ confusion)
Hard requirements:
- Title + subtitle include geo universe + time_window + binning method (Hexbin vs 2D bins).
- Legend clearly states what color represents (count vs weighted sum) and whether it’s log-scaled.
- Axis labels include units where relevant.
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Overlay highlighted geos (points) with labels for 1–5 selected items.
- Reference lines (median/benchmark) if using quadrant narratives.
- Facets by group or time_window.
- Annotate notable dense clusters or “empty zones” (structural tradeoffs).
#### Interpretation + QA Notes

How to read it: Darker (or more intense) bins mean “more observations” (or more weighted mass). Look for the dense core, secondary clusters, and whether the relationship is linear, curved, or segmented.  Common pitfalls:
- Bin size too large (hides structure) or too small (noisy speckling).
- Log-scaled counts without saying so (misleading).
- Mistaking density for “good” or “bad” without tying back to outcome metrics.
- Weighted bins used inconsistently (population-weighted vs unweighted comparisons can tell different stories).
Quick QA checks:
- Confirm the legend matches the statistic (count vs weighted sum).
- Bin resolution is appropriate (you can still see structure without noise).
- Filters/time_window match subtitle.
- Outliers handled intentionally (not silently dropped).
- If weights used: sanity-check total weight represented vs expected universe.
#### Example Question Bank

- Across all ZCTAs, where do most neighborhoods sit on income vs rent burden?
- Are there distinct clusters of ZCTAs with high growth but high rent burden?
- In a target CBSA, what’s the density pattern of home value-to-income vs rent-to-income?
- How does the density of affordability vs growth differ across Regions or CBSA Types?
- If weighted by population, where do most people fall on the affordability tradeoff curve?

## Story Upgraders

### Strength Strip / Scorecard Bars

#### Visual Overview

What it’s for: A compact “profile” view that compares multiple KPIs for one geography (or a small set) using consistent, normalized bars. It answers the same use case as a radar chart, but with higher readability and precision. Questions it answers: What are this market’s relative strengths/weaknesses across KPI categories? How does a selected market compare to peers across the same KPI set? Which dimensions drive a high/low composite score? Best when: You have a stable KPI set (e.g., Population/Economics/Housing/Affordability) and want a quick market profile for 1–3 highlighted geos (optionally + peer average). Works well in executive summaries and deep-dive “market card” sections. Not ideal when: You need to compare many geos at once (use heatmap table or ranked bars), the KPI set isn’t standardized yet, or you’re trying to communicate raw values without normalization.
#### Variants (choose your “mode” first)

- Single-geo profile: one market’s KPI shape (with benchmark line or peer average).
- Selected vs peers (small N): 2–3 markets on the same strip (side-by-side bars or grouped bars per metric).
- Category strip: metrics grouped into sections (Population/Economics/etc.) with section headers.
- Delta strip (vs benchmark): bars show difference from benchmark (above/below peer avg or national).
- Rank strip: bars show percentile or rank position rather than z-score (more intuitive for non-technical audiences).
#### Required Data Contract

Base grain: 1 row per geo per metric per snapshot/time_window (long/tidy).
Required fields:
- geo_level, geo_id, geo_name
- time_window (e.g., 2023, 2013–2023 CAGR)
- metric_id, metric_label
- metric_value (raw numeric)
- source, vintage
Optional fields (recommended):
- metric_group (e.g., Population/Economics/Housing/Affordability)
- direction (higher_is_better / lower_is_better) or a polarity flag
- normalized_value (precomputed; z-score/min-max/percentile)
- benchmark_id / benchmark_label (e.g., peer avg, US)
- highlight_flag (TRUE/FALSE)
- note (e.g., missingness, caveats)
Filters & assumptions:
- Default to a fixed KPI list (library-standard) per strip.
- Compare geos only within the same geo_level unless explicitly designed.
- Missing metrics should be explicit (empty bar or NA label), not silently dropped.
Pre-processing required (key step):
- Normalization is required for the core value displayed. Choose one standard method per variant:
- Percentile (0–100): most interpretable; recommended default.
- Z-score: best for analysis; less intuitive.
- Min-max (0–1): okay but sensitive to outliers.
- Apply direction so that “better” is consistently to the right (e.g., invert rent burden).
- If using benchmark comparisons, compute delta_value (geo minus benchmark) and/or show benchmark marker.
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- Y-axis = metric_label (optionally grouped by metric_group)
- X-axis = normalized_value (preferred: 0–100 percentile) or delta_value
- Color = geo_name (small N) or highlight_flag (highlight vs muted)
Hard requirements:
- Title + subtitle include geo(s) + time_window + normalization method (e.g., “Percentile within All CBSAs”).
- Consistent directionality (all bars interpret “more right = better”).
- Clear scale labeling (0–100 percentile, or z-score scale, etc.).
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Benchmark marker/line per metric (peer avg, US).
- Category headers and spacing (Population/Economics/etc.).
- Value labels (percentile or z) at bar end.
- Highlight a subset of “core” KPIs with stronger emphasis.
- Sort metrics within group (e.g., strongest → weakest) or keep fixed canonical order.
#### Interpretation + QA Notes

How to read it: Each row is a metric; the bar position shows relative standing (percentile/z) after aligning directionality. Look for consistent strength across a category and for obvious weak spots that drive risk.
Common pitfalls:
- Mixing raw values without normalization (misleading).
- Inconsistent polarity (some metrics where lower is better not inverted).
- Too many geos (becomes unreadable; switch to heatmap table).
- Normalizing across the wrong universe (e.g., percentiles within a filtered set without stating it).
Quick QA checks:
- Normalization method and comparison universe match subtitle.
- Polarity applied correctly (e.g., lower rent burden becomes higher score).
- No silent metric drop: missing metrics are visible.
- Metric list is the intended canonical set for that strip.
#### Example Question Bank

- What is this CBSA’s KPI profile across Population, Economics, Housing, and Affordability?
- Compared to its peer set, which dimensions are strengths vs weaknesses?
- Which KPIs are dragging down the Investment Score (or driving Overheating)?
- How does the profile differ between 2023 levels vs 10-year growth windows?
- Which county within a CBSA has the strongest overall profile (with the same KPI set)?

### Correlation Heatmap

#### Visual Overview

What it’s for: A matrix view showing how metrics move together across geographies (or within a defined universe). Used to identify redundancy, KPI “families,” and surprising relationships.  Questions it answers: Which metrics are strongly related (+/−)? Are we double-counting similar signals in scoring? What KPI groups naturally cluster (affordability vs growth vs housing supply)?  Best when: KPI selection, index design, exploratory analysis, and explaining “drivers that co-move” for a defined universe (All CBSAs, a region, a peer set, or within a CBSA’s counties/ZCTAs).  Not ideal when: Sample size is small (tiny peer set), relationships are nonlinear/heterogeneous, or the audience needs causal interpretation (correlation ≠ causation).
#### Variants (choose your “mode” first)

- Metric–metric correlation (single universe): default matrix for a defined filter (e.g., All CBSAs, 2023 snapshot).
- Spearman vs Pearson: Spearman for rank/monotonic relationships (often safer); Pearson for linear relationships.
- Clustered heatmap: reorder metrics by hierarchical clustering to reveal KPI families.
- Filtered/faceted heatmaps: compare correlation structure across Region/Division/CBSA Type or across time windows.
- Threshold/masked view: show only strong correlations (|r| ≥ threshold) to reduce noise.
#### Required Data Contract

Base grain: 1 row per geo per snapshot/time_window with many metrics available (wide, or long that can be pivoted wide).
Required fields (conceptual):
- geo_level, geo_id, geo_name
- time_window (single value per heatmap unless faceting)
- A set of numeric metric columns OR long format with metric_id, metric_value
- source, vintage (for the underlying metric set; can be summarized)
Recommended (for long format): metric_id, metric_label, metric_value
Optional fields:
- group (Region/Division/CBSA Type/State) for filtering/faceting
- include_flag per metric (to control which KPIs appear)
- weight (population/housing units) for weighted correlations (optional, advanced)
Filters & assumptions:
- Default to one geo_level and one time_window per heatmap.
- State the “analysis universe” (e.g., All CBSAs with sufficient coverage).
- Handle missingness intentionally: pairwise complete (common) vs listwise (stricter), and state it.
Pre-processing required:
- Choose curated metric set (canonical list for the analysis).
- Decide correlation method (recommended default: Spearman).
- Optionally transform heavily skewed metrics only if documented.
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings: X = metric_label; Y = metric_label; fill = correlation coefficient r (diverging scale centered at 0).
Hard requirements:
- Title includes universe + time_window (e.g., “KPI Correlations | CBSAs | 2023”).
- Subtitle states correlation method (Spearman/Pearson) and missingness approach (pairwise/listwise).
- Legend shows range (-1 to 1) and that 0 is neutral.
- If metrics are reordered, state the method (e.g., clustered).
- Source + vintage footnote (summarize if mixed sources).
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Cell labels (only for small matrices).
- Mask weak correlations (blank/grey if |r| < threshold).
- Cluster dendrogram (later).
- Facets by group (Region/Division/CBSA Type).
- Companion “top relationships” table (top +/− pairs) for narrative.
#### Interpretation + QA Notes

How to read it: Stronger colors = stronger relationships; sign shows direction. Look for blocks (metric families) and very high correlations that signal redundancy.  Common pitfalls: Treating correlation as causal; missingness driving patterns; too many metrics (unreadable); mixing level and growth metrics without clarity.  Quick QA checks: Universe matches title/subtitle; method stated; metric set is canonical; missingness approach explicit; symmetry + 1.0 diagonal.
#### Example Question Bank

- Which KPIs are redundant signals we should avoid double-counting in the Investment Score?
- Do growth metrics cluster separately from level metrics?
- Is rent burden more associated with income levels or housing supply indicators?
- How does correlation structure differ between Sweet Spot markets vs all CBSAs?
- Within a CBSA’s counties, which housing indicators co-move most?

### Highlight + Context Map

#### Visual Overview

What it’s for: A narrative map that puts a selected geography (or shortlist) in focus while keeping the surrounding geography visible for orientation and comparison. It’s your “camera zoom” map: here’s the place, here’s what it’s near, here’s how it sits in the broader pattern.  Questions it answers: Where is the target? What’s the surrounding context (neighbors, region, state)? Is the target an outlier relative to nearby areas? What does the local spatial pattern look like around the target?  Best when: Deep dives, executive summaries, and “market spotlight” sections. Works especially well at County/ZCTA where a plain choropleth can feel visually busy.  Not ideal when: You need to compare many targets at once (use small multiples or ranked bars + a standard choropleth), or when geography is not meaningful for the story (use scatter/bar instead).
#### Variants (choose your “mode” first)

- Single highlight (selected geo): highlight one CBSA/county/ZCTA, mute everything else.
- Highlight + neighbor ring: highlight target + adjacent geos (or within-buffer geos).
- Highlight on choropleth: full choropleth coloring by metric + emphasized outline for target.
- Inset zoom: main map shows broader area; inset zoom shows dense core (great for ZCTAs).
- Shortlist highlight: highlight 3–10 selected markets, everything else muted (best paired with a bar chart).
#### Required Data Contract

Base grain: 1 row per geo per snapshot/time_window, joinable to geometry.
Required fields (data):
- geo_level
- geo_id
- geo_name
- time_window
- source, vintage
- highlight_flag (TRUE/FALSE) or a highlight_id list used to create the flag
Plus one of the following, depending on variant:
- Pure highlight map (no metric): no metric required
- Highlight on choropleth: metric_value, metric_label (optional bin)
Required fields (geometry):
- geo_id
- geometry (sf)
Optional fields (recommended):
- context_group (state/region/division boundary label)
- neighbor_flag (TRUE/FALSE) if doing neighbor ring
- bin for binned choropleth background
- note (suppressed, missing, caveats)
Filters & assumptions:
- One geo_level per map (don’t mix CBSA + county polygons unless explicitly overlaying).
- One time_window unless doing small multiples.
- Missing geos (join issues) must be explicit.
Pre-processing required:
- Define highlight set (single ID or shortlist).
- If doing neighbor ring: compute adjacency (touching polygons) or distance buffer.
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- Highlight: strong outline/fill for highlight_flag == TRUE
- Context: muted fill/outline for non-highlight
- Optional background: choropleth fill by metric_value or bin
Hard requirements:
- Title includes highlighted geo name(s) + geo level.
- Subtitle includes time_window and what context is shown (e.g., “Counties within target CBSA” or “Neighbor counties shown”).
- Legend rules:
- If background choropleth: include metric legend + explicit “Highlighted market” key (or clear styling).
- If pure highlight: include a simple key (highlight vs context).
- Source + vintage footnote (and metric source if choropleth background).
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- State boundary outlines behind counties (helps orientation).
- Labels only for the highlight and maybe a few key neighbors.
- Inset zoom for dense ZCTA/tract views.
- Companion callout box with the highlight’s KPI values or rank.
#### Interpretation + QA Notes

How to read it: The highlight tells you “where to look,” the muted context tells you “what surrounds it,” and the optional choropleth layer tells you “how it compares.”  Common pitfalls: Over-styling (too many layers), context too zoomed out to be meaningful, missing join causing “ghost areas,” and highlights that don’t match the filter/time window in the subtitle.  Quick QA checks: Highlight IDs match the intended selection; join success rate is high; zoom extent matches stated context; legend clearly separates highlight from background metric.
#### Example Question Bank

- Where is the target CBSA and what counties/ZCTAs surround it?
- Within the target CBSA, which ZCTAs are the affordability outliers? (highlight + choropleth)
- Are the target county’s neighbors experiencing similar growth patterns?
- How does the target compare to adjacent counties on rent burden?
- Which “Sweet Spot” shortlist markets cluster geographically, and which are isolated?
### Slopegraph

#### Visual Overview

What it’s for: A clean “before vs after” comparison showing how values change between two time points across a set of geographies or categories.  Questions it answers: Which places improved or declined the most? Did the ordering shift? How big are the gaps between start and end?  Best when: Exactly two periods (or two scenarios), a moderate number of entities (roughly 5 to 25), and you want to emphasize direction and magnitude of change without a full time series.  Not ideal when: You have many time points (use line charts), too many entities (use ranked bars or small multiples), or you need precise intermediate-year dynamics.
#### Variants (choose your “mode” first)

- Geo change slopegraph: selected geo set across two years (CBSA, counties within a CBSA, ZCTAs within a CBSA).
- Rank slopegraph: show rank at two time points instead of value (if rank movement is the story).
- Indexed slopegraph: normalize to base = 100 at start year for easy relative comparison across different levels.
- Benchmark slopegraph: include benchmark series (US, region, peer average) as reference.
- Grouped slopegraph: facet or group by Region, Division, CBSA type when comparing multiple cohorts.
#### Required Data Contract

Base grain: 1 row per entity per period, for two periods only (long/tidy).
Required fields:
- geo_level
- geo_id
- geo_name
- period (year or label, but only two unique values in the plotted set)
- metric_id
- metric_label
- metric_value
- source
- vintage
Optional fields (recommended):
- group (Region, Division, CBSA Type, State)
- highlight_flag (TRUE/FALSE for selected focus geos)
- benchmark_flag or benchmark_label
- rank (if using rank variant)
- note (data caveats, definitional breaks)
Filters & assumptions:
- Exactly two period values per chart.
- One geo_level per chart unless explicitly designed.
- Entity set should be defined and stated (Top N, peer set, counties within CBSA, etc.).
- Missing values in either period should be explicit (either drop with a stated rule or show as missing and explain).
Pre-processing required:
- Select the two periods (start, end).
- Decide ordering: by end value, by change, or fixed canonical ordering.
- Optional: compute delta_value and pct_change for labeling or sorting.
- If indexed: compute index_value = metric_value / start_value * 100 per entity.
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- X-axis = period (two columns, start and end)
- Y-axis = metric_value (or index_value or rank)
- Line connects the same geo_id across the two periods
- Color = highlight_flag or group (use sparingly to avoid clutter)
Hard requirements:
- Title includes metric + entity universe (example: “Median Household Income Change, Selected CBSAs”).
- Subtitle includes the two periods and any transform (indexed, rank).
- Axis labels include units (percent, dollars, index).
- Clear label strategy: either label lines at endpoints or label highlighted subset only.
- Source + vintage footnote.
- Standard fonts and number formatting (per Standards).
Optional add-ons:
- End labels for all lines when N is small; otherwise only for highlights and top movers.
- Sort lines by end value (most common) or by change (if narrative is “movers”).
- Add benchmark line(s) (US, region avg) as distinct styled series.
- Add delta labels (+$ or +pp) at the end point for highlighted lines.
- Facet by group for cleaner comparisons across cohorts.
#### Interpretation + QA Notes

How to read it: Each line is one entity; slope shows direction and magnitude of change from start to end. Steeper slope means bigger change.  Common pitfalls: Too many lines; ambiguous ordering; mixing levels and growth without clarity; missing periods causing silent drops; inflation or definitional changes misread as real change.  Quick QA checks: Exactly two periods; entity count matches the intended filter; units correct; ordering logic matches subtitle; missing handling is explicit; if indexed, base period values exist for all included entities.
#### Example Question Bank

- Which CBSAs saw the largest change in real per capita income between 2013 and 2023?
- How did rent burden change from 2018 to 2023 for counties within the target CBSA?
- Did affordability improve or worsen pre vs post 2020 for a peer set of metros?
- Which ZCTAs in the target metro moved most on home value-to-income between 2019 and 2024?
- How did the target CBSA shift relative to its region benchmark between two periods?

### Heatmap Table (geo × metric or geo × year)
#### Visual Overview

What it’s for: A compact matrix for scanning lots of information quickly. It’s the best “shortlist + diagnose” view: rows are geographies (or metrics), columns are metrics (or years), and color encodes relative magnitude.  Questions it answers: Which geos look strong/weak across many KPIs? Which metrics are consistently high/low for a geo? How do geos compare within a peer set? How does one geo’s metrics evolve across years?  Best when: You need a high density summary (top tracts, shortlist of CBSAs, counties within a CBSA, selected ZCTAs) across many KPIs or across time. Great for exploratory analysis and appendix style “scan panels.”  Not ideal when: You need exact values as the primary takeaway (use tables with numbers, ranked bars), you have too many rows without filtering (becomes unreadable), or your metrics are on wildly different scales and you haven’t standardized them.
#### Variants (choose your “mode” first)

- Geo × Metric heatmap: rows = geos, columns = metrics (best for market profiles and shortlists).
- Geo × Year heatmap: rows = geos, columns = years for one metric (best for spotting timing patterns and breaks).
- Metric × Year heatmap (single geo): rows = metrics, columns = years (best for a single market “dashboard”).
- Binned heatmap (quantiles): colors represent percentile bins rather than continuous values (often more readable).
- Rank/percentile heatmap: cells show percentile/rank (recommended default for multi-metric views).
- Clustered heatmap: reorder rows/columns by similarity to reveal peer groupings (optional later).
#### Required Data Contract

Base grain: 1 row per geo per period per metric (long/tidy preferred).
Required fields:
- geo_level
- geo_id
- geo_name
- time_window (for snapshot views) or period (for year heatmaps)
- metric_id
- metric_label
- metric_value (numeric)
- source
- vintage
Optional fields (recommended):
- metric_group (Population/Economics/Housing/Affordability)
- normalized_value (percentile/z-score/rank) for comparable coloring
- direction (higher_is_better / lower_is_better) or polarity flag
- group (Region/Division/CBSA Type/State) for filtering/faceting
- highlight_flag (focus geos)
- note (suppressed, missing, caveats)
Filters & assumptions:
- For geo × metric: fix one time_window and a curated metric set.
- For geo × year: fix one metric_id and a defined year range.
- Use a clearly stated “universe” for normalization (All CBSAs, within CBSA counties, within CBSA ZCTAs).
- Missingness must be explicit (blank/NA fill), not silently dropped.
Pre-processing required:
- Decide and compute the displayed statistic:
- For multi-metric heatmaps, recommended default: percentile (0–100) with polarity applied so “better” is consistently higher.
- For single-metric geo × year, you can color by raw metric_value or percentile within year.
- Pivoting:
- Either pivot to wide for table-like rendering or keep long and map tile geometry in plotting.
- Optional: ordering:
- Rows by composite score, by a key metric, or by clustering.
- Columns in canonical order, or grouped by metric_group.
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- Tile position = (row entity, column entity)
- Fill color = normalized_value (preferred) or metric_value
- Optional text label in cell = value or percentile (only if sparse enough)
Hard requirements:
- Title includes what the matrix is (Geo × Metric or Geo × Year), geo_level, and universe definition.
- Subtitle includes time_window or year range and normalization method (percentile/z-score/raw).
- Legend clearly describes the fill statistic and directionality (especially if polarity applied).
- Clear missing data encoding (“No data”).
- Source + vintage footnote (can be summarized).
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Row or column grouping headers (metric_group sections).
- Highlight row(s) for selected geo(s).
- Sorting controls: by composite score, by key metric, by change.
- Add marginal summaries: row mean/median percentile, or “count of strong metrics.”
- Clustered reordering to reveal similar geos or correlated metric blocks (later).
- Facet by group (Region/Division) if building multiple panels.
#### Interpretation + QA Notes

How to read it: Scan across a row to see a geo’s profile; scan down a column to compare geos on a metric; look for blocks (systematic strengths/weaknesses) and anomalies (one-off spikes).  Common pitfalls: Mixing incomparable raw metrics; unclear polarity; overcrowding; normalization done on the wrong universe; missingness patterns misread as low values.  Quick QA checks: Universe and normalization stated and correct; polarity applied consistently; metric set is canonical; expected row/column counts; missing encoded distinctly; if percentiles used, distribution looks plausible (not all saturated).
#### Example Question Bank

- Across the top 25 tracts, which ones are consistently strong across growth, headroom, permits tailwind, and affordability guardrails?
- For counties in the target CBSA, which dimensions are strongest vs weakest (percentile heatmap)?
- For selected peer CBSAs, what does the full KPI profile look like in one scanable matrix?
- For one metric (rent burden), which ZCTAs show persistent stress across 2015–2023?
- Which metrics improved most in the target CBSA from 2013 to 2023 (metric × year heatmap)?

### Boxplot (with optional Violin)

#### 1) Visual Overview
**What it’s for:** A distribution comparison chart that summarizes spread, central tendency, and outliers across groups. It is the most efficient way to answer “how does this metric vary across places?” and “where does a highlighted geo sit relative to the distribution?”  
**Questions it answers:** What is the median and spread across groups? Are there long tails or extreme outliers? Do groups differ meaningfully (Region, Division, CBSA Type, peer set)? Where does the target geo land (above or below typical)?  
**Best when:** Comparing distributions of a single metric across categories or cohorts, especially for ZCTA or county level metrics where variation is large.  
**Not ideal when:** You need exact values for many entities (use ranked bars), you need the full distribution shape for precise tail behavior (use ridgeline or ECDF), or sample sizes are very small.

#### 2) Variants (choose your “mode” first)
- **Single-metric grouped boxplot:** default, compare groups (Region, Division, CBSA Type).
- **Boxplot + highlighted point:** show the target geo as a point overlay (recommended default for narratives).
- **Horizontal boxplot:** better for many groups or long labels.
- **Violin + box overlay:** show full density shape plus summary statistics (use when distribution shape matters).
- **Faceted boxplots:** compare multiple metrics using small multiples (limit metric count).
- **Binned boxplots by time_window:** compare distributions across windows (2013–2023 vs 2018–2023).

#### 3) Required Data Contract
**Base grain:** 1 row per geo per snapshot/time_window for one metric (long/tidy).

**Required fields:**
- `geo_level`
- `geo_id`
- `geo_name`
- `time_window` (or `period` if using years)
- `metric_id`
- `metric_label`
- `metric_value` (numeric)
- `source`
- `vintage`

**Optional fields (recommended):**
- `group` (Region, Division, CBSA Type, State, peer set label)
- `highlight_flag` (TRUE/FALSE)
- `weight_value` (population/housing units) if you later want weighted summaries (optional, advanced)
- `note` (suppressed, caveats)

**Filters & assumptions:**
- One `geo_level`, one `metric_id`, and one `time_window` per chart unless faceting.
- Define the universe clearly (All CBSAs, counties within target state, ZCTAs within a CBSA).
- Handle missing values explicitly (drop with stated rule or show missing count in subtitle/caption).

**Pre-processing required:**
- Decide outlier rule: default boxplot whiskers based on IQR; optionally clip extreme values for display only, with a note.
- Optional: transform heavily skewed metrics (log) only when documented.

#### 4) Visual Specs (Encoding + Elements + Add-ons)
**Core encodings:**
- X-axis = `group` (or `metric_label` if single group and multi-metric facet)
- Y-axis = `metric_value`
- Box shows median, IQR, whiskers; points beyond whiskers are outliers
- Overlay point for `highlight_flag` if using narrative variant

**Hard requirements:**
- Title includes metric + universe and `geo_level`.
- Subtitle includes `time_window`, grouping dimension, and any transforms (log).
- Axis labels include units.
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).

**Optional add-ons:**
- Overlay highlight point and label (target geo).
- Add jittered points for small N (to show raw distribution).
- Order groups by median value for readability.
- Add reference line for benchmark (US or peer average).
- Switch to violin when shape matters and N is sufficient.

#### 5) Interpretation + QA Notes
**How to read it:** The line inside the box is the median; the box is the middle 50%; whiskers show typical range; outlier points show extremes. Compare medians and spreads across groups.  
**Common pitfalls:** Over-interpreting outliers (data quality issues or small denominators), mixing universes without stating it, using too many groups with unreadable labels, skewed metrics that compress boxes.  
**Quick QA checks:** Universe and grouping match subtitle; units correct; missing handling is explicit; highlight point matches intended geo; if groups ordered, ordering logic matches stated approach.

#### 6) Example Question Bank
- How does rent burden vary across regions, and where does the target CBSA fall?
- For counties in the target CBSA, what is the distribution of median rent-to-income?
- Within the target CBSA, do ZCTAs show a long tail of high commute intensity?
- Are Sweet Spot markets outliers on affordability relative to all CBSAs?
- How does the distribution of income growth differ by CBSA type (metro vs micro)?

## Deep Dive Specialists

### Age Pyramid

#### Visual Overview

What it’s for: A demographic structure chart showing the distribution of population by age bins split by sex (or another binary group). It quickly communicates whether a place skews young, family-aged, or older, and where the bulges and gaps are.  Questions it answers: Is this place aging or young? Does it have a family formation bulge (25–44 plus children)? Is there a retiree concentration? How does the age structure differ from a benchmark (CBSA vs US, county vs CBSA, ZCTA vs county)?  Best when: You want a “who lives here” profile in a deep dive and you can compare one geography to a benchmark or a small set of peers.  Not ideal when: You need precise cross-geo comparisons across many markets (use age-band composition bars or a heatmap table), or when small geographies have unstable estimates.
#### Variants (choose your “mode” first)

- Single-geo pyramid (counts): descriptive, but less comparable across geos (use sparingly).
- Single-geo pyramid (percent of total): recommended for comparison-ready profiles.
- Geo vs benchmark overlay: target vs benchmark as mirrored outlines or side-by-side small multiples (recommended default).
- Small multiples (few geos): compare 3–6 geos (CBSA vs peer CBSAs; counties within CBSA).
- Age-band simplified pyramid: fewer bins (0–17, 18–34, 35–54, 55–64, 65+) when you need a high-level read.
#### Required Data Contract

Base grain: 1 row per geo per age_bin per sex per snapshot (year/vintage).
Required fields:
- geo_level
- geo_id
- geo_name
- period (year or ACS vintage year)
- age_bin (standard bins; recommended 5-year bins plus 85+)
- sex (Male/Female; or consistent coded values)
- pop_value (numeric count)
- source
- vintage
Optional fields (recommended):
- pop_total (for percent conversion; can be derived)
- pop_share (percent of total, derived)
- benchmark_flag / benchmark_label (US, CBSA avg, etc.)
- highlight_flag (for target vs benchmark emphasis)
- note (small sample, suppression, caveats)
Filters & assumptions:
- Default to one period per chart (one ACS vintage).
- Don’t mix geo levels unless it’s explicitly target vs benchmark (e.g., county vs CBSA).
- Use a consistent age_bin scheme across all pyramids in the library.
- If using percent, ensure both sexes sum to 100% of total population when combined (or 50/50 split by sex share if defined that way).
Pre-processing required:
- Standardize age bins (prefer 5-year bins; ensure a clean 85+ top bin).
- Compute pop_share = pop_value / sum(pop_value across age_bin and sex) per geo for percent variant.
- Choose sign convention for plotting:
- Male as negative values, Female as positive (classic), or vice versa, but be consistent across the library.
- If comparing to benchmark, ensure both datasets share identical bins and period.
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- Y-axis = age_bin (ordered youngest to oldest)
- X-axis = pop_share (preferred) or pop_value
- Fill or color = sex (male vs female)
- If benchmark variant: additional outline/alpha layer for benchmark vs target
Hard requirements:
- Title includes geo name + geo level (and benchmark name if used).
- Subtitle includes period and whether values are percent or counts.
- X-axis labels reflect the metric (percent of population, or population count) and show symmetry around 0 when using signed values.
- Clear legend for sex and benchmark (if applicable).
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Add vertical reference at 0 and symmetric axis limits for comparability across multiple pyramids.
- Add callouts for notable bulges (e.g., “25–34 concentration”).
- Add companion summary metrics near the chart: median age, dependency ratios, share under 18, share 65+.
- Small multiples for county profiles within a CBSA (limit panels to keep readable).
#### Interpretation + QA Notes

How to read it: Wider bars indicate larger population share in that age band for that sex. Look for bulges (dominant cohorts), pinches (missing cohorts), and the relative width of child-bearing and retirement-age groups.  Common pitfalls: Using counts when comparing geos; inconsistent bins across charts; axis limits changing across small multiples; over-interpreting noisy small-geo estimates; confusing sign convention.  Quick QA checks: Age bins cover full range and are ordered; male/female totals match expected totals; percent shares sum correctly; benchmark uses same bins and period; axis symmetry and labeling are correct.
#### Example Question Bank

- Does this CBSA skew younger or older than the national benchmark?
- Which counties within the CBSA have the strongest family formation profile (children plus 25–44)?
- Is the metro aging faster than peers (compare 2013 vs 2023 pyramids as small multiples)?
- Do target ZCTAs show a retiree concentration that differs from the broader county?
- How do demographic structure differences align with housing demand signals (family vs single-person households)?
### Bump Chart

#### Visual Overview

What it’s for: A rank-over-time chart that shows how ordering changes across periods. It’s the cleanest way to tell “who moved up, who moved down, who stayed stable” without focusing on raw values.  Questions it answers: Which CBSAs jumped in rank on a metric? Which fell? Are the leaders stable or rotating? Did the target market improve relative to peers?  Best when: You care about rank narrative across a limited set (top N, a peer list, counties within a CBSA) and have 3–10 time points.  Not ideal when: You need magnitude of change (use line or slopegraph), the entity set is huge (too many lines), or ranks are noisy due to small sample volatility.
#### Variants (choose your “mode” first)

- Top N bump (fixed set): choose top N at the end period (or start) and track them across time (recommended default).
- Peer set bump: fixed list of peer geos tracked over time (good for deep dives).
- Rolling top N bump: top N recalculated each year (more dynamic, but harder to interpret).
- Highlighted bump: many muted lines plus 1–3 highlighted geos (best for narrative).
- Grouped/faceted bump: facet by Region/Division/CBSA Type to avoid clutter.
#### Required Data Contract

Base grain: 1 row per geo per period per metric.
Required fields:
- geo_level
- geo_id
- geo_name
- period (year/date)
- metric_id
- metric_label
- metric_value (used to compute rank)
- source
- vintage
Optional fields (recommended):
- rank (precomputed, or compute during plot prep)
- group (Region/Division/CBSA Type/State)
- highlight_flag
- peer_flag (if using peer set)
- note (method changes, missingness)
Filters & assumptions:
- One geo_level and one metric_id per chart.
- Entity universe must be defined and stated:
- “Top 10 CBSAs by X in 2023”
- “Selected peer metros”
- “Counties within target CBSA”
- Handle ties explicitly (dense_rank vs row_number) and keep consistent across time.
- Missing periods should be visible or the entity should be dropped with a stated rule.
Pre-processing required:
- Compute ranks per period using a consistent method.
- Choose direction: rank 1 at top. Invert axis so smaller rank plots higher.
- Determine the entity set:
- Fixed top N based on end period (recommended for stable story), or
- fixed peer list, or
- dynamic top N (use cautiously).
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- X-axis = period
- Y-axis = rank (inverted so 1 is top)
- Line = one geo_id across time
- Color = highlight_flag (preferred) or group (only if small number of groups)
Hard requirements:
- Title includes metric + universe definition (e.g., “Top 15 CBSAs by Income Growth, Rank Over Time”).
- Subtitle includes year range, ranking method (dense_rank vs row_number), and how the entity set was selected (top N in end year vs peers).
- Axis labeling: y-axis indicates rank direction (1 at top).
- Endpoint labels: label the rightmost end for highlighted geos (and optionally all lines if N is small).
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Highlight the target geo(s) and mute others.
- Show rank change annotation at end (+/− positions).
- Facet by group to reduce clutter.
- Add faint gridlines per rank to help reading.
- Add “banding” for top 5/top 10 zones (subtle background stripes).
#### Interpretation + QA Notes

How to read it: Lines moving up represent improving rank; moving down represent declining rank. Crossing lines indicate changes in ordering.  Common pitfalls: Rank volatility mistaken for meaningful change; entity set changes year-to-year without being stated; ties handled inconsistently; too many lines; mixing levels and growth metrics without clarity.  Quick QA checks: Ranks computed per period correctly; y-axis inverted; entity universe matches title/subtitle; missing periods handled intentionally; tie method consistent.
#### Example Question Bank

- Which CBSAs moved into the top 10 for 5-year population growth over the last decade?
- Did the target CBSA improve in affordability rank relative to its peer set since 2018?
- Are the top performers stable, or is there churn in the top 15 for income growth?
- Which counties within the CBSA rose fastest in rent burden rank from 2013–2023?
- How did the “Sweet Spot” markets shift in rank on overheating risk over time?
### Waterfall Chart

#### Visual Overview

What it’s for: A decomposition chart that explains how a total is built from parts or how a total change is driven by contributing components. It’s the best “why did this change?” visual when you can express the story as additive pieces.  Questions it answers: What components drive the total? Which components contributed most to growth or decline? What offsets what? How does the target compare to a benchmark decomposition?  Best when: You have a clean additive breakdown (income components, GDP by sector, housing stock change components, population change components if you build them) and you want an explainable narrative.  Not ideal when: Components are not additive, definitions overlap, or the audience needs time dynamics across many periods (waterfall is typically one snapshot or one change window).
#### Variants (choose your “mode” first)

- Level decomposition: total level broken into components (e.g., total personal income = wages + proprietors + dividends + transfers).
- Change decomposition: change over a window broken into component changes (e.g., 2013→2023 change in income components).
- Benchmark comparison: two waterfalls side-by-side (target vs peer avg or target vs US).
- Percent contribution waterfall: components expressed as share of total change (more interpretable for some audiences).
- Grouped waterfall: components grouped into categories (e.g., “Earnings” vs “Transfers”) to reduce clutter.
#### Required Data Contract

Base grain: 1 row per component per geo per snapshot or change window.
Required fields:
- geo_level
- geo_id
- geo_name
- time_window (or start_period and end_period)
- total_label (e.g., “Total Personal Income”)
- component_id
- component_label
- component_value (for level decomposition) or component_delta (for change decomposition)
- unit_label (e.g., USD, percent, people) or implied via metric metadata
- source
- vintage
Optional fields (recommended):
- component_group (for grouping)
- benchmark_label / benchmark_flag (if comparing)
- highlight_flag (target emphasis)
- sort_order (canonical ordering of components)
- note (caveats, definitional changes)
Filters & assumptions:
- Components must sum to the total (level) or component deltas must sum to the total change (change).
- The component list should be stable and stated.
- One geo_level per chart unless benchmark comparison is explicit.
Pre-processing required:
- Choose ordering: canonical logical order beats magnitude sort for interpretation (example: earnings first, transfers later).
- For change waterfall: compute component_delta = value_end - value_start per component; compute total_delta.
- Optional: roll up small components into “Other” to keep component count manageable (target 5–10 bars).
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- X-axis = ordered components plus start and end totals
- Y-axis = running total position
- Bar height = component contribution (positive or negative)
Hard requirements:
- Title includes what is being decomposed and the geo universe (e.g., “Drivers of Personal Income Change, 2013→2023”).
- Subtitle includes time_window (or start/end periods), units, and whether it is level or change.
- Clear labeling of start total and end total (or total change) and units.
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Component value labels (only when not cluttered).
- Group separators or grouped totals (earnings vs transfers).
- Benchmark side-by-side waterfall (target vs benchmark).
- Percent share annotations (component contribution as % of total).
- Callouts for the top 1–2 drivers and top offsetting components.
#### Interpretation + QA Notes

How to read it: Start at the initial total, each component adds or subtracts, and you end at the final total or total change. The largest bars are the main drivers.  Common pitfalls: Components not truly additive; double counting; ordering that obscures the story; too many small components; mixing nominal and real dollars without clarity; definitional breaks across periods.  Quick QA checks: Sum of components equals total (or total delta) within tolerance; units consistent across components; period window correct; “Other” aggregation documented if used; benchmark uses same component definitions.
#### Example Question Bank

- What drove the change in personal income from 2013 to 2023 in the target CBSA (wages vs transfers vs dividends)?
- How does the income component mix differ between the target CBSA and the regional benchmark in 2023?
- What components explain GDP change by major sectors over the last decade?
- For housing stock change, what share is driven by 1-unit vs multi-unit additions (if available)?
- Which components offset growth (negative drivers) in the last 5 years for the target county?
### Bivariate Choropleth

#### Visual Overview

What it’s for: A map that encodes two metrics at once using a bivariate color grid (typically a 3×3 or 4×4 bin scheme). It answers “where do these two conditions overlap?” in a single view, which is hard to do with separate maps.  Questions it answers: Where are areas that are high on both metrics (or high on one and low on the other)? Where do growth and affordability overlap? Where are risk factors co-located?  Best when: You have two conceptually linked metrics and a clear story about their overlap, especially in deep dives at County or ZCTA (and sometimes CBSA).  Not ideal when: The audience needs precise values, you have more than two metrics, or you can’t keep the bin legend simple. It also works poorly if one metric is extremely skewed and bins collapse.
#### Variants (choose your “mode” first)

- 3×3 quantile bivariate (recommended default): low / medium / high for each metric.
- 4×4 quantile bivariate: more nuance, higher cognitive load.
- Custom threshold bivariate: bins defined by domain cutoffs (e.g., rent burden > 30%, growth > 5%).
- Benchmark-relative bivariate: above/below benchmark on each metric (simple, interpretable).
- Facet bivariate: same bivariate scheme repeated across time_window or across groups (use sparingly).
#### Required Data Contract

Base grain: 1 row per geo per snapshot/time_window, joinable to geometry.
Required fields (data):
- geo_level
- geo_id
- geo_name
- time_window
- x_value (metric A)
- y_value (metric B)
- x_label
- y_label
- source
- vintage
Required fields (geometry):
- geo_id
- geometry (sf)
Optional fields (recommended):
- x_bin and y_bin (precomputed bin labels 1–3 or 1–4)
- bivar_class (combined class like “1-3”)
- highlight_flag (focus geo outlines)
- group (Region/Division/CBSA Type for filtering/faceting)
- note (missingness, suppression)
Filters & assumptions:
- One geo_level and one time_window per map unless small multiples.
- Define the binning universe explicitly (All CBSAs, counties within state, ZCTAs within CBSA).
- Missing values must be explicit (No data class), not dropped.
Pre-processing required:
- Choose binning method:
- default: quantiles (3×3) computed within the chosen universe
- alternative: thresholds or benchmark-relative splits
- Compute x_bin, y_bin, and combined bivar_class.
- Check bin balance (avoid almost-empty classes).
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- Fill color = bivar_class using a fixed bivariate palette (3×3 or 4×4)
- Polygon geometry for chosen geo_level
Hard requirements:
- Title includes both metrics and geo scope (e.g., “Growth and Affordability Overlap by County”).
- Subtitle includes time_window, binning method (quantiles vs thresholds), and universe definition.
- Bivariate legend must show a clear 2D key: X axis metric A low→high and Y axis metric B low→high.
- Explicit missing category (“No data”).
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Highlight selected geos with outlines.
- Add small callouts for “high-high” cluster regions.
- Pair with companion ranked bar or scatter to give precision behind the map.
- Inset zoom for dense ZCTAs.
#### Interpretation + QA Notes

How to read it: Each color indicates the combination of bin levels for metric A and metric B. Focus on “high-high,” “low-low,” and the two tradeoff quadrants (“high-low,” “low-high”).  Common pitfalls: Legend confusion; too many bins; bins computed on the wrong universe; skewed distributions creating meaningless bins; interpreting bivariate colors as precise values.  Quick QA checks: Bin assignment matches the stated method; bin counts are reasonably balanced; missing values are labeled; legend orientation matches X/Y labels; same palette is reused across analyses for consistency.
#### Example Question Bank

- Where are counties that are high growth and still relatively affordable?
- Where are ZCTAs that combine high rent burden with low income (stress zones)?
- Within the target CBSA, where do high commute intensity and high permits tailwind overlap?
- Across CBSAs, which regions show the strongest overlap of economic strength and housing affordability?
- How does the overlap pattern change between 2013–2023 and 2018–2023 growth windows?
### Proportional Symbol Map (Bubble Map)

#### Visual Overview

What it’s for: A map that represents magnitude with symbol size, typically using points (centroids) placed within geographies. It’s the best option for mapping totals without area bias (large polygons dominating attention).  Questions it answers: Where are the biggest totals? How concentrated is activity? How do major centers compare? Where are secondary nodes?  Best when: The mapped quantity is a total (population, housing units, jobs, permits, parcels, trips) and you want to show concentration and hierarchy. Works well for CBSA, county, ZCTA and point data like parcels or amenities.  Not ideal when: You’re mapping rates/ratios that already control for size (choropleth is usually better), or when points overlap heavily without a clear decluttering strategy.
#### Variants (choose your “mode” first)

- Pure bubble map (size only): size encodes the metric, all bubbles same color.
- Bubble + category color: color encodes group (Region, CBSA type, cluster label) while size encodes magnitude.
- Bubble on context choropleth: choropleth shows a rate, bubbles show totals (use carefully).
- Top N bubbles only: show only the largest N to reduce clutter (recommended for national views).
- Bubble + highlight: muted bubbles for all, with 1–3 highlighted geos.
#### Required Data Contract

Base grain: 1 row per geography (or point entity) per snapshot/time_window.
Required fields (data):
- geo_level
- geo_id
- geo_name
- time_window
- size_value (numeric total mapped to symbol size)
- size_label (string, include unit)
- source
- vintage
Required fields (geometry):  Choose one:
- geometry (sf polygon) to derive centroids, or
- lon, lat (preferred for performance and explicit control)
Optional fields (recommended):
- color_group (Region/Division/CBSA Type/cluster label)
- highlight_flag
- label_flag (TRUE/FALSE for labeling top bubbles)
- note (suppression, missingness, caveats)
Filters & assumptions:
- One geo_level per map unless explicitly overlaying different entity types.
- Default to one time_window unless small multiples.
- If using centroids from polygons, be consistent about projection and centroid method (geographic vs projected).
- Handle missing size_value explicitly (drop with note or show as “No data” category).
Pre-processing required:
- Define scale strategy for size:
- typically map sqrt(size_value) to radius (perceptual fairness)
- set a min and max size so small values remain visible without huge bubbles dominating
- Decide decluttering rule: top N only, jitter, transparency, or aggregation.
#### Visual Specs (Encoding + Elements + Add-ons)

Core encodings:
- Point position = centroid or provided lon, lat
- Symbol size = size_value
- Optional color = color_group or highlight_flag
Hard requirements:
- Title includes what is being mapped and geo scope (e.g., “Population Concentration by County”).
- Subtitle includes time_window and whether bubbles represent totals and any filtering (Top N).
- Size legend clearly indicates scale (example values) and units.
- Source + vintage footnote.
- Standard fonts/number formatting (per Standards).
Optional add-ons:
- Labels for top N bubbles (or highlighted targets).
- Context layer: light state outlines or muted polygons for orientation.
- Highlight selected geos with distinct outline or color.
- Insets for dense regions (e.g., NYC area) where overlap is unavoidable.
- Pair with ranked bar chart to provide exact values.
#### Interpretation + QA Notes

How to read it: Bigger bubbles mean larger totals. Look for concentration (few dominant bubbles) vs dispersion (many similar bubbles).  Common pitfalls: Overlapping points hiding data; using bubbles for rates (confusing); size scaling that exaggerates differences; centroid placement that misleads in irregular shapes; combining many layers and losing readability.  Quick QA checks: Bubble size scaling is sensible; legend shows correct units and example values; filtering rules match subtitle; points are correctly located; missing values handled intentionally.
#### Example Question Bank

- Where are population and housing units most concentrated across the state or region?
- Which counties account for the majority of new permits (total units) in the last year?
- Within a CBSA, where are the largest ZCTAs by population, and how do they align with affordability stress?
- Where are the largest clusters of retail parcels within the target zones?
- How concentrated are jobs or establishments across counties in the target metro (if using CBP/QCEW)?
## Nice-to-Haves

### Flow Map (migration / commuting / trade)

#### Visual Overview

What it’s for: Show directional movement between origins and destinations (net flows or gross flows). Best for: IRS county migration, commuting flows, trade-like movements. Not ideal when: Too many OD pairs (hairball), weak geocoding, or the audience needs exact volumes rather than pattern.
#### Variants

- Top N flows only (recommended)
- Net flow map (in minus out)
- Inflow only / outflow only
- Chord or sankey companion (non-map)
- Facet by time_window
#### Required Data Contract

Base grain: 1 row per (origin, destination, period). Required fields: origin_id, origin_name, dest_id, dest_name, period or time_window, flow_value, source, vintage, plus geometry for origin and destination (centroids or lon/lat). Optional: net_flag, direction (in/out), highlight_flag, group. Pre-processing: filter to top N by absolute flow, optionally compute net, ensure consistent CRS.
#### Visual Specs

Encodings: line width = flow_value; arrow direction origin→dest; color = direction or highlight.  Hard requirements: state whether net or gross, clarify top N filter, include legend for width scale, source + vintage. Optional: basemap boundaries, labels for top nodes, inset for dense regions.
#### Interpretation + QA Notes

Pitfalls: hairballs, long-distance lines dominating, OD duplicates, net vs gross confusion. QA: totals match expected, top N rule applied, origin/dest points correct, units clear.
#### Question Bank

- What are the top inflow counties into the target CBSA counties?
- Are flows primarily local (within state) or long-distance?
- Which origins are the biggest net contributors?

### Stacked Area (composition over time)

#### Visual Overview

What it’s for: Show how a total and its parts evolve over time (levels or shares). Best for: industry mix over time, housing type mix, age-band shares over time. Not ideal when: Too many categories, categories churn over time, or you need precise comparisons of middle layers.
#### Variants

- Share (100%) stacked area (recommended for composition)
- Level stacked area (total plus parts)
- Small multiples by group
- Top K categories + “Other”
#### Required Data Contract

Base grain: 1 row per period per category per geo. Required fields: geo_level, geo_id, geo_name, period, category_id, category_label, value, source, vintage. Optional: share_value, category_group, note. Pre-processing: compute shares for 100% view; collapse small categories to Other; stable category mapping across years.
#### Visual Specs

Encodings: x = period; y = share or value; fill = category. Hard requirements: declare share vs level, stable legend order, source + vintage. Optional: label top categories at end, add total line overlay.
#### Interpretation + QA Notes

Pitfalls: visual dominance of bottom layer, too many categories, misleading total changes in share view. QA: shares sum to 100% per period, category set stable, totals match.
#### Question Bank

- How did the industry composition shift from 2013 to 2023?
- Is growth driven by one sector or broad-based?
### Ridgeline (distribution comparisons)

#### Visual Overview

What it’s for: Compare distributions across groups using stacked density curves. Best for: comparing ZCTA distributions across CBSAs, regions, or time windows. Not ideal when: audience is unfamiliar, sample size is tiny, or you need precise quantiles.
#### Variants

- Grouped ridgeline (regions / peer CBSAs)
- Time ridgeline (year per ridge)
- Weighted ridgeline (population weighted)
- Binned “joy histogram” alternative
#### Required Data Contract

Base grain: 1 row per observation with group label. Required fields: value, group_label, time_window (if used), source, vintage. Optional: weight_value, highlight_flag. Pre-processing: filter out extreme outliers or declare clipping, choose bandwidth, optionally weight.
#### Visual Specs

Encodings: x = value; y = group; density height = distribution. Hard requirements: units on x-axis, declare weighting if used, source + vintage. Optional: add median markers per ridge, facet by geo.
#### Interpretation + QA Notes

Pitfalls: misleading bandwidth, over-smoothing, groups with very different Ns, hard comparisons of tails. QA: group Ns reasonable, bandwidth consistent, units correct.
#### Question Bank

- How does rent burden distribution differ between target CBSA and peers?
- Are there long tails of stress neighborhoods?
### ECDF (threshold / distribution comparisons)

#### Visual Overview

What it’s for: A cumulative distribution curve that answers “what share is below/above X?” and compares distributions cleanly. Best for: threshold stories (rent burden > 30%, commute > 35 mins), comparing two or more groups. Not ideal when: you need intuitive reading for broad audiences without explanation, or too many lines.
#### Variants

- ECDF by group (2–5 lines)
- Weighted ECDF (population weighted)
- Difference ECDF (target minus benchmark)
#### Required Data Contract

Base grain: 1 row per observation.  Required fields: value, group_label, source, vintage.  Optional: weight_value, time_window.  Pre-processing: define thresholds and annotate them, handle missing, optionally weight.
#### Visual Specs

Encodings: x = value; y = cumulative share (0–1).  Hard requirements: annotate key thresholds, label lines clearly, source + vintage.  Optional: show median/percentile markers.
#### Interpretation + QA Notes

Pitfalls: unlabeled lines, unclear threshold, mixing universes, not stating weighting.  QA: cumulative ends at 1, group Ns correct, threshold line matches definition.
#### Question Bank

- What share of ZCTAs exceed 30% rent burden in the target CBSA vs peers?
- Is the entire distribution shifted or only the tail?
### Hex / Grid Map (tile map)

#### Visual Overview

What it’s for: Comparison-first mapping that removes area bias by placing geos on a regular grid/hex layout.  Best for: CBSA comparisons, state-level views, dashboards where shape isn’t the point.  Not ideal when: precise geography matters (local context, adjacency), or you don’t have a stable tile layout.
#### Variants

- State tile map
- CBSA tile map (custom layout)
- Hex tile map by region
- Highlight + tile map
#### Required Data Contract

Base grain: 1 row per geo per time_window.  Required fields: geo_id, geo_name, time_window, metric_value, metric_label, source, vintage, plus layout keys like tile_x, tile_y (and optional tile_group).  Pre-processing: build or source a layout mapping once, keep versioned.
#### Visual Specs

Encodings: tile position = (x,y); fill = metric.  Hard requirements: declare that layout is schematic, include legend and time_window, source + vintage.  Optional: labels for highlights, facets by group.
#### Interpretation + QA Notes

Pitfalls: layout misunderstood as geography, missing tiles due to layout gaps, inconsistent layout versions. QA: all expected geos mapped, no duplicates, layout version stated.
#### Question Bank

- Which CBSAs are top decile on growth without area bias dominating the view?
- Where do Sweet Spot markets sit in the national distribution?
### Point Map (markers)

#### Visual Overview

What it’s for: Show locations of discrete entities (parcels, amenities, job centers, listings) as points.  Best for: parcel shortlist maps, amenities maps, nodes on top of polygons.  Not ideal when: point counts are huge without clustering, or when polygons are the primary unit.
#### Variants

- Simple markers
- Clustered markers
- Category colored markers
- Markers over choropleth
- Heatmap density layer (if needed later)
#### Required Data Contract

Base grain: 1 row per entity.  Required fields: entity_id, entity_label (optional), lon, lat (or point geometry), time_window if relevant, source, vintage.  Optional: category, size_value, highlight_flag.  Pre-processing: validate coordinates, project consistently, filter to bounding area.
#### Visual Specs

Encodings: position = lon/lat; color = category; size = size_value. Hard requirements: map extent stated, legend for color/size, source + vintage. Optional: labels for highlights, clustering, insets.
#### Interpretation + QA Notes

Pitfalls: coordinate errors, overplotting, extent too wide/narrow, misleading symbol size.  QA: points fall in expected area, counts match filters, CRS consistent.
#### Question Bank

- Where are the top 50 retail parcels within target zones?
- Are amenities concentrated along key corridors?
### Radar Chart

#### Visual Overview

What it’s for: A “profile” chart comparing multiple metrics for a small number of geos.  Best for: high-level shape comparison when metrics are normalized and audience expects a stylized visual.  Not ideal when: precision matters, many geos/metrics, or scaling is not strictly standardized.
#### Variants

- Normalized radar (percentile or z-score) (only acceptable variant)
- Target vs benchmark radar
- Small multiple radars (rare)
#### Required Data Contract

Base grain: 1 row per geo per metric per time_window.  Required fields: geo_id, geo_name, time_window, metric_id, metric_label, normalized_value, source, vintage.  Optional: metric_group, highlight_flag.  Pre-processing: normalization required, polarity applied, metric set fixed.
#### Visual Specs

Encodings: angle = metric; radius = normalized_value.  Hard requirements: state normalization universe + method, limit ≤ 8 metrics and ≤ 5 geos, source + vintage.  Optional: companion strength strip or table.
#### Interpretation + QA Notes

Pitfalls: misread area/angles, normalization drift between charts, too much clutter.  QA: metric set identical, normalization stated, polarity correct.
#### Question Bank

- How does the target CBSA’s KPI profile compare to peer average across core categories?
- Which dimensions stand out as strengths or weaknesses?
