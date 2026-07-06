-- Major-CBSA cost correlation matrix inputs for the housing Costs section.
-- The goal is to center the matrix on 2019-to-2024 home-value and rent growth
-- while adding a small set of affordability, tightness, and pressure context
-- fields that help explain what tends to move with those cost changes.

with cbsa_2019 as (
    select
        geo_id,
        geo_name,
        annualized_median_rent,
        median_home_value
    from mart_housing.core_metrics
    where geo_level = 'cbsa'
      and year = 2019
      and major_cbsa_100k_flag
      and coalesce(state_abbr, '') <> 'PR'
),
cbsa_2024 as (
    select
        geo_id,
        geo_name,
        vacancy_rate,
        rent_to_income,
        value_to_income,
        acs_income_pc_growth_5yr,
        pop_growth_5yr,
        annualized_median_rent,
        median_home_value
    from mart_housing.core_metrics
    where geo_level = 'cbsa'
      and year = 2024
      and major_cbsa_100k_flag
      and coalesce(state_abbr, '') <> 'PR'
),
metric_frame as (
    select
        c24.geo_id,
        c24.geo_name,
        ((c24.median_home_value / nullif(c19.median_home_value, 0)) - 1.0) * 100.0 as home_value_growth_pct,
        ((c24.annualized_median_rent / nullif(c19.annualized_median_rent, 0)) - 1.0) * 100.0 as rent_growth_pct,
        (c24.vacancy_rate - c19_geo.vacancy_rate) * 100.0 as vacancy_change_pp,
        c24.rent_to_income * 100.0 as rent_to_income_pct,
        c24.value_to_income as value_to_income,
        c24.acs_income_pc_growth_5yr * 100.0 as income_pc_growth_5yr_pct,
        c24.pop_growth_5yr * 100.0 as pop_growth_5yr_pct
    from cbsa_2024 c24
    inner join cbsa_2019 c19
        on c24.geo_id = c19.geo_id
    inner join (
        select geo_id, vacancy_rate
        from mart_housing.core_metrics
        where geo_level = 'cbsa'
          and year = 2019
          and major_cbsa_100k_flag
          and coalesce(state_abbr, '') <> 'PR'
    ) c19_geo
        on c24.geo_id = c19_geo.geo_id
)
select
    'cbsa'::varchar as geo_level,
    m.geo_id,
    m.geo_name,
    '2019_to_2024_growth_and_2024_snapshot'::varchar as time_window,
    'home_value_growth_pct'::varchar as metric_id,
    'Home-value growth, 2019 to 2024 (%)'::varchar as metric_label,
    m.home_value_growth_pct as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    true as include_flag
from metric_frame m

union all

select
    'cbsa'::varchar as geo_level,
    m.geo_id,
    m.geo_name,
    '2019_to_2024_growth_and_2024_snapshot'::varchar as time_window,
    'rent_growth_pct'::varchar as metric_id,
    'Rent growth, 2019 to 2024 (%)'::varchar as metric_label,
    m.rent_growth_pct as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    true as include_flag
from metric_frame m

union all

select
    'cbsa'::varchar as geo_level,
    m.geo_id,
    m.geo_name,
    '2019_to_2024_growth_and_2024_snapshot'::varchar as time_window,
    'vacancy_change_pp'::varchar as metric_id,
    'Vacancy change, 2019 to 2024 (pp)'::varchar as metric_label,
    m.vacancy_change_pp as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    true as include_flag
from metric_frame m

union all

select
    'cbsa'::varchar as geo_level,
    m.geo_id,
    m.geo_name,
    '2019_to_2024_growth_and_2024_snapshot'::varchar as time_window,
    'rent_to_income_pct'::varchar as metric_id,
    'Rent-to-income, 2024 (%)'::varchar as metric_label,
    m.rent_to_income_pct as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    true as include_flag
from metric_frame m

union all

select
    'cbsa'::varchar as geo_level,
    m.geo_id,
    m.geo_name,
    '2019_to_2024_growth_and_2024_snapshot'::varchar as time_window,
    'value_to_income'::varchar as metric_id,
    'Value-to-income, 2024 (ratio)'::varchar as metric_label,
    m.value_to_income as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    true as include_flag
from metric_frame m

union all

select
    'cbsa'::varchar as geo_level,
    m.geo_id,
    m.geo_name,
    '2019_to_2024_growth_and_2024_snapshot'::varchar as time_window,
    'income_pc_growth_5yr_pct'::varchar as metric_id,
    'Income per-capita growth, 2019 to 2024 (%)'::varchar as metric_label,
    m.income_pc_growth_5yr_pct as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    true as include_flag
from metric_frame m

union all

select
    'cbsa'::varchar as geo_level,
    m.geo_id,
    m.geo_name,
    '2019_to_2024_growth_and_2024_snapshot'::varchar as time_window,
    'pop_growth_5yr_pct'::varchar as metric_id,
    'Population growth, 2019 to 2024 (%)'::varchar as metric_label,
    m.pop_growth_5yr_pct as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    true as include_flag
from metric_frame m;
