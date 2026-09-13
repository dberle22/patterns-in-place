-- Replace the quoted token before running. CBSA rows use their own geo_id;
-- county rows carry the governed parent CBSA code from dim_geo.
select geo_level, geo_id, geo_name, year, pop_total, renter_cost_to_income,
       owner_cost_to_income_mortgage, vacancy_rate,
       permits_per_1000_housing_units, pop_growth_5yr, hpi_5yr_pct,
       irs_net_migration_rate
from mart_explanation_q1.supply_demand_base
where (geo_level = 'cbsa' and geo_id = '__CBSA_CODE__')
   or (geo_level = 'county' and cbsa_code = '__CBSA_CODE__')
order by geo_level, geo_name, year;
