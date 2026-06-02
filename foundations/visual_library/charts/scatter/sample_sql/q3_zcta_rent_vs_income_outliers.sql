-- Q3: Which ZCTAs are outliers within a given CBSA on rent vs income?
--
-- Parameter decisions (edit in `params` CTE below):
-- 1) snapshot_year: single-year cross-section
-- 2) target_cbsa_geoid: CBSA filter used for ZCTA subset
-- 3) outlier_z_threshold: absolute z-score threshold for outlier flagging
-- 4) target_geo_id + target_geo_level: optional row highlight target
--
-- To run this for a different CBSA, only update `target_cbsa_geoid`.

WITH params AS (
  SELECT
    2023::INTEGER AS snapshot_year,
    '48900'::VARCHAR AS target_cbsa_geoid,
    2.0::DOUBLE AS outlier_z_threshold,
    'zcta'::VARCHAR AS target_geo_level,
    '28403'::VARCHAR AS target_geo_id
),
zcta_income AS (
  SELECT geo_id, geo_name, year, median_hh_income
  FROM metro_deep_dive.silver.income_kpi
  WHERE geo_level = 'zcta'
),
zcta_housing AS (
  SELECT geo_id, geo_name, year, median_gross_rent, hu_total
  FROM metro_deep_dive.silver.housing_kpi
  WHERE geo_level = 'zcta'
),
zcta_cbsa AS (
  SELECT zip_geoid AS geo_id, cbsa_geoid, rel_weight_hu, zip_pref_state
  FROM metro_deep_dive.silver.xwalk_zcta_cbsa
  WHERE cbsa_geoid = (SELECT target_cbsa_geoid FROM params)
),
base AS (
  SELECT
    'zcta'::VARCHAR AS geo_level,
    zi.geo_id,
    zi.geo_name,
    '2023_snapshot'::VARCHAR AS time_window,
    zi.median_hh_income::DOUBLE AS x_value,
    zh.median_gross_rent::DOUBLE AS y_value,
    'Median Household Income (2023, $)'::VARCHAR AS x_label,
    'Median Gross Rent (2023, $/month)'::VARCHAR AS y_label,
    'median_hh_income'::VARCHAR AS x_metric_id,
    'median_gross_rent'::VARCHAR AS y_metric_id,
    zc.zip_pref_state AS "group",
    COALESCE(zh.hu_total, zc.rel_weight_hu * 1000.0)::DOUBLE AS size_value,
    (zh.median_gross_rent * 12.0 / NULLIF(zi.median_hh_income, 0)) AS rent_income_ratio,
    CASE
      WHEN (SELECT target_geo_level FROM params) = 'zcta'
       AND zi.geo_id = (SELECT target_geo_id FROM params)
      THEN TRUE ELSE FALSE
    END AS target_flag
  FROM zcta_income zi
  JOIN zcta_housing zh
    ON zi.geo_id = zh.geo_id
   AND zi.year = zh.year
  JOIN zcta_cbsa zc
    ON zi.geo_id = zc.geo_id
  WHERE zi.year = (SELECT snapshot_year FROM params)
    AND zi.median_hh_income IS NOT NULL
    AND zh.median_gross_rent IS NOT NULL
)
SELECT
  geo_level,
  geo_id,
  geo_name,
  time_window,
  x_value,
  y_value,
  x_label,
  y_label,
  x_metric_id,
  y_metric_id,
  "group",
  size_value,
  CASE
    WHEN abs((rent_income_ratio - avg(rent_income_ratio) OVER ()) / NULLIF(stddev_samp(rent_income_ratio) OVER (), 0)) >= (SELECT outlier_z_threshold FROM params)
      THEN TRUE
    ELSE target_flag
  END AS label_flag,
  'silver.income_kpi + silver.housing_kpi + silver.xwalk_zcta_cbsa'::VARCHAR AS source,
  '2026-04-14'::VARCHAR AS vintage,
  CASE
    WHEN abs((rent_income_ratio - avg(rent_income_ratio) OVER ()) / NULLIF(stddev_samp(rent_income_ratio) OVER (), 0)) >= (SELECT outlier_z_threshold FROM params)
      THEN 'Outlier by rent/income z-score threshold'
    ELSE NULL
  END AS note
FROM base;
