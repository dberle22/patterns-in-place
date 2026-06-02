WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.affordability_wide
  WHERE geo_level = 'cbsa'
    AND income_pc_growth_5yr IS NOT NULL
),
cbsa_base AS (
  SELECT
    'bivar_cbsa_region_overlap' AS question_id,
    a.geo_level,
    a.geo_id,
    a.geo_name,
    '2018_to_2023_growth' AS time_window,
    a.income_pc_growth_5yr AS x_value,
    1.0 / NULLIF(a.rent_to_income, 0) AS y_value,
    '5-year per capita income growth' AS x_label,
    'Rent affordability' AS y_label,
    'gold.affordability_wide + foundation.market_cbsa_geometry + foundation.cbsa_features' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    f.census_region AS "group",
    FALSE AS highlight_flag,
    g.geom_wkt,
    'Affordability is encoded as the inverse of rent to income so higher bins mean more affordable.' AS note
  FROM gold.affordability_wide a
  JOIN foundation.market_cbsa_geometry g
    ON a.geo_id = g.cbsa_code
  LEFT JOIN foundation.cbsa_features f
    ON a.geo_id = f.cbsa_code
   AND a.year = f.year
  WHERE a.geo_level = 'cbsa'
    AND a.year = (SELECT year FROM latest_year)
    AND a.income_pc_growth_5yr IS NOT NULL
    AND a.rent_to_income IS NOT NULL
    AND COALESCE(f.primary_state_abbr, '') NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM cbsa_base;
