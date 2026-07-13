with ranked as (
    select
        p.geo_level,
        p.geo_id,
        p.geo_name,
        d.state_abbr,
        d.region_name,
        p.year,
        p.pop_total,
        p.diversity_index as metric_value,
        row_number() over (
            order by p.diversity_index desc, p.geo_name asc
        ) as rank_desc
    from gold.population_demographics p
    join gold.dim_geo d
      on p.geo_level = d.geo_level
     and p.geo_id = d.geo_id
    where p.geo_level = 'cbsa'
      and p.year = 2023
      and p.pop_total >= 500000
      and p.diversity_index is not null
)
select
    geo_level,
    geo_id,
    geo_name,
    state_abbr,
    year,
    '2023_snapshot' as time_window,
    'diversity_index' as metric_id,
    'Diversity index' as metric_label,
    metric_value,
    rank_desc,
    region_name as "group",
    false as highlight_flag,
    'gold.population_demographics + gold.dim_geo' as source,
    '2026-07-12' as vintage,
    'Filtered to CBSAs with population >= 500k. Diversity index is the probability that two randomly selected residents are from different racial or ethnic groups.' as note
from ranked
where rank_desc <= 15
order by rank_desc;
