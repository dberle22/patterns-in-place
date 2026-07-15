with metro_base as (
    select
        p.geo_level,
        p.geo_id,
        p.geo_name,
        p.year,
        p.pop_total,
        p.median_age,
        d.state_abbr
    from gold.population_demographics p
    join gold.dim_geo d
      on p.geo_level = d.geo_level
     and p.geo_id = d.geo_id
    where p.geo_level = 'cbsa'
      and p.year = 2023
      and p.pop_total >= 250000
      and p.median_age is not null
      and coalesce(d.state_abbr, '') <> 'PR'
)
select
    geo_level,
    geo_id,
    geo_name,
    '2023_snapshot' as time_window,
    'median_age' as metric_id,
    'Median age (years)' as metric_label,
    median_age as metric_value,
    'All major CBSAs' as "group",
    false as highlight_flag,
    false as label_flag,
    'gold.population_demographics + gold.dim_geo' as source,
    '2026-07-12' as vintage,
    'Distribution includes CBSAs with population >= 250k in 2023.' as note
from metro_base
order by median_age desc, geo_name;
