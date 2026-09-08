# Benchmarking Engine

Purpose:

- standardize comparison and benchmarking across markets, peers, regions, and national baselines
- provide one DuckDB schema for reusable benchmark tables and query surfaces

Current build trigger:

- opened by `docs/build_sequence.md` step `4`
- first immediate consumer is `analyses/position/profile/` for the Act 1
  fingerprint percentile table
- next named consumers are the Act 2 benchmark comparison layer and regional
  role work

Expected responsibilities:

- define reusable comparison logic
- identify where current benchmark logic already exists
- align outputs for Position, Explanation, and Thematic analyses

Working rule:

- start query-first and DuckDB-first
- build the narrowest comparison surface that satisfies the current consumer
- widen only when the next named consumer needs the same contract unchanged

## Proposed DuckDB Home

Use a dedicated schema:

- `mart_benchmarking`

This should be a reusable serving schema, not a one-off notebook artifact.

The basic idea is:

- upstream engines and analyses produce metric surfaces
- `mart_benchmarking` materializes metric metadata, benchmarkable metric rows,
  and comparison-set membership
- downstream analyses and issue builders call the Python benchmark helper to
  calculate summary results on demand

## What This Engine Should Own

- metric metadata needed for benchmark interpretation
- reusable comparison-set membership tables for `national`, `region`,
  `division`, `state`, and `peer_set`
- a benchmarkable long metric surface at CBSA grain
- a shared Python package that computes summary rows and member rows on demand

## What This Engine Should Not Own

- Intelligence Framework similarity generation
- geography hierarchy design beyond what `gold.dim_geo` already resolves
- raw KPI creation
- theme-specific metric derivation
- issue-layer formatting decisions

See:

- `PROPOSAL.md` for the recommended build shape
- `NOTES.md` for current repo audit and reuse candidates
- `CONTRACT.md` for the target engine contract
- `build_benchmark_schema.py` for the first-pass DuckDB build runner
- `queries/build_benchmark_schema.sql` for the build order reference
- `foundations/benchmarking_py/` for the reusable package
