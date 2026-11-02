-- Raw benchmark metrics, ACS 2020-24 5-year, one row per geography x metric:
-- the CBSAs in __CBSA_CODES__, New York State and the US.
WITH geos AS (
  SELECT 'cbsa' AS geo_level, UNNEST([__CBSA_CODES__]) AS geo_id
  UNION ALL SELECT 'state', '36'
  UNION ALL SELECT 'us', '1'
),
wide AS (
  SELECT
    g.geo_level,
    g.geo_id,
    p.geo_name,
    p.pop_total AS population,
    i.median_hh_income,
    p.pct_ba_plus AS ba_plus_share
  FROM geos AS g
  JOIN gold.population_demographics AS p
    ON lower(p.geo_level) = g.geo_level AND p.geo_id = g.geo_id AND p.year = 2024
  LEFT JOIN gold.economics_income_wide AS i
    ON lower(i.geo_level) = g.geo_level AND i.geo_id = g.geo_id AND i.year = 2024
)
UNPIVOT wide
ON population, median_hh_income, ba_plus_share
INTO NAME metric_id VALUE value
