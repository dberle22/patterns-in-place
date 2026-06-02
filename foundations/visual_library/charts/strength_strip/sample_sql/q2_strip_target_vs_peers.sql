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
cbsa_lookup AS (
  SELECT
    a.geo_id,
    a.geo_name,
    a.pop_total,
    MIN(s.census_division) AS census_division
  FROM gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  JOIN silver.xwalk_cbsa_county x
    ON a.geo_id = x.cbsa_code
  LEFT JOIN silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  WHERE a.geo_level = 'cbsa'
  GROUP BY 1, 2, 3
),
peer_pool AS (
  SELECT
    l.*,
    t.pop_total AS target_pop_total,
    ROW_NUMBER() OVER (
      ORDER BY ABS(l.pop_total - t.pop_total), l.geo_id
    ) AS peer_rank
  FROM cbsa_lookup l
  JOIN cbsa_lookup t
    ON t.geo_id = (SELECT target_geo_id FROM target_cbsa)
  WHERE l.census_division = t.census_division
    AND l.geo_id <> t.geo_id
    AND l.pop_total BETWEEN t.pop_total * 0.7 AND t.pop_total * 1.5
),
selected_cbsas AS (
  SELECT geo_id
  FROM peer_pool
  WHERE peer_rank <= 3

  UNION ALL

  SELECT target_geo_id
  FROM target_cbsa
),
universe_cbsas AS (
  SELECT l.geo_id
  FROM cbsa_lookup l
  JOIN cbsa_lookup t
    ON t.geo_id = (SELECT target_geo_id FROM target_cbsa)
  WHERE l.census_division = t.census_division
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
    a.geo_id = (SELECT target_geo_id FROM target_cbsa) AS highlight_flag,
    a.geo_id IN (SELECT geo_id FROM selected_cbsas) AS display_flag
  FROM gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  JOIN universe_cbsas s
    ON a.geo_id = s.geo_id
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
    'strip_target_vs_peers'::VARCHAR AS question_id,
    geo_level,
    geo_id,
    geo_name,
    '2023 South Atlantic peer set'::VARCHAR AS time_window,
    1 AS metric_order,
    'pop_growth_5yr'::VARCHAR AS metric_id,
    'Population growth (5yr)'::VARCHAR AS metric_label,
    'Growth'::VARCHAR AS metric_group,
    pop_growth_5yr::DOUBLE AS metric_value,
    'higher_is_better'::VARCHAR AS direction,
    'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + silver.xwalk_cbsa_county + silver.xwalk_state_region'::VARCHAR AS source,
    '2026-04-15'::VARCHAR AS vintage,
    NULL::DOUBLE AS benchmark_value,
    NULL::VARCHAR AS benchmark_label,
    highlight_flag,
    display_flag,
    'Percentiles are computed against the full South Atlantic CBSA universe; the chart only displays Wilmington plus its three closest population peers.'::VARCHAR AS note
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_target_vs_peers', geo_level, geo_id, geo_name, '2023 South Atlantic peer set', 2, 'median_hh_income', 'Median household income', 'Prosperity', median_hh_income::DOUBLE, 'higher_is_better', 'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + silver.xwalk_cbsa_county + silver.xwalk_state_region', '2026-04-15'::VARCHAR, NULL::DOUBLE, NULL::VARCHAR, highlight_flag, display_flag, 'Percentiles are computed against the full South Atlantic CBSA universe; the chart only displays Wilmington plus its three closest population peers.'
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_target_vs_peers', geo_level, geo_id, geo_name, '2023 South Atlantic peer set', 3, 'pct_ba_plus', 'Adults with BA+', 'Talent', pct_ba_plus::DOUBLE, 'higher_is_better', 'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + silver.xwalk_cbsa_county + silver.xwalk_state_region', '2026-04-15'::VARCHAR, NULL::DOUBLE, NULL::VARCHAR, highlight_flag, display_flag, 'Percentiles are computed against the full South Atlantic CBSA universe; the chart only displays Wilmington plus its three closest population peers.'
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_target_vs_peers', geo_level, geo_id, geo_name, '2023 South Atlantic peer set', 4, 'pct_unemployment_rate', 'Unemployment rate', 'Labor', pct_unemployment_rate::DOUBLE, 'lower_is_better', 'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + silver.xwalk_cbsa_county + silver.xwalk_state_region', '2026-04-15'::VARCHAR, NULL::DOUBLE, NULL::VARCHAR, highlight_flag, display_flag, 'Percentiles are computed against the full South Atlantic CBSA universe; the chart only displays Wilmington plus its three closest population peers.'
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_target_vs_peers', geo_level, geo_id, geo_name, '2023 South Atlantic peer set', 5, 'pct_rent_burden_30plus', 'Rent-burdened renter share', 'Affordability', pct_rent_burden_30plus::DOUBLE, 'lower_is_better', 'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + silver.xwalk_cbsa_county + silver.xwalk_state_region', '2026-04-15'::VARCHAR, NULL::DOUBLE, NULL::VARCHAR, highlight_flag, display_flag, 'Percentiles are computed against the full South Atlantic CBSA universe; the chart only displays Wilmington plus its three closest population peers.'
  FROM cbsa_base

  UNION ALL

  SELECT 'strip_target_vs_peers', geo_level, geo_id, geo_name, '2023 South Atlantic peer set', 6, 'permits_per_1000_population', 'Permits per 1,000 residents', 'Supply', permits_per_1000_population::DOUBLE, 'higher_is_better', 'gold.affordability_wide + gold.population_demographics + gold.economics_labor_wide + silver.xwalk_cbsa_county + silver.xwalk_state_region', '2026-04-15'::VARCHAR, NULL::DOUBLE, NULL::VARCHAR, highlight_flag, display_flag, 'Percentiles are computed against the full South Atlantic CBSA universe; the chart only displays Wilmington plus its three closest population peers.'
  FROM cbsa_base
)
SELECT *
FROM canonical_metrics
ORDER BY metric_order, geo_id;
