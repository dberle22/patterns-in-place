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

Epics 1–5 are complete. The market-parameterized builder reads the declared
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

Normalize an acquired run with the versioned core mapping:

```sh
python3 metro-deep-dive-program/engines/infrastructure/normalize_osm_infrastructure.py --market richmond_va
```

Validate a normalized run and produce its serving-candidate and QA artifacts:

```sh
python3 metro-deep-dive-program/engines/infrastructure/validate_osm_infrastructure.py --market richmond_va
```

This checks CRS declaration, geometry type, emptiness, validity, duplicate
identity, and deterministic repair eligibility. It writes retained and
rejected Parquet, a coverage/mapping/water-profile QA summary, and a bounded
SVG review sample beside the source run. No display derivative is created:
there is no named consumer need for simplification, area filtering, or
dissolve.

The geometry gate is complete, but its artifacts remain **serving candidates**
until Geography supplies an analytical CBSA geometry. The current boundary is
explicitly labelled `legacy_unclassified`, so this engine must not promote it
as the authoritative consumer-serving boundary.

Resolve a verified, read-only handoff for a future analysis with:

```sh
python3 metro-deep-dive-program/engines/infrastructure/publish_infrastructure_interface.py --market richmond_va
```

The [consumer interface](consumers/README.md) exposes source-faithful feature
geometry, classification, raw tags, and provenance. It does not define Q4
access, Q2 routing, barriers, catchments, corridors, or districts; those remain
owned by their named downstream methods. Corridor Intelligence may assign
grouping-specific roles to these features without rewriting their source
classification.

## Explore a market

Open the read-only Infrastructure Explorer after validating at least one market:

```sh
marimo edit metro-deep-dive-program/engines/infrastructure/INFRASTRUCTURE_EXPLORATION_NOTEBOOK.py
```

Choose a completed Richmond or Jacksonville run to review its provenance,
feature composition, water complexity, validation/rejection evidence, raw tags,
and a bounded geometry-map sample. The notebook does not change artifacts or
create an analysis result.

## Ownership

- Geography supplies the authoritative study boundary, boundary vintage,
  geometry role, CRS policy, and clipping predicate.
- This engine owns source extracts, feature identity, raw source tags,
  governed infrastructure mappings, geometry validation, and geometry QA.
- Analyses own access, routing, topology interpretation, barrier treatment,
  and catchments. Corridor Intelligence owns reproducible corridor grouping;
  Internal Structure and Issues own interpretation and editorial selection.
- POI owns place-like point anchors. A physical airport or port footprint may
  coexist with an airport or port POI without an automatic merge.

Stable code or tables move to `foundations/` only after two consumers use the
same interface unchanged.
