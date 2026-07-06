-- Major-CBSA permit-intensity map inputs for the housing Supply Character section.
-- We keep the logic chart-focused:
-- - major metros only for the current editorial universe
-- - current 2024 snapshot
-- - CBSA polygons from shared geography, with points derived in prep

with base as (
    select
        c.geo_id,
        c.geo_name,
        c.region_name,
        c.division_name,
        c.state_abbr,
        c.cbsa_pop_2024,
        c.permits_per_1000_housing_units
    from mart_housing.core_metrics c
    where c.geo_level = 'cbsa'
      and c.year = 2024
      and c.major_cbsa_100k_flag
      and coalesce(c.state_abbr, '') <> 'PR'
      and c.permits_per_1000_housing_units is not null
      and not isnan(c.permits_per_1000_housing_units)
      and not isinf(c.permits_per_1000_housing_units)
),
ranked as (
    select
        row_number() over (
            order by b.permits_per_1000_housing_units desc, b.geo_name
        ) as permit_rank,
        b.*
    from base b
)
select
    'supply_permit_intensity_map'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    r.geo_id,
    r.geo_name,
    '2024_snapshot'::varchar as time_window,
    r.permits_per_1000_housing_units as size_value,
    'Permits per 1,000 housing units'::varchar as size_label,
    'mart_housing.core_metrics + geo.cbsas'::varchar as source,
    '2026-07-05'::varchar as vintage,
    r.region_name as color_group,
    r.permit_rank <= 12 as label_flag,
    r.permit_rank <= 12 as highlight_flag,
    st_astext(g.geom) as geom_wkt,
    (
        'Division: ' || r.division_name ||
        ' | Bubble size shows 2024 permits per 1,000 housing units.'
    )::varchar as note
from ranked r
inner join geo.cbsas g
    on r.geo_id = g.cbsa_code
order by r.permit_rank, r.geo_name;
