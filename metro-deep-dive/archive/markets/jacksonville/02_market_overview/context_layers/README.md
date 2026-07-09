# Section 02 Context Layers

This workspace ingests map context layers from TIGER for Section 02 visualizations and downstream map reuse.

## Target layers
- CBSA boundary + county polygons/labels
- Major highways
- Water polygons
- Municipal boundaries (places)

## Script
- `01_ingest_context_layers.R`

## Outputs
All artifacts are written to `outputs/`:
- `section_02_context_cbsa_boundary_sf.rds`
- `section_02_context_county_sf.rds`
- `section_02_context_places_sf.rds`
- `section_02_context_major_roads_sf.rds`
- `section_02_context_water_sf.rds`
- `section_02_context_ingest_report.rds`

## Notes
- Runtime is upstream-only. These artifacts are consumed by section visuals and integration notebooks.
- Coordinate reference system for saved layers is EPSG:4326.
