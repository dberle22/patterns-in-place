with cbsa_snapshot as (
    select
        h.geo_id,
        h.geo_name,
        h.year,
        h.pop_total,
        h.vacancy_rate,
        d.state_abbr,
        d.cbsa_code,
        d.region_name
    from gold.housing_core_wide h
    inner join gold.dim_geo d
        on h.geo_level = d.geo_level
       and h.geo_id = d.geo_id
    where h.geo_level = 'cbsa'
      and h.year = 2024
      and h.pop_total >= 250000
      and h.vacancy_rate is not null
      and coalesce(d.state_abbr, '') not in ('PR', 'AK', 'HI')
),
cbsa_geometry as (
    select
        cbsa_code,
        st_asgeojson(geom) as geometry_json,
        st_astext(geom) as geom_wkt
    from geo.cbsas
),
joined as (
    select
        cs.*,
        cg.geometry_json,
        cg.geom_wkt
    from cbsa_snapshot cs
    inner join cbsa_geometry cg
        on cs.cbsa_code = cg.cbsa_code
),
tagged as (
    select
        *,
        case
            when vacancy_rate * 100.0 < 5 then 'Very tight (<5%)'
            when vacancy_rate * 100.0 < 8 then 'Tight (5-8%)'
            when vacancy_rate * 100.0 < 12 then 'Balanced (8-12%)'
            else 'Loose (12%+)'
        end as bin
    from joined
)
select
    'q025'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    geo_id,
    geo_name,
    state_abbr,
    '2024_snapshot'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate (%)'::varchar as metric_label,
    vacancy_rate * 100.0 as metric_value,
    'gold.housing_core_wide + gold.dim_geo + geo.cbsas'::varchar as source,
    '2026-07-12'::varchar as vintage,
    geometry_json,
    geom_wkt,
    bin,
    region_name as "group",
    (geo_name = 'Phoenix-Mesa-Chandler, AZ') as highlight_flag,
    false as neighbor_flag,
    (geo_name = 'Phoenix-Mesa-Chandler, AZ') as label_flag,
    case when geo_name = 'Phoenix-Mesa-Chandler, AZ' then 'Phoenix' else null end as label_text,
    (
        'Context CBSAs are colored by 2024 vacancy-rate tier. Phoenix is highlighted as the focal metro.'
    )::varchar as note
from tagged
order by highlight_flag desc, vacancy_rate asc, geo_name;
