# Boxplot Decisions

## First Implementation Pass

- Use the same chart API pattern as choropleth and the other validated chart types: `prep_boxplot(data, config)` followed by `render_boxplot(data, config, theme = NULL)`.
- Keep the data contract close to bar and choropleth because boxplots are single-metric geography comparisons with optional grouping and highlighting.
- Default to horizontal boxplots. This preserves long region, county, and CBSA-type labels and aligns with the visual library preference for comparison-first charts.
- Treat `group` as optional. Prep creates `box_group` and falls back to `"All observations"` for one-distribution views.
- Order groups by median by default for grouped comparisons, while allowing `group_order = "input"` or `"alphabetical"`.
- Use standard 1.5 IQR whiskers through `geom_boxplot()` and document display clipping separately when used.
- Put benchmark/reference lines in the renderer using the shared `benchmark_layer()` helper rather than bespoke annotations.
- Keep the first sample set chart-local. No broader shared-standard changes were needed beyond adding the boxplot contract and chart defaults.
