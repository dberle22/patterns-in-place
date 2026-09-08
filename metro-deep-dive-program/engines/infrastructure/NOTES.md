# Infrastructure Engine Audit Notes

## Audit completed 2026-09-08

This audit reviewed the legacy Richmond and Jacksonville OSM extraction,
cached PBF/GeoPackage artifacts, raw and promoted Parquet outputs, manifests,
and their app-facing consumers. It establishes the first engine contract; it
does not promote legacy cache schemas or mappings into a managed product.

## Epic 2 completed 2026-09-08

`acquire_osm_infrastructure.py` now provides one market-parameterized,
deterministic source-run path. It reads the checked-in declarations in
`sources/osm_infrastructure.yml`, hashes the cached PBF and GeoPackage adapter,
selects the narrow road/rail/river-canal vocabulary, clips candidates to the
current Geography CBSA geometry, and writes source-feature, rejected-feature,
and manifest artifacts under the ignored engine output directory.

| Market | Source selector | Bbox candidates | Retained market candidates | Rejected identity candidates | Outside governed boundary |
|---|---:|---:|---:|---:|---:|
| Richmond (`40060`) | 23,779 | 22,597 | 21,302 | 0 | 1,295 |
| Jacksonville (`27260`) | 26,107 | 23,722 | 22,570 | 305 | 847 |

Jacksonville's 305 rejections are core river polygons lacking an OSM feature
ID in the legacy GeoPackage adapter. They retain a deterministic geometry hash
and source tags in the rejected audit artifact, but cannot enter a serving
layer. Richmond contributes 224 river and 41 canal lines; Jacksonville
contributes 330 river and 55 canal lines, plus 86 identity-complete river
polygons. The manifest records bbox-to-market counts and polygon area by
feature group/type, so coverage loss is visible without an unbounded dissolve.

The run identifier is derived from market, dated snapshot, and PBF checksum.
A repeat run refuses to overwrite the matching artifact unless the operator
explicitly passes `--overwrite`; this behavior was confirmed for Richmond.

The current Geography lookup supplies the 2023 CBSA identity but labels the
available `geo.cbsas` geometry `legacy_unclassified`. The manifest carries that
role explicitly. It is sufficient for the source-run clip diagnostic but must
be replaced by the Geography analytical geometry before a validated serving
layer is promoted.

## Proven extraction evidence

| Market | Legacy entry point | Cached source evidence | Raw output and manifest | Downstream consumer |
|---|---|---|---|---|
| Richmond, VA | `metro-deep-dive/metro-area-explorer/industry/ingest_richmond_osmextract.R` | Richmond `openstreetmap_fr` PBF and GeoPackage | `outputs/richmond_va_osmextract/osmextract_infrastructure_{lines,points,polygons}.parquet`, manifest, and summary | `promote_richmond_osmextract.py` converts WKT to the Industry D4 GeoJSON-string cache read by `data_prep.py` and the D4 overlay |
| Jacksonville, FL | `metro-deep-dive/metro-area-explorer/place_intelligence/ingest_jax_osmextract.R` | Northeast Florida `openstreetmap_fr` PBF and GeoPackage | `outputs/jacksonville_fl/osmextract_infrastructure_{lines,points,polygons}.parquet`, manifest, and summary | `promote_jax_osmextract.py` converts WKT to the Place Intelligence GeoJSON-string cache read by `site_prep.py` and the D3 barrier work |

Both scripts use a provider-backed `osmextract` download, cache the source
locally, select declared OSM tags, preserve selected raw tags as JSON, and
write a manifest with provider, source URL, extract timestamp, and layer row
counts. That is the proven starting path. The older tiled-Overpass extractor
is useful prototype evidence only: it is subject to live-query failures. The
Virginia-wide `pyrosm` path is also a prototype and not the selected first
build path.

## Observed artifacts and schema

Both raw exports share a 14-field source-adapter shape:

`market_id`, `source_system`, `source_id`, `feature_name`, `layer_group`,
`category`, `subcategory`, `geometry_type`, `geometry_family`, `geometry_wkt`,
`centroid_lat`, `centroid_lon`, `attributes_json`, `extract_date`.

The two promotion scripts reduce that to a 13-field app cache by converting
`geometry_wkt` to a GeoJSON string named `geometry` and dropping
`geometry_family`. That adapter shape is intentionally not the engine
contract: it has no source release, source-asset checksum, governed boundary
vintage, mapping version/status, geometry-validation outcome, clipping
outcome, or retained/rejected accounting.

| Market | Lines | Points | Polygons | Core evidence |
|---|---:|---:|---:|---|
| Richmond | 23,246 | 57 | 179 | 5,300 highways, 16,572 major roads, 1,374 rail; no water selector was included in this run |
| Jacksonville | 25,431 | 36 | 20,201 | 7,227 highways, 15,926 major roads, 1,632 rail, 646 water lines, and 19,892 water polygons |

The raw and promoted line exports have complete, unique `source_id` values.
Point exports also have complete IDs, but points are outside the engine's
line/polygon serving scope. Polygon identity is not usable in either legacy
export: Richmond has 176 blank IDs among 179 polygons; Jacksonville has 18,878
rows that become the literal string `"None"` after promotion. The missing IDs
cover the majority of water and exploratory polygons. Those records are
valuable raw evidence but must be rejected from the normalized serving layer
until the source feature and geometry identity can be retained.

### Jacksonville water density review

The 19,892 water polygons are 19,891 distinct WKT geometries, so they are not
one duplicated geometry written repeatedly. The provider extract is Northeast
Florida rather than a governed CBSA: a read-only intersection with the current
tract-derived Jacksonville footprint retains 15,556 polygons. Clipping is
therefore necessary, but it does not make the fine-grained water surface go
away.

The source selector includes broad water surfaces. Its most frequent raw tags
are `water=reservoir` (6,353), untyped `natural=water` (6,002), `water=basin`
(2,992), `water=pond` (2,648), `water=lake` (1,117), and `water=river` (676).
In an equal-area projection, the median polygon is about 538 m² and the 95th
percentile is about 4,775 m². Fifty polygons of at least 100,000 m² account
for about 62% of summed raw feature area, while 18,949 polygons smaller than
5,000 m² account for only about 22%.

This is a display-resolution issue, not evidence that the raw water layer is
intrinsically invalid. The core analytical layer should retain valid,
identity-complete source features; a map-scale derivative can filter,
simplify, or deliberately dissolve only after its purpose is specified. A
global dissolve of touching water polygons would blur feature types and lose
source provenance, while a global size cutoff could erase water that matters
to a local question.

### Dissolve crash evidence

A full-market `ST_Union_Agg` over the 19,892 raw Jacksonville water polygons
caused a segmentation fault in DuckDB Spatial's GEOS aggregate finalization on
2026-09-08. This was a native-process crash, not a normal query error. It
confirms that any future display/generalization derivative must validate input
geometry first and execute in bounded partitions, with a recorded QA failure
path. Do not use an unbounded market-wide dissolve as a way to reduce map
feature counts.

## What is proven, exploratory, and blocked

| Area | Audit conclusion | Contract treatment |
|---|---|---|
| Provider-backed OSM extraction | Proven in both markets, with cached PBF/GeoPackage and a manifest | Baseline for Epic 2; add a declared source release/snapshot and checksum |
| Roads/highways and rail lines | Complete, unique source IDs in both audited outputs | First core mapping slice |
| Water | Present only in the Jacksonville selectors; the provider footprint is broader than the governed CBSA | First core mapping slice, but add the Richmond selectors and governed clipping before serving |
| Water display density | 15,556 Jacksonville polygons still intersect the current tract-derived market footprint; most are very small surfaces | Keep analytical source features; create a scale-specific derivative only after profiling and a named consumer |
| Airport, port, warehouse/logistics, industrial | Extracted with uneven geometry and identity quality; rules are broad and not qualitatively reviewed | Exploratory only; no core serving category |
| App-facing promotion scripts | Useful compatibility adapters for two legacy apps | Do not reuse as the engine build path or contract |
| Market boundary membership | Both builds select provider/place coverage, not a Geography-governed CBSA footprint | Must be added before a serving output is published |
| Geometry validity, repair, overlap review | No contract-level checks are recorded in the legacy manifests | Must be implemented in Epic 4 |

## Geography interface conclusion

The existing legacy helper derives a buffered bbox by unioning tract geometry
through county-to-CBSA relationships. That is acceptable only for acquisition
coverage. The engine instead depends on the Geography contract's vintaged CBSA
identity and analytical geometry for clipping and QA. It records the source
boundary, boundary vintage, analytical CRS, clipping outcome, and any repair;
it does not perform downstream geography assignment.

## Deferred extensions

- A routable network needs explicit node/edge topology, connectivity, turn,
  access, and restriction rules; raw OSM tags are retained now but no graph is
  implied.
- Travel-time and network-distance calculations belong to Q2/Q4 methods, not
  this source-normalization contract.
- A barrier is a use-case interpretation requiring crossings and an origin or
  catchment. Water, rail, and highways are not labelled barriers here.
- Corridor selection combines several engines and remains future Corridor
  Intelligence work.
- Simplified display geometry, national extract partitioning, table names, and
  reconciliation to official transportation or hydrography sources remain
  future decisions.

## Required plan adjustments before Epic 2

1. Make identity recovery for polygon features a gate, not a later QA detail.
   The build cannot claim a normalized polygon layer until it retains stable
   OSM feature/geometry identity or explicitly serves only the identity-complete
   subset.
2. Treat the `osmextract` PBF/GeoPackage as a declared source asset with a
   release/snapshot ID and checksum. Existing manifests provide a URL and
   extract time but not sufficient reproducibility evidence.
3. Resolve the governed CBSA boundary before extraction and use the bbox only
   as a covering acquisition window. Provider/place labels are not a boundary
   contract.
4. Parameterize the same core water selectors for Richmond and Jacksonville;
   current evidence is asymmetric because Richmond did not select water, not
   because water is outside scope.
5. Split water into source-supported linear and surface forms, then establish
   a separate display/generalization policy. Do not use a global area cutoff
   or a permanent dissolve as a substitute for that policy.
6. Make any dissolve a bounded, post-validation derivative with a QA failure
   outcome. The recorded DuckDB Spatial crash rules out an unbounded union of
   the raw market layer.

No source data was downloaded, no DuckDB table changed, and no legacy consumer
was migrated as part of this audit.
