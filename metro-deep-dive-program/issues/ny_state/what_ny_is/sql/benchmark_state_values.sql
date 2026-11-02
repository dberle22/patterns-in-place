-- The 50 states' values on the six benchmark metrics (DC and PR excluded), one row per state x metric.
-- Same definitions and years as benchmark_stack_up.sql. The notebook ranks Downstate and Rest of State
-- against the 49 states other than NY, "as if" each replaced New York (1 = highest, of 50).
WITH states AS (
  SELECT
    p.geo_id,
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
  WHERE p.year = 2024 AND p.geo_level = 'state' AND p.geo_id NOT IN ('11', '72')
),
gdp_pc AS (
  SELECT geo_id, nominal_gdp_total / pop_total AS gdp_per_capita
  FROM gold.economics_gdp_wide
  WHERE geo_level = 'state' AND year = 2023 AND geo_id NOT IN ('11', '72')
)
UNPIVOT (
  SELECT s.geo_id, s.population, s.median_age, s.foreign_born_share,
         s.median_hh_income, s.pop_growth, g.gdp_per_capita
  FROM states AS s
  LEFT JOIN gdp_pc AS g ON g.geo_id = s.geo_id
)
ON population, median_age, foreign_born_share, median_hh_income, pop_growth, gdp_per_capita
INTO NAME metric_id VALUE value
ORDER BY metric_id, geo_id
