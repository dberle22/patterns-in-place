-- Q3: Within the target CBSA, do ZCTAs show a long tail of high commute intensity?

WITH target_cbsa AS (
  SELECT '48900'::VARCHAR AS target_geo_id, 'Wilmington, NC'::VARCHAR AS target_name
),
latest_year AS (
  SELECT MAX(year) AS year
  FROM gold.transport_built_form_wide
  WHERE geo_level = 'zcta'
    AND mean_travel_time IS NOT NULL
),
target_zctas AS (
  SELECT
    zc.zip_geoid AS geo_id,
    MIN(cc.county_name) AS county_name
  FROM silver.xwalk_zcta_county zc
  JOIN silver.xwalk_cbsa_county cc
    ON zc.county_geoid = cc.county_geoid
  WHERE cc.cbsa_code = (SELECT target_geo_id FROM target_cbsa)
  GROUP BY 1
),
ranked AS (
  SELECT
    t.*,
    tz.county_name,
    (
      t.mean_travel_time *
      (COALESCE(t.pct_commute_drive_alone, 0) + COALESCE(t.pct_commute_carpool, 0))
    ) AS commute_intensity_proxy,
    ROW_NUMBER() OVER (
      ORDER BY
        t.mean_travel_time *
        (COALESCE(t.pct_commute_drive_alone, 0) + COALESCE(t.pct_commute_carpool, 0)) DESC,
        t.geo_id
    ) AS tail_rank
  FROM gold.transport_built_form_wide t
  JOIN target_zctas tz
    ON t.geo_id = tz.geo_id
  WHERE t.geo_level = 'zcta'
    AND t.year = (SELECT year FROM latest_year)
    AND t.mean_travel_time IS NOT NULL
)
SELECT
  'boxplot_target_cbsa_zcta_commute_tail'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  '2024_snapshot'::VARCHAR AS time_window,
  'commute_intensity_proxy'::VARCHAR AS metric_id,
  'Commute intensity proxy'::VARCHAR AS metric_label,
  commute_intensity_proxy::DOUBLE AS metric_value,
  county_name AS "group",
  tail_rank <= 3 AS highlight_flag,
  tail_rank <= 3 AS label_flag,
  NULL::DOUBLE AS weight_value,
  NULL::DOUBLE AS benchmark_value,
  'gold.transport_built_form_wide + silver.xwalk_zcta_county + silver.xwalk_cbsa_county'::VARCHAR AS source,
  CAST(year AS VARCHAR) AS vintage,
  'Target CBSA is Wilmington, NC; highlighted ZCTAs are the three highest commute-intensity proxy observations. Proxy = mean travel time multiplied by drive-alone plus carpool commute share.'::VARCHAR AS note
FROM ranked;
