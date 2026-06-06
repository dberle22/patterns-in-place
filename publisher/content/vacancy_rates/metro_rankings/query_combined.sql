-- Combined chart: 10 tightest major metros, the national average, and
-- 10 loosest major metros by 2024 housing vacancy rate.

with us_2024 as (
  select
    vacancy_rate * 100 as us_vacancy_pct
  from gold.housing_core_wide
  where geo_level = 'us'
    and year = 2024
),
allowed_cbsa as (
  select distinct
    cs.cbsa_code as geo_id
  from silver.xwalk_cbsa_state cs
  join silver.xwalk_state_region sr
    on cs.state_fips = sr.state_fips
),
major_cbsa_2024 as (
  select
    h.geo_level,
    h.geo_id,
    h.geo_name,
    p.pop_total,
    h.vacancy_rate * 100 as vacancy_rate_pct
  from gold.housing_core_wide h
  join gold.population_demographics p
    on h.geo_level = p.geo_level
   and h.geo_id = p.geo_id
   and h.year = p.year
  join allowed_cbsa a
    on h.geo_id = a.geo_id
  where h.geo_level = 'cbsa'
    and h.year = 2024
    and p.pop_total >= 250000
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
ranked as (
  select
    geo_level,
    geo_id,
    geo_name,
    pop_total,
    vacancy_rate_pct,
    row_number() over (order by vacancy_rate_pct asc, pop_total desc, geo_name) as tight_rank,
    row_number() over (order by vacancy_rate_pct desc, pop_total desc, geo_name) as loose_rank
  from major_cbsa_2024
),
tightest as (
  select
    'metro_rankings_combined'::varchar as question_id,
    geo_level,
    geo_id,
    geo_name,
    '2024 level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    vacancy_rate_pct as metric_value,
    'gold.housing_core_wide; gold.population_demographics'::varchar as source,
    '2026-05-14'::varchar as vintage,
    tight_rank as rank,
    'Tightest 10, national average, and loosest 10 major metros'::varchar as "group",
    'Tightest'::varchar as series,
    null::double as share_value,
    false as highlight_flag,
    null::double as benchmark_value,
    'Top 10 lowest vacancy-rate major metros.'::varchar as note
  from ranked
  where tight_rank <= 10
),
national as (
  select
    'metro_rankings_combined'::varchar as question_id,
    'us'::varchar as geo_level,
    'us'::varchar as geo_id,
    'United States'::varchar as geo_name,
    '2024 level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    us_vacancy_pct as metric_value,
    'gold.housing_core_wide'::varchar as source,
    '2026-05-14'::varchar as vintage,
    11 as rank,
    'Tightest 10, national average, and loosest 10 major metros'::varchar as "group",
    'National average'::varchar as series,
    null::double as share_value,
    true as highlight_flag,
    null::double as benchmark_value,
    'True national vacancy rate, not a CBSA average.'::varchar as note
  from us_2024
),
loosest as (
  select
    'metro_rankings_combined'::varchar as question_id,
    geo_level,
    geo_id,
    geo_name,
    '2024 level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    vacancy_rate_pct as metric_value,
    'gold.housing_core_wide; gold.population_demographics'::varchar as source,
    '2026-05-14'::varchar as vintage,
    11 + loose_rank as rank,
    'Tightest 10, national average, and loosest 10 major metros'::varchar as "group",
    'Loosest'::varchar as series,
    null::double as share_value,
    false as highlight_flag,
    null::double as benchmark_value,
    'Top 10 highest vacancy-rate major metros.'::varchar as note
  from ranked
  where loose_rank <= 10
)
select
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  metric_id,
  metric_label,
  metric_value,
  source,
  vintage,
  rank,
  "group",
  series,
  share_value,
  highlight_flag,
  benchmark_value,
  note
from tightest

union all

select
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  metric_id,
  metric_label,
  metric_value,
  source,
  vintage,
  rank,
  "group",
  series,
  share_value,
  highlight_flag,
  benchmark_value,
  note
from national

union all

select
  question_id,
  geo_level,
  geo_id,
  geo_name,
  time_window,
  metric_id,
  metric_label,
  metric_value,
  source,
  vintage,
  rank,
  "group",
  series,
  share_value,
  highlight_flag,
  benchmark_value,
  note
from loosest

order by metric_value asc, geo_name;
