WITH target AS (
  SELECT '48900'::VARCHAR AS geo_id
),
endpoints AS (
  SELECT *
  FROM gold.housing_core_wide
  WHERE geo_level = 'cbsa'
    AND geo_id = (SELECT geo_id FROM target)
    AND year IN (2019, 2024)
    AND struct_total IS NOT NULL
),
wide AS (
  SELECT
    MAX(geo_level) AS geo_level,
    geo_id,
    MAX(geo_name) AS geo_name,
    MAX(CASE WHEN year = 2019 THEN struct_sf_det END) AS sf_det_start,
    MAX(CASE WHEN year = 2024 THEN struct_sf_det END) AS sf_det_end,
    MAX(CASE WHEN year = 2019 THEN struct_small_mf END) AS small_mf_start,
    MAX(CASE WHEN year = 2024 THEN struct_small_mf END) AS small_mf_end,
    MAX(CASE WHEN year = 2019 THEN struct_mid_mf END) AS mid_mf_start,
    MAX(CASE WHEN year = 2024 THEN struct_mid_mf END) AS mid_mf_end,
    MAX(CASE WHEN year = 2019 THEN struct_large_mf END) AS large_mf_start,
    MAX(CASE WHEN year = 2024 THEN struct_large_mf END) AS large_mf_end,
    MAX(CASE WHEN year = 2019 THEN struct_mobile END) AS mobile_start,
    MAX(CASE WHEN year = 2024 THEN struct_mobile END) AS mobile_end,
    MAX(CASE WHEN year = 2019 THEN struct_total END) AS total_start,
    MAX(CASE WHEN year = 2024 THEN struct_total END) AS total_end
  FROM endpoints
  GROUP BY geo_id
),
components(component_id, component_label, sort_order, start_value, end_value) AS (
  SELECT 'sf_detached', 'Detached single-unit', 1, sf_det_start, sf_det_end FROM wide
  UNION ALL SELECT 'small_multifamily', '2-4 unit buildings', 2, small_mf_start, small_mf_end FROM wide
  UNION ALL SELECT 'mid_multifamily', '5-19 unit buildings', 3, mid_mf_start, mid_mf_end FROM wide
  UNION ALL SELECT 'large_multifamily', '20+ unit buildings', 4, large_mf_start, large_mf_end FROM wide
  UNION ALL SELECT 'mobile_other', 'Mobile homes', 5, mobile_start, mobile_end FROM wide
  UNION ALL
  SELECT
    'other_units',
    'Other/attached units',
    6,
    total_start - COALESCE(sf_det_start, 0) - COALESCE(small_mf_start, 0) - COALESCE(mid_mf_start, 0) - COALESCE(large_mf_start, 0) - COALESCE(mobile_start, 0),
    total_end - COALESCE(sf_det_end, 0) - COALESCE(small_mf_end, 0) - COALESCE(mid_mf_end, 0) - COALESCE(large_mf_end, 0) - COALESCE(mobile_end, 0)
  FROM wide
)
SELECT
  'waterfall_housing_stock_components' AS question_id,
  w.geo_level,
  w.geo_id,
  w.geo_name,
  '2019-2024 change' AS time_window,
  'Net housing stock change' AS total_label,
  c.component_id,
  c.component_label,
  c.end_value AS component_value,
  'gold.housing_core_wide' AS source,
  '2026-04-16' AS vintage,
  2019 AS start_period,
  2024 AS end_period,
  c.end_value - c.start_value AS component_delta,
  'housing units' AS unit_label,
  CASE
    WHEN c.component_id = 'sf_detached' THEN 'Single-unit'
    WHEN c.component_id IN ('small_multifamily', 'mid_multifamily', 'large_multifamily') THEN 'Multifamily'
    ELSE 'Other'
  END AS component_group,
  NULL::VARCHAR AS benchmark_label,
  TRUE AS highlight_flag,
  c.sort_order,
  'Other/attached units reconciles structure categories to total structure units.' AS note
FROM wide w
CROSS JOIN components c
WHERE c.start_value IS NOT NULL
  AND c.end_value IS NOT NULL
ORDER BY c.sort_order;
