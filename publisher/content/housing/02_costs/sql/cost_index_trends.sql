-- Indexed rent and home-value trend inputs for the housing Costs section.
-- We keep the logic explicit here so the visual script can focus on indexing and
-- presentation:
-- - United States level from the shared Gold mart
-- - housing-unit-weighted major-CBSA averages from the shared core mart
-- - 2019 through 2024 only for the first-pass cost run-up framing

with us_series as (
    select
        'United States'::varchar as scope_name,
        year as period,
        annualized_median_rent,
        median_home_value
    from gold.housing_core_wide
    where geo_level = 'us'
      and year between 2019 and 2024
      and annualized_median_rent is not null
      and median_home_value is not null
),
major_cbsa_series as (
    select
        'Major CBSA average'::varchar as scope_name,
        c.year as period,
        sum(c.hu_total * c.annualized_median_rent) / nullif(sum(c.hu_total), 0) as annualized_median_rent,
        sum(c.hu_total * c.median_home_value) / nullif(sum(c.hu_total), 0) as median_home_value
    from mart_housing.core_metrics c
    where c.geo_level = 'cbsa'
      and c.year between 2019 and 2024
      and c.major_cbsa_100k_flag
      and coalesce(c.state_abbr, '') <> 'PR'
      and c.hu_total is not null
      and c.annualized_median_rent is not null
      and c.median_home_value is not null
      and not isnan(c.annualized_median_rent)
      and not isinf(c.annualized_median_rent)
      and not isnan(c.median_home_value)
      and not isinf(c.median_home_value)
    group by c.year
),
all_series as (
    select * from us_series
    union all
    select * from major_cbsa_series
)
select
    'cost_index_trends'::varchar as question_id,
    case when s.scope_name = 'United States' then 'us' else 'cbsa' end as geo_level,
    case
        when s.scope_name = 'United States' then 'us_rent'
        else 'major_cbsa_rent'
    end::varchar as geo_id,
    'Annualized rent'::varchar as geo_name,
    s.period,
    '2019_to_2024_index'::varchar as time_window,
    'indexed_cost_level'::varchar as metric_id,
    'Indexed housing cost level'::varchar as metric_label,
    s.annualized_median_rent as metric_value,
    'gold.housing_core_wide + mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    s.scope_name as "group",
    false as highlight_flag,
    null::double as benchmark_value,
    2019 as index_base_period,
    'Housing-unit-weighted rent level for major-metro comparison series.'::varchar as note
from all_series s

union all

select
    'cost_index_trends'::varchar as question_id,
    case when s.scope_name = 'United States' then 'us' else 'cbsa' end as geo_level,
    case
        when s.scope_name = 'United States' then 'us_home_value'
        else 'major_cbsa_home_value'
    end::varchar as geo_id,
    'Home value'::varchar as geo_name,
    s.period,
    '2019_to_2024_index'::varchar as time_window,
    'indexed_cost_level'::varchar as metric_id,
    'Indexed housing cost level'::varchar as metric_label,
    s.median_home_value as metric_value,
    'gold.housing_core_wide + mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    s.scope_name as "group",
    false as highlight_flag,
    null::double as benchmark_value,
    2019 as index_base_period,
    'Housing-unit-weighted home-value level for major-metro comparison series.'::varchar as note
from all_series s
order by "group", geo_name, period;
