-- The national notebook uses this direct CBSA series for its 2014–2024 context.
select geo_id as cbsa_code, geo_name as cbsa_name, year, pop_total,
       pct_rent_burden_30plus, median_rent_to_all_hh_income_proxy,
       owner_cost_to_income_mortgage,
       vacancy_rate, permits_per_1000_housing_units, pop_growth_5yr,
       hpi_5yr_pct, irs_net_migration_rate
from mart_explanation_q1.supply_demand_base
where geo_level = 'cbsa' and year between 2014 and 2024;
