with top_10 as (
    select
        geo_id,
        geo_name,
        pop_total,
        row_number() over (order by pop_total desc, geo_name asc) as pop_rank
    from gold.population_demographics
    where geo_level = 'cbsa'
      and year = 2023
      and pop_total is not null
    qualify pop_rank <= 10
)
select
    h.geo_level,
    h.geo_id,
    h.geo_name,
    cast(h.year as varchar) as period,
    '2018_2023_level' as time_window,
    'median_gross_rent' as metric_id,
    'Median gross rent ($)' as metric_label,
    h.median_gross_rent as metric_value,
    h.geo_name as series,
    t.pop_rank <= 3 as highlight_flag,
    'Top 10 CBSAs by 2023 population' as "group",
    'gold.housing_core_wide + gold.population_demographics' as source,
    '2026-07-12' as vintage,
    'Series are the 10 largest CBSAs by 2023 population. Top three by population are highlighted more strongly.' as note
from gold.housing_core_wide h
join top_10 t
  on h.geo_id = t.geo_id
where h.geo_level = 'cbsa'
  and h.year between 2018 and 2023
  and h.median_gross_rent is not null
order by t.pop_rank, h.year;
