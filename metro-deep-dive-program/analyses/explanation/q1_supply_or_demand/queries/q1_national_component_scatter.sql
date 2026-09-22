-- National 2024 ACS snapshot. FHFA and ACS five-year fields use the same
-- endpoint; Zillow is retained only as optional diagnostic context.
select b.geo_id as cbsa_code, b.geo_name as cbsa_name, d.cbsa_type_short, b.pop_total,
       pct_rent_burden_30plus, pct_rent_burden_30plus_change_5yr,
       median_rent_to_all_hh_income_proxy, value_to_income,
       value_to_income_change_5yr, vacancy_rate,
       permits_per_1000_housing_units, permits_5yr_per_1000_start_units,
       housing_unit_growth_5yr, pop_growth_5yr, mobility_rate, hpi_5yr_pct,
       rent_growth_5yr, zhvi_annual_avg_yoy_pct, zori_annual_avg_yoy_pct
from mart_explanation_q1.supply_demand_base b
left join gold.dim_geo d on d.geo_level = 'cbsa' and d.geo_id = b.geo_id
where b.geo_level = 'cbsa' and b.year = 2024
  and pct_rent_burden_30plus is not null
  and vacancy_rate is not null
  and permits_per_1000_housing_units is not null
  and pop_growth_5yr is not null;
