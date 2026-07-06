-- Major-CBSA momentum-versus-strain scatter inputs for the housing Overheating section.
-- We use the component scores directly so the chart makes the composite more
-- interpretable instead of hiding it.

with base as (
    select
        o.geo_id,
        o.geo_name,
        o.region_name,
        o.division_name,
        o.pop_total,
        o.momentum_component_score,
        o.strain_component_score,
        o.provisional_overheating_score,
        o.provisional_overheating_score_pctile
    from mart_housing.overheating_matrix o
    where o.geo_level = 'cbsa'
      and o.year = 2024
      and o.major_cbsa_100k_flag
      and coalesce(o.state_abbr, '') <> 'PR'
),
ranked as (
    select
        b.*,
        row_number() over (
            order by b.provisional_overheating_score desc, b.geo_name
        ) as hottest_rank,
        row_number() over (
            order by b.provisional_overheating_score asc, b.geo_name
        ) as calmest_rank
    from base b
)
select
    'cbsa'::varchar as geo_level,
    r.geo_id,
    r.geo_name,
    '2024_snapshot'::varchar as time_window,
    r.momentum_component_score * 100.0 as x_value,
    r.strain_component_score * 100.0 as y_value,
    'Momentum component score (0-100)'::varchar as x_label,
    'Strain component score (0-100)'::varchar as y_label,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    r.region_name as "group",
    r.pop_total as size_value,
    (r.hottest_rank <= 6 or r.calmest_rank <= 4) as label_flag,
    (
        'Division: ' || r.division_name ||
        ' | Points are sized by 2024 population and component scores are shown on a 0-100 scale.'
    )::varchar as note,
    'momentum_component_score'::varchar as x_metric_id,
    'strain_component_score'::varchar as y_metric_id
from ranked r
order by r.provisional_overheating_score desc, r.geo_name;
