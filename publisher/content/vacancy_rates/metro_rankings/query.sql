-- Top 20 tightest major metros by 2024 housing vacancy rate.
-- Major metros are defined as CBSAs with population >= 250,000.

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
    'metro_rankings'::varchar as question_id,
    geo_level,
    geo_id,
    geo_name,
    '2024 level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    vacancy_rate_pct as metric_value,
    'gold.housing_core_wide; gold.population_demographics'::varchar as source,
    '2026-05-14'::varchar as vintage,
    row_number() over (order by vacancy_rate_pct asc, pop_total desc, geo_name) as rank,
    'Top 20 major metros by tightness (population >= 250k)'::varchar as "group",
    null::varchar as series,
    null::double as share_value,
    false as highlight_flag,
    (select us_vacancy_pct from us_2024)::double as benchmark_value,
    'Population filter removes small seasonal outliers.'::varchar as note
  from major_cbsa_2024
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
from ranked
where rank <= 20
order by rank, geo_name;
