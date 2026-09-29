-- All-market stored compatible-window turn results for context and target review.

SELECT
  method_version,
  cbsa_code,
  cbsa_name,
  frame_id,
  method_window_pair,
  end_year,
  frame_momentum_score_short,
  frame_momentum_score_medium,
  trajectory_salience_percentile_short,
  trajectory_salience_percentile_medium,
  shared_metric_count,
  supporting_metric_ids,
  signal_gate_percentile,
  turn_status
FROM mart_intelligence.intelligence_trajectory_turn_signals
ORDER BY method_version, frame_id, method_window_pair, end_year, cbsa_code;
