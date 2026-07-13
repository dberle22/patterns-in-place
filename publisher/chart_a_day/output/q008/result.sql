with ranked_2023 as (
    select
        p.geo_id,
        p.geo_name,
        p.year,
        p.pop_total,
        p.pop_growth_5yr,
        d.state_abbr,
        row_number() over (
            order by p.pop_growth_5yr desc, p.pop_total desc, p.geo_name
        ) as growth_rank
    from gold.population_demographics p
    inner join gold.dim_geo d
        on p.geo_level = d.geo_level
       and p.geo_id = d.geo_id
    where p.geo_level = 'cbsa'
      and p.year = 2023
      and p.pop_total >= 250000
      and p.pop_growth_5yr is not null
),
selected_metros as (
    select geo_id, geo_name, state_abbr, growth_rank
    from ranked_2023
    where growth_rank <= 5
),
history as (
    select
        p.geo_id,
        p.geo_name,
        p.year,
        p.pop_total,
        sm.state_abbr,
        sm.growth_rank,
        first_value(p.pop_total) over (
            partition by p.geo_id
            order by p.year
            rows between unbounded preceding and unbounded following
        ) as base_pop_2018
    from gold.population_demographics p
    inner join selected_metros sm
        on p.geo_id = sm.geo_id
    where p.geo_level = 'cbsa'
      and p.year between 2018 and 2023
      and p.pop_total is not null
)
select
    'q008'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    h.geo_id,
    h.geo_name,
    h.state_abbr,
    h.year as period,
    '2018_2023_indexed'::varchar as time_window,
    'pop_total_index_2018eq100'::varchar as metric_id,
    'Population index (2018 = 100)'::varchar as metric_label,
    (h.pop_total / nullif(h.base_pop_2018, 0)) * 100.0 as metric_value,
    'gold.population_demographics + gold.dim_geo'::varchar as source,
    '2026-07-12'::varchar as vintage,
    h.geo_name as series,
    h.growth_rank as rank_desc,
    null::double as benchmark_value,
    'Top 5 2023 growth leaders'::varchar as "group",
    false as highlight_flag,
    (
        'Selected metros are the five highest 2023 CBSA population-growth leaders among markets with population >= 250k. Indexed to 2018 = 100.'
    )::varchar as note
from history h
order by h.growth_rank, h.year;
