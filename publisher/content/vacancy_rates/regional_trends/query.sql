-- Regional vacancy trend line chart
-- Five series:
--   1. True US vacancy rate from geo_level = 'us'
--   2. Four Census region vacancy-rate series from geo_level = 'region'

with us_series as (
  select
    'regional_trends'::varchar as question_id,
    geo_level,
    '1'::varchar as geo_id,
    'United States'::varchar as geo_name,
    year as period,
    'level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    vacancy_rate * 100 as metric_value,
    'gold.housing_core_wide'::varchar as source,
    '2026-05-16'::varchar as vintage,
    'National benchmark'::varchar as "group",
    true as highlight_flag,
    null::double as benchmark_value,
    null::integer as index_base_period,
    'True US vacancy-rate series.'::varchar as note
  from gold.housing_core_wide
  where geo_level = 'us'
    and year between 2014 and 2024
    and vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
),
region_series as (
  select
    'regional_trends'::varchar as question_id,
    geo_level,
    geo_id,
    case geo_name
      when 'Northeast Region' then 'Northeast'
      when 'Midwest Region' then 'Midwest'
      when 'South Region' then 'South'
      when 'West Region' then 'West'
      else geo_name
    end::varchar as geo_name,
    year as period,
    'level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    vacancy_rate * 100 as metric_value,
    'gold.housing_core_wide'::varchar as source,
    '2026-05-16'::varchar as vintage,
    'Census region'::varchar as "group",
    false as highlight_flag,
    null::double as benchmark_value,
    null::integer as index_base_period,
    'Regional vacancy-rate series.'::varchar as note
  from gold.housing_core_wide
  where geo_level = 'region'
    and year between 2014 and 2024
    and vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
)
select *
from us_series

union all

select *
from region_series

order by highlight_flag desc, geo_name, period;
