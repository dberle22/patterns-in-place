-- CBSA vacancy distributions for the housing Vacancy section.
-- We build both grouped cuts now:
-- - major CBSAs by Census region
-- - major CBSAs by Census division
-- `major_cbsa_100k_flag` is the temporary section proxy for the
-- Intelligence Layer's major-market universe.

with base as (
    select
        c.geo_level,
        c.geo_id,
        c.geo_name,
        c.region_name,
        c.division_name,
        c.state_abbr,
        c.vacancy_rate
    from mart_housing.core_metrics c
    where c.geo_level = 'cbsa'
      and c.year = 2024
      and c.major_cbsa_100k_flag
      and coalesce(c.state_abbr, '') <> 'PR'
      and c.region_name is not null
      and c.division_name is not null
      and c.vacancy_rate is not null
      and not isnan(c.vacancy_rate)
      and not isinf(c.vacancy_rate)
)
select
    'vacancy_boxplot_region'::varchar as question_id,
    b.geo_level,
    b.geo_id,
    b.geo_name,
    '2024_snapshot'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    b.vacancy_rate as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    b.region_name as "group",
    false as highlight_flag,
    false as label_flag,
    null::double as weight_value,
    null::double as benchmark_value,
    'Major CBSA universe uses the temporary 100k-population section flag.'::varchar as note
from base b

union all

select
    'vacancy_boxplot_division'::varchar as question_id,
    b.geo_level,
    b.geo_id,
    b.geo_name,
    '2024_snapshot'::varchar as time_window,
    'vacancy_rate'::varchar as metric_id,
    'Vacancy rate'::varchar as metric_label,
    b.vacancy_rate as metric_value,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    b.division_name as "group",
    false as highlight_flag,
    false as label_flag,
    null::double as weight_value,
    null::double as benchmark_value,
    'Major CBSA universe uses the temporary 100k-population section flag.'::varchar as note
from base b
order by question_id, "group", geo_name;
