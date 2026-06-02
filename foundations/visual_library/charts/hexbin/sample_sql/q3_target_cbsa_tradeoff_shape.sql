-- Q3: In a target CBSA, what is the density pattern of home value-to-income vs rent-to-income?

WITH params AS (
  SELECT
    '35620'::VARCHAR AS target_cbsa_geoid
),
base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    '2023_snapshot'::VARCHAR AS time_window,
    a.value_to_income::DOUBLE AS x_value,
    a.rent_to_income::DOUBLE AS y_value,
    'Home Value / Income Ratio (2023)'::VARCHAR AS x_label,
    'Rent / Income Ratio (2023, %)'::VARCHAR AS y_label,
    x.cbsa_geoid,
    c.cbsa_name,
    a.pop_total::DOUBLE AS pop_total
  FROM metro_deep_dive.gold.affordability_wide a
  JOIN metro_deep_dive.silver.xwalk_zcta_cbsa x
    ON a.geo_id = x.zip_geoid
  LEFT JOIN (
    SELECT cbsa_code, cbsa_name, ROW_NUMBER() OVER (PARTITION BY cbsa_code ORDER BY county_geoid) AS rn
    FROM metro_deep_dive.silver.xwalk_cbsa_county
  ) c
    ON x.cbsa_geoid = c.cbsa_code
   AND c.rn = 1
  WHERE a.geo_level = 'zcta'
    AND a.year = 2023
    AND x.cbsa_geoid = (SELECT target_cbsa_geoid FROM params)
    AND a.value_to_income IS NOT NULL
    AND a.rent_to_income IS NOT NULL
),
scored AS (
  SELECT
    b.*,
    abs((b.x_value - avg(b.x_value) OVER ()) / NULLIF(stddev_samp(b.x_value) OVER (), 0)) +
      abs((b.y_value - avg(b.y_value) OVER ()) / NULLIF(stddev_samp(b.y_value) OVER (), 0)) AS extremity_score
  FROM base b
),
ranked AS (
  SELECT
    s.*,
    ROW_NUMBER() OVER (ORDER BY s.extremity_score DESC, s.pop_total DESC) AS extreme_rank
  FROM scored s
)
SELECT
  'hexbin_target_cbsa_tradeoff_shape'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  x_value,
  y_value,
  x_label,
  y_label,
  cbsa_name AS "group",
  NULL::DOUBLE AS weight_value,
  extreme_rank <= 5 AS highlight_flag,
  'gold.affordability_wide + silver.xwalk_zcta_cbsa + silver.xwalk_cbsa_county'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  CASE
    WHEN extreme_rank <= 5 THEN 'Highlighted local outlier with large combined x/y extremity.'
    ELSE NULL
  END AS note
FROM ranked;
