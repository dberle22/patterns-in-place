-- State vacancy choropleth query
-- Primary use: 2024 vacancy-rate map
-- Secondary uses supported in the same extract:
--   1. 2019 vacancy-rate baseline map
--   2. 2019 to 2024 vacancy-rate change map
--
-- Output shape:
-- - One row per geography per map-ready metric
-- - `metric_value` is the field the choropleth should color by
-- - Helper columns keep the 2019 level, 2024 level, and change together
--   for labels, annotations, or alternate map views

with state_base as (
  select
    h.geo_id,
    h.geo_name,
    dg.state_abbr,
    h.year,
    h.vacancy_rate * 100 as vacancy_rate_pct,
    sr.census_region,
    sr.census_division
  from gold.housing_core_wide h
  left join gold.dim_geo dg
    on h.geo_level = dg.geo_level
   and h.geo_id = dg.geo_id
  left join silver.xwalk_state_region sr
    on h.geo_id = sr.state_fips
  where h.geo_level = 'state'
    and h.year in (2019, 2024)
    and h.geo_id not in ('02', '15', '72') -- AK, HI, PR
    and h.vacancy_rate is not null
    and not isnan(h.vacancy_rate)
    and not isinf(h.vacancy_rate)
),
state_compare as (
  select
    y2024.geo_id,
    y2024.geo_name,
    y2024.state_abbr,
    y2024.census_region,
    y2024.census_division,
    y2019.vacancy_rate_pct as vacancy_rate_2019_pct,
    y2024.vacancy_rate_pct as vacancy_rate_2024_pct,
    y2024.vacancy_rate_pct - y2019.vacancy_rate_pct as vacancy_rate_change_pp
  from state_base y2019
  join state_base y2024
    on y2019.geo_id = y2024.geo_id
   and y2019.year = 2019
   and y2024.year = 2024
),
state_ranked as (
  select
    sc.*,
    row_number() over (order by sc.vacancy_rate_2024_pct asc, sc.geo_name) as tight_rank_2024,
    row_number() over (order by sc.vacancy_rate_2024_pct desc, sc.geo_name) as loose_rank_2024
  from state_compare sc
),
us_benchmarks as (
  select
    max(case when year = 2019 then vacancy_rate * 100 end) as us_vacancy_rate_2019_pct,
    max(case when year = 2024 then vacancy_rate * 100 end) as us_vacancy_rate_2024_pct,
    max(case when year = 2024 then vacancy_rate * 100 end)
      - max(case when year = 2019 then vacancy_rate * 100 end) as us_vacancy_rate_change_pp
  from gold.housing_core_wide
  where geo_level = 'us'
    and year in (2019, 2024)
    and vacancy_rate is not null
    and not isnan(vacancy_rate)
    and not isinf(vacancy_rate)
),
state_geometry as (
  select
    state_fips as geo_id,
    state_name as geo_name,
    st_astext(st_geomfromgeojson(cast(geojson_str as varchar))) as geom_wkt
  from geo.states
  where state_fips not in ('02', '15', '72') -- AK, HI, PR
),
map_rows as (
  select
    'state_map'::varchar as question_id,
    'state'::varchar as geo_level,
    sc.geo_id,
    sc.geo_name,
    '2024_snapshot'::varchar as time_window,
    'vacancy_rate_2024'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    sc.vacancy_rate_2024_pct as metric_value,
    ub.us_vacancy_rate_2024_pct as benchmark_value,
    sc.census_region as "group",
    false as highlight_flag,
    false as label_flag,
    null::varchar as label_text,
    'Primary map metric: 2024 state vacancy rate.'::varchar as note,
    sc.vacancy_rate_2019_pct,
    sc.vacancy_rate_2024_pct,
    sc.vacancy_rate_change_pp
  from state_ranked sc
  cross join us_benchmarks ub

  union all

  select
    'state_map'::varchar as question_id,
    'state'::varchar as geo_level,
    sc.geo_id,
    sc.geo_name,
    '2019_snapshot'::varchar as time_window,
    'vacancy_rate_2019'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    sc.vacancy_rate_2019_pct as metric_value,
    ub.us_vacancy_rate_2019_pct as benchmark_value,
    sc.census_region as "group",
    false as highlight_flag,
    false as label_flag,
    null::varchar as label_text,
    'Baseline map metric: 2019 state vacancy rate.'::varchar as note,
    sc.vacancy_rate_2019_pct,
    sc.vacancy_rate_2024_pct,
    sc.vacancy_rate_change_pp
  from state_ranked sc
  cross join us_benchmarks ub

  union all

  select
    'state_map'::varchar as question_id,
    'state'::varchar as geo_level,
    sc.geo_id,
    sc.geo_name,
    '2019_to_2024_change'::varchar as time_window,
    'vacancy_rate_change_pp'::varchar as metric_id,
    'Vacancy rate change since 2019 (pp)'::varchar as metric_label,
    sc.vacancy_rate_change_pp as metric_value,
    ub.us_vacancy_rate_change_pp as benchmark_value,
    sc.census_region as "group",
    false as highlight_flag,
    false as label_flag,
    null::varchar as label_text,
    'Secondary map metric: 2024 vacancy rate minus 2019 vacancy rate.'::varchar as note,
    sc.vacancy_rate_2019_pct,
    sc.vacancy_rate_2024_pct,
    sc.vacancy_rate_change_pp
  from state_ranked sc
  cross join us_benchmarks ub
)
select
  mr.question_id,
  mr.geo_level,
  mr.geo_id,
  mr.geo_name,
  mr.time_window,
  mr.metric_id,
  mr.metric_label,
  mr.metric_value,
  'ACS'::varchar as source,
  '2024'::varchar as vintage,
  sg.geom_wkt,
  mr.benchmark_value,
  mr."group",
  mr.highlight_flag,
  mr.label_flag,
  mr.label_text,
  mr.note,
  mr.vacancy_rate_2019_pct,
  mr.vacancy_rate_2024_pct,
  mr.vacancy_rate_change_pp
from map_rows mr
join state_geometry sg
  on mr.geo_id = sg.geo_id
 and mr.geo_name = sg.geo_name
order by
  case mr.time_window
    when '2024_snapshot' then 1
    when '2019_snapshot' then 2
    when '2019_to_2024_change' then 3
    else 4
  end,
  mr.geo_id;
