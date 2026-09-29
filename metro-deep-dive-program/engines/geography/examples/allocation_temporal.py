"""Examples use relationship helpers; aggregation remains metric-aware."""

from geography import allocation_edges, temporal_edges

# A consumer joins these rows to an additive tract metric and multiplies by
# weight. Rates, medians, and indexes need a metric-specific calculation.
place_population_edges = allocation_edges(con, target_level="place", basis="population")

# A 2010 count can be restated on the 2020 tract backbone with these edges.
# Keep change_type and quality_flag in any consumer-facing result.
tract_population_edges = temporal_edges(con, basis="population")
