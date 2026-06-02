WITH target_cbsa AS (
  SELECT '48900' AS target_geo_id
),
target_division AS (
  SELECT MIN(s.census_division) AS census_division
  FROM metro_deep_dive.silver.xwalk_cbsa_county x
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  WHERE x.cbsa_code = (SELECT target_geo_id FROM target_cbsa)
),
cbsa_division AS (
  SELECT
    x.cbsa_code AS geo_id,
    MIN(s.census_division) AS census_division
  FROM metro_deep_dive.silver.xwalk_cbsa_county x
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region s
    ON x.state_fips = s.state_fips
  GROUP BY 1
),
target_series AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year,
    a.rpp_real_pc_income,
    TRUE AS highlight_flag,
    NULL::VARCHAR AS benchmark_label
  FROM metro_deep_dive.gold.affordability_wide a
  WHERE a.geo_level = 'cbsa'
    AND a.geo_id = (SELECT target_geo_id FROM target_cbsa)
    AND a.year IN (2013, 2023)
    AND a.rpp_real_pc_income IS NOT NULL
),
benchmark_series AS (
  SELECT
    'cbsa_benchmark' AS geo_level,
    'south_atlantic_benchmark' AS geo_id,
    'South Atlantic CBSA average' AS geo_name,
    a.year,
    AVG(a.rpp_real_pc_income) AS rpp_real_pc_income,
    FALSE AS highlight_flag,
    'South Atlantic benchmark' AS benchmark_label
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN cbsa_division d
    ON a.geo_id = d.geo_id
  WHERE a.geo_level = 'cbsa'
    AND d.census_division = (SELECT census_division FROM target_division)
    AND a.year IN (2013, 2023)
    AND a.rpp_real_pc_income IS NOT NULL
  GROUP BY 1, 2, 3, 4, 6, 7
),
combined AS (
  SELECT * FROM target_series
  UNION ALL
  SELECT * FROM benchmark_series
)
SELECT
  'slope_target_vs_region' AS question_id,
  geo_level,
  geo_id,
  geo_name,
  year AS period,
  'rpp_real_pc_income' AS metric_id,
  'Real Per Capita Income' AS metric_label,
  rpp_real_pc_income::DOUBLE AS metric_value,
  'gold.affordability_wide' AS source,
  '2026-04-16' AS vintage,
  'Wilmington, NC vs Census division benchmark' AS "group",
  highlight_flag,
  benchmark_label,
  NULL::DOUBLE AS rank,
  'Benchmark is the target CBSA census-division aggregate from gold.affordability_wide.' AS note
FROM combined
ORDER BY benchmark_label NULLS FIRST, geo_name, year;
