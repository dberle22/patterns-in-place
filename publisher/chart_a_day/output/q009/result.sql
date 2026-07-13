select
    'q009'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    h.geo_id,
    h.geo_name,
    d.state_abbr,
    '2023_snapshot'::varchar as time_window,
    'rent_to_income'::varchar as metric_id,
    'Rent-to-income (%)'::varchar as metric_label,
    h.rent_to_income * 100.0 as metric_value,
    'gold.housing_core_wide + gold.dim_geo'::varchar as source,
    '2026-07-12'::varchar as vintage,
    'All major CBSAs'::varchar as "group",
    false as highlight_flag,
    false as label_flag,
    null::double as weight_value,
    null::double as benchmark_value,
    (
        'Distribution includes CBSAs with population >= 250k in 2023. Values are shown in percentage points for readability.'
    )::varchar as note
from gold.housing_core_wide h
inner join gold.dim_geo d
    on h.geo_level = d.geo_level
   and h.geo_id = d.geo_id
where h.geo_level = 'cbsa'
  and h.year = 2023
  and h.pop_total >= 250000
  and coalesce(d.state_abbr, '') <> 'PR'
  and h.rent_to_income is not null
order by h.rent_to_income desc, h.geo_name;
