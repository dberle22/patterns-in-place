with state_metrics as (
  select
    h.geo_level,
    h.geo_id,
    h.geo_name,
    dg.state_abbr,
    dg.region_name,
    h.year,
    h.rent_to_income as x_value,
    (-1.0 * h.vacancy_rate) as y_value
  from gold.housing_core_wide h
  join gold.dim_geo dg
    on h.geo_level = dg.geo_level
   and h.geo_id = dg.geo_id
  where h.geo_level = 'state'
    and h.year = 2023
    and h.geo_id not in ('02', '15', '72')
    and h.rent_to_income is not null
    and h.vacancy_rate is not null
),
state_geometry as (
  select
    state_fips as geo_id,
    state_name as geo_name,
    st_asgeojson(geom) as geometry_json,
    st_astext(geom) as geom_wkt
  from geo.states
  where state_fips not in ('02', '15', '72')
)
select
  'q027' as question_id,
  sm.geo_level,
  sm.geo_id,
  sm.geo_name,
  sm.state_abbr,
  '2023_snapshot' as time_window,
  sm.x_value,
  sm.y_value,
  'Rent-to-income ratio' as x_label,
  'Vacancy pressure (lower vacancy = worse)' as y_label,
  'gold.housing_core_wide + gold.dim_geo + geo.states' as source,
  '2023' as vintage,
  sg.geometry_json,
  sg.geom_wkt,
  sm.region_name as "group",
  false as highlight_flag,
  'Higher values on the vertical bivariate axis represent lower vacancy after sign inversion.' as note
from state_metrics sm
join state_geometry sg
  on sm.geo_id = sg.geo_id
 and sm.geo_name = sg.geo_name
order by sm.geo_name;
