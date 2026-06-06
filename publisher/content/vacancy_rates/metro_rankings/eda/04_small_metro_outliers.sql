-- EDA 04: inspect the highest-vacancy small CBSAs excluded by the 250k+
-- filter to confirm whether the cutoff is removing distorted seasonal markets.

with cbsa_2024 as (
  select
    h.geo_name,
    p.pop_total,
    h.hu_total,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  join gold.population_demographics p
    on h.geo_level = p.geo_level
   and h.geo_id = p.geo_id
   and h.year = p.year
  where h.geo_level = 'cbsa'
    and h.year = 2024
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
)
select
  geo_name,
  round(pop_total, 0) as pop_total,
  round(hu_total, 0) as hu_total,
  round(vacancy_rate_pct, 1) as vacancy_rate_pct
from cbsa_2024
where pop_total < 250000
order by vacancy_rate_pct desc, pop_total desc
limit 15;
