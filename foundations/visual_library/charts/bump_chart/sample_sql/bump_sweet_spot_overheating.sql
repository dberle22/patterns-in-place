-- Q5: How did Sweet Spot markets shift in overheating risk rank over time?

WITH cbsa_base AS (
  SELECT
    a.geo_level,
    a.geo_id,
    a.geo_name,
    a.year,
    p.pop_growth_5yr,
    i.income_pc_growth_5yr,
    a.value_to_income,
    a.pct_rent_burden_30plus,
    a.permits_per_1000_population
  FROM metro_deep_dive.gold.affordability_wide a
  LEFT JOIN metro_deep_dive.gold.population_demographics p
    ON a.geo_level = p.geo_level
   AND a.geo_id = p.geo_id
   AND a.year = p.year
  LEFT JOIN metro_deep_dive.gold.economics_income_wide i
    ON a.geo_level = i.geo_level
   AND a.geo_id = i.geo_id
   AND a.year = i.year
  WHERE a.geo_level = 'cbsa'
    AND a.year BETWEEN 2018 AND 2023
    AND p.pop_growth_5yr IS NOT NULL
    AND i.income_pc_growth_5yr IS NOT NULL
    AND a.value_to_income IS NOT NULL
    AND a.pct_rent_burden_30plus IS NOT NULL
),
scored_all AS (
  SELECT
    *,
    100 * (
      0.40 * PERCENT_RANK() OVER (PARTITION BY year ORDER BY income_pc_growth_5yr) +
      0.30 * PERCENT_RANK() OVER (PARTITION BY year ORDER BY pop_growth_5yr) +
      0.30 * PERCENT_RANK() OVER (PARTITION BY year ORDER BY value_to_income DESC)
    ) AS sweet_spot_score,
    100 * (
      0.35 * PERCENT_RANK() OVER (PARTITION BY year ORDER BY pop_growth_5yr) +
      0.25 * PERCENT_RANK() OVER (PARTITION BY year ORDER BY income_pc_growth_5yr) +
      0.25 * PERCENT_RANK() OVER (PARTITION BY year ORDER BY value_to_income) +
      0.15 * PERCENT_RANK() OVER (PARTITION BY year ORDER BY pct_rent_burden_30plus)
    ) AS overheating_score
  FROM cbsa_base
),
sweet_spot_latest AS (
  SELECT geo_id
  FROM scored_all
  WHERE year = 2023
  ORDER BY sweet_spot_score DESC, geo_name, geo_id
  LIMIT 12
),
scored AS (
  SELECT *
  FROM scored_all
  WHERE geo_id IN (SELECT geo_id FROM sweet_spot_latest)
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY year ORDER BY overheating_score DESC, geo_name, geo_id) AS overheating_rank
  FROM scored
)
SELECT
  'bump_sweet_spot_overheating'::VARCHAR AS question_id,
  geo_level,
  geo_id,
  geo_name,
  year AS period,
  'overheating_score'::VARCHAR AS metric_id,
  'Overheating Risk Score'::VARCHAR AS metric_label,
  overheating_score::DOUBLE AS metric_value,
  'gold.affordability_wide + gold.population_demographics + gold.economics_income_wide'::VARCHAR AS source,
  '2026-04-16'::VARCHAR AS vintage,
  'Latest-year Sweet Spot CBSA set'::VARCHAR AS "group",
  geo_id = '48900' AS highlight_flag,
  TRUE AS peer_flag,
  overheating_rank::DOUBLE AS rank,
  'Sweet Spot set is defined from latest-year growth and affordability screens; risk rank is within that fixed set each year.'::VARCHAR AS note
FROM ranked
ORDER BY geo_name, year;
