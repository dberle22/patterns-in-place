# Richmond POI and Infrastructure Review

**Market:** Richmond, VA (`market_id = 40060`)
**Last updated:** 2026-07-29
**Status:** Initial review scaffold; update after each ingestion run

## Purpose

This document is the results log for the Richmond-first D4 source review.

It should capture:
- what was ingested from OSM and Overture
- how much coverage each layer produced
- where the data looks strong
- where the data looks noisy or sparse
- what should move forward into D4 v1
- what should remain exploratory

This is the companion to [POI_INFRA_PROPOSAL.md](./POI_INFRA_PROPOSAL.md), which records the planning and recommendations.

## Run inventory

| Run date | Source | Script | Notes |
|---|---|---|---|
| 2026-07-29 | OSM | `ingest_richmond_osm.py` | Extraction attempted with metro bbox and then tiled requests; current result is a live Overpass blocker rather than landed geometry |
| 2026-07-29 | OSM | `ingest_richmond_osm_pyrosm.py` | New preferred Richmond OSM path; downloads a covering `.osm.pbf` and parses it locally with `pyrosm` |
| 2026-07-29 | OSM | `ingest_richmond_osmextract.R` | Provider-backed Richmond extract succeeded through `osmextract` using `openstreetmap_fr`, with real infra rows landed and categorized |
| 2026-07-29 | Overture | `ingest_richmond_overture.py` | Extraction succeeded against Overture `2026-06-17.0` public S3 release path |

## Extraction boundary

Expected first-pass extraction boundary:
- derive Richmond bbox from the CBSA geography backbone
- run bbox-based source extraction
- review whether over-capture outside the true metro footprint is acceptable

Record actual bbox used here after the first run:

```text
west=-78.290703
south=36.657218
east=-76.595644
north=38.058168
```

## Layer coverage summary

Populate this table from `outputs/richmond_va/spatial_manifest.json` after the run.

| Source | Layer | Geometry type | Row count | Initial read |
|---|---|---|---|---|
| OSM | highways | unknown | 0 | Overpass request reset before usable payload landed |
| OSM | major_roads | unknown | 0 | Overpass request reset before usable payload landed |
| OSM | rail | unknown | 0 | Overpass request reset before usable payload landed |
| OSM | airports | unknown | 0 | Overpass request reset before usable payload landed |
| OSM | ports | unknown | 0 | Overpass request reset before usable payload landed |
| OSM | warehouses_logistics | unknown | 0 | Overpass request reset before usable payload landed |
| OSM (`osmextract`) | highways | line | 5,300 | Richmond provider extract landed cleanly; plausible first-pass highway coverage |
| OSM (`osmextract`) | major_roads | line | 16,572 | Strong line coverage; looks like a realistic road backbone for review and map overlays |
| OSM (`osmextract`) | rail | line | 1,374 | Real Richmond rail features landed |
| OSM (`osmextract`) | airports | point/polygon | 115 | Airfield and airport-related features landed as mixed geometry |
| OSM (`osmextract`) | ports | point/polygon | 7 | Sparse but non-zero port/harbor-related coverage |
| OSM (`osmextract`) | warehouses_logistics | polygon | 114 | Early warehouse/logistics polygon coverage landed; still needs qualitative review |
| Overture | overture_pois | mixed | 76,913 | Real Richmond metro slice landed; strong enough for POI review |

## OSM review

### Expected layers
- highways
- major roads
- rail
- airports
- ports
- warehouse / logistics features

### Review notes

#### Highways and major roads
- Current status: blocked in live extraction
- What we learned: the Richmond metro bbox derived cleanly from the tract backbone, but Overpass requests for the full metro still reset even after fixing request formatting and adding a custom `User-Agent`
- Current read: this looks like a request-volume / request-shape problem rather than a conceptual source mismatch
- Recommended next path: use `pyrosm` for metro-scale OSM infra so we download once, parse locally, and avoid repeated live Overpass failures
- New result from `osmextract`: a dedicated Richmond provider extract landed `5,300` highway rows and `16,572` major-road rows, which is a much more credible first-pass infra surface than the failed Overpass pulls

#### Rail
- Same current blocker as highways: no landed Richmond rows yet because the Overpass requests reset before completion
- New result from `osmextract`: `1,374` Richmond rail line features landed

#### Airports
- Same current blocker as highways: no landed Richmond rows yet because the Overpass requests reset before completion
- New result from `osmextract`: airport-related features landed across both points and polygons, with `51` point records and `64` polygon records

#### Ports
- Same current blocker as highways: no landed Richmond rows yet because the Overpass requests reset before completion
- New result from `osmextract`: port/harbor-related coverage is sparse but present, with `6` point features and `1` polygon feature

#### Warehouses / logistics
- Same current blocker as highways: no landed Richmond rows yet because the Overpass requests reset before completion
- This remains exploratory even once OSM extraction is stable
- New result from `osmextract`: `114` warehouse/logistics polygons landed, which is enough to justify a closer Richmond quality review

## Overture review

### Expected first-wave POIs
- hospitals
- groceries
- airport / terminal anchors where useful
- port / logistics anchors where useful

### Category mapping comparison

We want to compare:
1. legacy / transitional category fields
2. newer `basic_category` / `taxonomy` fields

Record findings here:
- The richer Richmond Overture cache now preserves:
  - legacy `categories.primary`
  - newer `basic_category`
  - newer `taxonomy.primary`
  - `taxonomy.hierarchy`
- This is enough to compare transitional and newer category logic on the same Richmond slice

### Review notes

#### Hospitals
- Landed count currently classified into the first-wave amenity bucket: `255`
- The dominant Richmond hospital pattern is clean:
  - legacy category often = `hospital`
  - newer `basic_category` = `hospital`
  - newer `taxonomy_primary` = `hospital`
- Initial read: hospital classification looks strong enough to keep in D4 v1

#### Groceries
- Landed count currently classified into the first-wave amenity bucket: `999`
- Grocery coverage is broader and more varied than hospitals:
  - `grocery_store` = `424`
  - `supermarket` = `128`
  - `specialty_grocery_store` = `31`
  - `international_grocery_store` = `10`
  - smaller long-tail grocery-like categories also appear
- Initial read: the newer `basic_category = food_and_beverage_store` helps with rollup, but legacy and taxonomy-specific values still matter for detail

#### Facility anchors
- Overture also returns airport/port/logistics-adjacent place anchors and a wide long tail of other place records across the metro
- Initial read: we should keep these as available review context, but not treat every returned place as first-wave D4 content

## Data quality questions

Use this section to answer the core review questions:

1. Are OSM highways / rail / airports / ports clean enough for D4 now?
   - The `osmextract` Richmond provider run gives us a real first-pass answer: highways, major roads, and rail now look landed strongly enough to review for D4, while airports, ports, and warehouses/logistics still need qualitative inspection
2. Are warehouse / logistics features useful enough to keep in the first wave?
   - Still exploratory, but now with real evidence: `114` warehouse/logistics polygons landed from OSM, so this is no longer blocked by extraction failure alone
3. Do Overture hospitals and groceries have good enough coverage and labeling?
   - Yes, initial Richmond read is encouraging; hospitals look especially clean, and groceries have enough volume to support first-wave review
4. Which Overture category strategy is better for our taxonomy work?
   - Early recommendation: preserve both for now, but prefer the newer `basic_category` and `taxonomy` fields for governed rollups while keeping legacy `categories.primary` for comparison and back-compat checks
   - Classification priority should be: `basic_category` -> `taxonomy_primary` -> `taxonomy_hierarchy` -> `primary_category`, with `confidence` kept as a supporting quality filter rather than used as the category definition itself
5. Is bbox extraction acceptably clean, or do we need a clipping/filtering pass?
   - For Overture, bbox extraction is workable as a first pass; we should still review whether the outer rural edges add too much noise before locking the exact D4 display surface

## Recommendation

### Ready for D4 v1
- Overture Richmond POI extraction path
- First-wave amenity review for hospitals and groceries
- Richmond review workflow built around `spatial_manifest.json` plus notebook inspection
- `pyrosm` as the preferred OSM ingestion approach for Richmond-scale infrastructure review
- `osmextract` as the first OSM path that has actually landed a usable Richmond infrastructure surface in this repo

### Keep exploratory
- The exact Richmond OSM layer mix and tagging rules, even after the first `osmextract` run
- Warehouse / logistics inclusion
- Final decision on how aggressively to clip bbox-derived POIs to the true market footprint

### Follow-up work
- Compare the `osmextract` Richmond provider footprint against the true metro footprint to decide whether this source is close enough to our CBSA need or should be clipped further
- Profile sample geometries from the landed `osmextract` outputs and inspect false positives for airports, ports, and warehouses/logistics
- Add sample-map inspection to the notebook once OSM geometry lands
- Compare hospital and grocery results using legacy and newer Overture category fields in more detail
- Replace loose grocery substring logic with explicit category mapping rules built from the preserved Overture metadata fields

## Files to check alongside this review

- `outputs/richmond_va/osm_infrastructure_lines.parquet`
- `outputs/richmond_va/osm_infrastructure_polygons.parquet`
- `outputs/richmond_va/osm_infrastructure_points.parquet`
- `outputs/richmond_va_osmextract/osmextract_infrastructure_lines.parquet`
- `outputs/richmond_va_osmextract/osmextract_infrastructure_points.parquet`
- `outputs/richmond_va_osmextract/osmextract_infrastructure_polygons.parquet`
- `outputs/richmond_va_osmextract/osmextract_summary.json`
- `outputs/richmond_va/overture_pois.parquet`
- `outputs/richmond_va/spatial_manifest.json`
- `richmond_poi_infra_review.ipynb`
