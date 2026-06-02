WITH comparison_years AS (
  SELECT MIN(year) AS period FROM metro_deep_dive.silver.age_base WHERE geo_level = 'cbsa' AND geo_id = '48900' AND year >= 2013
  UNION ALL
  SELECT MAX(year) AS period FROM metro_deep_dive.silver.age_base WHERE geo_level = 'cbsa' AND geo_id = '48900'
),
selected_rows AS (
  SELECT
    'pyramid_peer_aging_compare' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year AS period,
    a.pop_totalE AS pop_total,
    CAST(a.year AS VARCHAR) AS facet_label,
    CASE WHEN a.geo_level = 'US' THEN 'United States' ELSE NULL END AS benchmark_label,
    a.geo_level <> 'US' AS highlight_flag,
    CASE WHEN a.geo_level = 'US' THEN 'National benchmark repeated for cohort-shape context.' ELSE 'Same CBSA shown in two ACS snapshots.' END AS note,
    a.* EXCLUDE (geo_level, geo_id, geo_name, year, pop_totalE)
  FROM metro_deep_dive.silver.age_base a
  JOIN comparison_years y
    ON a.year = y.period
  WHERE (a.geo_level = 'cbsa' AND a.geo_id = '48900')
     OR a.geo_level = 'US'
)
{{AGE_PYRAMID_HELPER}}
SELECT
  question_id, geo_level, geo_id, geo_name, period, age_bin, sex,
  SUM(pop_value)::DOUBLE AS pop_value,
  MAX(pop_total)::DOUBLE AS pop_total,
  NULL::DOUBLE AS pop_share,
  MAX(benchmark_label) AS benchmark_label,
  BOOL_OR(highlight_flag) AS highlight_flag,
  MAX(facet_label) AS facet_label,
  'silver.age_base ACS age-by-sex estimates' AS source,
  '2026-04-16' AS vintage,
  MAX(note) AS note
FROM standardized
GROUP BY question_id, geo_level, geo_id, geo_name, period, age_bin, sex, facet_label
ORDER BY period, highlight_flag DESC, age_bin, sex;
