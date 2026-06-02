-- Q4: How does correlation structure differ between a derived Sweet Spot shortlist and all CBSAs?
--
-- Because the warehouse does not currently expose a canonical Sweet Spot flag,
-- this sample derives a transparent shortlist of medium-sized metros using
-- 2024 growth, supply, and affordability signals.

WITH latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year
    FROM metro_deep_dive.gold.affordability_wide
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM metro_deep_dive.gold.population_demographics
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM metro_deep_dive.foundation.cbsa_features
  )
),
cbsa_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    a.pop_total,
    p.pop_growth_5yr,
    a.median_hh_income,
    a.pct_rent_burden_30plus,
    a.value_to_income,
    a.permits_per_1000_population,
    p.pct_ba_plus,
    f.cbsa_type,
    f.census_region
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  LEFT JOIN metro_deep_dive.gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN metro_deep_dive.foundation.cbsa_features f
    ON a.geo_id = f.cbsa_code
   AND f.year = 2019
  WHERE a.geo_level = 'cbsa'
),
medium_metros AS (
  SELECT *
  FROM cbsa_base
  WHERE cbsa_type = 'Metro Area'
    AND pop_total BETWEEN 250000 AND 1500000
    AND pop_growth_5yr IS NOT NULL
    AND pct_rent_burden_30plus IS NOT NULL
    AND value_to_income IS NOT NULL
    AND permits_per_1000_population IS NOT NULL
),
ranked_medium_metros AS (
  SELECT
    *,
    PERCENT_RANK() OVER (ORDER BY pop_growth_5yr) AS growth_pctl,
    PERCENT_RANK() OVER (ORDER BY permits_per_1000_population) AS supply_pctl,
    PERCENT_RANK() OVER (ORDER BY pct_rent_burden_30plus) AS burden_pctl,
    PERCENT_RANK() OVER (ORDER BY value_to_income) AS value_ratio_pctl
  FROM medium_metros
),
derived_sweet_spot AS (
  SELECT
    geo_id,
    geo_name
  FROM ranked_medium_metros
  WHERE growth_pctl >= 0.65
    AND supply_pctl >= 0.55
    AND burden_pctl <= 0.45
    AND value_ratio_pctl <= 0.45
  ORDER BY
    (growth_pctl + supply_pctl - burden_pctl - value_ratio_pctl) DESC,
    geo_name
  LIMIT 12
),
comparison_rows AS (
  SELECT
    'All CBSAs'::VARCHAR AS "group",
    b.geo_level,
    b.geo_id,
    b.geo_name,
    b.year,
    b.pop_growth_5yr,
    b.median_hh_income,
    b.pct_ba_plus,
    b.pct_rent_burden_30plus,
    b.value_to_income,
    b.permits_per_1000_population
  FROM cbsa_base b

  UNION ALL

  SELECT
    'Derived Sweet Spot shortlist'::VARCHAR AS "group",
    b.geo_level,
    b.geo_id,
    b.geo_name,
    b.year,
    b.pop_growth_5yr,
    b.median_hh_income,
    b.pct_ba_plus,
    b.pct_rent_burden_30plus,
    b.value_to_income,
    b.permits_per_1000_population
  FROM cbsa_base b
  JOIN derived_sweet_spot s
    ON b.geo_id = s.geo_id
),
metric_long AS (
  SELECT 'corr_sweet_spot_compare'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2024 CBSA comparison'::VARCHAR AS time_window, 'pop_growth_5yr'::VARCHAR AS metric_id, 'Population growth (5yr)'::VARCHAR AS metric_label, pop_growth_5yr::DOUBLE AS metric_value, "group"
  FROM comparison_rows
  UNION ALL
  SELECT 'corr_sweet_spot_compare', geo_level, geo_id, geo_name, '2024 CBSA comparison', 'median_hh_income', 'Median household income', median_hh_income::DOUBLE, "group"
  FROM comparison_rows
  UNION ALL
  SELECT 'corr_sweet_spot_compare', geo_level, geo_id, geo_name, '2024 CBSA comparison', 'pct_ba_plus', 'Adults with BA+', pct_ba_plus::DOUBLE, "group"
  FROM comparison_rows
  UNION ALL
  SELECT 'corr_sweet_spot_compare', geo_level, geo_id, geo_name, '2024 CBSA comparison', 'pct_rent_burden_30plus', 'Rent-burdened renter share', pct_rent_burden_30plus::DOUBLE, "group"
  FROM comparison_rows
  UNION ALL
  SELECT 'corr_sweet_spot_compare', geo_level, geo_id, geo_name, '2024 CBSA comparison', 'value_to_income', 'Value-to-income ratio', value_to_income::DOUBLE, "group"
  FROM comparison_rows
  UNION ALL
  SELECT 'corr_sweet_spot_compare', geo_level, geo_id, geo_name, '2024 CBSA comparison', 'permits_per_1000_population', 'Permits per 1,000 residents', permits_per_1000_population::DOUBLE, "group"
  FROM comparison_rows
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
  "group",
  TRUE AS include_flag,
  'affordability_wide + population_demographics + cbsa_features'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  'Derived Sweet Spot shortlist = medium-sized metros with above-median growth and permitting plus below-median rent burden and value-to-income.'::VARCHAR AS note
FROM metric_long
WHERE metric_value IS NOT NULL;
