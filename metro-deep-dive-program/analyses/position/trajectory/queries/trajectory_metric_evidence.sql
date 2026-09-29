-- Stored selected-market metric evidence across frames and compatible windows.

SELECT
  method_version,
  cbsa_code,
  cbsa_name,
  frame_id,
  topic_id,
  metric_id,
  metric_label,
  source_table,
  source_column,
  transform,
  polarity,
  window_name,
  window_years,
  start_year,
  end_year,
  observation_count,
  trend_estimator,
  start_raw_value,
  end_raw_value,
  endpoint_change_raw,
  start_percentile,
  end_percentile,
  percentile_point_change,
  trend_slope_transformed,
  polarity_aligned_slope,
  absolute_direction,
  coverage_status,
  momentum_percentile,
  relative_momentum_score,
  metric_salience_percentile,
  signal_tier
FROM mart_intelligence.intelligence_trajectory_metric
WHERE cbsa_code = '__CBSA_CODE__'
ORDER BY method_version, frame_id, window_name, metric_id, end_year;
