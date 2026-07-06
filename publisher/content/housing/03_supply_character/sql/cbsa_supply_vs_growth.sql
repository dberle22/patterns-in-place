-- Major-CBSA supply-versus-growth inputs for the housing Supply Character section.
-- The chart compares current permit intensity with five-year population growth
-- so we can see which fast-growing metros look supply-responsive versus strained.

with base as (
    select
        c.geo_id,
        c.geo_name,
        c.region_name,
        c.division_name,
        c.cbsa_pop_2024,
        c.permits_per_1000_housing_units,
        c.pop_growth_5yr * 100.0 as pop_growth_5yr_pct
    from mart_housing.core_metrics c
    where c.geo_level = 'cbsa'
      and c.year = 2024
      and c.major_cbsa_100k_flag
      and coalesce(c.state_abbr, '') <> 'PR'
      and c.permits_per_1000_housing_units is not null
      and c.pop_growth_5yr is not null
      and not isnan(c.permits_per_1000_housing_units)
      and not isinf(c.permits_per_1000_housing_units)
      and not isnan(c.pop_growth_5yr)
      and not isinf(c.pop_growth_5yr)
),
ranked as (
    select
        b.*,
        row_number() over (
            order by
                case when b.pop_growth_5yr_pct > 0 then b.pop_growth_5yr_pct end desc nulls last,
                b.geo_name
        ) as positive_growth_rank,
        row_number() over (
            order by
                case when b.permits_per_1000_housing_units > 20 then b.pop_growth_5yr_pct end desc nulls last,
                b.geo_name
        ) as high_supply_growth_rank,
        row_number() over (
            order by
                case when b.permits_per_1000_housing_units < 10 then b.pop_growth_5yr_pct end desc nulls last,
                b.geo_name
        ) as low_supply_growth_rank
    from base b
)
select
    'cbsa'::varchar as geo_level,
    r.geo_id,
    r.geo_name,
    '2024_snapshot_vs_2019_2024_growth'::varchar as time_window,
    r.permits_per_1000_housing_units as x_value,
    r.pop_growth_5yr_pct as y_value,
    'Permits per 1,000 housing units, 2024'::varchar as x_label,
    'Population growth, 2019 to 2024 (%)'::varchar as y_label,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    r.region_name as "group",
    r.cbsa_pop_2024 as size_value,
    (
        (r.permits_per_1000_housing_units > 20 and r.high_supply_growth_rank <= 4) or
        (r.permits_per_1000_housing_units < 10 and r.low_supply_growth_rank <= 4)
    ) as label_flag,
    (
        'Division: ' || r.division_name ||
        ' | Major CBSA universe uses the temporary 100k-population section flag.'
    )::varchar as note,
    'permits_per_1000_housing_units'::varchar as x_metric_id,
    'pop_growth_5yr_pct'::varchar as y_metric_id
from ranked r
order by r.pop_growth_5yr_pct desc, r.geo_name;
