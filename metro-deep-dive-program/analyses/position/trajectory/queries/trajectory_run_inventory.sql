-- Materialized method/window/frame inventory for valid Trajectory controls.
-- Aggregations describe availability and coverage only; all trajectory fields
-- remain the stored outputs of the Time-Series engine.

WITH frame_inventory AS (
  SELECT
    method_version,
    frame_id,
    window_name,
    end_year,
    COUNT(*) AS frame_row_count,
    COUNT(*) FILTER (WHERE coverage_status = 'eligible') AS eligible_frame_count,
    MIN(start_year) AS start_year,
    MAX(topic_count) AS max_topic_count,
    MAX(metric_count) AS max_metric_count
  FROM mart_intelligence.intelligence_trajectory_frame
  GROUP BY 1, 2, 3, 4
),
metric_inventory AS (
  SELECT
    method_version,
    frame_id,
    window_name,
    end_year,
    COUNT(*) AS metric_row_count,
    COUNT(DISTINCT metric_id) AS distinct_metric_count,
    COUNT(DISTINCT topic_id) AS distinct_topic_count,
    COUNT(*) FILTER (WHERE coverage_status = 'eligible') AS eligible_metric_count
  FROM mart_intelligence.intelligence_trajectory_metric
  GROUP BY 1, 2, 3, 4
),
series_inventory AS (
  SELECT
    method_version,
    frame_id,
    MIN(year) AS available_year_min,
    MAX(year) AS available_year_max,
    COUNT(*) AS series_row_count
  FROM mart_intelligence.intelligence_trajectory_series
  GROUP BY 1, 2
),
turn_inventory AS (
  SELECT
    method_version,
    frame_id,
    end_year,
    COUNT(*) AS turn_row_count,
    COUNT(DISTINCT method_window_pair) AS turn_window_pair_count
  FROM mart_intelligence.intelligence_trajectory_turn_signals
  GROUP BY 1, 2, 3
)
SELECT
  f.method_version,
  f.frame_id,
  f.window_name,
  f.start_year,
  f.end_year,
  f.frame_row_count,
  f.eligible_frame_count,
  f.max_topic_count,
  f.max_metric_count,
  m.metric_row_count,
  m.distinct_metric_count,
  m.distinct_topic_count,
  m.eligible_metric_count,
  s.available_year_min,
  s.available_year_max,
  s.series_row_count,
  t.turn_row_count,
  t.turn_window_pair_count
FROM frame_inventory AS f
LEFT JOIN metric_inventory AS m
  USING (method_version, frame_id, window_name, end_year)
LEFT JOIN series_inventory AS s
  USING (method_version, frame_id)
LEFT JOIN turn_inventory AS t
  USING (method_version, frame_id, end_year)
ORDER BY method_version, frame_id, window_name, end_year;
