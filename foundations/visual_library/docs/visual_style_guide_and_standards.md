# Visual Style Guide

This document is the canonical visual standard for the visual library. It defines the visual identity, implementation defaults, and shared design rules that chart code and chart documentation should follow.

## 1. Purpose

Create a reusable visual system in R for charts, maps, and tables that feel like part of the same analytical product.

This library should support:
- exploratory analysis that is polished enough to share
- notebooks and research memos
- presentation and strategy ready visuals
- spatial and market analysis
- repeated comparison workflows across metros, regions, states, tracts, and parcels

The goal is not just consistency. The goal is to make the visuals instantly readable and recognizably yours.

## 1A. Implementation Scope

This guide is also the implementation-facing standard for the library.

### Shared code locations
- Shared style and formatting: `visual_library/shared/standards.R`
- Shared prep and render helpers: `visual_library/shared/chart_utils.R`
- Data contract validations: `visual_library/shared/data_contracts.R`
- Query helpers for SQL-driven tests: `visual_library/shared/scatter_query_helpers.R`
- Registry-driven analytics harness: `visual_library/run_visual_library_tests.R`

### How to apply the standard
- Load `visual_library/shared/standards.R` in chart test and render scripts.
- Use shared prep and render functions from `visual_library/shared/`.
- Override defaults only when chart-specific requirements justify it.
- Record chart-specific exceptions in the relevant chart decision log.

### Current implementation defaults
- Export format: `PNG`
- Base theme: `theme_minimal()` wrapped by `visual_theme()`
- Background: white for panels and exports
- Number formatting: `scales` helpers
- Caption builder: `build_chart_notes()` for source, vintage, and notes
- Chart API pattern: `prep_<chart>(data, config)` then `render_<chart>(data, config, theme = NULL)`
- Registry status vocabulary: `scaffolded`, `implemented`, `validated`

### Core-15 chart coverage
- Daily Drivers: `line`, `scatter`, `bar`, `choropleth`, `hexbin`
- Story Upgraders: `strength_strip`, `correlation_heatmap`, `highlight_context_map`, `slopegraph`, `heatmap_table`
- Deep Dive Specialists: `age_pyramid`, `bump_chart`, `waterfall`, `bivariate_choropleth`, `proportional_symbol_map`

---

## 2. Visual Identity

### Style keywords
- analytical
- clean
- modern
- restrained
- comparison first
- map forward
- presentation ready
- explanatory
- data journalism light

### Overall feel
The charts should look like they come from a serious analytical workflow, not a marketing deck. They should feel polished, but not glossy. Visual emphasis should come from hierarchy, contrast, and annotation rather than decoration.

### Design philosophy
- clarity first
- comparison over ornament
- structure over visual novelty
- analytical framing in titles
- explanatory subtitles that help decode the chart
- strong target and benchmark highlighting
- maps treated as first class visuals, not side assets

---

## 3. Core Design Principles

### A. Lead with the analytical question
Titles should state the comparison, ranking, or question directly.

Examples:
- Top 20 Fastest Growing Metros
- Are Southern Metros Building Enough Housing?
- Wilmington, NC Overview KPIs

### B. Use subtitles to explain the read
Subtitles should clarify:
- time window
- geography scope
- metric definition
- binning logic
- highlight logic
- benchmark logic

Subtitles should do real work. They should not simply restate the title.

### C. Make the focal comparison obvious
Every chart should make it clear what the reader should compare:
- target vs peers
- top vs rest
- selected geography vs benchmark
- local context vs broader context
- rank vs distribution

### D. Use emphasis selectively
Only a few elements should get strong attention at once:
- target geography
- top performers
- outliers
- benchmark lines
- selected parcels or clusters

### E. Keep non data ink restrained
Theme elements should support interpretation without taking over:
- subtle gridlines only when they improve reading
- minimal borders
- modest legend styling
- quiet axes

### F. Keep charts and tables in the same family
Tables should use the same hierarchy, spacing, and tone as charts.

---

## 4. Output Modes

The library should support two standard output modes built from the same base system.

## Notebook mode
Use for exploration, internal analysis, and iterative work.

Characteristics:
- minimal annotation
- fewer labels
- lighter framing
- compact analytical utility
- no boxed map labels unless they add strong value

## Presentation mode
Use for communication, polished reports, and centerpiece charts.

Characteristics:
- richer annotation when useful
- more title and subtitle support
- optional boxed map labels
- stronger benchmark callouts
- more explicit story framing
- clearer emphasis on target, top group, or takeaway

Default rule:
- build all visuals from the same master theme
- add annotation and communication layers depending on mode
- avoid creating separate visual identities by mode

---

## 5. Layout and Theme Rules

### Default background
- use a very light cool neutral background by default
- keep the plotting area clean and minimal
- do not use heavy panel borders
- pure white is an acceptable override for export contexts where tint creates friction

### Gridlines
- default to minimal structure
- use gridlines only when they improve interpretation
- keep all gridlines as subtle as possible
- horizontal gridlines are preferred for bars and scatters when needed
- vertical gridlines should be used sparingly
- minor gridlines should be lighter than major gridlines or removed entirely

### Axes
- axis titles should be clear and direct
- axis text should be readable but secondary to data and labels
- avoid heavy axis lines
- avoid unnecessary ticks and clutter

### Margins and spacing
- keep moderate outer margins
- allow enough breathing room for titles, subtitles, and legends
- avoid cramped plotting areas
- spacing should feel deliberate, especially in maps and tables

### Legend placement
Default preference:
- bottom right when possible
- otherwise right side when that better preserves chart area and readability

Practical rules:
- bottom works well for many bars, scatters, and grouped comparisons
- right works well for maps and more complex encodings
- avoid top placement unless it strongly improves reading

### Facets
- facet titles should be simple and readable
- strip styling should be minimal
- facet layouts should prioritize comparison, not novelty

---

## 6. Typography Rules

### General principle
Typography should be neutral, analytical, consistent, and hierarchy driven.

### Font family
Recommended primary font:
- Inter

Fallback stack:
- Inter
- Arial
- Helvetica
- sans-serif

### Title
- left aligned by default
- bold or semibold
- direct and specific
- sentence case preferred
- slightly larger than standard ggplot defaults

### Subtitle
- left aligned
- smaller than title
- regular weight
- darker gray rather than full black
- used for method, timeframe, encoding, or interpretation note

### Axis text
- clear and readable
- lower priority than title and data labels
- avoid oversized tick labels

### Legend text
- concise and readable
- legend titles should be descriptive, not shorthand

### Data labels and annotations
- compact
- legible at chart scale
- used intentionally, not everywhere
- consistent sizing across chart types

### Caption, notes, and source
- smaller than subtitle
- subdued tone
- aligned consistently
- used for source, note, or methodological caveat

### Table typography
- titles and subtitles should match chart hierarchy
- headers should be slightly emphasized
- body text should remain clean and neutral
- numeric formatting should be visually even

---

## 7. Color System

The library should use a palette system, not a single universal palette.

## A. Neutral palette
Use for:
- axes
- gridlines
- non highlighted outlines
- table rules
- background series
- muted comparison elements

Desired feel:
- soft gray structure
- dark neutral for key text and outlines
- lighter neutral for secondary elements

## B. Sequential default palette
Use for:
- ordered bars
- continuous value fills
- continuous scatter encodings
- density or intensity maps

Default direction:
- viridis based
- ordered, readable, and reliable across charts and maps
- suitable as the main default family across the library

## C. Binned choropleth palette
Use for:
- quintiles
- deciles
- ordered category maps

Rules:
- classes must be clearly separable
- ordering should be easy to read
- should remain interpretable when many polygons are shown
- viridis based or closely aligned ordered palettes are preferred unless another palette materially improves readability

## D. Diverging and signed metric palette
Use for:
- positive vs negative change
- above vs below benchmark
- good vs bad outcomes

Rules:
- red for worse
- blue or green for better
- neutral midpoint should be clearly distinguishable
- use only when the sign or direction materially matters

## E. Highlight palette
Use for:
- selected metro
- target tract
- chosen parcel
- emphasized subgroup
- selected comparison point

Rule:
- highlight color depends on analytical meaning and chart type
- do not hardcode one universal highlight color
- if the highlight represents risk or underperformance, use a red family
- if the highlight represents strength or opportunity, use a blue or green family
- if the highlight is simple selection, choose the accent that best preserves the read of the chart

## F. Quadrant and comparison palette
Use for:
- high growth / high permits
- high growth / low permits
- low growth / low permits
- benchmark categories

Rule:
- colors should carry analytical meaning
- categories should stay stable across charts if reused often

## G. Context overlay palette
Use for:
- roads
- water
- boundaries
- clusters
- parcels
- municipal overlays

Rule:
- contextual layers should support the main read
- they should never overpower the core metric fill

### Color principles
- neutralize background entities
- reserve saturated colors for emphasis
- keep ordinal palettes intuitive
- use color consistently for repeated concepts
- do not rely on color alone when outline, label, shape, or linetype can help

---

## 8. Benchmark and Threshold Grammar

This should be codified tightly for consistency across the library.

### Use cases
Apply the same benchmark grammar to:
- medians
- thresholds
- zero lines
- benchmark cutoffs
- quadrant boundaries

### Visual treatment
- medium light gray dashed line
- lighter than the primary data marks
- visually consistent across bars, scatters, and other chart families

### Label style
- concise benchmark language
- neutral gray text
- smaller than subtitle but clearly readable
- placed close to the line when useful
- avoid verbose phrasing

### Annotation language
Keep language consistent. Examples:
- Median Pop CAGR: 0.8%
- Median Permits per 1k: 4.7
- Zero growth
- Regional median
- Benchmark threshold

### Default rule
When interpretation depends on the reference line, label it.
When the line is common and self evident, it may remain unlabeled in notebook mode.

---

## 9. Highlight, Benchmark, and Emphasis Rules

### Selected geography rule
When a target metro, tract, parcel, or district is important:
- emphasize with stronger outline, label, or distinct fill treatment
- background peers should remain quieter
- the target should be identifiable within 2 to 3 seconds

### Semantic highlight rule
Highlights should reflect meaning, not just selection.
Examples:
- risk or worse outcome uses red family emphasis
- stronger outcome or opportunity uses blue or green family emphasis
- neutral selection can use accent logic that best fits the chart type

### Top N rule
When ranking or scanning:
- top items may be labeled directly
- labels should be reserved for meaningful items, not every point
- top N should have consistent selection logic

### Benchmark groups
Benchmarks should feel secondary to the main target, but still clear:
- muted comparison colors
- clean legend language
- consistent ordering across charts

### Outlines
Outlines are important, especially for maps:
- selected outline stronger than background outline
- top items can be outlined without changing fill logic
- outlines should support hierarchy, not create clutter

---

## 10. Labeling and Annotation Rules

### Direct labels
Preferred when:
- there are few highlighted entities
- the identity of the target matters
- legends would make comparison slower

### Map labels
Default rule:
- boxed labels are not the default for all maps
- use boxed labels in presentation mode or when they add strong analytical value
- avoid boxed labels in basic exploratory maps unless needed

### Boxed label style
When used:
- white or light label box
- rounded rectangle
- thin dark border
- short connector line when needed

### Bar labels
- use clean end labels for ranked bars
- align consistently
- format values clearly
- avoid redundant legends when labels are sufficient

### Scatter labels
- label only top items, target items, or analytically notable outliers
- use repel logic when needed
- support median lines and quadrant framing

### Table notes
- sources and caveats should be quietly presented
- use the same voice as chart subtitles

### Presentation mode annotation
When a chart is a centerpiece, richer annotation is acceptable:
- more direct labels
- benchmark callouts
- explanatory notes
- stronger subtitle framing
- boxed map labels when justified

---

## 11. Number and Text Formatting Rules

### Percentages
- use percent format for growth, rates, and shares
- precision should be consistent within a chart
- default to 1 decimal unless cleaner as a whole number

### Currency
- use commas and a dollar sign
- compact notation is acceptable when space is limited
- keep the same format within chart and table families

### Large numbers
- use K, M, and B when space is limited
- use full comma separated values in tables when space allows

### Ranks
- keep rank formatting simple
- avoid overly verbose ordinal forms unless analytically useful

### Dates and periods
- keep time windows explicit in title or subtitle
- use compact readable forms
- standardize year ranges and trailing notation

### Missing data
- missing fill should be visually distinct but quiet
- it must not be confused with a low value

---

## 12. Chart Type Behavior Rules

## Ranked bars
- sort descending by default
- direct end labels are preferred
- use ordered color only when it aids interpretation
- allow one highlight series or selected bar treatment where relevant

## Grouped bars
- use only when side by side comparison is essential
- keep legend simple
- subgroup ordering should be stable across charts

## Scatterplots
- support reference lines by default
- selected and top points may be labeled
- background points should not compete with highlighted points
- point size can encode scale, but the legend must remain readable

## Boxplots and violins
- use to compare distributions clearly
- support selected group markers
- distribution should remain readable over decoration
- outliers should be present but not visually aggressive

## Heatmaps and matrix charts
- use for structured comparisons
- labels and scales should remain legible
- color range must preserve ordered interpretation

---

## 13. Map Rules

Maps need their own explicit system while still inheriting from the master theme.

## A. Regional comparison maps
Use for:
- metro or district comparison across states or regions
- broad binning and ranking stories

Rules:
- binned classes are preferred
- selected metro can be outlined and labeled
- top metros can be labeled if it aids the story
- state outlines should be visible but secondary
- legends should clearly communicate quintiles, deciles, or ordered bins
- default national comparison extent should be the contiguous 48 states plus DC unless a broader footprint is analytically necessary

## B. State or metro context maps
Use for:
- target geography in nearby context
- comparison within one state or one metro system

Rules:
- target area should stand out through outline and label
- adjacent units should remain readable
- regional framing should support the target story

## C. Local market and tract maps
Use for:
- tract level scoring
- corridor overlays
- roads, water, parcels, and other contextual layers

Rules:
- hierarchy must be very clear
- core metric fill first
- roads second
- boundaries third
- water and contextual layers should support, not dominate
- selected zones or shortlist areas should stand out immediately
- framing should fit the study area tightly enough that the local pattern reads before labels or notes are added

## C1. Shared Map Defaults
- subtitle wrapping should be on by default for map-family charts
- US outline and state outlines should be shared base-layer toggles, not ad hoc chart-local hacks
- diverging choropleths should default to the stronger shared diverging palette so above/below-benchmark stories read clearly at presentation size

## C2. Map Composition Presets
- `national_compact`
- use for single-panel contiguous-US county, CBSA, or state maps
- applies a shared contiguous-US extent with tighter framing for reviewable national surfaces

- `facet_national`
- use for small-multiple national maps where all panels must keep the same extent and remain readable at reduced size
- applies shared contiguous-US extent plus leaner framing and outline weights tuned for faceting

- `local_focus`
- use for metro, county-within-metro, tract, and future ZCTA maps
- fits the frame to the study-area bbox with light padding for outlines, labels, and local context

## D. Boundary hierarchy
Default hierarchy:
1. selected target boundary
2. major geography or study area outline
3. internal units
4. supporting context lines

## E. Map labels
- use boxed labels selectively
- favor labels for top or target geographies
- avoid overcrowding
- use leader lines only when needed

## F. Continuous vs binned fills
Default:
- binned for broad comparison maps
- continuous for local intensity or continuous surface like metrics
- choose based on interpretability, not just data type

---

## 14. Table Rules

Tables should feel like part of the same library, not an external add on.

### Structure
- titles and subtitles should follow the same hierarchy as charts
- use subtle horizontal rules
- avoid heavy cell fills
- emphasize through spacing and alignment

### Alignment
- text columns left aligned
- numeric columns right aligned
- headers readable and slightly emphasized

### Formatting
- keep percent and currency formatting consistent
- do not mix precision within the same column
- use comma formatting for large values
- keep ranks and IDs visually simple

### Tone
- neutral, clean, and research forward
- visually quiet but polished

---

## 15. Accessibility and Readability Rules

### Readability
- prioritize legibility at notebook and slide sizes
- avoid overly small labels
- do not overload any one chart with too many highlighted elements

### Color use
- do not rely only on color when outline, label, shape, or linetype can reinforce meaning
- legend breaks should be clear and interpretable
- highlighted entities should remain visible when printed or projected

### Density
- when information is dense, use hierarchy rather than shrinking everything
- reduce labels before reducing legibility

---

## 16. Override Philosophy

The style guide should be strong, but not rigid.

### Default rule
All visuals should inherit the base system unless there is a clear analytical reason not to.

### Acceptable overrides
- map specific needs
- dense local context layers
- signed metric logic that requires a specific diverging treatment
- presentation constraints
- highly specific chart contracts

### Not acceptable
- arbitrary palette changes
- inconsistent label logic
- major shifts in title and subtitle hierarchy
- one off styling that breaks the overall family look

---

## 17. Signature Elements to Preserve

These already feel most like the core identity of the library:
- analytical titles
- explanatory subtitles
- target geography highlighting
- selective boxed map labels
- benchmark and median lines
- ranked bars with direct values
- map first comparison storytelling
- chart and table pairings
- restrained theme with minimal background structure

---

## 18. Implementation Summary

This guide implies the following implementation structure:
- one master theme
- one typography system
- one neutral system
- viridis as the default sequential family
- official semantic palette variants by use case
- one benchmark grammar for medians, thresholds, and zero lines
- one set of chart defaults with mode specific add ons
- one family system across charts, maps, and tables

The next step is to translate this into the Core Function List and then chart-specific tests and examples.

---

## 19. Decision Log

### VS-001: Output format
- Question: What is the default export format?
- Answer: PNG only for now.
- Status: Decided
- Date: 2026-03-02

### VS-002: Fonts
- Question: What font family or families should be used across charts?
- Answer: Inter is the recommended primary font, with Arial, Helvetica, and sans-serif fallback.
- Status: Decided
- Date: 2026-04-14

### VS-003: Color palette
- Question: What default palette or palettes should be used by chart type?
- Answer: Default to a `viridis`-based sequential family; allow alternatives such as `set2` or semantic manual highlights when analytically justified.
- Status: Decided
- Date: 2026-03-04

### VS-004: Annotation style
- Question: What annotation style should be standard?
- Answer: Use direct labels and callout boxes selectively, with emphasis reserved for targets, outliers, benchmarks, and top items.
- Status: Decided
- Date: 2026-04-14

### VS-005: Brand constraints
- Question: Are there required brand colors, logo usage, or layout constraints?
- Answer: No separate brand system is required yet; use the analytical visual identity defined in this guide.
- Status: Decided
- Date: 2026-04-14

### VS-006: Scatter trend line standard
- Question: Should scatter trend lines be standard and configurable?
- Answer: Yes. Default on, dashed style, configurable opacity, and toggle off supported.
- Status: Decided
- Date: 2026-03-04

### VS-007: Notes and footer standard
- Question: How should side notes and footers be handled?
- Answer: Standardize via `build_chart_notes()` with source, vintage, and optional side or footer notes.
- Status: Decided
- Date: 2026-03-04

### VS-008: Legend cleanup
- Question: How should legends handle missing values and numeric formatting?
- Answer: Drop missing categories from legends by default and avoid scientific notation using readable numeric labels.
- Status: Decided
- Date: 2026-03-04

### VS-009: Shared chart API
- Question: What function signature should reusable chart functions use?
- Answer: Use `prep_<chart>(data, config)` and `render_<chart>(data, config, theme = NULL)` across the library.
- Status: Decided
- Date: 2026-04-14

### VS-010: Map rendering fallback
- Question: How should map-family charts behave when geometry is missing in smoke-test environments?
- Answer: Render a diagnostic placeholder panel and record the missing geometry dependency in chart-level docs instead of failing silently.
- Status: Decided
- Date: 2026-04-14

### VS-011: Shared map composition defaults
- Question: Which map-family layout and styling defaults should be standardized across choropleths and related maps?
- Answer: Standardize subtitle wrapping, contiguous-US national extent, optional US/state outline base layers, a stronger diverging palette, and shared composition presets (`national_compact`, `facet_national`, `local_focus`) while keeping all of them configurable per chart.
- Status: Decided
- Date: 2026-04-15
