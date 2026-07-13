-- Which states have the highest share of cost-burdened renters in 2023?
-- State-level choropleth for the share of renter households spending 30%+
-- of income on rent. Keep the footprint to the contiguous 48 states plus DC
-- so the national pattern reads cleanly at social size.

with us_2023 as (
  select
    pct_rent_burden_30plus * 100 as us_cost_burden_pct
  from gold.housing_core_wide
  where geo_level = 'us'
    and year = 2023
    and pct_rent_burden_30plus is not null
    and not isnan(pct_rent_burden_30plus)
    and not isinf(pct_rent_burden_30plus)
),
state_values as (
  select
    h.geo_level,
    h.geo_id,
    h.geo_name,
    dg.state_abbr,
    h.year,
    h.pct_rent_burden_30plus * 100 as metric_value
  from gold.housing_core_wide h
  left join gold.dim_geo dg
    on h.geo_level = dg.geo_level
   and h.geo_id = dg.geo_id
  where h.geo_level = 'state'
    and h.year = 2023
    and h.geo_id not in ('02', '15', '72') -- AK, HI, PR
    and h.pct_rent_burden_30plus is not null
    and not isnan(h.pct_rent_burden_30plus)
    and not isinf(h.pct_rent_burden_30plus)
),
state_geometry as (
  select
    state_fips as geo_id,
    state_name as geo_name,
    st_asgeojson(geom) as geometry_json,
    st_astext(geom) as geom_wkt
  from geo.states
  where state_fips not in ('02', '15', '72') -- AK, HI, PR
),
ranked as (
  select
    'q024'::varchar as question_id,
    sv.geo_level,
    sv.geo_id,
    sv.geo_name,
    sv.state_abbr,
    2023::integer as year,
    '2023_snapshot'::varchar as time_window,
    'pct_rent_burden_30plus'::varchar as metric_id,
    'Renter cost-burden share (%)'::varchar as metric_label,
    sv.metric_value,
    row_number() over (order by sv.metric_value desc, sv.geo_name) as rank_desc,
    row_number() over (order by sv.metric_value asc, sv.geo_name) as rank_asc,
    (select us_cost_burden_pct from us_2023)::double as benchmark_value,
    'State renter cost burden'::varchar as "group",
    false as highlight_flag,
    false as label_flag,
    null::varchar as label_text,
    'Contiguous 48 states plus DC only. Darker states indicate higher renter cost burden.'::varchar as note
  from state_values sv
)
select
  r.question_id,
  r.geo_level,
  r.geo_id,
  r.geo_name,
  r.state_abbr,
  r.year,
  r.time_window,
  r.metric_id,
  r.metric_label,
  r.metric_value,
  'gold.housing_core_wide; gold.dim_geo; geo.states'::varchar as source,
  '2026-07-12'::varchar as vintage,
  sg.geometry_json,
  sg.geom_wkt,
  r.rank_desc,
  r.rank_asc,
  r.benchmark_value,
  r."group",
  r.highlight_flag,
  r.label_flag,
  r.label_text,
  r.note
from ranked r
join state_geometry sg
  on r.geo_id = sg.geo_id
 and r.geo_name = sg.geo_name
order by r.rank_desc, r.geo_name;
