with metro_values as (
  select
    d.geo_level,
    d.geo_id,
    d.geo_name,
    dg.state_abbr,
    coalesce(dg.region_name, 'Unknown') as region_name,
    dg.cbsa_code,
    d.year,
    d.pop_total,
    d.pop_growth_5yr as size_value
  from gold.population_demographics d
  join gold.dim_geo dg
    on d.geo_level = dg.geo_level
   and d.geo_id = dg.geo_id
  where d.geo_level = 'cbsa'
    and d.year = 2023
    and d.pop_total > 100000
    and d.pop_growth_5yr is not null
    and coalesce(dg.state_abbr, '') not in ('PR', 'AK', 'HI')
),
ranked as (
  select
    *,
    row_number() over (order by size_value desc, geo_name) as size_rank
  from metro_values
),
cbsa_geometry as (
  select
    cbsa_code,
    st_asgeojson(geom) as geometry_json,
    st_astext(geom) as geom_wkt
  from geo.cbsas
)
select
  'q026' as question_id,
  r.geo_level,
  r.geo_id,
  r.geo_name,
  r.state_abbr,
  '2018_2023_growth' as time_window,
  r.size_value,
  '5-year population growth rate' as size_label,
  'gold.population_demographics + gold.dim_geo + geo.cbsas' as source,
  '2023' as vintage,
  cg.geometry_json,
  cg.geom_wkt,
  r.region_name as color_group,
  (r.size_rank <= 6) as label_flag,
  false as highlight_flag,
  'Bubble size reflects 2018-2023 population growth. Colors show Census region.' as note
from ranked r
join cbsa_geometry cg
  on r.cbsa_code = cg.cbsa_code
order by r.size_rank, r.geo_name;
