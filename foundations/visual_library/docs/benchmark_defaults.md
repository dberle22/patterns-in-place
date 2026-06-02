# Benchmark Defaults

## Purpose
Define default benchmark comparison sets by geography granularity.

## Decision Log

### BM-001: Metro Area defaults
- Question: What are default benchmarks for Metro Area analyses?
- Answer: Include `Division`, `National`, and `All Other Metro Areas`.
- Status: Decided
- Date: 2026-03-02

### BM-002: State defaults
- Question: What are default benchmarks for State analyses?
- Answer: Default to `National`, `Census Region`, and `Peer States by size/economy` when available.
- Status: Decided
- Date: 2026-04-14

### BM-003: County defaults
- Question: What are default benchmarks for County analyses?
- Answer: Default to `Parent CBSA`, `State`, and `National County Distribution`; include peer counties only when explicitly defined in the analysis.
- Status: Decided
- Date: 2026-04-14

### BM-004: Tract defaults
- Question: What are default benchmarks for Census Tract analyses?
- Answer: Default to `Parent County`, `Parent CBSA`, and tract distribution within the parent geography.
- Status: Decided
- Date: 2026-04-14

### BM-005: ZCTA defaults
- Question: What are default benchmarks for ZCTA analyses?
- Answer: Default to `Parent CBSA`, `Parent County`, and ZCTA distribution within the parent geography.
- Status: Decided
- Date: 2026-04-14

### BM-006: KPI score views
- Question: What benchmarks should normalized score views use?
- Answer: For `strength_strip` and multi-metric `heatmap_table`, normalize against the explicitly stated comparison universe, with `All CBSAs` as the default for CBSA-level scorecards.
- Status: Decided
- Date: 2026-04-14

## Proposed Structure for Implementation
Each benchmark definition should specify:
- `geo_level`
- `benchmark_set_id`
- `included_groups`
- `exclusion_rules`
- `weighting_method` (for example `metro_mean`, `pop_weighted`)
- `notes`
