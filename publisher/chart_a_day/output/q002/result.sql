with ranked as (
    select
        e.geo_level,
        e.geo_id,
        e.geo_name,
        d.region_name,
        e.year,
        e.median_hh_income as metric_value,
        row_number() over (
            order by e.median_hh_income desc, e.geo_name asc
        ) as rank_desc
    from gold.economics_income_wide e
    join gold.dim_geo d
      on e.geo_level = d.geo_level
     and e.geo_id = d.geo_id
    where e.geo_level = 'state'
      and e.year = 2023
      and e.median_hh_income is not null
)
select
    geo_level,
    geo_id,
    geo_name,
    year,
    '2023_snapshot' as time_window,
    'median_hh_income' as metric_id,
    'Median household income ($)' as metric_label,
    metric_value,
    rank_desc,
    region_name as "group",
    false as highlight_flag,
    'gold.economics_income_wide + gold.dim_geo' as source,
    '2026-07-12' as vintage,
    'Top 10 states by 2023 median household income. District of Columbia is included because it is present in the state grain of the semantic layer.' as note
from ranked
where rank_desc <= 10
order by rank_desc;
