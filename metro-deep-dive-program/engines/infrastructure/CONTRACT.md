# Infrastructure Engine Contract

Status: Epics 1–5 complete on 2026-09-08. Product names below are logical
names, not yet materialized DuckDB table names. Epic 2 records the current
Geography geometry role as `legacy_unclassified`; it is a clipped source-run
boundary, not a substitute for a future materialized analytical CBSA geometry.
The Epic 4 artifacts are geometry-validated serving candidates, not promoted
consumer-serving layers, until Geography supplies that analytical geometry.

## Contract boundary

The engine converts a declared source release and a governed market boundary
into source-faithful physical **line and polygon** features with reviewable
classification, geometry, and coverage evidence. A consumer can filter or
spatially relate those features, but cannot infer source identity, raw tag
evidence, or boundary vintage not published by the engine.

The engine does **not** create a routable graph, calculate travel time or
access, decide that a feature is a barrier, build catchments, or identify
corridors. Place-like points belong to the POI Engine; a source point retained
by an extract is audit evidence rather than a core infrastructure serving
feature.

## Logical products and grains

| Product | Grain | Required result |
|---|---|---|
| `infrastructure_source_run` | one source release × governed boundary × run | Reproducible provider, release, source asset, boundary, query, timing, and row-accounting evidence |
| `infrastructure_source_feature` | one source feature × source release × source geometry | Source-faithful line or polygon record, raw tags, source geometry, and validation outcome |
| `infrastructure_mapping_rule` | one versioned source-tag rule | Explicit governed `feature_group` and `feature_type` decision, rationale, status, and rule evidence |
| `infrastructure_feature` | one retained source feature × mapping version × market boundary | Validated, clipped analytical geometry with governed classification and run provenance |
| `infrastructure_display_feature` | one retained serving feature × display derivative | Optional simplified geometry; never replaces analytical geometry |
| `infrastructure_qa_*` | run × applicable feature/mapping/geometry group | Source accounting, coverage, validity, rejection, mapping, and review samples |

## Core feature record

`infrastructure_feature` is the serving record. Each retained record must
carry the fields below. A source may add fields but cannot substitute
unversioned display fields for them.

| Field group | Required fields | Rule |
|---|---|---|
| Identity | `source_system`, `source_release`, `source_feature_id`, `source_geometry_id`, `source_record_key` | `source_record_key` is a deterministic combination of source system, release, source feature identity, and source geometry identity where a source distinguishes them. It is not a cross-source real-world identity claim. |
| Classification | `feature_group`, `feature_type`, `feature_form`, `mapping_version`, `mapping_status`, `mapping_rule_id`, `mapping_evidence`, `review_status` | Core groups are `road`, `rail`, and `water_network`; `feature_form` distinguishes `linear` and `surface` water. Types stay source-supported and documented. `mapping_status` is `mapped`, `unmapped`, `ambiguous`, or `overridden`. |
| Source content | `source_name`, `source_tags`, `source_attributes` | Preserve raw OSM/provider tags and selected source attributes in structured form. Absent tags are null; governed values are not written back as raw tags. |
| Geometry | `geometry`, `geometry_type`, `source_crs`, `analytical_crs`, `geometry_status` | Analytical geometry is line or polygon, clipped to the governed boundary where needed. The source geometry and its CRS remain traceable. |
| Provenance | `market_id`, `market_boundary_geo_level`, `market_boundary_vintage`, `source_run_id`, `extracted_at`, `source_asset_uri`, `source_asset_checksum`, `source_query` | `market_id` is the Geography Engine's CBSA identity, not a market slug. A source release and extract time are distinct. A null checksum is explicit when unavailable. |
| Validation | `record_status`, `rejection_reason`, `is_within_market_boundary`, `was_clipped`, `was_repaired` | `record_status` is `retained` or `rejected`; rejection preserves identity, tags, geometry when present, and provenance. |

The engine publishes WGS 84 source geometry for interchange and declares an
appropriate projected analytical CRS whenever it performs length, area,
buffer, simplification, or repair. It does not promise one national projected
CRS.

## Classification boundary

The first governed contract is deliberately small:

| Status | Groups and types | Treatment |
|---|---|---|
| Core | `road` (`motorway`, `trunk`, `primary`, `secondary`, `tertiary`, and source-supported link variants); `rail` (`rail`, `light_rail`, `subway`); `water_network` (`river`, `canal`, and source-supported riverbank/river surfaces) | Normalize when raw tag evidence and valid source identity exist. Do not claim a complete transportation or hydrography network. |
| Conditional context | Named or analysis-material lake, reservoir, estuary, coastal water, or other major water body | A named analysis selects these with an explicit rule; they are not routine core output. |
| Source-side by default | Pond, basin, wastewater surface, tank, and untyped water surface | Preserve in the source extract for provenance and future review, but do not publish to routine consumers. |
| Exploratory | airport, port, warehouse/logistics, industrial footprints | Preserve raw tags and publish mapping/review status. Do not expose as a core category until qualitative review approves a rule. |
| Outside the serving contract | Points and POI-like anchors | Preserve in the raw extract or hand off to POI; do not coerce them into line/polygon infrastructure features. |

An unmapped or ambiguous line/polygon with a valid source identity is retained
with its mapping status. It is not silently dropped. A consumer must elect to
use an exploratory mapping.

## Analytical and display-resolution policy

The analytical feature layer retains every valid, identity-complete source
feature after governed-boundary clipping. It has no global minimum-area rule:
a small pond or water surface might be material to a named local analysis, and
the raw source record is needed for provenance and future QA.

If a map or other consumer cannot use the analytical resolution, the engine
may publish a separate `infrastructure_display_feature` derivative. Its run
must declare its purpose and scale, source feature population, feature type,
projected-CRS size threshold or simplification tolerance, and any dissolve or
component rule. A dissolved component retains all contributing
`source_record_key` values and is a display/generalization object, not a new
source feature. Do not globally dissolve features merely because they touch:
that can erase meaningful type, name, and provenance distinctions.

A dissolve may run only after geometry validation and repair/rejection. It
must operate in bounded spatial partitions and feature types, record its input
and output counts, and surface a failed geometry operation as QA rather than
terminating the market build. The raw analytical layer is never replaced by a
dissolve result.

Open park space is not part of the first water contract. It requires a named
consumer and a separate source/mapping decision rather than an implicit union
with water surfaces.

## Rejected-record behavior

The completed source cache is immutable. Normalization produces retained and
rejected streams, never a silent deletion.

| Condition | `record_status` | Required reason |
|---|---|---|
| Missing source feature or geometry identity | `rejected` | `missing_source_identity` |
| Duplicate source record key within one release | `rejected` except one documented retained record | `duplicate_source_identity` |
| Missing, empty, unsupported, or non-line/non-polygon geometry | `rejected` | `unsupported_geometry` |
| Invalid geometry that cannot be safely repaired | `rejected` | `invalid_geometry` |
| Valid geometry outside the governed market boundary | `rejected` from the market-serving output | `outside_market_boundary` |
| Valid geometry with no approved mapping | `retained` | no rejection; `mapping_status = unmapped` |

Repairs are allowed only for a documented, deterministic operation that
preserves the intended geometry class. The result must set `was_repaired`,
retain the source geometry, and record the repair method. A bounding box or
provider extract footprint is an acquisition convenience, not market
membership.

## Geography interface

Before an engine run, Geography supplies one declared market boundary with:

- `market_id` as the current CBSA `geo_id` (for example, `40060`),
  `market_boundary_geo_level = cbsa`, and its `boundary_vintage`;
- geometry role and source: use analytical geometry for clipping and spatial
  QA; use display geometry only for review products;
- boundary CRS plus the run's projected analytical CRS; and
- the clipping rule: retain an intersecting line or polygon after clipping to
  the governed boundary, recording `was_clipped`; exclude no-intersection
  features from the serving layer with `outside_market_boundary`.

The engine must not derive a market footprint from counties, tracts, a place
name, or a buffered bbox when the governed CBSA geometry is available. It may
use a bbox only to acquire a covering source extract. It must not assign
tracts, counties, ZIPs, or ZCTAs; those are Geography operations requested by
a consumer.

## Provenance, topology, and QA

Each source run declares source system, provider, source release or dated
snapshot, source asset URI and checksum where available, acquisition query or
partition, governed boundary identity and vintage, CRSs, extraction timestamp,
and extracted/retained/rejected/outside counts. The run also records counts by
feature group, type, geometry type, mapping status, and rejection reason.

Raw source identifiers and topology-relevant tags (such as OSM way/relation
identity, highway, railway, bridge, tunnel, layer, oneway, maxspeed, lanes,
and access when present) are preserved for a future network component. This
contract does not guarantee graph nodes, connectivity, turn restrictions,
routing, travel times, crossings, or barrier classification.

Before a consumer uses a run, its QA surface must show source coverage against
the market boundary, row accounting, identity completeness/duplicates,
geometry type/CRS/emptiness/validity/repair outcomes, clipped/outside counts,
mapping status and unmapped-tag distributions, overlapping or duplicate
feature diagnostics where material, and map-ready review samples.

## Consumer handoff

`consumers/infrastructure_consumer_interface_v1.yml` is the read-only
handoff declaration. It requires a candidate artifact to expose source record
identity, governed classification, geometry, raw tags and attributes, CRS and
geometry status, market/boundary provenance, source-run identity, and retained
record status. `publish_infrastructure_interface.py` verifies those fields and
returns the exact artifact URI; it does not copy data or materialize a table.

Q4 currently has no declared infrastructure input. Its eventual method may
select named physical context, but it owns the access definition and barrier
handling. Q2 may use the preserved road geometry and OSM bridge, tunnel,
layer, oneway, maxspeed, lanes, and access evidence in a named experiment, but
the engine does not supply topology, routing, or travel times. Catchment,
barrier, and Corridor Intelligence methods may spatially relate retained
features, without receiving an infrastructure-engine conclusion.

The adoption registry starts empty. A real analysis must record its name,
market, source run, and interface version only after using the interface
unchanged. Promotion remains an Epic 6 decision: it requires the Geography
analytical-boundary gate and two consumers using the same interface unchanged.
