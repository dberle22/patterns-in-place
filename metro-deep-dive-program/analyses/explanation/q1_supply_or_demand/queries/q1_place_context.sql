-- Place permit coverage is intentionally reported both by record and reach.
select year, count(*) as place_count,
       round(100.0 * avg(has_permit_data::int), 1) as permit_row_pct,
       round(100.0 * sum(case when has_permit_data then pop_total else 0 end)
           / nullif(sum(pop_total), 0), 1) as permit_population_weighted_pct
from mart_explanation_q1.supply_demand_base
where geo_level = 'place'
group by year
order by year;
