-- Read the reusable benchmarkable metric surface for one target CBSA.
-- Use benchmark_engine.py to calculate comparison summaries on demand from
-- this metric layer plus the materialized comparison-set tables.

SELECT
  frame_id,
  theme_group,
  metric_id,
  metric_label,
  metric_family,
  metric_type,
  unit,
  year,
  value_direction,
  preferred_summary_stat,
  value AS target_value,
  source_name,
  vintage_note
FROM mart_benchmarking.benchmark_cbsa_metrics
WHERE geo_level = 'cbsa'
  AND geo_id = '__CBSA_CODE__'
ORDER BY
  frame_id,
  theme_group,
  metric_id;
