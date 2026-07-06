-- Major-CBSA momentum-versus-strain bivariate map inputs for the housing Overheating section.
-- The map focuses on two component families that are easiest to explain
-- visually:
-- - momentum: how hard prices/rents have been running
-- - strain: how stretched affordability already looks

with base as (
    select
        o.geo_id,
        o.geo_name,
        o.region_name,
        o.division_name,
        o.momentum_component_score,
        o.strain_component_score,
        o.provisional_overheating_score
    from mart_housing.overheating_matrix o
    where o.geo_level = 'cbsa'
      and o.year = 2024
      and o.major_cbsa_100k_flag
      and coalesce(o.state_abbr, '') <> 'PR'
),
ranked as (
    select
        row_number() over (
            order by b.provisional_overheating_score desc, b.geo_name
        ) as hottest_rank,
        b.*
    from base b
)
select
    'overheating_bivariate_map'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    r.geo_id,
    r.geo_name,
    '2024_snapshot'::varchar as time_window,
    r.momentum_component_score * 100.0 as x_value,
    r.strain_component_score * 100.0 as y_value,
    'Momentum component score (0-100)'::varchar as x_label,
    'Strain component score (0-100)'::varchar as y_label,
    'mart_housing.overheating_matrix + geo.cbsas'::varchar as source,
    '2026-07-05'::varchar as vintage,
    st_astext(g.geom) as geom_wkt,
    r.hottest_rank <= 8 as highlight_flag,
    (
        'Region: ' || r.region_name ||
        ' | Division: ' || r.division_name ||
        ' | Darker high-high metros combine stronger recent momentum with stronger affordability strain.'
    )::varchar as note
from ranked r
inner join geo.cbsas g
    on r.geo_id = g.cbsa_code
order by r.geo_name;
