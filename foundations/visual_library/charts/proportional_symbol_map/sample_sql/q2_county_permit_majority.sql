WITH latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.housing_core_wide
  WHERE geo_level = 'county'
    AND permits_total_units IS NOT NULL
),
county_base AS (
  SELECT
    'bubble_permit_majority_counties' AS question_id,
    h.geo_level,
    h.geo_id,
    h.geo_name,
    CAST(h.year AS VARCHAR) || '_snapshot' AS time_window,
    h.permits_total_units AS size_value,
    'Permitted housing units' AS size_label,
    'gold.housing_core_wide + geo.counties' AS source,
    CAST(h.year AS VARCHAR) AS vintage,
    c.STATE_NAME AS color_group,
    c.STUSPS,
    ST_X(ST_PointOnSurface(c.geom)) AS lon,
    ST_Y(ST_PointOnSurface(c.geom)) AS lat
  FROM gold.housing_core_wide h
  JOIN geo.counties c
    ON h.geo_id = c.county_geoid
  WHERE h.geo_level = 'county'
    AND h.year = (SELECT year FROM latest_year)
    AND h.permits_total_units IS NOT NULL
    AND h.permits_total_units > 0
    AND c.STUSPS NOT IN ('AK', 'HI', 'PR')
),
ranked AS (
  SELECT
    *,
    SUM(size_value) OVER (ORDER BY size_value DESC, geo_name, geo_id) /
      SUM(size_value) OVER () AS cumulative_share
  FROM county_base
)
SELECT
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  size_value,
  size_label,
  source,
  vintage,
  CASE WHEN cumulative_share <= 0.50 THEN 'Top counties to 50% of units' ELSE 'Remaining counties' END AS color_group,
  cumulative_share <= 0.50 AS highlight_flag,
  cumulative_share <= 0.25 AS label_flag,
  lon,
  lat,
  'Color separates counties that cumulatively account for the first half of permitted units after ranking by total units.' AS note
FROM ranked;
