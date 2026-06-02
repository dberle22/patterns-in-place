# Hexbin Decisions

## Decision H-001: Default density mode
- Question: Which density mode should be the default in the shared implementation?
- Answer: Default to hexbin when the `hexbin` package is available and fall back to `geom_bin_2d()` otherwise.
- Status: Decided
- Date: 2026-04-14

## Decision H-002: Review sample target CBSA
- Question: Which metro should anchor the chart-local tradeoff-shape sample?
- Answer: Use `35620` (`New York-Newark-Jersey City, NY-NJ`) because the ZCTA count is large enough to produce a meaningful density shape for review.
- Status: Decided
- Date: 2026-04-15

## Decision H-003: Outlier handling in review samples
- Question: How should national sample outputs handle extreme tails?
- Answer: Use light percentile trimming in prep for the national review outputs so the dense core remains readable, and disclose the trim directly in chart subtitles.
- Status: Decided
- Date: 2026-04-15

## Decision H-004: Final approval state
- Question: What should count as the approved close-out state for the first hexbin implementation?
- Answer: Close the chart type with the true `Hexbin` geometry render set, the five canonical DuckDB-backed question outputs, and the current shared prep/render defaults.
- Status: Approved
- Date: 2026-04-15
