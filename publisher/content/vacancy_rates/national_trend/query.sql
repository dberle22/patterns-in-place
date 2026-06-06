-- National vacancy trend line chart
-- Two series:
--   1. True US vacancy rate from geo_level = 'us'
--   2. Housing-unit-weighted CBSA vacancy rate for comparison

with us_series as (
  select
    'national_trend'::varchar as question_id,
    geo_level,
    geo_id,
    geo_name,
    year as period,
    'level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    vacancy_rate * 100 as metric_value,
    'gold.housing_core_wide'::varchar as source,
    '2026-05-13'::varchar as vintage,
    'National'::varchar as "group",
    true as highlight_flag,
    null::double as benchmark_value,
    null::integer as index_base_period,
    'US headline series'::varchar as note
  from gold.housing_core_wide
  where geo_level = 'us'
    and year between 2012 and 2024
    and vacancy_rate is not null
),
cbsa_weighted_series as (
  select
    'national_trend'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    'weighted_cbsa'::varchar as geo_id,
    'US Metro Average (Weighted)'::varchar as geo_name,
    year as period,
    'level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    sum(hu_total * vacancy_rate) / nullif(sum(hu_total), 0) * 100 as metric_value,
    'gold.housing_core_wide'::varchar as source,
    '2026-05-13'::varchar as vintage,
    'Metro benchmark'::varchar as "group",
    false as highlight_flag,
    null::double as benchmark_value,
    null::integer as index_base_period,
    'Housing-unit-weighted CBSA rollup'::varchar as note
  from gold.housing_core_wide
  where geo_level = 'cbsa'
    and year between 2012 and 2024
    and vacancy_rate is not null
    and hu_total is not null
  group by year
)
select *
from us_series

union all

select *
from cbsa_weighted_series

order by highlight_flag desc, geo_id, period;
