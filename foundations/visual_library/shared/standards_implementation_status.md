# Shared Standards Implementation Status

This document tracks which rules from [visual_style_guide_and_standards.md](../visual_style_guide_and_standards.md) are already codified in shared infrastructure and which rules still need downstream implementation in chart renderers, prep logic, or both.

Source of truth:
- Canonical standard: [visual_style_guide_and_standards.md](../visual_style_guide_and_standards.md)
- Shared primitives: [standards.R](./standards.R)
- Shared chart helpers: [chart_utils.R](./chart_utils.R)

## How to use this document

When adding or reviewing a chart:
- Start with the shared helpers first.
- Only add chart-specific styling when the standard cannot be expressed centrally.
- If a style-guide rule is not yet encoded in shared code, mark whether it belongs in render logic, prep logic, or both.

Status vocabulary:
- `Shared`: already codified in `standards.R` or `chart_utils.R`
- `Renderer`: still needs adoption or implementation in chart render functions
- `Prep`: still needs adoption or implementation in prep functions
- `Both`: requires work in both prep and renderer layers
- `Subjective`: intentionally left as guided judgment rather than strict code

## Codified In Shared Infrastructure

### Theme and layout
- `Shared`: one master chart theme via `visual_theme()`
- `Shared`: one map variant via `visual_map_theme()`
- `Shared`: restrained non-data ink, quiet axes, minimal borders, moderate plot margins
- `Shared`: cool light neutral background with white override path through config
- `Shared`: subtle gridline defaults, with chart-configurable `grid` behavior
- `Shared`: default legend position config hook
- `Shared`: notebook vs presentation mode defaults through `visual_output_mode()`, `visual_mode_defaults()`, and `resolve_chart_config()`

### Typography
- `Shared`: `Inter` as the default primary font family
- `Shared`: title, subtitle, caption, axis, legend, and strip hierarchy in the base theme
- `Shared`: captions styled smaller and quieter than subtitles

### Color system
- `Shared`: neutral palette for text, axes, gridlines, outlines, background series, and missing fills
- `Shared`: sequential default family set to `viridis`
- `Shared`: semantic highlight palette with selection, opportunity, strength, and risk variants
- `Shared`: diverging palette with better / midpoint / worse semantics
- `Shared`: context-layer palette scaffold for roads, water, and boundaries
- `Shared`: config slots for binned palette, missing fill, neutral comparison fill, and diverging fills

### Caption and note grammar
- `Shared`: standardized source / vintage / note / method / footer caption assembly via `build_chart_notes()`
- `Shared`: metadata extraction from data frames via `extract_chart_metadata()`
- `Shared`: config-driven caption construction via `chart_caption_from_config()`
- `Shared`: `apply_plot_labels()` now uses the shared note grammar by default

### Benchmark and annotation grammar
- `Shared`: canonical benchmark line defaults through `benchmark_style_defaults()`
- `Shared`: benchmark/reference-line helper via `benchmark_layer()`
- `Shared`: benchmark label text helper via `benchmark_label_text()`
- `Shared`: label application helper via `apply_benchmark_layer()`
- `Shared`: direct-label and boxed-label helper via `label_layer()`
- `Shared`: target/top-item label row selection helper via `pick_label_rows()`
- `Shared`: generic annotation callout helper via `annotation_note_label()`

### Number formatting
- `Shared`: percent, dollar, compact number, integer, rank, and year-range formatting helpers
- `Shared`: unified formatter dispatch through `value_label_formatter()` and `format_value_vector()`

### Shared config structure
- `Shared`: chart defaults now carry output mode, font, background, benchmark defaults, label defaults, palette hooks, and caption hooks
- `Shared`: backward-compatible config merge path through `chart_default_config()`, `merge_chart_config()`, and `resolve_chart_config()`

## Still Needs Downstream Renderer Work

These rules are now possible to implement consistently, but most chart renderers have not yet been refactored to use the shared helpers everywhere.

### Theme adoption
- `Renderer`: switch renderers that still call `visual_theme()` directly to pass full resolved config when mode/background/grid/legend differences matter
- `Renderer`: use `resolve_chart_theme()` where chart families need config-aware theme resolution

### Benchmark grammar adoption
- `Renderer`: replace ad hoc dashed lines with `benchmark_layer()` and `apply_benchmark_layer()`
- `Renderer`: label medians, thresholds, and zero lines in presentation mode by default
- `Renderer`: make reference-line language consistent across scatter, bar, line, and specialty charts

### Label and annotation adoption
- `Renderer`: replace custom `geom_text()` or `geom_label_repel()` blocks with `label_layer()` where feasible
- `Renderer`: use boxed labels selectively for map-family presentation outputs
- `Renderer`: standardize top-N and target labeling through `pick_label_rows()`

### Number formatting adoption
- `Renderer`: replace local formatter logic with `value_label_formatter()` or `format_value_vector()`
- `Renderer`: keep percent / dollar / compact number precision consistent within each chart

### Color semantics adoption
- `Renderer`: use semantic highlight meaning rather than one-off hardcoded highlight colors
- `Renderer`: ensure background peers remain neutral while target items carry emphasis
- `Renderer`: adopt missing-fill defaults and neutral comparison fills consistently

### Legend behavior
- `Renderer`: implement practical bottom-right vs right-side legend placement decisions by chart family
- `Renderer`: clean up legend titles and ordering to match the style guide
- `Renderer`: drop missing categories from legends where not analytically meaningful

## Still Needs Downstream Prep Work

These rules depend on the input data carrying the right metadata or analytical flags.

### Subtitle and caption inputs
- `Prep`: create clean subtitle-ready fields for timeframe, geography scope, metric definition, benchmark logic, and highlight logic
- `Prep`: propagate `source`, `vintage`, and any method notes consistently into prepared frames

### Highlight and label logic
- `Prep`: compute `highlight_flag`, `label_flag`, and top-N selection fields consistently
- `Prep`: mark target vs peer vs benchmark groups in a reusable way across chart families

### Benchmark inputs
- `Prep`: provide benchmark columns or benchmark metadata where chart interpretation depends on a threshold or median
- `Prep`: standardize benchmark labels such as regional median, zero growth, or threshold names

### Formatting metadata
- `Prep`: carry metric display type metadata where possible so charts can pick percent / currency / compact number rules without custom branching
- `Prep`: standardize period labels and year-range representations before render time

## Needs Both Prep And Renderer Work

### Analytical framing
- `Both`: titles should lead with the analytical question, but this still depends on prep metadata and renderer defaults
- `Both`: subtitles should explain timeframe, scope, encoding, and benchmark logic without restating the title

### Comparison hierarchy
- `Both`: target vs peers, top vs rest, and local vs benchmark framing need both prep flags and renderer emphasis
- `Both`: semantic highlight behavior depends on both analytical classification and visual mapping

### Accessibility and density control
- `Both`: reduce labels before shrinking legibility when charts get dense
- `Both`: reinforce meaning with outline, label, or linetype instead of relying only on color

### Map-specific behavior
- `Both`: boundary hierarchy for selected target, study area, internal units, and context overlays
- `Both`: boxed map labels only when they add analytical value
- `Both`: binned vs continuous fill decisions based on interpretability, not just data type

### Chart-family defaults
- `Both`: ranked bars should default to descending sort plus clean end labels
- `Both`: scatters should support target/top/outlier labels plus benchmark framing
- `Both`: grouped comparisons need stable subgroup ordering and consistent legend language
- `Both`: heatmaps and matrix charts need readable scale and label decisions

## Intentionally Not Fully Codified In Shared Code

These are real standards, but they are too contextual to encode as rigid defaults without causing false precision.

- `Subjective`: exact title wording and analytical headline quality
- `Subjective`: when a subtitle is explanatory enough vs too verbose
- `Subjective`: when richer presentation annotation materially improves the read
- `Subjective`: when boxed map labels truly add value rather than clutter
- `Subjective`: when a non-viridis palette is analytically justified

## Suggested Next Steps

High-value downstream follow-up:
1. Refactor `render_scatter.R`, `render_bar.R`, and `render_line.R` to adopt `resolve_chart_config()`, `chart_caption_from_config()`, `benchmark_layer()`, and `label_layer()`.
2. Add prep conventions for `highlight_flag`, `label_flag`, benchmark metadata, and metric display type.
3. Create a small renderer checklist so each chart family can be marked as “shared-standard compliant”.
