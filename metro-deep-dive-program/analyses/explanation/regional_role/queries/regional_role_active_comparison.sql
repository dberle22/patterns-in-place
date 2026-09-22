-- Active-lens member comparison at the target metric's latest available year.
WITH target_metric AS (
  SELECT geo_id AS target_cbsa_code, metric_id, metric_label, unit, year, value AS target_value
  FROM mart_benchmarking.benchmark_cbsa_metrics
  WHERE geo_id = '__CBSA_CODE__' AND metric_id = '__METRIC_ID__'
  QUALIFY ROW_NUMBER() OVER (ORDER BY year DESC NULLS LAST) = 1
)
SELECT membership.member_cbsa_code, member.geo_name AS member_cbsa_name,
       membership.member_role, membership.distance_miles,
       metric.metric_id, metric.metric_label, metric.unit, metric.year,
       metric.value, target.target_value,
       metric.value - target.target_value AS difference_from_target,
       PERCENT_RANK() OVER (ORDER BY metric.value) AS lens_percentile
FROM mart_geography.region_lens_membership AS membership
INNER JOIN target_metric AS target ON membership.target_cbsa_code = target.target_cbsa_code
INNER JOIN gold.dim_geo AS member
  ON member.geo_level = 'cbsa' AND member.geo_id = membership.member_cbsa_code
LEFT JOIN mart_benchmarking.benchmark_cbsa_metrics AS metric
  ON metric.geo_id = membership.member_cbsa_code
 AND metric.metric_id = target.metric_id
 AND metric.year IS NOT DISTINCT FROM target.year
WHERE membership.target_cbsa_code = '__CBSA_CODE__'
  AND membership.lens_id = '__LENS_ID__'
  AND membership.parameter_value = '__PARAMETER_VALUE__'
ORDER BY membership.member_role DESC, metric.value DESC NULLS LAST, member.geo_name;
