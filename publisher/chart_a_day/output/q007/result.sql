with selected_metros as (
    select *
    from (
        values
            ('Austin-Round Rock-San Marcos, TX'),
            ('Nashville-Davidson--Murfreesboro--Franklin, TN'),
            ('Denver-Aurora-Centennial, CO'),
            ('Charlotte-Concord-Gastonia, NC-SC')
    ) as t(geo_name)
),
metro_values as (
    select
        h.geo_id,
        h.geo_name,
        h.year,
        h.pop_total,
        h.median_gross_rent,
        d.state_abbr,
        d.region_name,
        d.division_name,
        row_number() over (
            order by h.median_gross_rent desc, h.geo_name
        ) as rank_desc
    from gold.housing_core_wide h
    inner join gold.dim_geo d
        on h.geo_level = d.geo_level
       and h.geo_id = d.geo_id
    inner join selected_metros s
        on h.geo_name = s.geo_name
    where h.geo_level = 'cbsa'
      and h.year = 2023
      and h.median_gross_rent is not null
),
us_benchmark as (
    select avg(median_gross_rent) as benchmark_value
    from gold.housing_core_wide
    where geo_level = 'cbsa'
      and year = 2023
      and pop_total >= 250000
      and median_gross_rent is not null
)
select
    'q007'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    mv.geo_id,
    mv.geo_name,
    mv.state_abbr,
    mv.year,
    '2023_snapshot'::varchar as time_window,
    'median_gross_rent'::varchar as metric_id,
    'Median gross rent ($)'::varchar as metric_label,
    mv.median_gross_rent as metric_value,
    'gold.housing_core_wide + gold.dim_geo'::varchar as source,
    '2026-07-12'::varchar as vintage,
    mv.rank_desc,
    null::bigint as rank_asc,
    ub.benchmark_value,
    mv.region_name as "group",
    false as highlight_flag,
    false as label_flag,
    null::varchar as label_text,
    (
        'Selected peer metros only. 2023 rents shown as annual snapshot values; US benchmark is the average across CBSAs with population >= 250k.'
    )::varchar as note
from metro_values mv
cross join us_benchmark ub
order by mv.rank_desc;
