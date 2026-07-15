with ranked as (
    select
        h.geo_level,
        h.geo_id,
        h.geo_name,
        d.state_abbr,
        d.region_name,
        h.year,
        h.pop_total,
        h.rent_to_income * 100.0 as metric_value,
        row_number() over (
            order by h.rent_to_income desc, h.geo_name asc
        ) as rank_desc
    from gold.housing_core_wide h
    join gold.dim_geo d
      on h.geo_level = d.geo_level
     and h.geo_id = d.geo_id
    where h.geo_level = 'cbsa'
      and h.year = 2023
      and h.pop_total >= 250000
      and h.rent_to_income is not null
      and coalesce(d.state_abbr, '') <> 'PR'
)
select
    geo_level,
    geo_id,
    geo_name,
    state_abbr,
    year,
    '2023_snapshot' as time_window,
    'rent_to_income' as metric_id,
    'Rent-to-income ratio (%)' as metric_label,
    metric_value,
    rank_desc,
    region_name as "group",
    false as highlight_flag,
    'gold.housing_core_wide + gold.dim_geo' as source,
    '2026-07-12' as vintage,
    'Filtered to CBSAs with population >= 250k and excludes Puerto Rico metros so the ranking stays focused on the contiguous-US affordability pattern.' as note
from ranked
where rank_desc <= 15
order by rank_desc;
