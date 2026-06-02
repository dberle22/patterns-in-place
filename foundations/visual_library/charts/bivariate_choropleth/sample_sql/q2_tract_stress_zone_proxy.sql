WITH target_cbsa AS (
  SELECT
    '12060' AS cbsa_code,
    'Atlanta-Sandy Springs-Roswell, GA' AS cbsa_name
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'tract'
),
tract_base AS (
  SELECT
    'bivar_stress_zone_zctas' AS question_id,
    'tract' AS geo_level,
    a.geo_id,
    a.geo_name,
    '2024_snapshot' AS time_window,
    a.pct_rent_burden_30plus AS x_value,
    -1.0 * a.median_hh_income AS y_value,
    'Rent burden' AS x_label,
    'Lower household income' AS y_label,
    'gold.affordability_wide + foundation.market_tract_geometry' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    t.cbsa_name AS "group",
    FALSE AS highlight_flag,
    g.geom_wkt,
    'Tract geometry is used as the reviewable small-area proxy until a ZCTA geometry layer is available.' AS note
  FROM gold.affordability_wide a
  JOIN foundation.market_tract_geometry g
    ON a.geo_id = g.tract_geoid
  JOIN target_cbsa t
    ON g.cbsa_code = t.cbsa_code
  WHERE a.geo_level = 'tract'
    AND a.year = (SELECT year FROM latest_year)
    AND a.pct_rent_burden_30plus IS NOT NULL
    AND a.median_hh_income IS NOT NULL
)
SELECT *
FROM tract_base;
