WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM metro_deep_dive.silver.age_kpi
  WHERE geo_level = 'county'
),
housing_latest AS (
  SELECT MAX(year) AS year
  FROM metro_deep_dive.gold.housing_core_wide
  WHERE geo_level = 'county'
),
county_scores AS (
  SELECT
    k.geo_id,
    k.geo_name,
    (k.pct_age_0_4 + k.pct_age_5_14 + k.pct_age_25_34 + k.pct_age_35_44) AS family_share,
    h.occ_occupied,
    h.owner_occupied,
    h.renter_occupied,
    ROW_NUMBER() OVER (
      ORDER BY (k.pct_age_0_4 + k.pct_age_5_14 + k.pct_age_25_34 + k.pct_age_35_44) DESC, k.geo_name
    ) AS demand_rank
  FROM metro_deep_dive.silver.age_kpi k
  JOIN metro_deep_dive.silver.xwalk_cbsa_county x
    ON k.geo_id = x.county_geoid
  LEFT JOIN metro_deep_dive.gold.housing_core_wide h
    ON k.geo_id = h.geo_id
   AND h.geo_level = 'county'
   AND h.year = (SELECT year FROM housing_latest)
  WHERE k.geo_level = 'county'
    AND k.year = (SELECT year FROM latest_year)
    AND x.cbsa_code = '48900'
),
selected_rows AS (
  SELECT
    'pyramid_housing_demand_alignment' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year AS period,
    a.pop_totalE AS pop_total,
    CONCAT(s.geo_name, ' family-formation profile') AS facet_label,
    NULL::VARCHAR AS benchmark_label,
    TRUE AS highlight_flag,
    CONCAT(
      'Family-age share is ', CAST(ROUND(100 * s.family_share, 1) AS VARCHAR),
      '%; housing context fields are carried from gold.housing_core_wide where available.'
    ) AS note,
    a.* EXCLUDE (geo_level, geo_id, geo_name, year, pop_totalE)
  FROM metro_deep_dive.silver.age_base a
  JOIN county_scores s
    ON a.geo_id = s.geo_id
  WHERE a.geo_level = 'county'
    AND a.year = (SELECT year FROM latest_year)
    AND s.demand_rank = 1
  UNION ALL
  SELECT
    'pyramid_housing_demand_alignment' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year AS period,
    a.pop_totalE AS pop_total,
    CONCAT(s.geo_name, ' family-formation profile') AS facet_label,
    'Wilmington CBSA' AS benchmark_label,
    FALSE AS highlight_flag,
    'CBSA benchmark supports reading whether the county family-age bulge is locally distinctive.' AS note,
    a.* EXCLUDE (geo_level, geo_id, geo_name, year, pop_totalE)
  FROM metro_deep_dive.silver.age_base a
  CROSS JOIN county_scores s
  WHERE a.geo_level = 'cbsa'
    AND a.geo_id = '48900'
    AND a.year = (SELECT year FROM latest_year)
    AND s.demand_rank = 1
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
  'silver.age_base ACS age-by-sex estimates; gold.housing_core_wide for housing context' AS source,
  '2026-04-16' AS vintage,
  MAX(note) AS note
FROM standardized
GROUP BY question_id, geo_level, geo_id, geo_name, period, age_bin, sex, facet_label
ORDER BY facet_label, highlight_flag DESC, age_bin, sex;
