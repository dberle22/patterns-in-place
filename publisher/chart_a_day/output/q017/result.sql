with top_15 as (
    select
        geo_id,
        geo_name,
        pop_total,
        row_number() over (order by pop_total desc, geo_name asc) as pop_rank
    from gold.population_demographics
    where geo_level = 'cbsa'
      and year = 2023
      and pop_total is not null
    qualify pop_rank <= 15
),
metro_values as (
    select
        t.geo_id,
        t.geo_name,
        t.pop_rank,
        h.year,
        h.rent_to_income * 100.0 as metric_value
    from top_15 t
    join gold.housing_core_wide h
      on t.geo_id = h.geo_id
    where h.geo_level = 'cbsa'
      and h.year in (2018, 2023)
      and h.rent_to_income is not null
),
endpoint_delta as (
    select
        geo_id,
        max(case when year = 2018 then metric_value end) as value_2018,
        max(case when year = 2023 then metric_value end) as value_2023
    from metro_values
    group by 1
)
select
    'cbsa' as geo_level,
    mv.geo_id,
    mv.geo_name,
    cast(mv.year as varchar) as period,
    'rent_to_income' as metric_id,
    'Rent-to-income ratio (%)' as metric_label,
    mv.metric_value,
    d.value_2023 - d.value_2018 as delta_value,
    d.value_2023 < d.value_2018 as highlight_flag,
    'Top 15 CBSAs by 2023 population' as "group",
    'gold.population_demographics + gold.housing_core_wide' as source,
    '2026-07-12' as vintage,
    'Exactly two periods are shown: 2018 and 2023. Metros with a lower 2023 rent-to-income ratio than 2018 are highlighted as rare affordability improvements.' as note
from metro_values mv
join endpoint_delta d
  on mv.geo_id = d.geo_id
order by mv.pop_rank, mv.year;
