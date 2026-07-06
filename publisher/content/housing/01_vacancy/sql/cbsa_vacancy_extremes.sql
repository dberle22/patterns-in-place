-- Major-CBSA vacancy extremes for the housing Vacancy section.
-- We keep the business logic light:
-- - reuse the shared 2024 core mart
-- - filter to major CBSAs now
-- - return separate top/bottom framing for the notebook to render as two bars

with base as (
    select
        c.geo_level,
        c.geo_id,
        c.geo_name,
        c.state_abbr,
        c.region_name,
        c.division_name,
        c.vacancy_rate
    from mart_housing.core_metrics c
    where c.geo_level = 'cbsa'
      and c.year = 2024
      and c.major_cbsa_100k_flag
      and coalesce(c.state_abbr, '') <> 'PR'
      and c.vacancy_rate is not null
      and not isnan(c.vacancy_rate)
      and not isinf(c.vacancy_rate)
),
us_benchmark as (
    select
        sum(c.hu_total * c.vacancy_rate) / nullif(sum(c.hu_total), 0) as us_vacancy_rate
    from mart_housing.core_metrics c
    where c.geo_level = 'state'
      and c.year = 2024
      and c.state_abbr <> 'PR'
      and c.vacancy_rate is not null
      and c.hu_total is not null
),
tightest as (
    select
        row_number() over (order by b.vacancy_rate asc, b.geo_name) as rank,
        b.*
    from base b
),
loosest as (
    select
        row_number() over (order by b.vacancy_rate desc, b.geo_name) as rank,
        b.*
    from base b
)
select
    'vacancy_bar_tightest'::varchar as question_id,
    t.geo_level,
    t.geo_id,
    t.geo_name,
    '2024_snapshot'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    t.vacancy_rate as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    t.rank,
    'Tightest major CBSAs'::varchar as "group",
    null::varchar as series,
    null::double as share_value,
    false as highlight_flag,
    ub.us_vacancy_rate as benchmark_value,
    (
        'Region: ' || t.region_name ||
        ' | Division: ' || t.division_name ||
        ' | Major CBSA universe uses the temporary 100k-population section flag.'
    )::varchar as note
from tightest t
cross join us_benchmark ub
where t.rank <= 10

union all

select
    'vacancy_bar_loosest'::varchar as question_id,
    l.geo_level,
    l.geo_id,
    l.geo_name,
    '2024_snapshot'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    l.vacancy_rate as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    l.rank,
    'Loosest major CBSAs'::varchar as "group",
    null::varchar as series,
    null::double as share_value,
    false as highlight_flag,
    ub.us_vacancy_rate as benchmark_value,
    (
        'Region: ' || l.region_name ||
        ' | Division: ' || l.division_name ||
        ' | Major CBSA universe uses the temporary 100k-population section flag.'
    )::varchar as note
from loosest l
cross join us_benchmark ub
where l.rank <= 10
order by question_id, rank;
