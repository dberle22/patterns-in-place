with miami_value as (
    select
        h.geo_id,
        h.geo_name,
        h.year,
        h.pct_rent_burden_30plus,
        d.state_abbr,
        d.region_name
    from gold.housing_core_wide h
    inner join gold.dim_geo d
        on h.geo_level = d.geo_level
       and h.geo_id = d.geo_id
    where h.geo_level = 'cbsa'
      and h.year = 2023
      and h.geo_name = 'Miami-Fort Lauderdale-West Palm Beach, FL'
      and h.pct_rent_burden_30plus is not null
),
us_benchmark as (
    select
        pct_rent_burden_30plus as benchmark_value
    from gold.housing_core_wide
    where geo_level = 'us'
      and year = 2023
      and pct_rent_burden_30plus is not null
)
select
    'q011'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    mv.geo_id,
    mv.geo_name,
    mv.state_abbr,
    mv.year,
    '2023_snapshot'::varchar as time_window,
    'pct_rent_burden_30plus'::varchar as metric_id,
    'Cost-burdened renter share (%)'::varchar as metric_label,
    mv.pct_rent_burden_30plus * 100.0 as metric_value,
    'gold.housing_core_wide + gold.dim_geo'::varchar as source,
    '2026-07-12'::varchar as vintage,
    1::bigint as rank_desc,
    null::bigint as rank_asc,
    ub.benchmark_value * 100.0 as benchmark_value,
    mv.region_name as "group",
    true as highlight_flag,
    true as label_flag,
    'Miami'::varchar as label_text,
    (
        'Single-metro benchmark comparison. National benchmark comes from the United States row in gold.housing_core_wide for 2023.'
    )::varchar as note
from miami_value mv
cross join us_benchmark ub;
