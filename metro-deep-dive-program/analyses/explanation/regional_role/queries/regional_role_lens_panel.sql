-- One comparable metric panel across the four default lenses.
WITH target_metric AS (
  SELECT geo_id AS target_cbsa_code, metric_id, metric_label, unit, year, value AS target_value
  FROM mart_benchmarking.benchmark_cbsa_metrics
  WHERE geo_id = '__CBSA_CODE__' AND metric_id = '__METRIC_ID__'
  QUALIFY ROW_NUMBER() OVER (ORDER BY year DESC NULLS LAST) = 1
),
selected_members AS (
  SELECT target_cbsa_code, lens_id, parameter_value, member_cbsa_code
  FROM mart_geography.region_lens_membership
  WHERE target_cbsa_code = '__CBSA_CODE__'
    AND (lens_id <> 'cbsa_centroid_250mi' OR parameter_value = '250')
),
member_values AS (
  SELECT members.lens_id, members.parameter_value, members.member_cbsa_code,
         metrics.value
  FROM selected_members AS members
  INNER JOIN target_metric ON members.target_cbsa_code = target_metric.target_cbsa_code
  LEFT JOIN mart_benchmarking.benchmark_cbsa_metrics AS metrics
    ON metrics.geo_id = members.member_cbsa_code
   AND metrics.metric_id = target_metric.metric_id
   AND metrics.year IS NOT DISTINCT FROM target_metric.year
)
SELECT values_by_lens.lens_id, values_by_lens.parameter_value,
       metric.metric_id, metric.metric_label, metric.unit, metric.year,
       metric.target_value,
       COUNT(*) AS member_count,
       COUNT(values_by_lens.value) AS metric_coverage_count,
       AVG(values_by_lens.value) AS member_mean,
       MEDIAN(values_by_lens.value) AS member_median,
       QUANTILE_CONT(values_by_lens.value, 0.25) AS member_p25,
       QUANTILE_CONT(values_by_lens.value, 0.75) AS member_p75
FROM member_values AS values_by_lens
CROSS JOIN target_metric AS metric
GROUP BY 1,2,3,4,5,6,7
ORDER BY lens_id, TRY_CAST(parameter_value AS INTEGER);
