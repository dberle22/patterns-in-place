# Visual Library Workflow

## Purpose
This document outlines example workflows we have taken to build out our visual library and samples. Once we have a few examples of what worked well and what didn't then we can align on a specific agent.

## Bar Chart

### What You Asked For

You set the process really well:

Start with the chart’s spec and question coverage docs.
1. Align the shared prep_*.R and render_*.R functions to the spec and the visual style guide.
2. Build DuckDB-backed sample queries that answer the chart’s canonical business questions.
3. Put everything into a sample render script that is easy to review:
4. each question should have a visible query block, prep block, render block, and output file.
5. Iterate on correctness and visual quality by reviewing the exported PNGs.

That instruction structure worked very well because it combined:

- business intent
- chart contract
- implementation targets
- testing expectations
- reviewable output

### What We Changed

For bar charts, we worked across three layers.

In prep_bar.R, we made the prep layer more reusable and spec-aligned:

- explicit filtering by question_id, metric_id, and time_window
- ranking and display order handling
- support for top_n and bottom_n
- retention of highlighted targets even when truncating
- support for alternate sorting like absolute benchmark deltas
- metadata fields like truncated_flag and preserved rank

In render_bar.R, we made rendering match the style guide more closely:

- standards-aware config resolution and theming
- cleaner label and axis formatting
- highlight vs comparison coloring
- diverging bar support for benchmark charts
- shared subtitle and caption logic
- configurable spacing, expansion, and margins
- per-chart legend placement control

In test_bar_render.R, we made the sample harness explicit and reviewable:

- one DuckDB SQL builder per business question
- separate prep/render/export blocks for each output
- contract validation before rendering
- saved PNG outputs for each canonical question

### How We Iterated

The iteration pattern was basically:

1. Implement the first pass from the spec.
2. Run the sample script end to end.
3. Review the exported charts and compare them to expected business meaning.
4. Fix either:
    - data logic
    - metric scaling
    - subtitle/caption wording
    - layout/spacing
    - legend placement
5. Re-run the full script and inspect again.

That helped us catch several important issues:

- CURRENT_DATE in SQL triggered a DuckDB extension issue, so we injected vintage dates from R instead.
- The state benchmark chart needed a fallback because the us benchmark field was missing in the mart.
- Rent-to-income needed to use annualized rent logic correctly.
- The 5-year income growth scale needed to be corrected after over-adjustment.
- The diverging benchmark chart needed extra label room.
- The benchmark legend looked better at the bottom than on the right.

### A Good Reusable Pattern

For the next chart type, I’d recommend giving instructions in this shape:

1. Read [chart_spec.md] and question_coverage.md.
2. Update shared prep_<chart>.R and render_<chart>.R so they match the spec and visual_style_guide_and_standards.md.
3. Build DuckDB-backed sample question queries.
4. Create or update test_<chart>_render.R so each question has:
    - a query block
    - a prep block
    - a render block
    - an export path
5. Save outputs to the sample output folder so they are easy to review.
6. Then iterate with me on:
    - data correctness
    - metric scaling
    - titles/subtitles/captions
    - spacing/labels/legend placement

That pattern worked because it kept us moving from:
spec -> shared functions -> sample data -> rendered outputs -> visual QA

## Line Chart

### What You Asked For

The line chart request followed the same strong pattern as the bar chart work:

Start with the chart’s spec and question coverage docs.
1. Align the shared `prep_line.R` and `render_line.R` functions to the spec and the visual style guide.
2. Build DuckDB-backed sample queries from the Gold layer.
3. Put everything into a sample render script that is easy to review.
4. Make sure each question has a visible query block, prep block, render block, and output file.
5. Iterate by reviewing exported PNGs for correctness and readability.

That structure worked well again because it gave us:

- a clear chart contract
- a shared-function target
- real sample data instead of placeholder data
- visible outputs for review
- a natural iteration loop

### What We Changed

For line charts, we ended up working across four layers.

In `prep_line.R`, we made the prep layer more reusable and more spec-aligned:

- filtering by `question_id`, `time_window`, `metric_id`, `geo_ids`, and period range
- support for `single`, `multi`, `indexed`, and `rolling` variants
- indexed-series calculation with base-period guards
- optional completion of missing periods so gaps render intentionally
- duplicate-key checks to enforce one row per geo/metric/period
- better handling of highlight flags and metadata

In `render_line.R`, we made the renderer more standards-aware:

- standards-based config resolution and theming
- better default title and subtitle generation
- unit-aware axis formatting
- clearer selected-vs-peer line treatment
- default zero-baseline behavior to reduce misleading slope exaggeration
- benchmark support tied into shared defaults
- line color routing through shared palette config instead of local hardcoding

In `test_line_render.R`, we made the harness explicit and easier to review:

- one DuckDB SQL builder per business question
- separate query/prep/render/export blocks
- contract validation before rendering
- output PNGs saved for each canonical question

In the shared standards layer, we improved future maintainability:

- centralized comparison palette defaults
- centralized benchmark color defaults
- shared peer/series palette helpers
- the same reset path now works across line and bar charts

### How We Iterated

The iteration loop was very similar to the bar chart process:

1. Implement the first pass from the line spec.
2. Run the sample script end to end.
3. Review the PNGs against the business questions.
4. Fix either:
    - data logic
    - metric scaling
    - title/subtitle/caption wording
    - baseline/axis behavior
    - legend and peer color readability
    - file/folder organization
5. Re-run and inspect again.

That process helped us catch a few useful issues:

- the first line sample harness was too thin compared with bar, so we rebuilt it around explicit question blocks
- ad hoc R/DuckDB inspection needed safer SQL quoting
- the first peer palette changes were technically correct but visually too subtle
- the y-axis default was making level charts feel skewed, so we moved to a zero-baseline default
- file placement drifted from the intended structure, so we moved SQL into `sample_sql/` and the runner into the chart folder
- benchmark/comparison color logic was too local, so we moved it into shared defaults

### What Worked Well

A few parts of this process worked especially well:

- starting from the chart spec and question coverage docs gave the implementation a clear target
- using real Gold-layer queries made the review meaningful right away
- requiring reviewable PNG outputs made visual QA fast
- iterating on the shared renderer instead of patching only the test script created reusable improvements
- once we centralized palette defaults, the design system got easier to manage

## A Good Workflow for an Agent

Across bar and line charts, this looks like a good reusable workflow for an agent:

1. Read the chart spec and question coverage doc first.
2. Update the shared `prep_<chart>.R` and `render_<chart>.R` files before touching the sample harness.
3. Build one real DuckDB-backed query per canonical business question.
4. Structure the sample runner so each output has:
    - a query block
    - a prep block
    - a render block
    - an export path
5. Save outputs to a stable `sample_output/` folder for review.
6. Run the script end to end after each meaningful change.
7. Use the rendered PNGs to drive iteration on:
    - correctness
    - metric scaling
    - titles/subtitles/captions
    - spacing/labels/legend placement
8. When a styling decision starts repeating, move it into `visual_library/shared/` instead of solving it chart by chart.

That pattern seems to work because it keeps the work moving from:
spec -> shared functions -> real query outputs -> rendered PNGs -> visual QA -> shared standardization

## What Still Needs Care

Even with a good workflow, a few things still need deliberate attention:

- subtle visual changes can be hard to judge without rerendering, even when the code changed correctly
- folder conventions need to stay explicit so helper files do not drift into the wrong place
- defaults that are good for one chart variant may be less good for another, like zero-baseline behavior on indexed or narrow-range line charts
- chart-specific fixes should be watched carefully so they do not become one-off logic that really belongs in shared standards
- palette changes are easy to overfit; some should be captured as future improvement notes rather than solved immediately
