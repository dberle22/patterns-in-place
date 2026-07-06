-- Housing-unit-weighted vacancy trends for the housing Vacancy section.
-- The section asked for:
-- - national average
-- - weighted CBSA average
-- - weighted region and division averages
-- We keep the weighting explicit in the SQL so the notebook stays focused on
-- framing and rendering.

with us_series as (
    select
        year as period,
        'us'::varchar as geo_level,
        'us'::varchar as geo_id,
        'United States'::varchar as geo_name,
        vacancy_rate as metric_value
    from gold.housing_core_wide
    where geo_level = 'us'
      and year between 2012 and 2024
      and vacancy_rate is not null
      and not isnan(vacancy_rate)
      and not isinf(vacancy_rate)
),
cbsa_weighted as (
    select
        c.year as period,
        'cbsa'::varchar as geo_level,
        'weighted_cbsa'::varchar as geo_id,
        'Major CBSA average'::varchar as geo_name,
        sum(c.hu_total * c.vacancy_rate) / nullif(sum(c.hu_total), 0) as metric_value
    from mart_housing.core_metrics c
    where c.geo_level = 'cbsa'
      and c.major_cbsa_100k_flag
      and coalesce(c.state_abbr, '') <> 'PR'
      and c.year between 2012 and 2024
      and c.vacancy_rate is not null
      and c.hu_total is not null
      and not isnan(c.vacancy_rate)
      and not isinf(c.vacancy_rate)
    group by c.year
),
region_weighted as (
    select
        c.year as period,
        'region'::varchar as geo_level,
        min(c.region_id)::varchar as geo_id,
        c.region_name::varchar as geo_name,
        sum(c.hu_total * c.vacancy_rate) / nullif(sum(c.hu_total), 0) as metric_value
    from mart_housing.core_metrics c
    where c.geo_level = 'state'
      and c.region_name is not null
      and c.state_abbr <> 'PR'
      and c.year between 2012 and 2024
      and c.vacancy_rate is not null
      and c.hu_total is not null
      and not isnan(c.vacancy_rate)
      and not isinf(c.vacancy_rate)
    group by c.year, c.region_name
),
division_weighted as (
    select
        c.year as period,
        'division'::varchar as geo_level,
        min(c.division_id)::varchar as geo_id,
        c.division_name::varchar as geo_name,
        sum(c.hu_total * c.vacancy_rate) / nullif(sum(c.hu_total), 0) as metric_value
    from mart_housing.core_metrics c
    where c.geo_level = 'state'
      and c.division_name is not null
      and c.state_abbr <> 'PR'
      and c.year between 2012 and 2024
      and c.vacancy_rate is not null
      and c.hu_total is not null
      and not isnan(c.vacancy_rate)
      and not isinf(c.vacancy_rate)
    group by c.year, c.division_name
)
select
    'vacancy_trend_regions'::varchar as question_id,
    s.geo_level,
    s.geo_id,
    s.geo_name,
    s.period,
    'level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    s.metric_value,
    'gold.housing_core_wide + mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    'National and region averages'::varchar as "group",
    case when s.geo_name = 'United States' then true else false end as highlight_flag,
    null::double as benchmark_value,
    null::integer as index_base_period,
    'Housing-unit-weighted region and major-CBSA series.'::varchar as note
from (
    select * from us_series
    union all
    select * from cbsa_weighted
    union all
    select * from region_weighted
) s

union all

select
    'vacancy_trend_divisions'::varchar as question_id,
    s.geo_level,
    s.geo_id,
    s.geo_name,
    s.period,
    'level'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    s.metric_value,
    'gold.housing_core_wide + mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    'National and division averages'::varchar as "group",
    case when s.geo_name = 'United States' then true else false end as highlight_flag,
    null::double as benchmark_value,
    null::integer as index_base_period,
    'Housing-unit-weighted division and major-CBSA series.'::varchar as note
from (
    select * from us_series
    union all
    select * from cbsa_weighted
    union all
    select * from division_weighted
) s
order by question_id, geo_name, period;
