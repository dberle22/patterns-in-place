# Visual Contract Data Dictionary

## Purpose
Provide shared field definitions across chart contracts so each chart is not defined from scratch.

## Core Fields
- `geo_level` (character): Geography granularity (`us`, `region`, `division`, `state`, `cbsa`, `county`, `tract`, `zcta`).
- `geo_id` (character): Stable identifier for the geography.
- `geo_name` (character): Display name for the geography.
- `period` (integer/date): Time key (year now; extendable to date/quarter/month).
- `metric_id` (character): Stable metric identifier.
- `metric_label` (character): Human-readable metric label.
- `metric_value` (numeric): Value for the metric at the specified grain/time.
- `source` (character): Source system/table.
- `vintage` (character): Data release/version stamp.

## Variant and Metadata Fields
- `time_window` (character): Transform window (`level`, `indexed`, `rolling_3yr`, etc.).
- `group` (character): Grouping dimension for color/facet/benchmarks.
- `highlight_flag` (logical): Marks selected geographies.
- `benchmark_value` (numeric): Benchmark series value when encoded as separate field.
- `index_base_period` (integer): Base period for indexed transforms.
- `note` (character): Data caveat or break annotation.

## Paired-Metric Fields (Scatter and similar)
- `x_metric_id`, `x_metric_label`, `x_metric_value`
- `y_metric_id`, `y_metric_label`, `y_metric_value`
- `size_metric_value` (optional)

## Ranking, Scoring, and Matrix Fields
- `rank` (numeric): Rank within a comparison universe for the active period.
- `series` (character): Variant/group series identifier for grouped bars or multi-series comparisons.
- `normalized_value` (numeric): Standardized score, percentile, z-score, or similar comparison-ready value.
- `direction` (character): Metric polarity such as `higher_is_better` or `lower_is_better`.
- `metric_group` (character): Higher-level grouping for KPI families.
- `weight_value` (numeric): Weight used in weighted density/correlation/statistical views.

## Map and Geometry Fields
- `geometry` (sf geometry): Polygon or point geometry for map-based charts.
- `lon`, `lat` (numeric): Explicit coordinates for symbol/point maps.
- `bin` (character): Precomputed legend class for choropleths.
- `x_bin`, `y_bin` (integer/character): Bivariate class inputs for two-metric maps.
- `bivar_class` (character): Combined bivariate legend class such as `1-3`.
- `context_group` (character): Context grouping label used in highlight maps.
- `neighbor_flag` (logical): Whether the row is in the immediate context set around a highlight geography.

## Composition and Decomposition Fields
- `share_value` (numeric): Share within a category or total.
- `total_label` (character): Named total used in a decomposition chart.
- `component_id`, `component_label` (character): Stable and human-readable component identifiers.
- `component_value` (numeric): Additive level value for a decomposition.
- `component_delta` (numeric): Additive change contribution for a decomposition.
- `component_group` (character): Parent bucket for grouped decomposition components.
- `sort_order` (integer): Canonical order for components or categories.

## Demographic Structure Fields
- `age_bin` (character): Standardized age-band label.
- `sex` (character): Demographic split key for pyramids.
- `pop_value` (numeric): Population count for a demographic slice.
- `pop_share` (numeric): Share of the total population for a demographic slice.

## Contract Rules
- Required vs optional status is chart-specific.
- `metric_id` semantics must be consistent across geographies within a comparison.
- `period` type must be consistent within a dataset.
- One contract exists per chart type; variant-specific rules are enforced in prep/validation and chart specs rather than by duplicating the base field dictionary.
