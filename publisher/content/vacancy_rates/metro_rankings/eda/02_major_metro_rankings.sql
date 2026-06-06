-- EDA 02: rank major metros (population >= 250k) by 2024 vacancy rate and
-- inspect both the tight and loose ends of the distribution.

with cbsa_2024 as (
  select
    h.geo_id,
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
    and p.pop_total >= 250000
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
ranked as (
  select
    geo_name,
    pop_total,
    hu_total,
    vacancy_rate_pct,
    row_number() over (order by vacancy_rate_pct asc, pop_total desc) as tight_rank,
    row_number() over (order by vacancy_rate_pct desc, pop_total desc) as loose_rank
  from cbsa_2024
)
select
  'tightest_15'::varchar as list_name,
  tight_rank as rank,
  geo_name,
  round(pop_total, 0) as pop_total,
  round(hu_total, 0) as hu_total,
  round(vacancy_rate_pct, 1) as vacancy_rate_pct
from ranked
where tight_rank <= 15

union all

select
  'loosest_15'::varchar as list_name,
  loose_rank as rank,
  geo_name,
  round(pop_total, 0) as pop_total,
  round(hu_total, 0) as hu_total,
  round(vacancy_rate_pct, 1) as vacancy_rate_pct
from ranked
where loose_rank <= 15

order by list_name, rank;
