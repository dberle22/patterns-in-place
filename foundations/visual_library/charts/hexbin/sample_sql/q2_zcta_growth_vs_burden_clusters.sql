-- Q2: Are there distinct clusters with both high growth and high rent burden?

WITH region_lookup AS (
  SELECT
    zc.zip_geoid AS geo_id,
    MIN(sr.census_region) AS census_region
  FROM metro_deep_dive.silver.xwalk_zcta_county zc
  LEFT JOIN metro_deep_dive.silver.xwalk_county_state cs
    ON zc.county_geoid = cs.county_geoid
  LEFT JOIN metro_deep_dive.silver.xwalk_state_region sr
    ON cs.state_fip = sr.state_fips
  GROUP BY 1
),
base AS (
  SELECT
    p.geo_level,
    p.geo_id,
    p.geo_name,
    '2018_to_2023_growth'::VARCHAR AS time_window,
    p.pop_growth_5yr * 100.0 AS x_value,
    a.pct_rent_burden_30plus::DOUBLE AS y_value,
    'Population Growth (5Y, %)'::VARCHAR AS x_label,
    'Rent-Burdened Households (2023, %)'::VARCHAR AS y_label,
    rl.census_region AS "group",
    a.pop_total::DOUBLE AS pop_total
  FROM metro_deep_dive.gold.population_demographics p
  JOIN metro_deep_dive.gold.affordability_wide a
    ON p.geo_level = a.geo_level
   AND p.geo_id = a.geo_id
   AND p.year = a.year
  LEFT JOIN region_lookup rl
    ON p.geo_id = rl.geo_id
  WHERE p.geo_level = 'zcta'
    AND p.year = 2023
    AND p.pop_growth_5yr IS NOT NULL
    AND a.pct_rent_burden_30plus IS NOT NULL
),
thresholds AS (
  SELECT
    quantile_cont(x_value, 0.975) AS x_cut,
    quantile_cont(y_value, 0.975) AS y_cut
  FROM base
),
flagged AS (
  SELECT
    b.*,
    b.x_value >= t.x_cut AND b.y_value >= t.y_cut AS hotspot_flag
  FROM base b
  CROSS JOIN thresholds t
),
ranked AS (
  SELECT
    f.*,
    CASE
      WHEN f.hotspot_flag THEN
        ROW_NUMBER() OVER (
          PARTITION BY f.hotspot_flag
          ORDER BY f.pop_total DESC, f.y_value DESC, f.x_value DESC
        )
      ELSE NULL
    END AS hotspot_rank
  FROM flagged f
)
SELECT
  'hexbin_growth_vs_burden_clusters'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  x_value,
  y_value,
  x_label,
  y_label,
  "group",
  NULL::DOUBLE AS weight_value,
  COALESCE(hotspot_rank <= 4, FALSE) AS highlight_flag,
  'gold.population_demographics + gold.affordability_wide + silver.xwalk_zcta_county + silver.xwalk_county_state + silver.xwalk_state_region'::VARCHAR AS source,
  '2026-04-15'::VARCHAR AS vintage,
  CASE
    WHEN hotspot_rank <= 4 THEN 'Highlighted from the extreme high-growth / high-burden tail.'
    ELSE NULL
  END AS note
FROM ranked;
