-- A tract-count metric allocated to Census Places. The basis is explicit and
-- quality remains visible; do not apply this pattern to rates or medians.
select edge.target_geo_id as place_geoid,
       sum(metric.value * edge.weight) as allocated_value,
       max(edge.quality_flag) as allocation_quality
from some_tract_metric as metric
join mart_geography.allocation_edges as edge
  on metric.tract_geoid = edge.source_geo_id
where edge.target_geo_level = 'place'
  and edge.weight_basis = 'population'
group by 1;

-- A 2010 tract-count metric restated to 2020 tracts. Preserve the change type
-- so downstream presentation can disclose a split or redrawn geography.
select edge.to_geo_id as tract_geoid_2020,
       sum(metric.value * edge.weight) as restated_value,
       max(edge.change_type) as boundary_change_type
from some_2010_tract_metric as metric
join mart_geography.temporal_edges as edge
  on metric.tract_geoid_2010 = edge.from_geo_id
where edge.weight_basis = 'population'
group by 1;
