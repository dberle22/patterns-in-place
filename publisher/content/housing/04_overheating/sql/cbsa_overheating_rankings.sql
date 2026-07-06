-- Major-CBSA overheating rankings for the housing Overheating section.
-- This file produces both:
-- - the hottest metros under the provisional composite
-- - a stricter "still affordable" shortlist that requires below-median rent
--   and value strain before rewarding lower momentum and lower strain

with base as (
    select
        o.geo_id,
        o.geo_name,
        o.region_name,
        o.division_name,
        o.pop_total,
        o.provisional_overheating_score,
        o.provisional_overheating_score_pctile,
        o.momentum_component_score,
        o.pressure_component_score,
        o.strain_component_score,
        o.tightness_component_score,
        o.rent_to_income,
        o.value_to_income
    from mart_housing.overheating_matrix o
    where o.geo_level = 'cbsa'
      and o.year = 2024
      and o.major_cbsa_100k_flag
      and coalesce(o.state_abbr, '') <> 'PR'
),
thresholds as (
    select
        median(rent_to_income) as median_rent_to_income,
        median(value_to_income) as median_value_to_income
    from base
),
hottest as (
    select
        row_number() over (
            order by b.provisional_overheating_score desc, b.geo_name
        ) as rank,
        b.*
    from base b
),
still_affordable_universe as (
    select
        b.*,
        (
            1.0 - (0.6 * b.strain_component_score + 0.4 * b.momentum_component_score)
        ) as still_affordable_score
    from base b
    cross join thresholds t
    where b.rent_to_income <= t.median_rent_to_income
      and b.value_to_income <= t.median_value_to_income
),
still_affordable as (
    select
        row_number() over (
            order by s.still_affordable_score desc,
                     s.provisional_overheating_score asc,
                     s.geo_name
        ) as rank,
        s.*
    from still_affordable_universe s
)
select
    'overheating_hottest'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    h.geo_id,
    h.geo_name,
    '2024_snapshot'::varchar as time_window,
    'provisional_overheating_score'::varchar as metric_id,
    'Provisional overheating score'::varchar as metric_label,
    h.provisional_overheating_score * 100.0 as metric_value,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    h.rank,
    'Hottest major CBSAs'::varchar as "group",
    null::varchar as series,
    h.provisional_overheating_score_pctile * 100.0 as share_value,
    false as highlight_flag,
    50.0::double as benchmark_value,
    (
        'Region: ' || h.region_name ||
        ' | Division: ' || h.division_name ||
        ' | Bars show the provisional composite score scaled to a 0-100 index.'
    )::varchar as note
from hottest h
where h.rank <= 10

union all

select
    'overheating_still_affordable'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    s.geo_id,
    s.geo_name,
    '2024_snapshot'::varchar as time_window,
    'still_affordable_score'::varchar as metric_id,
    'Still-affordable shortlist score'::varchar as metric_label,
    s.still_affordable_score * 100.0 as metric_value,
    'mart_housing.overheating_matrix'::varchar as source,
    '2026-07-05'::varchar as vintage,
    s.rank,
    'Still-affordable shortlist'::varchar as "group",
    null::varchar as series,
    s.provisional_overheating_score_pctile * 100.0 as share_value,
    false as highlight_flag,
    50.0::double as benchmark_value,
    (
        'Region: ' || s.region_name ||
        ' | Division: ' || s.division_name ||
        ' | Shortlist first requires below-median rent and value strain, then prefers lower strain and lower momentum.'
    )::varchar as note
from still_affordable s
where s.rank <= 10
order by question_id, rank;
