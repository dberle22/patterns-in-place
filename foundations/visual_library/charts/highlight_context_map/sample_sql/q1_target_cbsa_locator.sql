WITH target_cbsa AS (
  SELECT
    '12060' AS cbsa_code,
    'Atlanta-Sandy Springs-Roswell, GA' AS cbsa_name
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM foundation.cbsa_features
),
cbsa_base AS (
  SELECT
    'highlight_target_locator' AS question_id,
    'cbsa' AS geo_level,
    g.cbsa_code AS geo_id,
    g.cbsa_name AS geo_name,
    '2024_locator' AS time_window,
    'foundation.market_cbsa_geometry' AS source,
    CAST(f.year AS VARCHAR) AS vintage,
    f.census_region AS context_group,
    g.cbsa_code = t.cbsa_code AS highlight_flag,
    g.cbsa_code = t.cbsa_code AS label_flag,
    CASE WHEN g.cbsa_code = t.cbsa_code THEN 'Atlanta' END AS label_text,
    g.geom_wkt
  FROM foundation.market_cbsa_geometry g
  LEFT JOIN foundation.cbsa_features f
    ON g.cbsa_code = f.cbsa_code
   AND f.year = (SELECT year FROM latest_year)
  CROSS JOIN target_cbsa t
  WHERE COALESCE(f.primary_state_abbr, '') NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM cbsa_base;
