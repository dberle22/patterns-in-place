-- EDA 03: summarize the 2024 vacancy-rate distribution for major metros and
-- compare it with the national benchmark.

with us_2024 as (
  select vacancy_rate * 100 as us_vacancy_pct
  from gold.housing_core_wide
  where geo_level = 'us'
    and year = 2024
),
cbsa_2024 as (
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
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
major_cbsa_2024 as (
  select *
  from cbsa_2024
  where pop_total >= 250000
)
select
  count(*) as metros_250k,
  round(min(vacancy_rate_pct), 1) as min_pct,
  round(percentile_cont(0.10) within group (order by vacancy_rate_pct), 1)
    as p10_pct,
  round(percentile_cont(0.25) within group (order by vacancy_rate_pct), 1)
    as p25_pct,
  round(percentile_cont(0.50) within group (order by vacancy_rate_pct), 1)
    as median_pct,
  round(avg(vacancy_rate_pct), 1) as avg_pct,
  round(percentile_cont(0.75) within group (order by vacancy_rate_pct), 1)
    as p75_pct,
  round(percentile_cont(0.90) within group (order by vacancy_rate_pct), 1)
    as p90_pct,
  round(max(vacancy_rate_pct), 1) as max_pct,
  round((select us_vacancy_pct from us_2024), 1) as us_vacancy_pct,
  count_if(vacancy_rate_pct < (select us_vacancy_pct from us_2024))
    as tighter_than_us_count,
  count_if(vacancy_rate_pct >= (select us_vacancy_pct from us_2024))
    as looser_than_us_count,
  round(avg(vacancy_rate_pct - (select us_vacancy_pct from us_2024)), 1)
    as avg_gap_vs_us_pp,
  round(
    sum(hu_total * vacancy_rate_pct) / nullif(sum(hu_total), 0),
    1
  ) as housing_unit_weighted_cbsa_pct
from major_cbsa_2024;
