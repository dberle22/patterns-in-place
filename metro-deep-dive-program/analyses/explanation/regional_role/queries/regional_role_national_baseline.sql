-- National metropolitan benchmark at the target metric's latest available year.
WITH target_metric AS (
  SELECT geo_id AS target_cbsa_code, geo_name AS target_cbsa_name,
         metric_id, metric_label, unit, year, value AS target_value
  FROM mart_benchmarking.benchmark_cbsa_metrics
  WHERE geo_id = '__CBSA_CODE__' AND metric_id = '__METRIC_ID__'
  QUALIFY ROW_NUMBER() OVER (ORDER BY year DESC NULLS LAST) = 1
),
national_members AS (
  SELECT members.member_geo_id
  FROM mart_benchmarking.benchmark_sets AS sets
  INNER JOIN mart_benchmarking.benchmark_set_members AS members
    ON sets.comparison_set_id = members.comparison_set_id
  INNER JOIN target_metric ON sets.target_geo_id = target_metric.target_cbsa_code
  WHERE sets.comparison_set_type = 'national'
)
SELECT target.target_cbsa_code, target.target_cbsa_name, target.metric_id,
       target.metric_label, target.unit, target.year, target.target_value,
       COUNT(metrics.value) AS comparison_n,
       AVG(metrics.value) AS comparison_mean,
       MEDIAN(metrics.value) AS comparison_median,
       CASE WHEN COUNT(metrics.value) > 1 THEN
         (COUNT(CASE WHEN metrics.value < target.target_value THEN 1 END)::DOUBLE
          + 0.5 * COUNT(CASE WHEN metrics.value = target.target_value THEN 1 END)::DOUBLE)
         / COUNT(metrics.value)
       END AS target_percentile
FROM target_metric AS target
CROSS JOIN national_members AS national
LEFT JOIN mart_benchmarking.benchmark_cbsa_metrics AS metrics
  ON metrics.geo_id = national.member_geo_id
 AND metrics.metric_id = target.metric_id
 AND metrics.year IS NOT DISTINCT FROM target.year
GROUP BY 1,2,3,4,5,6,7;
