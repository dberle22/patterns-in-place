with west_cbsa as (
    select
        h.geo_level,
        h.geo_id,
        h.geo_name,
        h.year,
        h.pop_total,
        h.median_gross_rent,
        d.region_name
    from gold.housing_core_wide h
    join gold.dim_geo d
      on h.geo_level = d.geo_level
     and h.geo_id = d.geo_id
    where h.geo_level = 'cbsa'
      and h.year = 2023
      and h.pop_total >= 250000
      and h.median_gross_rent is not null
      and d.region_name = 'West'
),
west_benchmark as (
    select avg(median_gross_rent) as west_avg_rent
    from west_cbsa
),
phoenix as (
    select *
    from west_cbsa
    where geo_name = 'Phoenix-Mesa-Chandler, AZ'
)
select
    p.geo_level,
    p.geo_id,
    p.geo_name,
    '2023_snapshot' as time_window,
    'median_gross_rent' as metric_id,
    'Median gross rent ($)' as metric_label,
    p.median_gross_rent as metric_value,
    1 as rank_desc,
    w.west_avg_rent as benchmark_value,
    true as highlight_flag,
    'gold.housing_core_wide + gold.dim_geo' as source,
    '2026-07-12' as vintage,
    'Benchmark is the average 2023 median gross rent across Western-region CBSAs with population >= 250k.' as note
from phoenix p
cross join west_benchmark w;
