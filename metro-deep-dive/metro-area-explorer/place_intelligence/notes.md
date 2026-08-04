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

## 2026-08-01 — D5 source contract: FEMA NRI + NFHL
- Confirmed existing NRI table and grain locally before building on it: `patterns_in_place.silver.fema_nri` already exists with `tract`, `county`, and `cbsa` rows, all at year `2025`.
- The matching Gold surface also exists at `patterns_in_place.gold.environment_wide`, but D5 now reads NRI directly from the Silver table so the tract catchment apportionment and the CBSA benchmark come from one source contract.
- Official NFHL source for the screening lookup: FEMA ArcGIS REST service at `https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer`.
- Layer contract confirmed on Saturday, August 1, 2026:
  - Flood Hazard Zones = layer `28`
  - FIRM Panels = layer `3`
  - Flood-zone fields used in v0 = `FLD_ZONE`, `ZONE_SUBTY`, `SFHA_TF`, `STATIC_BFE`, `DEPTH`, `SOURCE_CIT`
  - Panel fields used in v0 = `FIRM_PAN`, `EFF_DATE`, `PANEL`, `SUFFIX`, `DFIRM_ID`
- Live Baymeadows point lookup validation for `3832 Baymeadows Road, Jacksonville, FL 32217`:
  - flood zone = `X`
  - zone subtype = `AREA OF MINIMAL FLOOD HAZARD`
  - SFHA flag = `F`
  - FIRM panel = `12031C0553J`
  - panel effective date = `2018-11-02`
- Live 1-mile ring-share validation for the same Baymeadows site after the ArcGIS polygon parser fix:
  - area shares summed to exactly `1.0`
  - the largest class in the ring was `X / AREA OF MINIMAL FLOOD HAZARD` at roughly `65.4%`
  - notable water-adjacent shares also appeared in `OPEN WATER` (~`16.3%`) and several `AE` subtypes, which is directionally consistent with the nearby drainage/water context even though the site point itself is outside the SFHA
- Jacksonville 5-mile-envelope sanity check against the live NFHL zone layer returned `1,419` intersecting flood-zone features, which is high enough that the app code now batches object-id fetches rather than assuming a single page.
- Copy posture locked for v0: NFHL is the parcel/ring screening surface, NRI is the catchment hazard-context surface, and the brief must state clearly that the output is not a flood determination, elevation certificate, or insurance rating.
