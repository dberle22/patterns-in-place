with metro_universe as (
  select
    pd.geo_id,
    dg.geo_name,
    hc.rent_to_income,
    hc.vacancy_rate,
    pd.pop_growth_5yr
  from gold.population_demographics pd
  join gold.housing_core_wide hc
    on pd.geo_id = hc.geo_id
   and pd.geo_level = hc.geo_level
   and pd.year = hc.year
  join gold.dim_geo dg
    on pd.geo_id = dg.geo_id
   and pd.geo_level = dg.geo_level
  where pd.geo_level = 'cbsa'
    and pd.year = 2023
    and pd.pop_total >= 250000
    and hc.rent_to_income is not null
    and hc.vacancy_rate is not null
    and pd.pop_growth_5yr is not null
),
ranked as (
  select
    geo_id,
    geo_name,
    'rent_to_income' as metric_id,
    'Rent-to-income ratio' as metric_label,
    'Housing stress' as metric_group,
    rent_to_income as metric_value,
    cume_dist() over (order by rent_to_income) * 100.0 as normalized_value
  from metro_universe

  union all

  select
    geo_id,
    geo_name,
    'vacancy_rate' as metric_id,
    'Vacancy rate' as metric_label,
    'Housing stress' as metric_group,
    vacancy_rate as metric_value,
    cume_dist() over (order by -vacancy_rate) * 100.0 as normalized_value
  from metro_universe

  union all

  select
    geo_id,
    geo_name,
    'pop_growth_5yr' as metric_id,
    '5-year population growth' as metric_label,
    'Demand pressure' as metric_group,
    pop_growth_5yr as metric_value,
    cume_dist() over (order by pop_growth_5yr) * 100.0 as normalized_value
  from metro_universe
),
shortlist as (
  select *
  from ranked
  where geo_name in (
    'Austin-Round Rock-San Marcos, TX',
    'Dallas-Fort Worth-Arlington, TX',
    'Phoenix-Mesa-Chandler, AZ',
    'Nashville-Davidson--Murfreesboro--Franklin, TN',
    'Charlotte-Concord-Gastonia, NC-SC',
    'Atlanta-Sandy Springs-Roswell, GA',
    'Tampa-St. Petersburg-Clearwater, FL',
    'Orlando-Kissimmee-Sanford, FL'
  )
)
select
  'q019' as question_id,
  'cbsa' as geo_level,
  geo_id,
  geo_name,
  metric_id,
  metric_label,
  metric_value,
  normalized_value,
  metric_group,
  '2023' as time_window,
  true as highlight_flag,
  case metric_id
    when 'rent_to_income' then format('{:.1f}%', metric_value * 100.0)
    when 'vacancy_rate' then format('{:.1f}%', metric_value * 100.0)
    when 'pop_growth_5yr' then format('{:.1f}%', metric_value * 100.0)
    else null
  end as cell_label,
  case geo_name
    when 'Austin-Round Rock-San Marcos, TX' then 8
    when 'Dallas-Fort Worth-Arlington, TX' then 7
    when 'Phoenix-Mesa-Chandler, AZ' then 6
    when 'Nashville-Davidson--Murfreesboro--Franklin, TN' then 5
    when 'Charlotte-Concord-Gastonia, NC-SC' then 4
    when 'Atlanta-Sandy Springs-Roswell, GA' then 3
    when 'Tampa-St. Petersburg-Clearwater, FL' then 2
    when 'Orlando-Kissimmee-Sanford, FL' then 1
    else 0
  end as row_order,
  case metric_id
    when 'rent_to_income' then 1
    when 'vacancy_rate' then 2
    when 'pop_growth_5yr' then 3
    else 99
  end as metric_order,
  'Stress percentile is computed within the 2023 CBSA universe with population >= 250k. Higher fill means more housing stress or demand pressure.' as note,
  'gold.population_demographics + gold.housing_core_wide + gold.dim_geo' as source,
  '2026-07-12' as vintage
from shortlist
order by row_order desc, metric_order asc;
