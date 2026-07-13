with cbsa_universe as (
  select
    hc.vacancy_rate
  from gold.population_demographics pd
  join gold.housing_core_wide hc
    on pd.geo_id = hc.geo_id
   and pd.geo_level = hc.geo_level
   and pd.year = hc.year
  where pd.geo_level = 'cbsa'
    and pd.year = 2023
    and pd.pop_total >= 250000
    and hc.vacancy_rate is not null
),
tiers as (
  select
    case
      when vacancy_rate < 0.04 then 'Very tight (<4%)'
      when vacancy_rate < 0.07 then 'Tight (4-7%)'
      when vacancy_rate < 0.10 then 'Balanced (7-10%)'
      else 'Loose (>10%)'
    end as component_label
  from cbsa_universe
),
counts as (
  select
    component_label,
    count(*) as metro_count,
    count(*) * 1.0 / sum(count(*)) over () as share_value
  from tiers
  group by 1
),
totals as (
  select sum(metro_count) as metro_total
  from counts
)
select
  'q020' as question_id,
  'US' as geo_level,
  '1' as geo_id,
  'United States' as geo_name,
  '2023' as time_window,
  'Share of large metros' as total_label,
  lower(replace(replace(component_label, ' ', '_'), '(', '')) as component_id,
  component_label,
  share_value as component_value,
  'share' as unit_label,
  'Vacancy tier' as component_group,
  case component_label
    when 'Very tight (<4%)' then 1
    when 'Tight (4-7%)' then 2
    when 'Balanced (7-10%)' then 3
    when 'Loose (>10%)' then 4
    else 99
  end as sort_order,
  'Vacancy tiers are computed across 2023 CBSAs with population >= 250k. Waterfall bars show each tier''s share of the 196-metro universe and sum to 100%.' as note,
  'gold.population_demographics + gold.housing_core_wide' as source,
  '2026-07-12' as vintage
from counts
cross join totals
order by sort_order asc;
