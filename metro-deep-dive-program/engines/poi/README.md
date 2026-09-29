# POI Engine

The POI Engine prepares governed, analysis-ready **place points**. Its first
consumer is Richmond Q4 Daily-needs access; Corridor Intelligence and Internal
Structure are the next planned consumers. It does not define an amenity basket,
calculate access, model barriers, or identify structural candidates. Corridor
Intelligence may aggregate eligible governed categories as membership evidence
without changing POI's source classifications.

Start with:

- [Build plan](POI_ENGINE_BUILD_PLAN.md)
- [Contract](CONTRACT.md)
- [Audit notes](NOTES.md)
- [Richmond POI data shape](DATA_SHAPE.md)
- [Source inventory](sources/README.md)
- [Taxonomy workflow](taxonomy/README.md)
- [QA outputs](qa/README.md)

## Current state

Epics 1–5 are complete for Richmond and Jacksonville. The engine acquires a
source-faithful cache, normalizes source identity and provenance, applies the
first governed taxonomy mapping, and assigns retained points to governed tract,
county, and Census Place geometry with QA. Place results are direct analytical
point assignments; `no_census_place` and boundary ambiguity remain visible.
First-analysis adoption remains open.

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
