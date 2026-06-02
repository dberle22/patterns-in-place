-- Q1: How does rent burden vary across regions, and where does the target CBSA fall?

WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'cbsa'
    AND pct_rent_burden_30plus IS NOT NULL
),
cbsa_region AS (
  SELECT
    cbsa_code,
    MIN(census_region) AS census_region
  FROM foundation.cbsa_features
  WHERE year = (SELECT year FROM latest_year)
    AND primary_state_abbr NOT IN ('AK', 'HI', 'PR')
  GROUP BY 1
)
SELECT
  'boxplot_rent_burden_by_region'::VARCHAR AS question_id,
  a.geo_level,
  a.geo_id,
  a.geo_name,
  '2024_snapshot'::VARCHAR AS time_window,
  'pct_rent_burden_30plus'::VARCHAR AS metric_id,
  'Rent-burdened renter households (%)'::VARCHAR AS metric_label,
  a.pct_rent_burden_30plus::DOUBLE AS metric_value,
  r.census_region AS "group",
  a.geo_id = '48900' AS highlight_flag,
  a.geo_id = '48900' AS label_flag,
  NULL::DOUBLE AS weight_value,
  NULL::DOUBLE AS benchmark_value,
  'gold.affordability_wide + foundation.cbsa_features'::VARCHAR AS source,
  CAST(a.year AS VARCHAR) AS vintage,
  'Target highlight is Wilmington, NC; regions exclude AK, HI, and PR.'::VARCHAR AS note
FROM gold.affordability_wide a
JOIN cbsa_region r
  ON a.geo_id = r.cbsa_code
WHERE a.geo_level = 'cbsa'
  AND a.year = (SELECT year FROM latest_year)
  AND a.pct_rent_burden_30plus IS NOT NULL;
