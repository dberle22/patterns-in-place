WITH params AS (
  SELECT '48900'::VARCHAR AS cbsa_code
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.population_demographics
  WHERE geo_level = 'zcta'
),
target_zctas AS (
  SELECT DISTINCT
    zip_geoid AS geo_id,
    zip_pref_state,
    rel_weight_pop
  FROM silver.xwalk_zcta_cbsa
  WHERE cbsa_geoid = (SELECT cbsa_code FROM params)
),
zcta_points AS (
  SELECT
    zt.zip_geoid AS geo_id,
    SUM(zt.rel_weight_pop * ST_X(ST_PointOnSurface(ST_GeomFromText(g.geom_wkt)))) /
      NULLIF(SUM(zt.rel_weight_pop), 0) AS lon,
    SUM(zt.rel_weight_pop * ST_Y(ST_PointOnSurface(ST_GeomFromText(g.geom_wkt)))) /
      NULLIF(SUM(zt.rel_weight_pop), 0) AS lat
  FROM silver.xwalk_zcta_tract zt
  JOIN foundation.market_tract_geometry g
    ON zt.tract_geoid = g.tract_geoid
  WHERE g.cbsa_code = (SELECT cbsa_code FROM params)
  GROUP BY 1
),
zcta_base AS (
  SELECT
    'bubble_largest_zctas_in_cbsa' AS question_id,
    p.geo_level,
    p.geo_id,
    p.geo_name,
    CAST(p.year AS VARCHAR) || '_snapshot' AS time_window,
    p.pop_total AS size_value,
    'ZCTA population' AS size_label,
    'gold.population_demographics + silver.xwalk_zcta_cbsa + silver.xwalk_zcta_tract + foundation.market_tract_geometry' AS source,
    CAST(p.year AS VARCHAR) AS vintage,
    tz.zip_pref_state AS color_group,
    p.pop_total >= quantile_cont(p.pop_total, 0.85) OVER () AS label_flag,
    zp.lon,
    zp.lat
  FROM gold.population_demographics p
  JOIN target_zctas tz
    ON p.geo_id = tz.geo_id
  JOIN zcta_points zp
    ON p.geo_id = zp.geo_id
  WHERE p.geo_level = 'zcta'
    AND p.year = (SELECT year FROM latest_year)
    AND p.pop_total IS NOT NULL
)
SELECT *
FROM zcta_base;
