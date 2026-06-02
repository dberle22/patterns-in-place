-- Q3: Is rent burden more associated with income or supply indicators?

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
    FROM metro_deep_dive.gold.economics_labor_wide
    WHERE geo_level = 'cbsa'
  )
),
cbsa_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    a.pct_rent_burden_30plus,
    a.median_hh_income,
    a.median_gross_rent,
    a.value_to_income,
    a.vacancy_rate,
    a.permits_per_1000_population,
    p.pct_ba_plus,
    l.pct_unemployment_rate
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  LEFT JOIN metro_deep_dive.gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN metro_deep_dive.gold.economics_labor_wide l
    ON a.geo_level = l.geo_level
   AND a.geo_id = l.geo_id
   AND a.year = l.year
  WHERE a.geo_level = 'cbsa'
),
metric_long AS (
  SELECT 'corr_rent_burden_driver_scan'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2024 CBSA snapshot'::VARCHAR AS time_window, 'pct_rent_burden_30plus'::VARCHAR AS metric_id, 'Rent-burdened renter share'::VARCHAR AS metric_label, pct_rent_burden_30plus::DOUBLE AS metric_value
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_rent_burden_driver_scan', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'median_hh_income', 'Median household income', median_hh_income::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_rent_burden_driver_scan', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'median_gross_rent', 'Median gross rent', median_gross_rent::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_rent_burden_driver_scan', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'value_to_income', 'Value-to-income ratio', value_to_income::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_rent_burden_driver_scan', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'vacancy_rate', 'Vacancy rate', vacancy_rate::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_rent_burden_driver_scan', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'permits_per_1000_population', 'Permits per 1,000 residents', permits_per_1000_population::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_rent_burden_driver_scan', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'pct_ba_plus', 'Adults with BA+', pct_ba_plus::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_rent_burden_driver_scan', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'pct_unemployment_rate', 'Unemployment rate', pct_unemployment_rate::DOUBLE
  FROM cbsa_base
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
  TRUE AS include_flag,
  'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  'Driver scan uses the national CBSA universe so the rent-burden row can be read against both income-side and supply-side indicators.'::VARCHAR AS note
FROM metric_long
WHERE metric_value IS NOT NULL;
