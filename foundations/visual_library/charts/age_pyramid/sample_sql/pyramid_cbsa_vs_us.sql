WITH selected_rows AS (
  SELECT
    'pyramid_cbsa_vs_us' AS question_id,
    geo_level,
    geo_id,
    geo_name,
    year AS period,
    pop_totalE AS pop_total,
    CASE WHEN geo_level = 'US' THEN 'Wilmington, NC' ELSE geo_name END AS facet_label,
    CASE WHEN geo_level = 'US' THEN 'United States' ELSE NULL END AS benchmark_label,
    geo_level <> 'US' AS highlight_flag,
    CASE WHEN geo_level = 'US' THEN 'National benchmark' ELSE NULL END AS note,
    *
  FROM metro_deep_dive.silver.age_base
  WHERE year = (
      SELECT MAX(year)
      FROM metro_deep_dive.silver.age_base
      WHERE geo_level = 'cbsa'
        AND geo_id = '48900'
    )
    AND ((geo_level = 'cbsa' AND geo_id = '48900') OR geo_level = 'US')
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
ORDER BY highlight_flag DESC, geo_name, age_bin, sex;
