-- Renter and owner affordability stay separate even when shown together.
select geo_level, geo_id, geo_name, renter_cost_to_income,
       owner_cost_to_income_mortgage, owner_cost_to_income_no_mortgage,
       renter_inexpensive_30_flag, renter_stress_test_50_flag
from mart_explanation_q1.supply_demand_base
where year = 2024 and geo_level in ('cbsa', 'county', 'tract', 'zcta', 'place');
