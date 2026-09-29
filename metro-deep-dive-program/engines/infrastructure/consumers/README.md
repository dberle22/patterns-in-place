# Infrastructure Consumer Handoff

The first consumer interface is the validated local Parquet artifact at
`validated/osm_core_v1/infrastructure_feature.parquet`, resolved by
`publish_infrastructure_interface.py`. It is read-only and source-faithful:
consumers retain the geometry, governed feature classification, raw OSM tags,
and source-run provenance rather than receiving a precomputed barrier,
network, access, or corridor result.

The interface is currently a **serving candidate**. Its source run records a
`legacy_unclassified` CBSA boundary, so an analysis may inspect or prototype
against it but must not publish an authoritative market-boundary result until
Geography supplies analytical CBSA geometry and the run is rebuilt.

The declared consumers and allowed fields are in
[`infrastructure_consumer_interface_v1.yml`](infrastructure_consumer_interface_v1.yml).
No analysis has adopted this interface unchanged yet. When one does, add the
analysis name, market, source-run ID, and interface version to that registry;
do not alter the infrastructure artifact to embed the analysis method.

## Census Place physical-context interface

`build_place_overlap.py` materializes a separate local interface after
Geography provides `geo.places_analysis`. Its feature-overlap artifact is
keyed by source run, retained source record, Census Place, and Place boundary
vintage; it records only positive-measure intersections. Its Place summary is
grouped by feature group, type, and form, with line length and polygon area in
separate columns. The companion QA surface reports Place and feature coverage
instead of fabricating zero-overlap rows.

This is relationship context for Q6, not an anchor result. It does not assert
barriers, connectivity, travel time, access, or an infrastructure score.
