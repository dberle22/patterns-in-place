# Place Intelligence Notes

## 2026-07-31
- Milestone 0 is intentionally thin: scaffold first, then schema/loader/tests.
- The source spec lived under `exploration/place_intelligence/`; the build plan explicitly relocates the section implementation under `metro-deep-dive/metro-area-explorer/place_intelligence/`.

## 2026-08-01 — D4 source contract: FDOT AADT
- Official source: FDOT Transportation Data and Analytics GIS / Traffic Information pages.
- Accepted ingest path for v0: statewide FDOT AADT GIS layer queried from the official ArcGIS FeatureServer, clipped locally to a market bbox.
- Format: official FDOT statewide GIS traffic layer, exposed both as downloadable statewide zip shapefiles/geodatabases and as a queryable ArcGIS FeatureServer polyline layer.
- Layer confirmed: `Annual Average Daily Traffic` FeatureServer layer 0 at `https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0`.
- Geometry and schema sanity check on Saturday, August 1, 2026: the service returned polyline features with fields including `YEAR_`, `ROADWAY`, `AADT`, `BEGIN_POST`, `END_POST`, `COUNTY`, `DESC_FRM`, and `DESC_TO`; statewide count query returned `21,612` records.
- Update cadence: FDOT GIS page says the statewide GIS downloads are updated weekly; FDOT Traffic Information page says traffic data is collected through the calendar year, converted to annual statistics in the first quarter of the next year, and posted by April each year. The same page states that 2025 traffic data is currently available.
- License/disclaimer posture: FDOT publishes the GIS data on an "as is" / "as available" basis with no warranties and an explicit liability disclaimer. That is acceptable for this app-local v0 cache as long as we preserve provenance and do not overstate precision in the brief copy.
- Why this clears the D4 spike: it is a clean statewide geospatial source with official provenance, documented update cadence, and a queryable API. This is materially different from a per-county manual-download or PDF-only workflow, so D4 stays in scope for v0.
