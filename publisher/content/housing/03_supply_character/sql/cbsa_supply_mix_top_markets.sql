-- Major-CBSA supply-mix comparison inputs for the housing Supply Character section.
-- We limit the chart to the fastest-building major metros so the mix comparison
-- stays readable as a publishable first-pass artifact.

with base as (
    select
        c.geo_id,
        c.geo_name,
        c.region_name,
        c.division_name,
        c.permits_per_1000_housing_units,
        c.permits_share_multifam_units,
        c.permits_share_units_1_unit,
        c.pct_struct_multifam,
        c.pct_struct_1_unit,
        greatest(
            1.0 - coalesce(c.pct_struct_multifam, 0) - coalesce(c.pct_struct_1_unit, 0),
            0.0
        ) as pct_struct_other
    from mart_housing.core_metrics c
    where c.geo_level = 'cbsa'
      and c.year = 2024
      and c.major_cbsa_100k_flag
      and coalesce(c.state_abbr, '') <> 'PR'
      and c.permits_per_1000_housing_units is not null
      and c.permits_share_multifam_units is not null
      and c.permits_share_units_1_unit is not null
      and c.pct_struct_multifam is not null
      and c.pct_struct_1_unit is not null
),
top_markets as (
    select
        row_number() over (
            order by b.permits_per_1000_housing_units desc, b.geo_name
        ) as permit_rank,
        b.*
    from base b
    qualify permit_rank <= 15
)
select
    'supply_mix_permits'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    '2024_snapshot'::varchar as time_window,
    'share'::varchar as metric_id,
    'Share of units (%)'::varchar as metric_label,
    t.permits_share_units_1_unit * 100.0 as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    'Single-unit permits'::varchar as series,
    t.permit_rank,
    t.permits_per_1000_housing_units as benchmark_value,
    (
        'Region: ' || t.region_name ||
        ' | Division: ' || t.division_name ||
        ' | Ranked by permits per 1,000 housing units.'
    )::varchar as note
from top_markets t

union all

select
    'supply_mix_permits'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    '2024_snapshot'::varchar as time_window,
    'share'::varchar as metric_id,
    'Share of units (%)'::varchar as metric_label,
    t.permits_share_multifam_units * 100.0 as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    'Multifamily permits'::varchar as series,
    t.permit_rank,
    t.permits_per_1000_housing_units as benchmark_value,
    (
        'Region: ' || t.region_name ||
        ' | Division: ' || t.division_name ||
        ' | Ranked by permits per 1,000 housing units.'
    )::varchar as note
from top_markets t

union all

select
    'supply_mix_stock'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    '2024_snapshot'::varchar as time_window,
    'share'::varchar as metric_id,
    'Share of units (%)'::varchar as metric_label,
    t.pct_struct_1_unit * 100.0 as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    'Single-unit stock'::varchar as series,
    t.permit_rank,
    t.permits_per_1000_housing_units as benchmark_value,
    (
        'Region: ' || t.region_name ||
        ' | Division: ' || t.division_name ||
        ' | Stock chart includes an Other category for mobile or uncategorized structure types.'
    )::varchar as note
from top_markets t

union all

select
    'supply_mix_stock'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    '2024_snapshot'::varchar as time_window,
    'share'::varchar as metric_id,
    'Share of units (%)'::varchar as metric_label,
    t.pct_struct_multifam * 100.0 as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    'Multifamily stock'::varchar as series,
    t.permit_rank,
    t.permits_per_1000_housing_units as benchmark_value,
    (
        'Region: ' || t.region_name ||
        ' | Division: ' || t.division_name ||
        ' | Stock chart includes an Other category for mobile or uncategorized structure types.'
    )::varchar as note
from top_markets t

union all

select
    'supply_mix_stock'::varchar as question_id,
    'cbsa'::varchar as geo_level,
    t.geo_id,
    t.geo_name,
    '2024_snapshot'::varchar as time_window,
    'share'::varchar as metric_id,
    'Share of units (%)'::varchar as metric_label,
    t.pct_struct_other * 100.0 as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    'Other stock types'::varchar as series,
    t.permit_rank,
    t.permits_per_1000_housing_units as benchmark_value,
    (
        'Region: ' || t.region_name ||
        ' | Division: ' || t.division_name ||
        ' | Stock chart includes an Other category for mobile or uncategorized structure types.'
    )::varchar as note
from top_markets t
order by question_id, permit_rank, series;
