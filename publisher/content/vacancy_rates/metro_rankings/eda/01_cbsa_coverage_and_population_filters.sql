-- EDA 01: confirm 2024 CBSA coverage and show how population cutoffs change
-- the ranking universe.

with cbsa_2024 as (
  select
    h.geo_id,
    h.geo_name,
    h.hu_total,
    h.vacancy_rate,
    p.pop_total
  from gold.housing_core_wide h
  left join gold.population_demographics p
    on h.geo_level = p.geo_level
   and h.geo_id = p.geo_id
   and h.year = p.year
  where h.geo_level = 'cbsa'
    and h.year = 2024
),
cbsa_2024_finite as (
  select
    geo_id,
    geo_name,
    hu_total,
    pop_total,
    vacancy_rate * 100 as vacancy_rate_pct
  from cbsa_2024
  where vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
)
select
  'coverage'::varchar as section,
  'all_cbsa_2024'::varchar as pop_bucket,
  count(*) as metros,
  count_if(vacancy_rate is null) as null_vacancy_rows,
  count_if(vacancy_rate is not null and isnan(vacancy_rate)) as nan_vacancy_rows,
  count_if(vacancy_rate is not null and isinf(vacancy_rate)) as inf_vacancy_rows,
  count_if(hu_total is null) as null_hu_rows,
  count_if(pop_total is null) as null_pop_rows,
  round(min(pop_total), 0) as min_pop,
  round(max(pop_total), 0) as max_pop,
  null::double as min_vacancy_pct,
  null::double as median_vacancy_pct,
  null::double as avg_vacancy_pct,
  null::double as max_vacancy_pct
from cbsa_2024

union all

select
  'distribution'::varchar as section,
  'all'::varchar as pop_bucket,
  count(*) as metros,
  null::bigint as null_vacancy_rows,
  null::bigint as nan_vacancy_rows,
  null::bigint as inf_vacancy_rows,
  null::bigint as null_hu_rows,
  null::bigint as null_pop_rows,
  null::double as min_pop,
  null::double as max_pop,
  round(min(vacancy_rate_pct), 1) as min_vacancy_pct,
  round(percentile_cont(0.5) within group (order by vacancy_rate_pct), 1)
    as median_vacancy_pct,
  round(avg(vacancy_rate_pct), 1) as avg_vacancy_pct,
  round(max(vacancy_rate_pct), 1) as max_vacancy_pct
from cbsa_2024_finite

union all

select
  'distribution'::varchar as section,
  '250k+'::varchar as pop_bucket,
  count(*) as metros,
  null::bigint as null_vacancy_rows,
  null::bigint as nan_vacancy_rows,
  null::bigint as inf_vacancy_rows,
  null::bigint as null_hu_rows,
  null::bigint as null_pop_rows,
  null::double as min_pop,
  null::double as max_pop,
  round(min(vacancy_rate_pct), 1) as min_vacancy_pct,
  round(percentile_cont(0.5) within group (order by vacancy_rate_pct), 1)
    as median_vacancy_pct,
  round(avg(vacancy_rate_pct), 1) as avg_vacancy_pct,
  round(max(vacancy_rate_pct), 1) as max_vacancy_pct
from cbsa_2024_finite
where pop_total >= 250000

union all

select
  'distribution'::varchar as section,
  '500k+'::varchar as pop_bucket,
  count(*) as metros,
  null::bigint as null_vacancy_rows,
  null::bigint as nan_vacancy_rows,
  null::bigint as inf_vacancy_rows,
  null::bigint as null_hu_rows,
  null::bigint as null_pop_rows,
  null::double as min_pop,
  null::double as max_pop,
  round(min(vacancy_rate_pct), 1) as min_vacancy_pct,
  round(percentile_cont(0.5) within group (order by vacancy_rate_pct), 1)
    as median_vacancy_pct,
  round(avg(vacancy_rate_pct), 1) as avg_vacancy_pct,
  round(max(vacancy_rate_pct), 1) as max_vacancy_pct
from cbsa_2024_finite
where pop_total >= 500000

union all

select
  'distribution'::varchar as section,
  '1m+'::varchar as pop_bucket,
  count(*) as metros,
  null::bigint as null_vacancy_rows,
  null::bigint as nan_vacancy_rows,
  null::bigint as inf_vacancy_rows,
  null::bigint as null_hu_rows,
  null::bigint as null_pop_rows,
  null::double as min_pop,
  null::double as max_pop,
  round(min(vacancy_rate_pct), 1) as min_vacancy_pct,
  round(percentile_cont(0.5) within group (order by vacancy_rate_pct), 1)
    as median_vacancy_pct,
  round(avg(vacancy_rate_pct), 1) as avg_vacancy_pct,
  round(max(vacancy_rate_pct), 1) as max_vacancy_pct
from cbsa_2024_finite
where pop_total >= 1000000

order by section, pop_bucket;
