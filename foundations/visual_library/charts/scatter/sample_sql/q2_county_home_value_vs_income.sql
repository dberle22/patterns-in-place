-- Q2: Which counties have unusually high home values relative to incomes?
--
-- Parameter decisions (edit in `params` CTE below):
-- 1) snapshot_year: single-year cross-section for county comparison
-- 2) top_ratio_quantile: percentile cutoff used to flag outliers
-- 3) target_geo_id + target_geo_level: optional row highlight target
--
-- To update for another geography level, replace county sources and xwalks accordingly.

WITH params AS (
  SELECT
    2023::INTEGER AS snapshot_year,
    0.95::DOUBLE AS top_ratio_quantile,
    'county'::VARCHAR AS target_geo_level,
    '37129'::VARCHAR AS target_geo_id
),
county_income AS (
  SELECT geo_id, geo_name, year, median_hh_income
  FROM metro_deep_dive.gold.affordability_wide
  WHERE geo_level = 'county'
),
county_housing AS (
  SELECT geo_id, geo_name, year, median_home_value, hu_total
  FROM metro_deep_dive.gold.affordability_wide
  WHERE geo_level = 'county'
),
county_meta AS (
  SELECT
    cs.county_geoid AS geo_id,
    sr.census_division,
    ROW_NUMBER() OVER (PARTITION BY cs.county_geoid ORDER BY cs.state_fip) AS rn
  FROM metro_deep_dive.silver.xwalk_county_state cs
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region sr
    ON cs.state_fip = sr.state_fips
),
county_meta_dedup AS (
  SELECT geo_id, census_division
  FROM county_meta
  WHERE rn = 1
),
base AS (
  SELECT
    'county'::VARCHAR AS geo_level,
    ci.geo_id,
    ci.geo_name,
    '2023_snapshot'::VARCHAR AS time_window,
    ci.median_hh_income::DOUBLE AS x_value,
    ch.median_home_value::DOUBLE AS y_value,
    'Median Household Income (2023, $)'::VARCHAR AS x_label,
    'Median Home Value (2023, $)'::VARCHAR AS y_label,
    'median_hh_income'::VARCHAR AS x_metric_id,
    'median_home_value'::VARCHAR AS y_metric_id,
    cm.census_division AS "group",
    ch.hu_total::DOUBLE AS size_value,
    (ch.median_home_value / NULLIF(ci.median_hh_income, 0)) AS value_income_ratio,
    CASE
      WHEN (SELECT target_geo_level FROM params) = 'county'
       AND ci.geo_id = (SELECT target_geo_id FROM params)
      THEN TRUE ELSE FALSE
    END AS target_flag
  FROM county_income ci
  JOIN county_housing ch
    ON ci.geo_id = ch.geo_id
   AND ci.year = ch.year
  LEFT JOIN county_meta_dedup cm
    ON ci.geo_id = cm.geo_id
  WHERE ci.year = (SELECT snapshot_year FROM params)
    AND ci.median_hh_income IS NOT NULL
    AND ch.median_home_value IS NOT NULL
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
    WHEN cume_dist() OVER (ORDER BY value_income_ratio) >= (SELECT top_ratio_quantile FROM params)
      THEN TRUE
    ELSE target_flag
  END AS label_flag,
  'gold.affordability_wide + silver.xwalk_county_state + silver.xwalk_state_region'::VARCHAR AS source,
  '2026-04-14'::VARCHAR AS vintage,
  CASE
    WHEN cume_dist() OVER (ORDER BY value_income_ratio) >= (SELECT top_ratio_quantile FROM params)
      THEN 'Top ratio outlier by median_home_value / median_hh_income'
    ELSE NULL
  END AS note
FROM base;
