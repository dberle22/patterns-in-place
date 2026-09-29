-- Annual major-CBSA context for local trend charts. The weighted mean reflects
-- the resident experience; the unweighted 25th–75th percentiles show the
-- breadth of the CBSA distribution without making a narrow local axis appear
-- to be a large national movement.
with cbsa as (
    select *
    from mart_explanation_q1.supply_demand_base
    where geo_level = 'cbsa' and pop_total >= 100000
)
select
    year,
    sum(pct_rent_burden_30plus * pop_total) / nullif(sum(case when pct_rent_burden_30plus is not null then pop_total end), 0) as renter_burden_weighted_mean,
    quantile_cont(pct_rent_burden_30plus, 0.25) as renter_burden_p25,
    quantile_cont(pct_rent_burden_30plus, 0.75) as renter_burden_p75,
    sum(value_to_income * pop_total) / nullif(sum(case when value_to_income is not null then pop_total end), 0) as value_to_income_weighted_mean,
    quantile_cont(value_to_income, 0.25) as value_to_income_p25,
    quantile_cont(value_to_income, 0.75) as value_to_income_p75,
    sum(vacancy_rate * pop_total) / nullif(sum(case when vacancy_rate is not null then pop_total end), 0) as vacancy_weighted_mean,
    quantile_cont(vacancy_rate, 0.25) as vacancy_p25,
    quantile_cont(vacancy_rate, 0.75) as vacancy_p75,
    sum(permits_per_1000_housing_units * pop_total) / nullif(sum(case when permits_per_1000_housing_units is not null then pop_total end), 0) as permits_weighted_mean,
    quantile_cont(permits_per_1000_housing_units, 0.25) as permits_p25,
    quantile_cont(permits_per_1000_housing_units, 0.75) as permits_p75,
    sum(housing_unit_growth_5yr * pop_total) / nullif(sum(case when housing_unit_growth_5yr is not null then pop_total end), 0) as housing_growth_weighted_mean,
    quantile_cont(housing_unit_growth_5yr, 0.25) as housing_growth_p25,
    quantile_cont(housing_unit_growth_5yr, 0.75) as housing_growth_p75,
    sum(pop_growth_5yr * pop_total) / nullif(sum(case when pop_growth_5yr is not null then pop_total end), 0) as population_growth_weighted_mean,
    quantile_cont(pop_growth_5yr, 0.25) as population_growth_p25,
    quantile_cont(pop_growth_5yr, 0.75) as population_growth_p75
from cbsa
group by year
order by year;
