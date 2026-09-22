-- Place display geometry is Census 2024 cartographic-boundary geometry. The
-- membership rule remains context only: overlapping Places never partition a
-- CBSA or allocate their permits to tracts.
with market_places as (
    select distinct edge.target_geo_id as place_id
    from mart_geography.allocation_edges edge
    join mart_geography.rollup_tract_to_cbsa membership
      on edge.source_geo_id = membership.tract_geoid
    where edge.source_geo_level = 'tract'
      and edge.target_geo_level = 'place'
      and edge.weight_basis = 'population'
      and edge.weight > 0
      and membership.cbsa_code = '__CBSA_CODE__'
)
select q.geo_id as place_id, q.geo_name, q.pct_rent_burden_30plus,
       q.median_rent_to_all_hh_income_proxy, q.vacancy_rate, q.pop_growth_5yr,
       q.permits_per_1000_housing_units, q.permits_total_units, geometry.geom_wkb
from market_places
join mart_explanation_q1.supply_demand_base q on market_places.place_id = q.geo_id
join geo.places_display geometry on q.geo_id = geometry.place_geoid
where q.geo_level = 'place' and q.year = 2024;
