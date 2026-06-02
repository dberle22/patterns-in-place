WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM metro_deep_dive.silver.age_kpi
  WHERE geo_level = 'zcta'
),
target_zctas AS (
  SELECT
    k.geo_id,
    k.geo_name,
    x.county_geoid,
    c.county_name,
    (k.pct_age_65_74 + k.pct_age_75_84 + k.pct_age_85p) AS retiree_share,
    ROW_NUMBER() OVER (
      ORDER BY (k.pct_age_65_74 + k.pct_age_75_84 + k.pct_age_85p) DESC, k.geo_name
    ) AS retiree_rank
  FROM metro_deep_dive.silver.age_kpi k
  JOIN metro_deep_dive.silver.xwalk_zcta_cbsa z
    ON k.geo_id = z.zip_geoid
  LEFT JOIN metro_deep_dive.silver.xwalk_zcta_county x
    ON k.geo_id = x.zip_geoid
  LEFT JOIN metro_deep_dive.silver.xwalk_county_state c
    ON x.county_geoid = c.county_geoid
  WHERE k.geo_level = 'zcta'
    AND k.year = (SELECT year FROM latest_year)
    AND z.cbsa_geoid = '48900'
    AND z.rel_weight_pop > 0
    AND k.pop_total >= 2500
),
selected_rows AS (
  SELECT
    'pyramid_zcta_retiree_profile' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year AS period,
    a.pop_totalE AS pop_total,
    CONCAT(t.geo_name, ' vs ', COALESCE(t.county_name, 'county')) AS facet_label,
    NULL::VARCHAR AS benchmark_label,
    TRUE AS highlight_flag,
    CONCAT('Retiree concentration rank among Wilmington CBSA ZCTAs with population >= 2,500: ', CAST(t.retiree_rank AS VARCHAR)) AS note,
    a.* EXCLUDE (geo_level, geo_id, geo_name, year, pop_totalE)
  FROM metro_deep_dive.silver.age_base a
  JOIN target_zctas t
    ON a.geo_id = t.geo_id
  WHERE a.geo_level = 'zcta'
    AND a.year = (SELECT year FROM latest_year)
    AND t.retiree_rank <= 3
  UNION ALL
  SELECT
    'pyramid_zcta_retiree_profile' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year AS period,
    a.pop_totalE AS pop_total,
    CONCAT(t.geo_name, ' vs ', COALESCE(t.county_name, 'county')) AS facet_label,
    COALESCE(t.county_name, 'County benchmark') AS benchmark_label,
    FALSE AS highlight_flag,
    'County benchmark repeats behind each selected ZCTA facet.' AS note,
    a.* EXCLUDE (geo_level, geo_id, geo_name, year, pop_totalE)
  FROM metro_deep_dive.silver.age_base a
  JOIN target_zctas t
    ON a.geo_id = t.county_geoid
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_year)
    AND t.retiree_rank <= 3
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
