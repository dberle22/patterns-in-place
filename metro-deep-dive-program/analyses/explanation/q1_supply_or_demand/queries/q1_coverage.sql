-- National coverage inventory. Place coverage is shown both by rows and by
-- resident population so partial BPS coverage is not mistaken for reach.
select
    geo_level,
    count(*) as row_count,
    count(distinct geo_id) as geography_count,
    round(100.0 * avg(has_core_affordability_data::int), 1) as core_affordability_pct,
    round(100.0 * avg(has_five_year_population_growth::int), 1) as population_growth_5yr_pct,
    round(100.0 * avg(has_permit_data::int), 1) as permit_row_pct,
    round(100.0 * sum(case when has_permit_data then pop_total else 0 end)
        / nullif(sum(pop_total), 0), 1) as permit_population_weighted_pct,
    round(100.0 * avg(has_price_context::int), 1) as price_context_pct
from mart_explanation_q1.supply_demand_base
where year = 2024
group by geo_level
order by geo_level;
