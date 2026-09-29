# POI Engine Audit Notes

## Audit completed 2026-09-08

This audit reviewed the legacy Richmond and Jacksonville Overture ingests,
their landed caches and manifests, their downstream use, and Stoop's public
and curated place governance patterns. It establishes evidence for the POI
contract; it does not promote the legacy cache schema into a managed product.

## Legacy Overture inventory

| Market | Legacy entry point | Cache and manifest | Release / extraction | Observed source records |
|---|---|---|---|---:|
| Richmond, VA (`40060`) | `metro-deep-dive/metro-area-explorer/industry/ingest_richmond_overture.py` | `industry/outputs/richmond_va/overture_pois.parquet`; `spatial_manifest.json` | Overture `2026-06-17.0`; 2026-07-29 | 76,913 |
| Jacksonville, FL (`27260`) | `metro-deep-dive/metro-area-explorer/place_intelligence/ingest_jax_overture.py` | `place_intelligence/outputs/jacksonville_fl/overture_pois.parquet`; `spatial_manifest.json` | Overture `2026-06-17.0`; 2026-08-01 | 107,489 |

Both wrappers call the shared `industry/ingest_spatial.py` Overture path. It
uses a tract-derived, buffered bbox for extraction, reads a declared Overture
Places release, writes one local Parquet cache, and merges an Overture layer
summary into `spatial_manifest.json`. Richmond's manifest records a 76,913-row
mixed-geometry layer; Jacksonville's records 107,489 rows.

Both landed Parquet files share this 13-field cache shape:

`market_id`, `source_system`, `source_id`, `feature_name`, `layer_group`,
`category`, `subcategory`, `geometry_type`, `geometry`, `centroid_lat`,
`centroid_lon`, `attributes_json`, `extract_date`.

Direct cache checks found one distinct, non-null `source_id` per row and no
missing centroid coordinate in either extract. This is a useful baseline, not
a substitute for contract-level coordinate validation or true-boundary
filtering. The category evidence is nested inside `attributes_json`: legacy
`categories.primary`, `basic_category`, `taxonomy.primary`,
`taxonomy.hierarchy`, `confidence`, and freeform address.

## What is reusable and what is not

The shared extractor already preserves the raw Overture category fields and
source IDs, and its source/release path is explicit. It is suitable evidence
for Epic 2 refactoring.

It is not yet the engine acquisition contract because it:

- duplicates thin market wrappers instead of accepting one market parameter;
- records only a cache-oriented layer summary, without a run ID, source
  release field, true-boundary vintage, checksums, or retained/rejected/outside
  accounting;
- treats bbox membership as the finished extract rather than applying the
  governed market boundary; and
- applies exploratory substring classification in `_categorize_overture_place`.

That classifier produced promising Richmond review counts (255 hospitals and
999 groceries), but its airport, port, logistics, education, and broad place
rules are not approved managed mappings. Do not use it as the production
taxonomy implementation.

The pilot release (`2026-06-17.0`) is no longer available in Overture's public
bucket as of Epic 2. The checked-in acquisition registry therefore declares
the current available `2026-08-19.0` release and records its full partition
path. The legacy caches remain the audit baseline; they are not a rebuildable
source release.

## Epic 2 verification — 2026-09-08

`acquire_overture_places.py` is the shared Overture path. It resolves CBSA
membership through `mart_geography.rollup_county_to_cbsa`, unions the
Geography-owned tract boundary, prefilters the remote source with that
boundary's bbox, then uses the true boundary for `ST_Intersects` retention.
It writes all native Overture fields unchanged to a local source cache and a
per-run manifest containing the source release, boundary vintage, query,
checksum, timestamps, and row accounting.

Dry-run checks against Overture Places `2026-08-19.0` returned:

| Market | Bbox candidates | Retained in governed boundary | Outside boundary |
|---|---:|---:|---:|
| Richmond | 72,534 | 61,513 | 11,021 |
| Jacksonville | 105,090 | 86,933 | 18,157 |

Richmond was repeated with the same release and boundary and returned the
same counts. A real Richmond run wrote and validated a 61,513-record
source-faithful cache against its manifest. These counts are a source-release
baseline, not an assertion that either market's POI inventory is complete.

## Epic 3 verification — 2026-09-08

`normalize_overture_places.py` derives the `poi_source_place` contract from a
declared source-run manifest. It keeps raw categories and source attributes,
uses `ST_PointOnSurface` as the documented representative-point method, and
validates IDs, coordinates, and true-boundary membership. Retained and
rejected records are separate local artifacts with checksums.

The Richmond run yielded 61,513 retained records, zero rejected records, and
zero exact source-identity duplicate groups. A deliberately conservative
same-normalized-name / 4-decimal coordinate-grid diagnostic yielded six
near-duplicate candidate groups. Those candidates remain review evidence; no
record was merged, dropped, or given a canonical identity.

## Source-adapter rule

Epic 3 is the common source-adapter layer. Overture, official specialist sources, and curated/article-derived records can each retain native IDs and provenance while receiving the same validation and duplicate-review treatment. OSM roads, rail, and other physical geometry remain Infrastructure Engine inputs; only OSM features intentionally used as place-like records enter this engine.

## Epic 5 verification — 2026-09-08

Richmond's 61,513 classified records were assigned to both a tract (2020
vintage) and county (2023 vintage) through governed point-in-polygon joins.
Structured source postcodes plus a freeform-address fallback supplied a postal
ZIP for 60,120 records; 1,393 lacked one.
Postal ZIP is source evidence, not a Census ZCTA point assignment. The
Geography Engine has no governed ZCTA geometry surface, so a true ZCTA
assignment remains a recorded dependency.

## Epic 4 verification — 2026-09-08

The first approved mapping registry, `q4_overture_v1`, uses exact preserved
Overture `taxonomy.primary` values. It maps hospitals, seven grocery variants,
pharmacies, schools, and universities into descriptive governed categories;
it does not define the Q4 daily-needs basket. Richmond yielded 1,053 mapped
and 60,460 unmapped records. The latter remain in an explicit review queue.
No rule overlaps, ambiguous automated matches, or manual overrides exist yet.

## Downstream consumers and program fit

The program names the POI Engine as the input to Q4 Daily-needs access and
Internal Structure context. Q4 is the first consumer: it needs an amenity
inventory, tract access distribution, and Richmond access map, while keeping
its daily-needs basket and access method analysis-owned. Corridor Intelligence
may aggregate eligible governed POI categories as soft, versioned membership
evidence; Internal Structure then reviews that evidence and any additional
context without rewriting the engine run.

This follows the workbook's required split: POI owns classified,
provenance-rich, geographically assigned place points; the daily-needs method
owns amenity selection, reach, and scoring. No POI work should pre-build an
access score or corridor definition.

## Stoop governance patterns audited

Stoop has distinct public baseline and curated-place paths. The reusable
patterns are:

| Pattern | Evidence | POI Engine adoption |
|---|---|---|
| Stable source identity | `public_poi/build_dim.py` derives a deterministic source-system/source-ID key | Keep source system, release, and source ID; do not claim cross-source identity. |
| Separate public and curated lanes | Public `dim_public_poi` and curated canonical place workflows | Keep curated records distinguishable from public baseline records. |
| Discovery separate from production rules | Classification strategy and mapping mart | Profile source categories separately; publish only approved managed rules. |
| Evidence, review queue, durable overrides | Classification recommendations, review queue, and active overrides | Carry mapping rule, evidence, review status, and active override state. |
| Source lineage survives canonical use | Curated workflow keeps source systems and record IDs | Preserve source provenance even if a later consumer adds entity resolution. |

Stoop's NYC editorial taxonomy and restaurant text-scoring model are not MDD's
taxonomy. The POI Engine adopts its governance controls, not its labels,
geographic assumptions, or source-specific matching hierarchy.

## Decisions now locked

- Public baseline, official/specialist, and curated POIs are distinct source
  lanes.
- The initial durable identity is source system + source release + source ID.
- Source taxonomy, governed categories, and analysis amenity baskets are
  separate layers.
- Invalid and outside-boundary records are reported, not silently dropped.
- Similarity creates duplicate candidates for review only; no automatic
  canonical merge is in scope.
- Tract assignment uses the Geography Engine and retains its boundary vintage.

## Open questions carried into later epics

| Question | When to resolve |
|---|---|
| Exact managed DuckDB schemas/table names and cache-retention location | Epic 2, once the repeatable acquisition path is selected |
| Stable `source_run_id` format and checksum policy | Epic 2 |
| Representative-point method for non-point Overture geometries | Epic 3, before geographic assignment |
| Near-duplicate thresholds and review sample size | Epic 3, using both pilot markets |
| First approved Q4 mappings beyond the preliminary hospital/grocery evidence | Epic 4 with Richmond Q4 |
| Whether an official/specialist source replaces a public baseline category | Consumer-driven; no default replacement |
| Cross-release or cross-source entity resolution | Defer until a consumer needs a canonical entity |
| Refresh cadence and national partition strategy | After the first repeatable Richmond/Jacksonville build |
