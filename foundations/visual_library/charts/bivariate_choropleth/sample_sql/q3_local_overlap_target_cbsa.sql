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
    'bivar_local_overlap_target_cbsa' AS question_id,
    'tract' AS geo_level,
    a.geo_id,
    a.geo_name,
    '2024_snapshot' AS time_window,
    a.pct_rent_burden_30plus AS x_value,
    tbf.mean_travel_time AS y_value,
    'Rent burden' AS x_label,
    'Mean commute time' AS y_label,
    'gold.affordability_wide + gold.transport_built_form_wide + foundation.market_tract_geometry' AS source,
    CAST(a.year AS VARCHAR) AS vintage,
    target.cbsa_name AS "group",
    FALSE AS highlight_flag,
    g.geom_wkt,
    'High-high areas combine renter cost pressure with longer commute exposure.' AS note
  FROM gold.affordability_wide a
  JOIN gold.transport_built_form_wide tbf
    ON a.geo_level = tbf.geo_level
   AND a.geo_id = tbf.geo_id
   AND a.year = tbf.year
  JOIN foundation.market_tract_geometry g
    ON a.geo_id = g.tract_geoid
  JOIN target_cbsa target
    ON g.cbsa_code = target.cbsa_code
  WHERE a.geo_level = 'tract'
    AND a.year = (SELECT year FROM latest_year)
    AND a.pct_rent_burden_30plus IS NOT NULL
    AND tbf.mean_travel_time IS NOT NULL
)
SELECT *
FROM tract_base;
