with top_20 as (
    select
        geo_id,
        geo_name,
        pop_total,
        row_number() over (order by pop_total desc, geo_name asc) as pop_rank
    from gold.population_demographics
    where geo_level = 'cbsa'
      and year = 2023
      and pop_total is not null
    qualify pop_rank <= 20
),
base as (
    select
        t.geo_id,
        t.geo_name,
        t.pop_rank,
        h.year,
        h.vacancy_rate * 100.0 as metric_value
    from top_20 t
    join gold.housing_core_wide h
      on t.geo_id = h.geo_id
    where h.geo_level = 'cbsa'
      and h.year between 2015 and 2023
      and h.vacancy_rate is not null
),
ranks as (
    select
        *,
        row_number() over (partition by year order by metric_value asc, geo_name asc) as rank
    from base
),
endpoint_rank_change as (
    select
        geo_id,
        max(case when year = 2015 then rank end) as rank_2015,
        max(case when year = 2023 then rank end) as rank_2023
    from ranks
    group by 1
)
select
    'cbsa' as geo_level,
    r.geo_id,
    r.geo_name,
    cast(r.year as varchar) as period,
    'vacancy_rate' as metric_id,
    'Vacancy rate (%)' as metric_label,
    r.metric_value,
    r.rank,
    abs(e.rank_2015 - e.rank_2023) >= 3 as highlight_flag,
    false as peer_flag,
    'Top 20 CBSAs by 2023 population' as "group",
    'gold.population_demographics + gold.housing_core_wide' as source,
    '2026-07-12' as vintage,
    'Fixed top-20 metro universe based on 2023 population. Rank 1 means the lowest vacancy rate in that year, so upward movement indicates tighter housing conditions.' as note
from ranks r
join endpoint_rank_change e
  on r.geo_id = e.geo_id
order by r.pop_rank, r.year;
