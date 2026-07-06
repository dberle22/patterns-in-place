-- State vacancy choropleth for the housing Vacancy section.
-- This query keeps the map logic focused on chart-ready shaping:
-- - one row per state
-- - current 2024 snapshot only
-- - contiguous-US framing for the opening national map
-- The shared section mart already owns the vacancy metric definition.

with state_snapshot as (
    select
        c.geo_id,
        c.geo_name,
        c.state_abbr,
        c.region_name,
        c.division_name,
        c.vacancy_rate
    from mart_housing.core_metrics c
    where c.geo_level = 'state'
      and c.year = 2024
      and c.state_abbr not in ('AK', 'HI', 'PR')
      and c.vacancy_rate is not null
      and not isnan(c.vacancy_rate)
      and not isinf(c.vacancy_rate)
),
state_geometry as (
    select
        s.state_fips as geo_id,
        s.state_name as geo_name,
        st_astext(s.geom) as geom_wkt
    from geo.states s
    where s.state_abbr not in ('AK', 'HI', 'PR')
)
select
    'vacancy_state_map'::varchar as question_id,
    'state'::varchar as geo_level,
    ss.geo_id,
    ss.geo_name,
    '2024_snapshot'::varchar as time_window,
    ss.vacancy_rate * 100.0 as metric_value,
    'Vacancy rate (%)'::varchar as metric_label,
    'mart_housing.core_metrics + geo.states'::varchar as source,
    '2026-07-05'::varchar as vintage,
    sg.geom_wkt,
    null::double as benchmark_value,
    ss.region_name as "group",
    false as highlight_flag,
    (
        'Division: ' || ss.division_name ||
        ' | State vacancy rate shown in percentage points for legend readability.'
    )::varchar as note
from state_snapshot ss
inner join state_geometry sg
    on ss.geo_id = sg.geo_id
   and ss.geo_name = sg.geo_name
order by ss.geo_id;
