-- Tract evidence remains direct and 2020-vintage for the current snapshot.
select q.geo_id as tract_geoid, q.geo_name as tract_name, q.year, q.pop_total,
       q.hu_total, q.vacancy_rate, q.annualized_median_rent, q.median_hh_income,
       q.median_rent_to_all_hh_income_proxy, q.owner_cost_to_income_mortgage,
       q.owner_cost_to_income_no_mortgage, q.pct_rent_burden_30plus,
       q.pop_growth_1yr, q.pop_growth_5yr, q.pct_struct_multifam
from mart_explanation_q1.supply_demand_base q
join mart_geography.rollup_tract_to_cbsa membership
  on q.geo_id = membership.tract_geoid
where q.geo_level = 'tract' and q.year = 2024
  and membership.cbsa_code = '__CBSA_CODE__';
