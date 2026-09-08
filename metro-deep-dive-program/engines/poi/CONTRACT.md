# POI Engine Contract

Status: Epic 1 contract locked on 2026-09-08. Names below are logical product
names, not yet materialized DuckDB table names.

## Contract boundary

The engine converts an explicitly declared source release and governed study
area into source-faithful, classified point records with reviewable quality
evidence. A consumer may filter those records into an amenity basket, but may
not infer source identity, category evidence, or geographic vintage that the
engine did not publish.

The engine does **not** own source-to-source canonical entities, access or
network calculations, barrier logic, catchments, or corridor selection.

## Logical products and grains

| Product | Grain | Required result |
|---|---|---|
| `poi_source_run` | one source release × market boundary × extraction run | Reproducible source, release, boundary, query/cache location, timing, and row-accounting evidence |
| `poi_source_place` | one source record × source release | Source-faithful normalized place record, including raw taxonomy and coordinates or an explicit rejection |
| `poi_taxonomy_rule` | one versioned source-category/rule | Controlled governed-category decision, rationale, status, and rule evidence |
| `poi_classified_place` | one retained source place × mapping version | Normalized place plus mapping status and evidence; no silent unmapped drop |
| `poi_geography_assignment` | one retained source place × geography level × boundary vintage | Point assignment result or explicit non-assignment reason |
| `poi_qa_*` | run × applicable source/category/geography group | Counts and review samples for source coverage, mappings, coordinates, duplicates, and assignments |

## Source-place record

`poi_source_place` is the contract's central record. All retained records must
carry the following fields. A source may add fields, but cannot replace these
with unversioned or display-only values.

| Field group | Required fields | Rule |
|---|---|---|
| Identity | `source_system`, `source_release`, `source_id`, `source_record_key` | `source_record_key` is a deterministic combination of source system, release, and source ID. It is durable within a release, not an assertion of cross-source identity. |
| Source content | `source_name`, `source_address`, `source_postal_zip`, `source_category_primary`, `source_category_basic`, `source_taxonomy_primary`, `source_taxonomy_hierarchy`, `source_attributes` | Preserve available raw values; `source_postal_zip` retains a structured provider postcode separately from freeform street text. Absent source fields are null, not synthesized classifications. |
| Geometry | `geometry`, `geometry_type`, `longitude`, `latitude`, `coordinate_status` | Geometry is preserved when supplied. Longitude/latitude are the validated analytical point, normally the source point or a documented representative point for a non-point geometry. |
| Provenance | `market_id`, `market_boundary_vintage`, `source_run_id`, `extracted_at`, `source_query`, `cache_uri` | A record can always be traced to one declared run and the extraction boundary used for that run. |
| Validation | `record_status`, `rejection_reason`, `is_within_market_boundary` | `record_status` is `retained` or `rejected`; rejected records retain identity and provenance. |

`source_release` is mandatory even when a provider release is only known as a
dated snapshot. `extracted_at` records when the engine read it; it is not a
substitute for the provider's release identity.

## Rejected-record behavior

The raw source cache is immutable for a completed run. Normalization produces
a retained stream and a rejected-record stream; it never silently removes a
source record.

| Condition | `record_status` | Required reason |
|---|---|---|
| Missing source ID | `rejected` | `missing_source_id` |
| Duplicate source ID inside the same source release | `rejected` except one documented retained record | `duplicate_source_identity` |
| Missing, non-numeric, or out-of-range coordinate | `rejected` | `invalid_coordinate` |
| Cannot derive a representative point from supplied geometry | `rejected` | `unusable_geometry` |
| Valid point outside true governed market boundary | `rejected` from the market-serving output | `outside_market_boundary` |
| Valid source record with no approved mapping | `retained` | no rejection; classification status is `unmapped` |

The source-run QA must report every rejection reason. A bbox is an extraction
convenience only; the governed boundary determines market membership.

## Taxonomy and consumer boundary

Three label layers are intentionally separate:

| Layer | Owner | Examples | Rule |
|---|---|---|---|
| Source taxonomy | Source | Overture `basic_category`, `taxonomy.primary` | Preserved verbatim enough to reproduce a mapping decision. |
| Governed category | POI Engine | `grocery`, `hospital`, `university`, `school` | Stable descriptive category from a versioned managed rule, with match evidence and review state. |
| Amenity basket | Analysis | `daily_needs` | Consumer-defined grouping of governed categories; never stored as if it were a source or universal POI category. |

Each `poi_classified_place` must retain `mapping_version`, `mapping_status`
(`mapped`, `unmapped`, `ambiguous`, or `overridden`), `mapping_rule_id`,
`mapping_evidence`, and `review_status`. Overrides are durable, versioned,
explicitly active decisions that take precedence over an automated rule.

## Identity, duplicates, and refresh

- Initial identity is `source_system + source_release + source_id`.
- A refreshed source release may represent the same real-world place, but it
  is not automatically merged across releases or sources.
- Exact duplicate source identities are validation failures. Name/coordinate
  similarity produces a duplicate candidate QA output only; it never merges
  records automatically.
- A source run must declare the source release, market boundary identifier and
  vintage, query or partition specification, cache location/checksum where
  available, extraction timestamp, and extract/retain/reject/outside counts.

## Geography and QA

`source_address` is retained as source-provided address evidence. It does not replace point-in-polygon assignment, but supports review when a coordinate assignment is unexpected.

Only retained records with valid coordinates are eligible for assignment.
Assignments call the Geography Engine and retain `geo_level`, `geo_id`,
`boundary_vintage`, assignment method, and assignment status. The first
required levels are tract, county, and ZCTA. A source-provided postal ZIP is address evidence, not a Census ZCTA assignment or geography identity.

Before a consumer uses a run, its QA surface must show coordinate validity,
identity duplicates, mapped/unmapped/ambiguous/overridden counts, counts by
source and governed category, market and tract assignment coverage, and
review samples for high-volume, sparse, and ambiguous categories.
