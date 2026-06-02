WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM metro_deep_dive.silver.age_kpi
  WHERE geo_level = 'county'
),
target_counties AS (
  SELECT
    k.geo_id,
    k.geo_name,
    (k.pct_age_0_4 + k.pct_age_5_14 + k.pct_age_25_34 + k.pct_age_35_44) AS family_profile_share,
    ROW_NUMBER() OVER (
      ORDER BY (k.pct_age_0_4 + k.pct_age_5_14 + k.pct_age_25_34 + k.pct_age_35_44) DESC, k.geo_name
    ) AS family_rank
  FROM metro_deep_dive.silver.age_kpi k
  JOIN metro_deep_dive.silver.xwalk_cbsa_county x
    ON k.geo_id = x.county_geoid
  WHERE k.geo_level = 'county'
    AND k.year = (SELECT year FROM latest_year)
    AND x.cbsa_code = '48900'
),
selected_rows AS (
  SELECT
    'pyramid_county_family_profile' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year AS period,
    a.pop_totalE AS pop_total,
    CONCAT(t.geo_name, ' vs Wilmington CBSA') AS facet_label,
    NULL::VARCHAR AS benchmark_label,
    TRUE AS highlight_flag,
    CONCAT('Family profile rank within Wilmington CBSA: ', CAST(t.family_rank AS VARCHAR)) AS note,
    a.* EXCLUDE (geo_level, geo_id, geo_name, year, pop_totalE)
  FROM metro_deep_dive.silver.age_base a
  JOIN target_counties t
    ON a.geo_id = t.geo_id
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_year)
    AND t.family_rank <= 3
  UNION ALL
  SELECT
    'pyramid_county_family_profile' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year AS period,
    a.pop_totalE AS pop_total,
    CONCAT(t.geo_name, ' vs Wilmington CBSA') AS facet_label,
    'Wilmington CBSA' AS benchmark_label,
    FALSE AS highlight_flag,
    'Benchmark repeats the CBSA age structure behind each county facet.' AS note,
    a.* EXCLUDE (geo_level, geo_id, geo_name, year, pop_totalE)
  FROM metro_deep_dive.silver.age_base a
  CROSS JOIN target_counties t
  WHERE a.geo_level = 'cbsa'
    AND a.geo_id = '48900'
    AND a.year = (SELECT year FROM latest_year)
    AND t.family_rank <= 3
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
ORDER BY facet_label, highlight_flag DESC, age_bin, sex;
