# POI Engine

The POI Engine prepares governed, analysis-ready **place points**. Its first
consumer is Richmond Q4 Daily-needs access; Corridors is the second intended
consumer. It does not define an amenity basket, calculate access, model
barriers, or identify corridors.

Start with:

- [Build plan](POI_ENGINE_BUILD_PLAN.md)
- [Contract](CONTRACT.md)
- [Audit notes](NOTES.md)
- [Richmond POI data shape](DATA_SHAPE.md)
- [Source inventory](sources/README.md)
- [Taxonomy workflow](taxonomy/README.md)
- [QA outputs](qa/README.md)

## Current state

Epics 1–3 are complete. The engine acquires a source-faithful cache, then
normalizes source identity, raw taxonomy, provenance, representative-point
coordinates, validation outcomes, and duplicate-review candidates. Production
taxonomy mappings and tract assignment remain unbuilt.

## Ownership

- Geography supplies authoritative market boundaries, tract geometry,
  point-in-polygon rules, and boundary vintages.
- This engine owns source-place identity, source provenance, source taxonomy,
  governed category mappings, point assignments, and place QA.
- Q4 owns its daily-needs basket and access calculation.
- Infrastructure owns physical line and polygon features; a place anchor does
  not merge with an infrastructure footprint by default.

Stable code or tables move to `foundations/` only after two consumers use the
same interface unchanged.
