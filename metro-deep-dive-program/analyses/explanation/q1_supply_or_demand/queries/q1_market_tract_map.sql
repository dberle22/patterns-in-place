-- WKB is decoded in Python so this reader works without loading DuckDB Spatial.
select q.geo_id as tract_geoid, q.pct_rent_burden_30plus,
       q.median_rent_to_all_hh_income_proxy, q.vacancy_rate, q.pop_growth_5yr,
       q.annualized_median_rent, geography.geom_wkb
from mart_explanation_q1.supply_demand_base q
join mart_geography.rollup_tract_to_cbsa membership
  on q.geo_id = membership.tract_geoid
join geo.tracts_all_us geography on q.geo_id = geography.tract_geoid
where q.geo_level = 'tract' and q.year = 2024
  and membership.cbsa_code = '__CBSA_CODE__';
