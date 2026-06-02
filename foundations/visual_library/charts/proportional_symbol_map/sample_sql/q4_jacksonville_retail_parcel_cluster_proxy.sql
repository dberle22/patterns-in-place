WITH params AS (
  SELECT '27260'::VARCHAR AS cbsa_code
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM foundation.tract_features
  WHERE cbsa_code = (SELECT cbsa_code FROM params)
),
tract_scores AS (
  SELECT
    t.*,
    (
      0.30 * COALESCE(t.pop_growth_pctl, 0) +
      0.25 * COALESCE(t.density_pctl, 0) +
      0.25 * COALESCE(t.price_proxy_pctl, 0) +
      0.20 * COALESCE(t.income_pctl, 0)
    ) AS target_zone_score
  FROM foundation.tract_features t
  WHERE t.cbsa_code = (SELECT cbsa_code FROM params)
    AND t.year = (SELECT year FROM latest_year)
    AND t.pop_total IS NOT NULL
    AND t.pop_density IS NOT NULL
),
tract_base AS (
  SELECT
    'bubble_retail_parcel_clusters' AS question_id,
    'tract' AS geo_level,
    s.tract_geoid AS geo_id,
    'Tract ' || s.tract_geoid AS geo_name,
    CAST(s.year AS VARCHAR) || '_snapshot' AS time_window,
    s.pop_total AS size_value,
    'Population in retail target-zone proxy tract' AS size_label,
    'foundation.tract_features + foundation.market_tract_geometry' AS source,
    CAST(s.year AS VARCHAR) AS vintage,
    CASE
      WHEN s.eligible_v1 = 1 THEN 'Eligible target-zone tract'
      ELSE 'Context tract'
    END AS color_group,
    s.eligible_v1 = 1 AS highlight_flag,
    s.target_zone_score >= quantile_cont(s.target_zone_score, 0.92) OVER () AS label_flag,
    ST_X(ST_PointOnSurface(ST_GeomFromText(g.geom_wkt))) AS lon,
    ST_Y(ST_PointOnSurface(ST_GeomFromText(g.geom_wkt))) AS lat,
    s.target_zone_score,
    'Parcel-level retail clusters are not yet materialized in DuckDB; this sample uses high-scoring Jacksonville tracts as the target-zone proxy.' AS note
  FROM tract_scores s
  JOIN foundation.market_tract_geometry g
    ON s.tract_geoid = g.tract_geoid
),
ranked AS (
  SELECT
    *,
    quantile_cont(target_zone_score, 0.75) OVER () AS target_zone_score_q75
  FROM tract_base
)
SELECT *
FROM ranked
WHERE highlight_flag
   OR target_zone_score >= target_zone_score_q75;
