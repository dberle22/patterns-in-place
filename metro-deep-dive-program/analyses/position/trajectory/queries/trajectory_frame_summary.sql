-- Stored selected-market frame trajectory outputs across its available windows.

SELECT
  method_version,
  cbsa_code,
  cbsa_name,
  frame_id,
  window_name,
  window_years,
  start_year,
  end_year,
  topic_count,
  metric_count,
  coverage_status,
  start_position_percentile,
  end_position_percentile,
  percentile_point_change,
  frame_momentum_score,
  trajectory_salience_percentile,
  position_band,
  movement_direction,
  absolute_direction,
  signal_tier,
  signal_p80,
  signal_p90,
  signal_p95,
  trajectory_label
FROM mart_intelligence.intelligence_trajectory_frame
WHERE cbsa_code = '__CBSA_CODE__'
ORDER BY method_version, frame_id, window_name, end_year;
