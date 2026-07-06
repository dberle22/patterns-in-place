-- Major-CBSA vacancy change versus cost change inputs for the housing Costs section.
-- We use a simple 2019-to-2024 before/after framing so the chart can focus on
-- whether tighter markets also saw stronger rent or home-value growth.

with cbsa_2019 as (
    select
        geo_id,
        geo_name,
        region_name,
        division_name,
        state_abbr,
        cbsa_pop_2024,
        vacancy_rate,
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
        region_name,
        division_name,
        state_abbr,
        cbsa_pop_2024,
        vacancy_rate,
        annualized_median_rent,
        median_home_value
    from mart_housing.core_metrics
    where geo_level = 'cbsa'
      and year = 2024
      and major_cbsa_100k_flag
      and coalesce(state_abbr, '') <> 'PR'
),
paired as (
    select
        c24.geo_id,
        c24.geo_name,
        c24.region_name,
        c24.division_name,
        c24.state_abbr,
        c24.cbsa_pop_2024,
        (c24.vacancy_rate - c19.vacancy_rate) * 100.0 as vacancy_change_pp,
        ((c24.annualized_median_rent / nullif(c19.annualized_median_rent, 0)) - 1.0) * 100.0 as rent_growth_pct,
        ((c24.median_home_value / nullif(c19.median_home_value, 0)) - 1.0) * 100.0 as home_value_growth_pct
    from cbsa_2019 c19
    inner join cbsa_2024 c24
        on c19.geo_id = c24.geo_id
    where c19.vacancy_rate is not null
      and c24.vacancy_rate is not null
      and c19.annualized_median_rent is not null
      and c24.annualized_median_rent is not null
      and c19.median_home_value is not null
      and c24.median_home_value is not null
),
rent_panel as (
    select
        p.*,
        'Rent growth'::varchar as cost_metric_label,
        'rent_growth_2019_2024'::varchar as y_metric_id,
        p.rent_growth_pct as y_value,
        row_number() over (
            order by
                case when p.vacancy_change_pp < 0 and p.rent_growth_pct > 0 then p.rent_growth_pct end desc nulls last,
                p.geo_name
        ) as tight_rank,
        row_number() over (
            order by
                case when p.vacancy_change_pp > 0 and p.rent_growth_pct > 0 then p.rent_growth_pct end desc nulls last,
                p.geo_name
        ) as contradiction_rank
    from paired p
),
value_panel as (
    select
        p.*,
        'Home-value growth'::varchar as cost_metric_label,
        'home_value_growth_2019_2024'::varchar as y_metric_id,
        p.home_value_growth_pct as y_value,
        row_number() over (
            order by
                case when p.vacancy_change_pp < 0 and p.home_value_growth_pct > 0 then p.home_value_growth_pct end desc nulls last,
                p.geo_name
        ) as tight_rank,
        row_number() over (
            order by
                case when p.vacancy_change_pp > 0 and p.home_value_growth_pct > 0 then p.home_value_growth_pct end desc nulls last,
                p.geo_name
        ) as contradiction_rank
    from paired p
)
select
    'cbsa'::varchar as geo_level,
    s.geo_id,
    s.geo_name,
    '2019_to_2024_change'::varchar as time_window,
    s.vacancy_change_pp as x_value,
    s.y_value,
    'Vacancy-rate change (percentage points, 2019 to 2024)'::varchar as x_label,
    case
        when s.cost_metric_label = 'Rent growth' then 'Annualized rent growth (%)'
        else 'Home-value growth (%)'
    end::varchar as y_label,
    'mart_housing.core_metrics'::varchar as source,
    '2026-07-05'::varchar as vintage,
    s.cost_metric_label as "group",
    s.region_name,
    s.cbsa_pop_2024 as size_value,
    (
        (s.vacancy_change_pp < 0 and s.tight_rank <= 4) or
        (s.vacancy_change_pp > 0 and s.contradiction_rank <= 3)
    ) as label_flag,
    (
        'Region: ' || s.region_name ||
        ' | Division: ' || s.division_name ||
        ' | Major CBSA universe uses the temporary 100k-population section flag.'
    )::varchar as note,
    'vacancy_change_pp_2019_2024'::varchar as x_metric_id,
    s.y_metric_id
from (
    select * from rent_panel
    union all
    select * from value_panel
) s
where s.y_value is not null
  and not isnan(s.y_value)
  and not isinf(s.y_value)
order by "group", y_value desc, geo_name;
