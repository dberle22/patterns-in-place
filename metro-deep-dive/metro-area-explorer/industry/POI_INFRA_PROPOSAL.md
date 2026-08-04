# POI and Infrastructure Proposal for D4

**Last updated:** 2026-07-29
**Status:** Proposed approach for review and future implementation

## Summary

This note records the current recommended approach for D4 in the Industry section.

The working split is:
- **OSM via `pyrosm` and a downloaded `.osm.pbf` extract** for infrastructure geometry
- **Overture** for first-class POIs and amenities

We are explicitly **not** trying to deduplicate or merge those sources in the first Richmond pass. Richmond is the proving ground, so every layer is exploratory until we inspect the outputs and approve them.

## Recommended source roles

### OSM / `pyrosm`

Use OSM as the first-pass source for infrastructure geometry:
- highways
- major roads
- rail
- airport-related geometry
- port / harbor-related geometry
- warehouse / logistics features where tagging is good enough
- industrial / manufacturing land where mapped as polygons
- office / business park geometry where mapped as polygons
- campus-like site geometry for universities and schools when mapped as real footprints

Why:
- OSM is better for true geometry-heavy infrastructure overlays
- `pyrosm` gives us a more stable metro-scale path than live Overpass requests by downloading a covering PBF once and then parsing locally
- line and polygon geometry are the main need for D4's physical-structure view

### Overture

Use Overture as the first-class source for POIs and amenities:
- airports and terminals as place anchors when useful
- ports / logistics facilities when they exist as place records
- hospitals
- groceries
- universities
- schools
- future amenity expansion: parks, culture, food, civic anchors

Why:
- Overture is a cleaner fit for place-like records than raw OSM tagging
- we want it treated as a governed POI input, not a fallback
- it gives us a strong path toward future promotion into the points layer

## Decisions locked for the first Richmond pass

- **Infrastructure geometry source:** OSM
- **POI source:** Overture
- **Do not mix or deduplicate sources yet:** yes, keep them separate
- **Include first-wave amenities:** yes, include at least hospitals, groceries, universities, and schools
- **Warehouse / logistics handling:** exploratory in Richmond first
- **Category mapping approach for Overture:** try both legacy and newer approaches during exploration and compare results

## POIs vs. geometries

This is the key modeling split for the first D4 layer system.

### Geometry-first layers

These are features we primarily want as lines or polygons because the footprint or corridor shape matters:
- roads
- highways
- rail corridors
- airport grounds, runways, terminals, and airfield polygons
- port / harbor polygons and linear access features
- warehouse campuses
- industrial land and manufacturing sites
- office parks and business parks
- university and school campus/site geometry when it exists as a mapped footprint

Primary source rule:
- **OSM owns geometry-first layers**

### POI-first layers

These are features we primarily want as place records, markers, or labeled anchors:
- hospitals
- groceries
- universities
- schools
- airport / terminal place anchors
- port / logistics place anchors
- future amenity and civic place records

Primary source rule:
- **Overture owns POI-first layers**

### Important nuance

Some real-world features exist in both forms:
- a university can have a campus polygon in OSM and a university place record in Overture
- an airport can have runway and parcel geometry in OSM and a place anchor in Overture
- an industrial park can have OSM landuse/building geometry and also a named place/facility record elsewhere

For the first pass:
- keep those roles separate
- do not deduplicate across OSM and Overture yet
- interpret OSM as the physical footprint layer
- interpret Overture as the place/label layer

## Source-priority recommendation

For the current no-dedup first pass, I recommend:
- **OSM priority for infrastructure overlays**
- **Overture priority for POI markers**

That means:
- if a feature is fundamentally part of the physical network or built structure, prefer OSM
- if a feature is fundamentally a place or amenity record, prefer Overture

I do **not** recommend an OSM-first rule across everything.

Why:
- OSM is stronger for roads, rail, and physical infrastructure geometry
- Overture is the better first-class POI system for amenities and facilities
- a global OSM-first rule would blur the source split we are trying to keep clean

So the source-priority rule should be:

| Use case | Preferred source |
|---|---|
| Roads / rail / corridor geometry | OSM |
| Ports / airports as geometry overlays | OSM |
| POIs and amenities (hospitals, groceries, facility anchors) | Overture |

## First-wave Richmond layer set

### OSM infrastructure layers
- highways
- major roads
- rail
- airports
- ports
- warehouse / logistics features
- industrial / manufacturing polygons where tags support them
- office / business park polygons where tags support them
- university / school campus geometry where tags support them

### Overture POI layers
- hospitals
- groceries
- universities
- schools
- airport / terminal place anchors where useful
- port / logistics place anchors where useful

## Recommended Overture preparation pattern

For Overture, the scalable pattern is:
- ingest the broad Richmond metro POI slice once
- preserve the raw source metadata fields
- classify downstream into our canonical categories
- build D4 and future thematic views from the classified layer

Recommended priority for classification logic:
1. `basic_category` for broad rollups
2. `taxonomy_primary` for specific labels
3. `taxonomy_hierarchy` for parent/child rollup logic and ambiguity resolution
4. `primary_category` as fallback and debugging context
5. `confidence` as a quality signal, not a category signal

Important implication:
- we should **not** rely on loose substring matching for production category assignment
- sensitive buckets like groceries should move to explicit allowlists or mapping rules
- the same rule should apply to education categories like universities and schools

## Short-term storage recommendation

Keep the first pass app-local and cache-based.

Recommended output shape:
- `outputs/<market_id>/osm_infrastructure_lines.parquet`
- `outputs/<market_id>/osm_infrastructure_polygons.parquet`
- `outputs/<market_id>/osm_infrastructure_points.parquet`
- `outputs/<market_id>/overture_pois.parquet`
- `outputs/<market_id>/spatial_manifest.json`

Manifest fields should include:
- `market_id`
- `bbox`
- `extract_date`
- `source`
- `layer_name`
- `query_config`
- `row_count`
- `geometry_type`
- `notes_on_sparse_or_missing_layers`

## Longer-term storage recommendation

This Richmond-first implementation should be treated as a precursor to Foundations Track 17, not the final governed storage design.

Long-term direction:
- Overture place records can eventually promote into `dim_point_of_interest`
- OSM road / rail / other linear infrastructure should **not** be forced into `dim_point_of_interest`
- non-point infrastructure should live in separate spatial tables when we formalize the Foundations version

## Overture mapping exploration

We should test both of these during Richmond exploration:

1. The older or transitional place category fields
2. The newer `basic_category` / taxonomy-oriented fields

Goal of the comparison:
- see which one gives more stable hospital and grocery classification
- see which one is easier to map to our future POI taxonomy
- avoid locking the wrong field too early

## Bounding box approach for a metro area

For a whole metro area, yes: we get the metro footprint coordinates and pass a bounding box to the extractor.

Recommended first-pass approach:
- take the market's county or tract geometry from our existing DuckDB geography backbone
- gather all tract or county shapes that belong to the target CBSA
- compute the min/max longitude and latitude across those geometries
- optionally add a small outward buffer
- pass that bbox into Overpass and Overture queries

Conceptually:

```text
CBSA counties/tracts -> union of market footprint -> bounding box -> source query
```

This is a pragmatic query boundary, not a claim that the metro itself is a rectangle.

### Why use bbox at all?

- `pyrosm` can use a bbox to download a covering OSM extract and then crop locally
- Overture cloud access also supports bbox-style filtering well
- it keeps the first pass simple and reproducible

### Important caveat

A bbox will include some land outside the true metro footprint. That is acceptable for first-pass extraction, but the review step should confirm whether we need a second pass that clips or filters results more tightly to the actual market footprint.

Recommended Richmond-first rule:
- use bbox for extraction
- review extracted layers
- only add finer clipping if the over-capture is meaningfully noisy

## Recommended next step

Before more app work, use Richmond as the test market and inspect:
- OSM highways / rail / airports / ports / logistics coverage
- Overture hospitals and groceries coverage
- the difference between the two Overture category-mapping approaches
- whether bbox-only extraction is clean enough for review

If Richmond looks good, we can then lock the D4 implementation spec more confidently and decide what gets promoted into a reusable ingestion framework.

## Richmond execution plan

This is the concrete first-pass work plan for the Richmond run.

### 1. Ingestion scripts

Create and maintain two Richmond-first entrypoints:
- `ingest_richmond_osm_pyrosm.py`
- `ingest_richmond_overture.py`

Responsibilities:
- derive or accept the Richmond bbox
- run only the source-specific extraction logic
- write cache outputs under `outputs/richmond_va/`
- avoid app-specific joins or presentation logic

#### OSM script scope
- highways
- major roads
- rail
- airports
- ports
- warehouse / logistics features
- cache the covering Richmond `.osm.pbf` under `outputs/richmond_va/osm_raw/`
- parse locally rather than depending on repeated live Overpass calls

#### Overture script scope
- hospitals
- groceries
- airport / terminal anchors where useful
- port / logistics anchors where useful
- both category-mapping approaches for comparison where feasible

### 2. Cache outputs

Expected first-pass outputs:
- `outputs/richmond_va/osm_infrastructure_lines.parquet`
- `outputs/richmond_va/osm_infrastructure_polygons.parquet`
- `outputs/richmond_va/osm_infrastructure_points.parquet`
- `outputs/richmond_va/overture_pois.parquet`
- `outputs/richmond_va/spatial_manifest.json`

### 3. Review artifacts

Create a durable review package for Richmond:
- `RICHMOND_POI_INFRA_REVIEW.md`
- `richmond_poi_infra_review.ipynb`

The markdown should capture:
- what was ingested
- row counts by layer
- category coverage
- geometry mix
- obvious gaps, noise, and tagging caveats
- recommendation on what is ready for D4 v1 vs. what stays exploratory

The notebook should capture:
- sample queries and inspection code
- sample rows by layer
- category distribution checks
- lightweight preview maps or plots if helpful
- comparison of Overture category-mapping approaches

### 4. Review questions for the Richmond run

We should explicitly answer these after ingestion:
- Are OSM highways / rail / airports / ports clean enough for D4 now?
- Are warehouse / logistics features useful enough to keep in the first wave?
- Do Overture hospitals and groceries have good enough coverage and labeling?
- Which Overture category strategy is better for our taxonomy work?
- Is bbox extraction acceptably clean, or do we need a second clipping/filtering pass?

### 5. Expected deliverable back to review

After the Richmond run, the expected review package is:
- source-specific ingestion scripts
- cached outputs
- manifest
- markdown summary
- notebook evidence

This proposal file is the planning and monitoring document for that run. The markdown review file is the results document.
