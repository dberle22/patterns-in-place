-- Common-grain benchmark only: Q1 does not inherit the publisher composite.
select q.geo_id as cbsa_code, q.geo_name as cbsa_name,
       publisher.provisional_overheating_score,
       publisher.momentum_component_score,
       publisher.pressure_component_score,
       publisher.strain_component_score,
       publisher.tightness_component_score
from mart_explanation_q1.supply_demand_base q
join mart_housing.overheating_matrix publisher
  on q.geo_level = publisher.geo_level
 and q.geo_id = publisher.geo_id
 and q.year = publisher.year
where q.geo_level = 'cbsa' and q.year = 2024;
