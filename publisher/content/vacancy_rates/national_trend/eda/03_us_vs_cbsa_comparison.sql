-- EDA 03: compare the true US series against different CBSA rollups.
-- This helps decide whether a second "US metro average" line belongs in the
-- final chart.

with base as (
  select
    geo_level,
    year,
    vacancy_rate,
    hu_total,
    hu_total * vacancy_rate as vacant_units_est
  from gold.housing_core_wide
  where geo_level in ('us', 'cbsa')
    and vacancy_rate is not null
    and hu_total is not null
)
select
  year,
  round(max(case when geo_level = 'us' then vacancy_rate end) * 100, 1)
    as us_vacancy_rate_pct,
  round(
    avg(case when geo_level = 'cbsa' then vacancy_rate end) * 100,
    1
  ) as cbsa_unweighted_avg_pct,
  round(
    median(case when geo_level = 'cbsa' then vacancy_rate end) * 100,
    1
  ) as cbsa_median_pct,
  round(
    sum(case when geo_level = 'cbsa' then vacant_units_est end)
    / nullif(sum(case when geo_level = 'cbsa' then hu_total end), 0)
    * 100,
    1
  ) as cbsa_weighted_pct,
  count(case when geo_level = 'cbsa' then 1 end) as cbsa_count
from base
group by 1
order by 1;
