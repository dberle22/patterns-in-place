WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS cbsa_code
),
target_counties AS (
  SELECT county_geoid
  FROM foundation.market_county_geometry
  WHERE cbsa_code = (SELECT cbsa_code FROM target_cbsa)
),
county_components AS (
  SELECT
    geo_id,
    MAX(geo_name) AS geo_name,
    SUM(CASE WHEN period = 2023 THEN real_gdp_construction END) - SUM(CASE WHEN period = 2018 THEN real_gdp_construction END) AS construction_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_manufacturing END) - SUM(CASE WHEN period = 2018 THEN real_gdp_manufacturing END) AS manufacturing_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_trade END) - SUM(CASE WHEN period = 2018 THEN real_gdp_trade END) AS trade_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_information END) - SUM(CASE WHEN period = 2018 THEN real_gdp_information END) AS information_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_fire END) - SUM(CASE WHEN period = 2018 THEN real_gdp_fire END) AS fire_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_professional END) - SUM(CASE WHEN period = 2018 THEN real_gdp_professional END) AS professional_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_edu_health END) - SUM(CASE WHEN period = 2018 THEN real_gdp_edu_health END) AS edu_health_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_leisure END) - SUM(CASE WHEN period = 2018 THEN real_gdp_leisure END) AS leisure_delta,
    SUM(CASE WHEN period = 2023 THEN real_gdp_gov END) - SUM(CASE WHEN period = 2018 THEN real_gdp_gov END) AS gov_delta,
    SUM(CASE WHEN period = 2023 THEN calc_real_gdp_other END) - SUM(CASE WHEN period = 2018 THEN calc_real_gdp_other END) AS other_delta
  FROM gold.economics_industry_wide
  WHERE geo_level = 'county'
    AND geo_id IN (SELECT county_geoid FROM target_counties)
    AND period IN (2018, 2023)
  GROUP BY geo_id
),
scored AS (
  SELECT
    *,
    COALESCE(construction_delta, 0) + COALESCE(manufacturing_delta, 0) + COALESCE(trade_delta, 0) +
      COALESCE(information_delta, 0) + COALESCE(fire_delta, 0) + COALESCE(professional_delta, 0) +
      COALESCE(edu_health_delta, 0) + COALESCE(leisure_delta, 0) + COALESCE(gov_delta, 0) +
      COALESCE(other_delta, 0) AS net_delta,
    LEAST(construction_delta, 0) + LEAST(manufacturing_delta, 0) + LEAST(trade_delta, 0) +
      LEAST(information_delta, 0) + LEAST(fire_delta, 0) + LEAST(professional_delta, 0) +
      LEAST(edu_health_delta, 0) + LEAST(leisure_delta, 0) + LEAST(gov_delta, 0) +
      LEAST(other_delta, 0) AS negative_delta
  FROM county_components
),
selected AS (
  SELECT *
  FROM scored
  WHERE net_delta > 0
    AND negative_delta < 0
  ORDER BY ABS(negative_delta) DESC, net_delta DESC
  LIMIT 1
),
components(component_id, component_label, sort_order, component_delta) AS (
  SELECT 'construction', 'Construction', 1, construction_delta FROM selected
  UNION ALL SELECT 'manufacturing', 'Manufacturing', 2, manufacturing_delta FROM selected
  UNION ALL SELECT 'trade', 'Trade', 3, trade_delta FROM selected
  UNION ALL SELECT 'information', 'Information', 4, information_delta FROM selected
  UNION ALL SELECT 'fire', 'Finance/real estate', 5, fire_delta FROM selected
  UNION ALL SELECT 'professional', 'Professional services', 6, professional_delta FROM selected
  UNION ALL SELECT 'edu_health', 'Education/health', 7, edu_health_delta FROM selected
  UNION ALL SELECT 'leisure', 'Leisure/hospitality', 8, leisure_delta FROM selected
  UNION ALL SELECT 'gov', 'Government', 9, gov_delta FROM selected
  UNION ALL SELECT 'other', 'Other sectors', 10, other_delta FROM selected
)
SELECT
  'waterfall_negative_offsets' AS question_id,
  'county' AS geo_level,
  s.geo_id,
  s.geo_name,
  '2018-2023 change' AS time_window,
  'Net real GDP change' AS total_label,
  c.component_id,
  c.component_label,
  c.component_delta / 1000000.0 AS component_value,
  'gold.economics_industry_wide; foundation.market_county_geometry' AS source,
  '2026-04-16' AS vintage,
  2018 AS start_period,
  2023 AS end_period,
  c.component_delta / 1000000.0 AS component_delta,
  '$ millions' AS unit_label,
  CASE
    WHEN c.component_delta < 0 THEN 'Offsetting sectors'
    ELSE 'Growth sectors'
  END AS component_group,
  NULL::VARCHAR AS benchmark_label,
  c.component_delta < 0 AS highlight_flag,
  c.sort_order,
  'County selected from the Wilmington CBSA because it has positive net real GDP growth with at least one negative sector offset.' AS note
FROM selected s
CROSS JOIN components c
WHERE c.component_delta IS NOT NULL
ORDER BY c.sort_order;
