with universe as (
  select
    d.geo_level,
    d.geo_id,
    d.geo_name,
    d.year,
    d.pop_total,
    d.pop_growth_5yr,
    h.rent_to_income,
    h.vacancy_rate,
    i.income_pc_growth_5yr
  from gold.population_demographics d
  join gold.housing_core_wide h
    using (geo_level, geo_id, geo_name, year)
  join gold.economics_income_wide i
    using (geo_level, geo_id, geo_name, year)
  where d.geo_level = 'cbsa'
    and d.year = 2023
    and d.pop_total > 250000
)
select
  'q022' as question_id,
  geo_level,
  geo_id,
  geo_name,
  '2023_cross_section' as time_window,
  metric_id,
  metric_label,
  metric_value,
  true as include_flag,
  'Patterns in Place gold tables: population_demographics, housing_core_wide, economics_income_wide' as source,
  '2023' as vintage,
  'All CBSAs with 2023 population above 250k. Spearman correlation is calculated downstream on the long metric frame.' as note
from (
  select geo_level, geo_id, geo_name, 'rent_to_income' as metric_id, 'Rent-to-income ratio' as metric_label, rent_to_income as metric_value from universe
  union all
  select geo_level, geo_id, geo_name, 'vacancy_rate' as metric_id, 'Vacancy rate' as metric_label, vacancy_rate as metric_value from universe
  union all
  select geo_level, geo_id, geo_name, 'income_pc_growth_5yr' as metric_id, 'Per capita income growth (5y)' as metric_label, income_pc_growth_5yr as metric_value from universe
  union all
  select geo_level, geo_id, geo_name, 'pop_growth_5yr' as metric_id, 'Population growth (5y)' as metric_label, pop_growth_5yr as metric_value from universe
) metrics
where metric_value is not null
order by geo_name, metric_id;
