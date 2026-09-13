-- Place membership is evidence from population-weighted tract-to-Place edges.
-- It supports context only and never allocates Place permits into a tract score.
with market_places as (
    select edge.target_geo_id as place_id,
           count(distinct edge.source_geo_id) as contributing_tract_count,
           max(edge.quality_flag) as allocation_quality
    from mart_geography.allocation_edges edge
    join mart_geography.rollup_tract_to_cbsa membership
      on edge.source_geo_id = membership.tract_geoid
    where edge.source_geo_level = 'tract'
      and edge.target_geo_level = 'place'
      and edge.weight_basis = 'population'
      and edge.weight > 0
      and membership.cbsa_code = '__CBSA_CODE__'
    group by edge.target_geo_id
)
select q.geo_id as place_id, q.geo_name, q.pop_total, q.permits_total_units,
       q.permits_per_1000_housing_units, q.renter_cost_to_income,
       q.vacancy_rate, market_places.contributing_tract_count,
       market_places.allocation_quality
from market_places
join mart_explanation_q1.supply_demand_base q
  on market_places.place_id = q.geo_id
where q.geo_level = 'place' and q.year = 2024;
