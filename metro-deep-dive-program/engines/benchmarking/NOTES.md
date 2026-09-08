# Notes

Use this file to audit current benchmark logic, comparison datasets, and
regional rollup needs.

## Repo audit — 2026-09-03

### Current benchmark logic already in repo

- `metro-deep-dive-program/analyses/position/profile/queries/profile_percentiles.sql`
  already exposes framework-native national percentile rows for `Act 1`
- `metro-deep-dive-program/analyses/position/peers/queries/peer_benchmark_top5.sql`
  already builds an ad hoc target-plus-peers comparison surface from
  `mart_intelligence.intelligence_cross_frame`
- `metro-deep-dive/metro-area-explorer/industry/data_prep.py` includes
  reusable benchmark table builders for `us` and `division` comparison rows
- `metro-deep-dive/metro-area-explorer/place_intelligence/data_builds/d2/shared.py`
  includes a separate benchmark stack for site-level `cbsa`, `county`,
  `state`, and `national` comparisons plus tract-distribution percentiles

### Strong reuse candidates

- query-first comparison-set logic from the Position analyses
- explicit denominator handling from Place Intelligence percentile logic
- `us` and `division` benchmark-table shaping from Industry D1/D5
- `gold.dim_geo` as the canonical source for division and state membership

### Recommended benchmark universe for first pass

- target level: `cbsa`
- member level: `cbsa`
- include only metro CBSA rows from `gold.dim_geo`
- comparison sets: `national`, `region`, `division`, `state`, `peer_set`

### DuckDB shape recommendation

Materialize a dedicated schema:

- `mart_benchmarking`

Recommended first tables:

- `benchmark_metric_catalog`
- `benchmark_sets`
- `benchmark_set_members`
- `benchmark_cbsa_metrics`

### Current implementation direction

- materialize the reusable metadata, metric, and comparison-set tables
- compute summary benchmark rows on demand in Python
- compute head-to-head member rows on demand in Python
- avoid materializing the full `target x benchmark set x metric x member` table
  unless a later consumer proves it is worth the size cost

### Important differences to preserve

- Place Intelligence benchmarks a ring against tract distributions and selected
  geography rows; that is not the same denominator as metro-to-metro
  benchmarking
- Intelligence Framework percentiles are already modeled upstream; the
  Benchmarking engine should not recompute those unless we are comparing a new
  KPI surface
- peer sets should come from the Intelligence Framework, not from geography

### Open questions to resolve in implementation

- when should percentile output be integer-rounded versus decimal?
- should `peer_set` summaries use mean, median, or both by default?
- do we need a comparison-set registry table immediately, or can we begin with
  query views and promote later?
- multi-state rule now implemented as two methods:
  `state_primary` and `state_member`
