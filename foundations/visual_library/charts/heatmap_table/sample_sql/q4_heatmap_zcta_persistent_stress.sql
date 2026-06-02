-- Q4: For rent burden, which ZCTAs show persistent stress across years?

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
target_zctas AS (
  SELECT DISTINCT zip_geoid AS geo_id
  FROM silver.xwalk_zcta_cbsa
  WHERE cbsa_geoid = (SELECT target_geo_id FROM target_cbsa)
),
zcta_years AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year,
    a.pct_rent_burden_30plus
  FROM gold.affordability_wide a
  JOIN target_zctas z
    ON a.geo_id = z.geo_id
  WHERE a.geo_level = 'zcta'
    AND a.year BETWEEN 2015 AND 2023
),
display_zctas AS (
  SELECT geo_id
  FROM zcta_years
  GROUP BY geo_id
  HAVING COUNT(pct_rent_burden_30plus) >= 4
  ORDER BY AVG(pct_rent_burden_30plus) DESC NULLS LAST
  LIMIT 18
),
metric_long AS (
  SELECT
    'heatmap_zcta_persistent_stress'::VARCHAR AS question_id,
    geo_level,
    geo_id,
    geo_name,
    '2015-2023 annual rent burden'::VARCHAR AS time_window,
    year::VARCHAR AS period,
    'pct_rent_burden_30plus'::VARCHAR AS metric_id,
    'Rent-burdened renter share'::VARCHAR AS metric_label,
    'Affordability stress'::VARCHAR AS metric_group,
    pct_rent_burden_30plus::DOUBLE AS metric_value,
    'higher_is_better'::VARCHAR AS direction,
    geo_id IN (SELECT geo_id FROM display_zctas) AS display_flag
  FROM zcta_years
)
SELECT
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  period,
  metric_id,
  metric_label,
  metric_value,
  'gold.affordability_wide + silver.xwalk_zcta_cbsa'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  metric_group,
  direction,
  display_flag,
  CASE WHEN metric_value IS NULL THEN NULL ELSE CAST(ROUND(metric_value * 100, 1) AS VARCHAR) || '%' END AS value_label,
  'Higher percentile means greater rent-burden stress within that year; displayed rows are the 18 highest average-stress Wilmington-area ZCTAs with enough observed years.'::VARCHAR AS note
FROM metric_long
ORDER BY display_flag DESC, geo_name, period;
