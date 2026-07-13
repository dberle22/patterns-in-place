-- How has the vacancy rate trended nationally since 2015?
-- This is the simplest CE trend proof point: one national series, annual
-- values only, no peer comparison layer, and a clean 2015+ window.

select
  'q006'::varchar as question_id,
  geo_level,
  geo_id,
  geo_name,
  year as period,
  '2015_2024_level'::varchar as time_window,
  'vacancy_rate'::varchar as metric_id,
  'Vacancy rate'::varchar as metric_label,
  vacancy_rate * 100 as metric_value,
  'gold.housing_core_wide'::varchar as source,
  '2026-07-12'::varchar as vintage,
  'National vacancy trend'::varchar as "group",
  'United States'::varchar as series,
  true as highlight_flag,
  null::double as benchmark_value,
  null::integer as index_base_period,
  'True national vacancy-rate series from the US row in gold.housing_core_wide.'::varchar as note
from gold.housing_core_wide
where geo_level = 'us'
  and year between 2015 and 2024
  and vacancy_rate is not null
  and not isnan(vacancy_rate)
  and not isinf(vacancy_rate)
order by period;
