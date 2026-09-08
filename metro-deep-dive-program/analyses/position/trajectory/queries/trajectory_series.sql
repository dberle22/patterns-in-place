-- Stored selected-market annual observations and national-percentile lineage.

SELECT
  method_version,
  cbsa_code,
  cbsa_name,
  frame_id,
  topic_id,
  metric_id,
  metric_label,
  source_schema,
  source_table,
  source_column,
  transform,
  polarity,
  year,
  raw_value,
  transformed_value,
  national_percentile,
  eligibility_status
FROM mart_intelligence.intelligence_trajectory_series
WHERE cbsa_code = '__CBSA_CODE__'
ORDER BY method_version, frame_id, metric_id, year;
