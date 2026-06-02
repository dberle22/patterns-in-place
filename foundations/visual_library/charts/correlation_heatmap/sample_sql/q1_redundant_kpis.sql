-- Q1: Which metrics appear redundant across the national CBSA universe?

WITH latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year
    FROM metro_deep_dive.gold.affordability_wide
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM metro_deep_dive.gold.economics_income_wide
    WHERE geo_level = 'cbsa'
  )
),
cbsa_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    a.median_hh_income,
    a.acs_income_pc,
    a.calc_income_pc,
    a.median_gross_rent,
    a.annualized_median_rent,
    a.median_home_value,
    a.rent_to_income,
    a.value_to_income
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  WHERE a.geo_level = 'cbsa'
),
metric_long AS (
  SELECT 'corr_redundant_kpis'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2024 CBSA snapshot'::VARCHAR AS time_window, 'median_hh_income'::VARCHAR AS metric_id, 'Median household income'::VARCHAR AS metric_label, median_hh_income::DOUBLE AS metric_value
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_redundant_kpis', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'acs_income_pc', 'ACS per-capita income', acs_income_pc::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_redundant_kpis', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'calc_income_pc', 'Calculated per-capita income', calc_income_pc::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_redundant_kpis', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'median_gross_rent', 'Median gross rent', median_gross_rent::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_redundant_kpis', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'annualized_median_rent', 'Annualized median rent', annualized_median_rent::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_redundant_kpis', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'median_home_value', 'Median home value', median_home_value::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_redundant_kpis', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'rent_to_income', 'Rent-to-income ratio', rent_to_income::DOUBLE
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_redundant_kpis', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'value_to_income', 'Value-to-income ratio', value_to_income::DOUBLE
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
  'gold.affordability_wide + gold.economics_income_wide'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  'National CBSA matrix built from intentionally overlapping affordability and income metrics to reveal redundant signals.'::VARCHAR AS note
FROM metric_long
WHERE metric_value IS NOT NULL;
