# Infrastructure Engine

The Infrastructure Engine prepares governed, source-faithful physical
**line and polygon** features for Metro Deep Dive analyses. Its first core
vocabulary is roads/highways, rail, and a river/canal water network. Airport, port, warehouse,
logistics, and industrial footprints remain review-only until a mapping review
graduates them.

Start with:

- [Build plan](INFRASTRUCTURE_ENGINE_BUILD_PLAN.md)
- [Contract](CONTRACT.md)
- [Audit notes](NOTES.md)
- [Source inventory](sources/README.md)
- [QA outputs](qa/README.md)

## Current state

Epics 1–2 are complete. The market-parameterized builder reads the declared
cached OSM asset, records PBF and GeoPackage checksums, clips core candidates
to the Geography CBSA boundary, and writes a deterministic local source run
with a manifest and rejected-identity stream. The current Geography geometry
is explicitly marked `legacy_unclassified`; Epic 4 must not promote it as an
analytical serving geometry without the corresponding Geography product.

Run a declared market with:

```sh
python3 metro-deep-dive-program/engines/infrastructure/acquire_osm_infrastructure.py --market richmond_va
```

Add `--dry-run` to inspect the run without writing artifacts. Runs are written
below `engines/infrastructure/outputs/`, which is intentionally local and
ignored by Git.

## Ownership

- Geography supplies the authoritative study boundary, boundary vintage,
  geometry role, CRS policy, and clipping predicate.
- This engine owns source extracts, feature identity, raw source tags,
  governed infrastructure mappings, geometry validation, and geometry QA.
- Analyses own access, routing, topology interpretation, barrier treatment,
  catchments, and corridor selection.
- POI owns place-like point anchors. A physical airport or port footprint may
  coexist with an airport or port POI without an automatic merge.

Stable code or tables move to `foundations/` only after two consumers use the
same interface unchanged.
