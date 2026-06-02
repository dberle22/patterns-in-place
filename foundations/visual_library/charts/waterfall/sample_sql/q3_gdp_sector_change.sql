WITH target AS (
  SELECT '48900'::VARCHAR AS geo_id
),
endpoints AS (
  SELECT *
  FROM gold.economics_industry_wide
  WHERE geo_level = 'cbsa'
    AND geo_id = (SELECT geo_id FROM target)
    AND period IN (2013, 2023)
),
wide AS (
  SELECT
    MAX(geo_level) AS geo_level,
    geo_id,
    MAX(geo_name) AS geo_name,
    MAX(CASE WHEN period = 2013 THEN real_gdp_natural_resources END) AS natural_resources_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_natural_resources END) AS natural_resources_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_manufacturing END) AS manufacturing_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_manufacturing END) AS manufacturing_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_construction END) AS construction_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_construction END) AS construction_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_trade END) AS trade_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_trade END) AS trade_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_transportation END) AS transportation_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_transportation END) AS transportation_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_information END) AS information_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_information END) AS information_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_fire END) AS fire_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_fire END) AS fire_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_professional END) AS professional_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_professional END) AS professional_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_edu_health END) AS edu_health_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_edu_health END) AS edu_health_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_leisure END) AS leisure_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_leisure END) AS leisure_end,
    MAX(CASE WHEN period = 2013 THEN real_gdp_gov END) AS gov_start,
    MAX(CASE WHEN period = 2023 THEN real_gdp_gov END) AS gov_end,
    MAX(CASE WHEN period = 2013 THEN calc_real_gdp_other END) AS other_start,
    MAX(CASE WHEN period = 2023 THEN calc_real_gdp_other END) AS other_end
  FROM endpoints
  GROUP BY geo_id
),
components(component_id, component_label, sort_order, start_value, end_value) AS (
  SELECT 'natural_resources', 'Natural resources', 1, natural_resources_start, natural_resources_end FROM wide
  UNION ALL SELECT 'manufacturing', 'Manufacturing', 2, manufacturing_start, manufacturing_end FROM wide
  UNION ALL SELECT 'construction', 'Construction', 3, construction_start, construction_end FROM wide
  UNION ALL SELECT 'trade', 'Trade', 4, trade_start, trade_end FROM wide
  UNION ALL SELECT 'transportation', 'Transportation', 5, transportation_start, transportation_end FROM wide
  UNION ALL SELECT 'information', 'Information', 6, information_start, information_end FROM wide
  UNION ALL SELECT 'fire', 'Finance/real estate', 7, fire_start, fire_end FROM wide
  UNION ALL SELECT 'professional', 'Professional services', 8, professional_start, professional_end FROM wide
  UNION ALL SELECT 'edu_health', 'Education/health', 9, edu_health_start, edu_health_end FROM wide
  UNION ALL SELECT 'leisure', 'Leisure/hospitality', 10, leisure_start, leisure_end FROM wide
  UNION ALL SELECT 'gov', 'Government', 11, gov_start, gov_end FROM wide
  UNION ALL SELECT 'other', 'Other sectors', 12, other_start, other_end FROM wide
)
SELECT
  'waterfall_gdp_sector_change' AS question_id,
  w.geo_level,
  w.geo_id,
  w.geo_name,
  '2013-2023 change' AS time_window,
  'Net real GDP change' AS total_label,
  c.component_id,
  c.component_label,
  c.end_value / 1000000.0 AS component_value,
  'gold.economics_industry_wide' AS source,
  '2026-04-16' AS vintage,
  2013 AS start_period,
  2023 AS end_period,
  (c.end_value - c.start_value) / 1000000.0 AS component_delta,
  '$ millions' AS unit_label,
  CASE
    WHEN c.component_id IN ('natural_resources', 'manufacturing', 'construction') THEN 'Goods'
    WHEN c.component_id IN ('trade', 'transportation', 'information') THEN 'Market services'
    WHEN c.component_id IN ('fire', 'professional') THEN 'Business services'
    WHEN c.component_id IN ('edu_health', 'leisure', 'gov') THEN 'Local services'
    ELSE 'Other'
  END AS component_group,
  NULL::VARCHAR AS benchmark_label,
  TRUE AS highlight_flag,
  c.sort_order,
  'Sector components are from the industry wide table; Other reconciles sector sum to total real GDP.' AS note
FROM wide w
CROSS JOIN components c
WHERE c.start_value IS NOT NULL
  AND c.end_value IS NOT NULL
ORDER BY c.sort_order;
