-- Q5: Within a target CBSA's counties, which housing indicators co-move most?

WITH target_cbsa AS (
  SELECT
    '12060'::VARCHAR AS cbsa_code,
    'Atlanta-Sandy Springs-Roswell, GA'::VARCHAR AS cbsa_name
),
latest_common_year AS (
  SELECT MIN(max_year) AS year
  FROM (
    SELECT MAX(year) AS max_year
    FROM metro_deep_dive.gold.affordability_wide
    WHERE geo_level = 'county'
    UNION ALL
    SELECT MAX(year) AS max_year
    FROM metro_deep_dive.gold.housing_core_wide
    WHERE geo_level = 'county'
  )
),
county_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    y.year,
    t.cbsa_name,
    a.median_gross_rent,
    a.median_home_value,
    a.value_to_income,
    a.pct_rent_burden_30plus,
    a.vacancy_rate,
    a.permits_per_1000_population,
    h.pct_struct_multifam,
    h.owner_occ_rate
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN latest_common_year y
    ON a.year = y.year
  JOIN metro_deep_dive.silver.xwalk_cbsa_county x
    ON a.geo_id = x.county_geoid
  JOIN target_cbsa t
    ON x.cbsa_code = t.cbsa_code
  LEFT JOIN metro_deep_dive.gold.housing_core_wide h
    ON a.geo_level = h.geo_level
   AND a.geo_id = h.geo_id
   AND a.year = h.year
  WHERE a.geo_level = 'county'
),
metric_long AS (
  SELECT 'corr_county_within_cbsa'::VARCHAR AS question_id, geo_level, geo_id, geo_name, '2024 Atlanta county housing profile'::VARCHAR AS time_window, 'median_gross_rent'::VARCHAR AS metric_id, 'Median gross rent'::VARCHAR AS metric_label, median_gross_rent::DOUBLE AS metric_value
  FROM county_base
  UNION ALL
  SELECT 'corr_county_within_cbsa', geo_level, geo_id, geo_name, '2024 Atlanta county housing profile', 'median_home_value', 'Median home value', median_home_value::DOUBLE
  FROM county_base
  UNION ALL
  SELECT 'corr_county_within_cbsa', geo_level, geo_id, geo_name, '2024 Atlanta county housing profile', 'value_to_income', 'Value-to-income ratio', value_to_income::DOUBLE
  FROM county_base
  UNION ALL
  SELECT 'corr_county_within_cbsa', geo_level, geo_id, geo_name, '2024 Atlanta county housing profile', 'pct_rent_burden_30plus', 'Rent-burdened renter share', pct_rent_burden_30plus::DOUBLE
  FROM county_base
  UNION ALL
  SELECT 'corr_county_within_cbsa', geo_level, geo_id, geo_name, '2024 Atlanta county housing profile', 'vacancy_rate', 'Vacancy rate', vacancy_rate::DOUBLE
  FROM county_base
  UNION ALL
  SELECT 'corr_county_within_cbsa', geo_level, geo_id, geo_name, '2024 Atlanta county housing profile', 'permits_per_1000_population', 'Permits per 1,000 residents', permits_per_1000_population::DOUBLE
  FROM county_base
  UNION ALL
  SELECT 'corr_county_within_cbsa', geo_level, geo_id, geo_name, '2024 Atlanta county housing profile', 'pct_struct_multifam', 'Multifamily share of structures', pct_struct_multifam::DOUBLE
  FROM county_base
  UNION ALL
  SELECT 'corr_county_within_cbsa', geo_level, geo_id, geo_name, '2024 Atlanta county housing profile', 'owner_occ_rate', 'Owner-occupancy rate', owner_occ_rate::DOUBLE
  FROM county_base
)
SELECT
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  metric_id,
  metric_label,
  metric_value,
  TRUE AS include_flag,
  'gold.affordability_wide + gold.housing_core_wide + silver.xwalk_cbsa_county'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  'Atlanta counties are used because the CBSA has a large enough county set to make within-metro housing co-movement readable.'::VARCHAR AS note
FROM metric_long
WHERE metric_value IS NOT NULL;
