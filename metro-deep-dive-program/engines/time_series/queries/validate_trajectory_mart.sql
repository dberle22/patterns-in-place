-- Run after the engine build. Every query should return zero rows except the
-- final coverage summary, which is a review surface rather than a failure.

SELECT method_version, cbsa_code, metric_id, year, COUNT(*) AS row_count
FROM mart_intelligence.intelligence_trajectory_series
GROUP BY 1, 2, 3, 4
HAVING COUNT(*) > 1;

SELECT method_version, cbsa_code, metric_id, window_name, end_year, COUNT(*) AS row_count
FROM mart_intelligence.intelligence_trajectory_metric
GROUP BY 1, 2, 3, 4, 5
HAVING COUNT(*) > 1;

SELECT method_version, cbsa_code, frame_id, window_name, end_year, COUNT(*) AS row_count
FROM mart_intelligence.intelligence_trajectory_frame
GROUP BY 1, 2, 3, 4, 5
HAVING COUNT(*) > 1;

SELECT method_version, cbsa_code, frame_id, method_window_pair, end_year, COUNT(*) AS row_count
FROM mart_intelligence.intelligence_trajectory_turn_signals
GROUP BY 1, 2, 3, 4, 5
HAVING COUNT(*) > 1;

SELECT frame_id, window_name, coverage_status, COUNT(*) AS cbsa_count
FROM mart_intelligence.intelligence_trajectory_frame
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
