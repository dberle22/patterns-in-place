# Correlation Heatmap Decisions

## Decision CH-001: Default correlation method
- Question: Which correlation method should the library use by default?
- Answer: Default to Spearman in documentation and smoke tests because it is more robust for monotonic but non-linear KPI relationships.
- Status: Decided
- Date: 2026-04-14

## Decision CH-002: Sweet Spot comparison proxy
- Question: How should the sample runner answer the Sweet Spot comparison question before a canonical shortlist flag exists in DuckDB?
- Answer: Use a documented derived shortlist of medium-sized metros with relatively strong growth and permitting plus relatively lower rent burden and value-to-income ratios, then facet that against the full CBSA universe.
- Status: Temporary
- Date: 2026-04-15
