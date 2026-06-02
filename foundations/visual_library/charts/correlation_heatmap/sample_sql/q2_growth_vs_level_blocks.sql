-- Q2: Do growth metrics cluster separately from level metrics?

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
    a.median_hh_income,
    a.pct_rent_burden_30plus,
    a.permits_per_1000_population,
    p.pop_total,
    p.pct_ba_plus,
    p.pop_growth_5yr,
    p.pop_cagr_10yr,
    a.income_pc_growth_5yr,
    l.lfpr_growth_5yr
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
  SELECT 'corr_growth_vs_level_blocks'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2024 CBSA snapshot'::VARCHAR AS time_window, 'pop_total'::VARCHAR AS metric_id, 'Population level'::VARCHAR AS metric_label, pop_total::DOUBLE AS metric_value, 'level'::VARCHAR AS metric_group
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'median_hh_income', 'Median household income', median_hh_income::DOUBLE, 'level'
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'pct_ba_plus', 'Adults with BA+', pct_ba_plus::DOUBLE, 'level'
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'rent_burden_30plus', 'Rent-burdened renter share', pct_rent_burden_30plus::DOUBLE, 'level'
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'permits_per_1000_population', 'Permits per 1,000 residents', permits_per_1000_population::DOUBLE, 'level'
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'pop_growth_5yr', 'Population growth (5yr)', pop_growth_5yr::DOUBLE, 'growth'
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'pop_cagr_10yr', 'Population CAGR (10yr)', pop_cagr_10yr::DOUBLE, 'growth'
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'income_pc_growth_5yr', 'Per-capita income growth (5yr)', income_pc_growth_5yr::DOUBLE, 'growth'
  FROM cbsa_base
  UNION ALL
  SELECT 'corr_growth_vs_level_blocks', geo_level, geo_id, geo_name, '2024 CBSA snapshot', 'lfpr_growth_5yr', 'Labor-force participation growth (5yr)', lfpr_growth_5yr::DOUBLE, 'growth'
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
  metric_group AS "group",
  TRUE AS include_flag,
  'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  'Mixed level and growth KPI set for national CBSAs; intended to show whether growth metrics form a distinct block under clustered ordering.'::VARCHAR AS note
FROM metric_long
WHERE metric_value IS NOT NULL;
