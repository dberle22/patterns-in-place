-- Q1: Across a shortlist, which tracts are consistently strong across guardrails?

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year FROM gold.housing_core_wide WHERE geo_level = 'tract'
    UNION ALL
    SELECT MAX(year) AS max_year FROM gold.population_demographics WHERE geo_level = 'tract'
  )
),
target_tracts AS (
  SELECT DISTINCT xt.tract_geoid AS geo_id
  FROM silver.xwalk_tract_county xt
  JOIN silver.xwalk_cbsa_county xc
    ON xt.state_fip = xc.state_fips
   AND xt.county_fip = xc.county_fips
  WHERE xc.cbsa_code = (SELECT target_geo_id FROM target_cbsa)
),
tract_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    a.median_hh_income,
    p.pct_ba_plus,
    a.vacancy_rate,
    a.pct_rent_burden_30plus,
    a.value_to_income
  FROM gold.housing_core_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  JOIN target_tracts t
    ON a.geo_id = t.geo_id
  LEFT JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  WHERE a.geo_level = 'tract'
),
scored AS (
  SELECT
    *,
    (
      PERCENT_RANK() OVER (ORDER BY median_hh_income)
      + PERCENT_RANK() OVER (ORDER BY pct_ba_plus)
      + PERCENT_RANK() OVER (ORDER BY vacancy_rate)
      + PERCENT_RANK() OVER (ORDER BY pct_rent_burden_30plus DESC)
      + PERCENT_RANK() OVER (ORDER BY value_to_income DESC)
    ) / 5.0 AS shortlist_score
  FROM tract_base
),
display_tracts AS (
  SELECT geo_id
  FROM scored
  ORDER BY shortlist_score DESC NULLS LAST, geo_name
  LIMIT 25
),
metric_long AS (
  SELECT 'heatmap_shortlist_scan'::VARCHAR AS question_id, geo_level, geo_id, geo_name, 'latest tract profile'::VARCHAR AS time_window, 1 AS metric_order, 'median_hh_income'::VARCHAR AS metric_id, 'Median household income'::VARCHAR AS metric_label, 'Prosperity'::VARCHAR AS metric_group, median_hh_income::DOUBLE AS metric_value, 'higher_is_better'::VARCHAR AS direction, geo_id IN (SELECT geo_id FROM display_tracts) AS display_flag, shortlist_score
  FROM scored
  UNION ALL
  SELECT 'heatmap_shortlist_scan', geo_level, geo_id, geo_name, 'latest tract profile', 2, 'pct_ba_plus', 'Adults with BA+', 'Talent', pct_ba_plus::DOUBLE, 'higher_is_better', geo_id IN (SELECT geo_id FROM display_tracts), shortlist_score
  FROM scored
  UNION ALL
  SELECT 'heatmap_shortlist_scan', geo_level, geo_id, geo_name, 'latest tract profile', 3, 'vacancy_rate', 'Vacancy rate', 'Housing headroom', vacancy_rate::DOUBLE, 'higher_is_better', geo_id IN (SELECT geo_id FROM display_tracts), shortlist_score
  FROM scored
  UNION ALL
  SELECT 'heatmap_shortlist_scan', geo_level, geo_id, geo_name, 'latest tract profile', 4, 'pct_rent_burden_30plus', 'Rent-burdened renter share', 'Affordability', pct_rent_burden_30plus::DOUBLE, 'lower_is_better', geo_id IN (SELECT geo_id FROM display_tracts), shortlist_score
  FROM scored
  UNION ALL
  SELECT 'heatmap_shortlist_scan', geo_level, geo_id, geo_name, 'latest tract profile', 5, 'value_to_income', 'Home value-to-income', 'Affordability', value_to_income::DOUBLE, 'lower_is_better', geo_id IN (SELECT geo_id FROM display_tracts), shortlist_score
  FROM scored
)
SELECT
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  metric_id,
  metric_label,
  metric_value,
  source,
  vintage,
  metric_group,
  direction,
  display_flag,
  metric_order,
  shortlist_score AS row_order,
  CASE
    WHEN metric_value IS NULL THEN NULL
    WHEN metric_id = 'median_hh_income' THEN '$' || CAST(ROUND(metric_value, 0) AS VARCHAR)
    WHEN metric_id IN ('pct_ba_plus', 'vacancy_rate', 'pct_rent_burden_30plus') THEN CAST(ROUND(metric_value * 100, 1) AS VARCHAR) || '%'
    ELSE CAST(ROUND(metric_value, 1) AS VARCHAR)
  END AS value_label,
  'Percentiles normalize across all Wilmington, NC CBSA tracts; displayed rows are the top 25 by a simple average tract guardrail score.'::VARCHAR AS note
FROM metric_long
CROSS JOIN (
  SELECT
    'gold.housing_core_wide + gold.population_demographics + silver.xwalk_tract_county'::VARCHAR AS source,
    '2026-04-16'::VARCHAR AS vintage
)
ORDER BY display_flag DESC, row_order DESC NULLS LAST, geo_name, metric_order;
