with metro_growth as (
    select
        p.geo_level,
        p.geo_id,
        p.geo_name,
        p.year,
        p.pop_total,
        p.pop_growth_5yr,
        d.state_abbr
    from gold.population_demographics p
    join gold.dim_geo d
      on p.geo_level = d.geo_level
     and p.geo_id = d.geo_id
    where p.geo_level = 'cbsa'
      and p.year = 2023
      and p.pop_total >= 250000
      and p.pop_growth_5yr is not null
      and coalesce(d.state_abbr, '') <> 'PR'
),
ranked as (
    select
        *,
        row_number() over (order by pop_growth_5yr desc, geo_name asc) as rank_desc
    from metro_growth
)
select
    geo_level,
    geo_id,
    geo_name,
    '2018_2023_growth' as time_window,
    'pop_growth_5yr' as metric_id,
    'Five-year population growth (%)' as metric_label,
    pop_growth_5yr * 100.0 as metric_value,
    rank_desc,
    rank_desc <= 5 as highlight_flag,
    'gold.population_demographics + gold.dim_geo' as source,
    '2026-07-12' as vintage,
    'Ranking is limited to CBSAs with population >= 250k in 2023.' as note
from ranked
where rank_desc <= 15
order by rank_desc;
