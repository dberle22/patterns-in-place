-- How New York Stacks Up: one tidy row per metric x geography.
-- Parameters (replaced in the notebook):
--   __DOWNSTATE__  seed column that defines Downstate (downstate_core | downstate_mta | downstate_redc)
--   __SEED_PATH__  path to foundations/etl/reference/ny_county_regions.csv
-- Downstate and Rest of State are built from counties. NY Total and US are the published figures.
-- Median age and median household income are pooled from bins in the notebook
-- (sql/benchmark_median_bins.sql), so they appear here only as published NY / US rows.
-- state_rank: NY's rank among the 50 states (1 = highest; DC and PR excluded), on NY Total rows only.

WITH seed AS (
  SELECT
    county_geoid,
    CASE WHEN __DOWNSTATE__ THEN 'Downstate' ELSE 'Rest of State' END AS geography
  FROM read_csv('__SEED_PATH__', types = {'county_geoid': 'VARCHAR'})
),

-- County building blocks ---------------------------------------------------
county_pop AS (
  SELECT s.geography, p.year, SUM(p.pop_total) AS pop
  FROM gold.population_demographics AS p
  JOIN seed AS s ON s.county_geoid = p.geo_id
  WHERE p.geo_level = 'county' AND p.year IN (2012, 2024)
  GROUP BY ALL
),
county_fb AS (
  SELECT s.geography, SUM(m.pop_foreign_born) AS fb, SUM(m.pop_foreign_born + m.pop_native) AS base
  FROM gold.migration_wide AS m
  JOIN seed AS s ON s.county_geoid = m.geo_id
  WHERE m.geo_level = 'county' AND m.year = 2024
  GROUP BY ALL
),
county_gdp AS (
  SELECT s.geography, SUM(g.nominal_gdp_total) AS gdp, SUM(g.pop_total) AS pop
  FROM gold.economics_gdp_wide AS g
  JOIN seed AS s ON s.county_geoid = g.geo_id
  WHERE g.geo_level = 'county' AND g.year = 2023
  GROUP BY ALL
),

-- State and US figures ------------------------------------------------------
-- One row per state (50 + DC) and the US, metric values side by side.
states AS (
  SELECT
    p.geo_id,
    CASE WHEN lower(p.geo_level) = 'us' THEN 'US' ELSE 'state' END AS level,
    p.pop_total AS population,
    p.median_age,
    m.pct_foreign_born AS foreign_born_share,
    i.median_hh_income,
    p.pop_total / p12.pop_total - 1 AS pop_growth
  FROM gold.population_demographics AS p
  JOIN gold.population_demographics AS p12
    ON p12.geo_level = p.geo_level AND p12.geo_id = p.geo_id AND p12.year = 2012
  LEFT JOIN gold.migration_wide AS m
    ON lower(m.geo_level) = lower(p.geo_level) AND m.geo_id = p.geo_id AND m.year = 2024
  LEFT JOIN gold.economics_income_wide AS i
    ON lower(i.geo_level) = lower(p.geo_level) AND i.geo_id = p.geo_id AND i.year = 2024
  WHERE p.year = 2024
    AND (p.geo_level = 'state' AND p.geo_id NOT IN ('72') OR lower(p.geo_level) = 'us')
),
state_gdp AS (
  SELECT geo_id, nominal_gdp_total AS gdp, pop_total AS pop
  FROM gold.economics_gdp_wide
  WHERE geo_level = 'state' AND year = 2023 AND geo_id NOT IN ('72')
),
-- The gold US row has no GDP, so the US is the sum of the 50 states and DC.
gdp_pc AS (
  SELECT geo_id, 'state' AS level, gdp / pop AS gdp_per_capita FROM state_gdp
  UNION ALL
  SELECT '1', 'US', SUM(gdp) / SUM(pop) FROM state_gdp
),
published_long AS (
  UNPIVOT (
    SELECT s.geo_id, s.level, s.population, s.median_age, s.foreign_born_share,
           s.median_hh_income, s.pop_growth, g.gdp_per_capita
    FROM states AS s
    LEFT JOIN gdp_pc AS g ON g.geo_id = s.geo_id AND g.level = s.level
  )
  ON population, median_age, foreign_born_share, median_hh_income, pop_growth, gdp_per_capita
  INTO NAME metric_id VALUE value
),
ranked AS (
  SELECT
    *,
    CASE WHEN level = 'state' AND geo_id <> '11'
      THEN RANK() OVER (PARTITION BY metric_id, (level = 'state' AND geo_id <> '11') ORDER BY value DESC)
    END AS state_rank
  FROM published_long
),

-- Tidy rows -----------------------------------------------------------------
rows AS (
  -- Downstate / Rest of State, built from counties
  SELECT geography, 'population' AS metric_id, 2024 AS year, pop AS value, 'sum' AS method,
         NULL::INTEGER AS state_rank
  FROM county_pop WHERE year = 2024
  UNION ALL
  SELECT geography, 'foreign_born_share', 2024, fb / base, 'ratio_of_sums', NULL FROM county_fb
  UNION ALL
  SELECT geography, 'gdp_per_capita', 2023, gdp / pop, 'ratio_of_sums', NULL FROM county_gdp
  UNION ALL
  SELECT p24.geography, 'pop_growth', 2024, p24.pop / p12.pop - 1, 'ratio_of_sums', NULL
  FROM county_pop AS p24
  JOIN county_pop AS p12 ON p12.geography = p24.geography AND p12.year = 2012
  WHERE p24.year = 2024
  UNION ALL
  -- NY Total and US, published
  SELECT
    CASE WHEN level = 'US' THEN 'US' ELSE 'NY Total' END,
    metric_id,
    CASE WHEN metric_id = 'gdp_per_capita' THEN 2023 ELSE 2024 END,
    value,
    CASE WHEN metric_id = 'gdp_per_capita' AND level = 'US' THEN 'sum_of_states' ELSE 'published' END,
    state_rank
  FROM ranked
  WHERE geo_id = '36' OR level = 'US'
)

SELECT
  m.lens,
  r.metric_id,
  m.metric_label,
  r.geography,
  r.year,
  r.value,
  r.state_rank,
  CASE WHEN r.state_rank IS NOT NULL THEN 50 END AS rank_of,
  '__DOWNSTATE__' AS downstate_definition,
  r.method,
  m.metric_order
FROM rows AS r
JOIN (
  VALUES
    ('Who Lives Here', 'population', 'Population', 1),
    ('Who Lives Here', 'median_age', 'Median age', 2),
    ('Who Lives Here', 'foreign_born_share', 'Foreign-born share', 3),
    ('What People Do Here', 'median_hh_income', 'Median household income', 4),
    ('What People Do Here', 'gdp_per_capita', 'GDP per capita', 5),
    ('Where It''s Headed', 'pop_growth', 'Population growth, 2012–2024', 6)
) AS m (lens, metric_id, metric_label, metric_order)
  ON m.metric_id = r.metric_id
ORDER BY m.metric_order, CASE r.geography WHEN 'Downstate' THEN 1 WHEN 'Rest of State' THEN 2 WHEN 'NY Total' THEN 3 ELSE 4 END
