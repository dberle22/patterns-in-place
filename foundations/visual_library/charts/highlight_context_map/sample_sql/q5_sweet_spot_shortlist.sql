WITH shortlist AS (
  SELECT * FROM (
    VALUES
      ('12420', 'Austin-Round Rock-Georgetown, TX', 'Austin'),
      ('16740', 'Charlotte-Concord-Gastonia, NC-SC', 'Charlotte'),
      ('27260', 'Jacksonville, FL', 'Jacksonville'),
      ('34980', 'Nashville-Davidson--Murfreesboro--Franklin, TN', 'Nashville'),
      ('39580', 'Raleigh-Cary, NC', 'Raleigh')
  ) AS t(cbsa_code, cbsa_name, label_text)
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM foundation.cbsa_features
),
cbsa_base AS (
  SELECT
    'highlight_shortlist_geography' AS question_id,
    'cbsa' AS geo_level,
    g.cbsa_code AS geo_id,
    g.cbsa_name AS geo_name,
    '2024_shortlist' AS time_window,
    'foundation.market_cbsa_geometry' AS source,
    CAST(f.year AS VARCHAR) AS vintage,
    f.census_region AS context_group,
    g.cbsa_code IN (SELECT cbsa_code FROM shortlist) AS highlight_flag,
    FALSE AS neighbor_flag,
    g.cbsa_code IN (SELECT cbsa_code FROM shortlist) AS label_flag,
    s.label_text,
    g.geom_wkt
  FROM foundation.market_cbsa_geometry g
  LEFT JOIN shortlist s
    ON g.cbsa_code = s.cbsa_code
  LEFT JOIN foundation.cbsa_features f
    ON g.cbsa_code = f.cbsa_code
   AND f.year = (SELECT year FROM latest_year)
  WHERE COALESCE(f.primary_state_abbr, '') NOT IN ('AK', 'HI', 'PR')
)
SELECT *
FROM cbsa_base;
