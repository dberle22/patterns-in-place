# Waterfall Decisions

## Decision WF-001: Default ordering rule
- Question: How should waterfall components be ordered by default?
- Answer: Use a canonical logical component order rather than absolute magnitude sorting so the narrative remains interpretable across runs.
- Status: Decided
- Date: 2026-04-14

## Decision WF-002: Terminal total bar
- Question: How should the first production waterfall render make the final additive result explicit?
- Answer: `prep_waterfall()` appends a terminal total bar by default after computing the cumulative component path. Samples can override the total label, but the shared behavior keeps level, change, and benchmark waterfalls reviewable without one-off runner logic.
- Status: Decided
- Date: 2026-04-16

## Decision WF-003: Benchmark comparison layout
- Question: How should target-versus-benchmark waterfalls be shown?
- Answer: Use faceted side-by-side waterfalls keyed by `benchmark_label` instead of mixing target and benchmark components in one cumulative path. This preserves additive interpretation while keeping component definitions comparable.
- Status: Decided
- Date: 2026-04-16
