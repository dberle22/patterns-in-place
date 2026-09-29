-- The renter burden measure and market-price proxy answer different questions.
select geo_level, geo_id, geo_name, pct_rent_burden_30plus,
       pct_rent_burden_30plus_change_5yr, median_rent_to_all_hh_income_proxy,
       owner_cost_to_income_mortgage, owner_cost_to_income_no_mortgage,
       value_to_income, value_to_income_change_5yr
from mart_explanation_q1.supply_demand_base
where year = 2024 and geo_level in ('cbsa', 'county', 'tract', 'zcta', 'place');
