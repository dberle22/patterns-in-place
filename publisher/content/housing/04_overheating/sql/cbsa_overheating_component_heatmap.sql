-- Major-CBSA overheating component heatmap inputs for the housing Overheating section.
-- We translate the component scores to a 0-100 scale so the heatmap can compare
-- them directly across metros without mixing incompatible raw units.

with top_markets as (
    select
        row_number() over (
            order by o.provisional_overheating_score desc, o.geo_name
        ) as overheating_rank,
        o.geo_id,
        o.geo_name,
        o.provisional_overheating_score,
        o.provisional_overheating_score_pctile,
        o.momentum_component_score,
        o.pressure_component_score,
        o.strain_component_score,
        o.tightness_component_score
    from mart_housing.overheating_matrix o
    where o.geo_level = 'cbsa'
      and o.year = 2024
      and o.major_cbsa_100k_flag
      and coalesce(o.state_abbr, '') <> 'PR'
    qualify overheating_rank <= 10
)
select
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    'momentum_component_score'::varchar as metric_id,
    'Momentum'::varchar as metric_label,
    t.momentum_component_score * 100.0 as metric_value,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    '2024_snapshot'::varchar as time_window,
    t.overheating_rank,
    t.momentum_component_score * 100.0 as normalized_value,
    'higher_is_better'::varchar as direction
from top_markets t

union all

select
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    'pressure_component_score'::varchar as metric_id,
    'Pressure'::varchar as metric_label,
    t.pressure_component_score * 100.0 as metric_value,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    '2024_snapshot'::varchar as time_window,
    t.overheating_rank,
    t.pressure_component_score * 100.0 as normalized_value,
    'higher_is_better'::varchar as direction
from top_markets t

union all

select
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    'strain_component_score'::varchar as metric_id,
    'Strain'::varchar as metric_label,
    t.strain_component_score * 100.0 as metric_value,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    '2024_snapshot'::varchar as time_window,
    t.overheating_rank,
    t.strain_component_score * 100.0 as normalized_value,
    'higher_is_better'::varchar as direction
from top_markets t

union all

select
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    'tightness_component_score'::varchar as metric_id,
    'Tightness / supply'::varchar as metric_label,
    t.tightness_component_score * 100.0 as metric_value,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    '2024_snapshot'::varchar as time_window,
    t.overheating_rank,
    t.tightness_component_score * 100.0 as normalized_value,
    'higher_is_better'::varchar as direction
from top_markets t

union all

select
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    'provisional_overheating_score_pctile'::varchar as metric_id,
    'Composite percentile'::varchar as metric_label,
    t.provisional_overheating_score_pctile * 100.0 as metric_value,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    '2024_snapshot'::varchar as time_window,
    t.overheating_rank,
    t.provisional_overheating_score_pctile * 100.0 as normalized_value,
    'higher_is_better'::varchar as direction
from top_markets t
order by overheating_rank, metric_label;
