-- Raw CBSA component inputs used for the national supply-versus-demand scatter.
select b.geo_id as cbsa_code, b.geo_name as cbsa_name, d.cbsa_type_short, b.pop_total,
       renter_cost_to_income, vacancy_rate, permits_per_1000_housing_units,
       pop_growth_5yr, mobility_rate, hpi_5yr_pct, zhvi_annual_avg_yoy_pct,
       zori_annual_avg_yoy_pct
from mart_explanation_q1.supply_demand_base b
left join gold.dim_geo d on d.geo_level = 'cbsa' and d.geo_id = b.geo_id
where b.geo_level = 'cbsa' and b.year = 2024
  and renter_cost_to_income is not null
  and vacancy_rate is not null
  and permits_per_1000_housing_units is not null
  and pop_growth_5yr is not null;
