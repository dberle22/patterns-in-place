WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id
),
latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year
    FROM gold.affordability_wide
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM gold.population_demographics
    WHERE geo_level = 'cbsa'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM gold.economics_labor_wide
    WHERE geo_level = 'cbsa'
  )
),
cbsa_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    p.pop_growth_5yr,
    a.median_hh_income,
    p.pct_ba_plus,
    l.pct_unemployment_rate,
    a.pct_rent_burden_30plus,
    a.permits_per_1000_population,
    a.geo_id = (SELECT target_geo_id FROM target_cbsa) AS highlight_flag
  FROM gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  LEFT JOIN gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN gold.economics_labor_wide l
    ON a.geo_level = l.geo_level
   AND a.geo_id = l.geo_id
   AND a.year = l.year
  WHERE a.geo_level = 'cbsa'
),
canonical_metrics AS (
  SELECT
    'strip_cbsa_profile'::VARCHAR AS question_id,
    geo_level,
    geo_id,
    geo_name,
    '2023 profile'::VARCHAR AS time_window,
    1 AS metric_order,
    'pop_growth_5yr'::VARCHAR AS metric_id,
    'Population growth (5yr)'::VARCHAR AS metric_label,
    'Growth'::VARCHAR AS metric_group,
    pop_growth_5yr::DOUBLE AS metric_value,
    'higher_is_better'::VARCHAR AS direction,
    'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide'::VARCHAR AS source,
    '2026-04-15'::VARCHAR AS vintage,
    NULL::DOUBLE AS benchmark_value,
    NULL::VARCHAR AS benchmark_label,
    highlight_flag,
    'Percentile normalization runs across all CBSAs in the latest common year.'::VARCHAR AS note
  FROM cbsa_base

  UNION ALL

  SELECT
    'strip_cbsa_profile',
    geo_level,
    geo_id,
    geo_name,
    '2023 profile',
    2,
    'median_hh_income',
    'Median household income',
    'Prosperity',
    median_hh_income::DOUBLE,
    'higher_is_better',
    'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide',
    '2026-04-15'::VARCHAR,
    NULL::DOUBLE,
    NULL::VARCHAR,
    highlight_flag,
    'Percentile normalization runs across all CBSAs in the latest common year.'
  FROM cbsa_base

  UNION ALL

  SELECT
    'strip_cbsa_profile',
    geo_level,
    geo_id,
    geo_name,
    '2023 profile',
    3,
    'pct_ba_plus',
    'Adults with BA+',
    'Talent',
    pct_ba_plus::DOUBLE,
    'higher_is_better',
    'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide',
    '2026-04-15'::VARCHAR,
    NULL::DOUBLE,
    NULL::VARCHAR,
    highlight_flag,
    'Percentile normalization runs across all CBSAs in the latest common year.'
  FROM cbsa_base

  UNION ALL

  SELECT
    'strip_cbsa_profile',
    geo_level,
    geo_id,
    geo_name,
    '2023 profile',
    4,
    'pct_unemployment_rate',
    'Unemployment rate',
    'Labor',
    pct_unemployment_rate::DOUBLE,
    'lower_is_better',
    'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide',
    '2026-04-15'::VARCHAR,
    NULL::DOUBLE,
    NULL::VARCHAR,
    highlight_flag,
    'Percentile normalization runs across all CBSAs in the latest common year.'
  FROM cbsa_base

  UNION ALL

  SELECT
    'strip_cbsa_profile',
    geo_level,
    geo_id,
    geo_name,
    '2023 profile',
    5,
    'pct_rent_burden_30plus',
    'Rent-burdened renter share',
    'Affordability',
    pct_rent_burden_30plus::DOUBLE,
    'lower_is_better',
    'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide',
    '2026-04-15'::VARCHAR,
    NULL::DOUBLE,
    NULL::VARCHAR,
    highlight_flag,
    'Percentile normalization runs across all CBSAs in the latest common year.'
  FROM cbsa_base

  UNION ALL

  SELECT
    'strip_cbsa_profile',
    geo_level,
    geo_id,
    geo_name,
    '2023 profile',
    6,
    'permits_per_1000_population',
    'Permits per 1,000 residents',
    'Supply',
    permits_per_1000_population::DOUBLE,
    'higher_is_better',
    'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide',
    '2026-04-15'::VARCHAR,
    NULL::DOUBLE,
    NULL::VARCHAR,
    highlight_flag,
    'Percentile normalization runs across all CBSAs in the latest common year.'
  FROM cbsa_base
)
SELECT *
FROM canonical_metrics
ORDER BY metric_order, geo_id;
