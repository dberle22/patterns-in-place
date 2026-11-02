-- Age and household income bin counts for pooled medians, ACS 2020-24.
-- Parameters as in benchmark_stack_up.sql (__DOWNSTATE__, __SEED_PATH__).
-- Groups: Downstate, Rest of State, and all 62 counties ("NY counties") to check the
-- pooled method against the published NY median.
-- Bin edges come from the column names: 'under5' -> [0, 5), '22_24' -> [22, 25), '20' -> [20, 21),
-- '85_plus' -> [85, open); income 'lt10k' -> [0, 10000), '10k_15k' -> [10000, 15000), '200k_plus' -> open.

WITH seed AS (
  SELECT
    county_geoid,
    CASE WHEN __DOWNSTATE__ THEN 'Downstate' ELSE 'Rest of State' END AS geography
  FROM read_csv('__SEED_PATH__', types = {'county_geoid': 'VARCHAR'})
),
groups AS (
  SELECT county_geoid, geography FROM seed
  UNION ALL
  SELECT county_geoid, 'NY counties' FROM seed
),
age_long AS (
  UNPIVOT (
    SELECT geo_id, COLUMNS('^pop_age_(male|female)_.*E$')
    FROM silver.age_base
    WHERE geo_level = 'county' AND year = 2024 AND geo_id LIKE '36%'
  )
  ON COLUMNS('^pop_age_.*E$') INTO NAME col VALUE n
),
age_bins AS (
  SELECT
    geo_id,
    'median_age' AS metric_id,
    regexp_replace(col, '^pop_age_(male|female)_|E$', '', 'g') AS bin,
    n
  FROM age_long
),
income_long AS (
  UNPIVOT (
    SELECT geo_id, COLUMNS('^hh_inc_(lt|[0-9]).*E$')  -- bins only, not hh_inc_totalE
    FROM silver.income_base
    WHERE geo_level = 'county' AND year = 2024 AND geo_id LIKE '36%'
  )
  ON COLUMNS('^hh_inc_.*E$') INTO NAME col VALUE n
),
income_bins AS (
  SELECT geo_id, 'median_hh_income' AS metric_id, regexp_replace(col, '^hh_inc_|E$', '', 'g') AS bin, n
  FROM income_long
),
bins AS (
  SELECT * FROM age_bins
  UNION ALL
  SELECT * FROM income_bins
),
edges AS (
  SELECT DISTINCT
    metric_id,
    bin,
    -- Income bins are in thousands of dollars in the name.
    CASE WHEN metric_id = 'median_hh_income' THEN 1000 ELSE 1 END AS scale,
    CASE
      WHEN bin IN ('under5', 'lt10k') THEN 0
      ELSE CAST(regexp_extract(bin, '^(\d+)', 1) AS DOUBLE)
    END AS lower_raw,
    CASE
      WHEN bin LIKE '%plus' THEN NULL
      WHEN bin = 'under5' THEN 5
      WHEN bin = 'lt10k' THEN 10
      WHEN metric_id = 'median_hh_income' THEN CAST(regexp_extract(bin, '_(\d+)k$', 1) AS DOUBLE)
      -- Age bins name the last year in the bin, so the upper edge is one more.
      WHEN bin LIKE '%\_%' ESCAPE '\' THEN CAST(regexp_extract(bin, '_(\d+)$', 1) AS DOUBLE) + 1
      ELSE CAST(bin AS DOUBLE) + 1
    END AS upper_raw
  FROM bins
)

SELECT
  g.geography,
  b.metric_id,
  b.bin,
  e.lower_raw * e.scale AS bin_lower,
  e.upper_raw * e.scale AS bin_upper,
  SUM(b.n) AS n
FROM bins AS b
JOIN groups AS g ON g.county_geoid = b.geo_id
JOIN edges AS e ON e.metric_id = b.metric_id AND e.bin = b.bin
GROUP BY ALL
ORDER BY g.geography, b.metric_id, bin_lower
