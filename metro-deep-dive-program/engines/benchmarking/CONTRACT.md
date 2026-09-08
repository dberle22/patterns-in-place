# Contract

This contract describes the target reusable surface for the Benchmarking
engine. It is intentionally narrow enough for step `4` of the build sequence,
but broad enough that `division` and `peer_set` consumers can adopt it without
breaking the signature later.

## Source

- DuckDB schema: `mart_benchmarking` proposed
- geography dimension: `gold.dim_geo`
- future peer membership source: Intelligence Framework promoted peer outputs

## Current Proposed Tables

| Table | Grain | Current role |
|---|---|---|
| `benchmark_metric_catalog` | `1 row per metric_id` | Metric metadata and benchmark interpretation rules |
| `benchmark_cbsa_metrics` | `1 row per geography + metric + year` | First reusable long metric surface feeding benchmark summaries |
| `benchmark_sets` | `1 row per comparison_set_id` | Reusable benchmark-set definitions |
| `benchmark_set_members` | `1 row per comparison_set_id + member geography` | Membership of national, region, division, state, and peer-set comparison sets |

## Primary Keys

| Table | Primary key |
|---|---|
| `benchmark_metric_catalog` | `metric_id` |
| `benchmark_cbsa_metrics` | `geo_level`, `geo_id`, `metric_id`, `year` |
| `benchmark_sets` | `comparison_set_id` |
| `benchmark_set_members` | `comparison_set_id`, `member_geo_level`, `member_geo_id` |

## Shared Join Keys

- `target_geo_level`
- `target_geo_id`
- `member_geo_level`
- `member_geo_id`
- `comparison_set_id`
- `metric_id`
- `year`

## 1. Supported comparison sets

Build in this order:

1. `national`
2. `region`
3. `division`
4. `state_primary`
5. `state_member`
6. `peer_set`

Hold for later:

- `nearby_metros`
- `same_cluster`
- tract, place, and ZCTA comparison sets

## 2. Required input surfaces

### Metric surface

Expected minimal columns:

- `metric_id`
- `metric_label`
- `geo_level`
- `geo_id`
- `year`
- `value`

Optional but preferred:

- `value_direction`
- `source_name`
- `vintage_note`

Expected metric types:

- `level`
- `share`
- `rate`
- `index`
- `change`
- `rank`
- `percentile`

Expected metric families:

- `population`
- `housing`
- `income_wages`
- `industry`
- `labor`
- `mobility`
- `health_environment`
- `framework_scores`
- `market_structure`

### Comparison membership surface

Expected minimal columns:

- `target_geo_level`
- `target_geo_id`
- `comparison_set_id`
- `comparison_set_type`
- `member_geo_level`
- `member_geo_id`

Optional but preferred:

- `member_rank`
- `membership_source`

## 3. Core documented fields

### 1. Metric catalog surface

Use these for stable interpretation across analyses:

- `metric_id`
- `metric_label`
- `metric_family`
- `metric_type`
- `unit`
- `value_direction`
- `preferred_summary_stat`
- `source_schema`
- `source_table`
- `source_column`

### 2. CBSA metric surface

Use these as the first reusable benchmarkable metric layer:

- `geo_level`
- `geo_id`
- `geo_name`
- `frame_id`
- `theme_group`
- `metric_id`
- `metric_family`
- `metric_type`
- `unit`
- `value_direction`
- `preferred_summary_stat`
- `metric_label`
- `value`
- `year`
- `source_name`
- `vintage_note`

### 3. Comparison-set definition surface

Use these to understand what each benchmark is benchmarking against:

- `comparison_set_id`
- `comparison_set_type`
- `target_geo_level`
- `target_geo_id`
- `comparison_label`
- `comparison_description`
- `membership_source`

### 4. Comparison-set membership surface

Use these to inspect or reuse set membership directly:

- `comparison_set_id`
- `comparison_set_type`
- `target_geo_level`
- `target_geo_id`
- `member_geo_level`
- `member_geo_id`
- `member_geo_name`
- `member_rank`
- `member_role`
- `membership_source`

### 5. On-demand benchmark result surface

The callable benchmark result surface should return one row per:

- `target_geo_level`
- `target_geo_id`
- `metric_id`
- `year`
- `comparison_set_id`

Required output columns:

- `target_geo_level`
- `target_geo_id`
- `target_geo_name`
- `metric_id`
- `metric_label`
- `year`
- `comparison_set_id`
- `comparison_set_type`
- `comparison_n`
- `target_value`
- `comparison_mean`
- `comparison_median`
- `comparison_min`
- `comparison_max`
- `percentile_rank`
- `rank_asc`
- `rank_desc`
- `delta_from_mean`
- `delta_from_median`

Preferred when straightforward:

- `comparison_stddev`
- `pct_diff_from_mean`
- `pct_diff_from_median`
- `z_score`
- `source_name`
- `vintage_note`
- `membership_source`

## 4. Rank and percentile behavior

- Percentiles should be explicit about denominator through `comparison_n`
- Percentiles should be computed within the active comparison set only
- The engine should not silently mix comparison sets in one result row
- `rank_asc` and `rank_desc` should both be available so downstream consumers
  do not have to infer metric direction from ranking math
- Metric direction should be carried as metadata when needed, not hard-coded
  into the ranking function

## 5. Assumptions and caveats

- `gold.dim_geo` is the canonical geography dimension for CBSA-to-division and
  CBSA-to-state lookup
- `state_primary` is defined as the state containing the most county rows in
  the target CBSA footprint, with ties broken by ascending `state_fips`
- `state_member` creates one comparison set per state touched by the target
  CBSA footprint
- the first benchmark universe should be metro CBSA rows, not all CBSA rows
- Intelligence Framework peer outputs are the canonical metro peer source
- the Benchmarking engine compares already-computed metrics; it does not own
  metric creation
- small peer sets are analytically useful but statistically limited, so
  denominator context must stay visible
- mixed-vintage comparisons should remain visible via provenance fields rather
  than hidden upstream
- `peer_set` belongs in the same schema, but can arrive after the geographic
  comparison sets land
- the current design keeps detailed member values and benchmark summaries
  on-demand in Python rather than materializing the fully exploded output table
