with selected_metros as (
    select *
    from (
        values
            ('12420', 'Austin-Round Rock-San Marcos, TX'),
            ('19100', 'Dallas-Fort Worth-Arlington, TX'),
            ('26420', 'Houston-Pasadena-The Woodlands, TX'),
            ('38060', 'Phoenix-Mesa-Chandler, AZ'),
            ('12060', 'Atlanta-Sandy Springs-Roswell, GA'),
            ('45300', 'Tampa-St. Petersburg-Clearwater, FL'),
            ('36740', 'Orlando-Kissimmee-Sanford, FL'),
            ('34980', 'Nashville-Davidson--Murfreesboro--Franklin, TN')
    ) as t(geo_id, geo_name)
)
select
    h.geo_level,
    h.geo_id,
    h.geo_name,
    cast(h.year as varchar) as period,
    '2015_2023_level' as time_window,
    'median_hh_income' as metric_id,
    'Median household income ($)' as metric_label,
    h.median_hh_income as metric_value,
    h.geo_name as series,
    h.geo_id in ('12420', '38060') as highlight_flag,
    'Selected Sun Belt metros' as "group",
    'gold.housing_core_wide' as source,
    '2026-07-12' as vintage,
    'Metro set: Austin, Dallas, Houston, Phoenix, Atlanta, Tampa, Orlando, and Nashville. Austin and Phoenix are highlighted for readability.' as note
from gold.housing_core_wide h
join selected_metros s
  on h.geo_id = s.geo_id
where h.geo_level = 'cbsa'
  and h.year between 2015 and 2023
  and h.median_hh_income is not null
order by s.geo_name, h.year;
