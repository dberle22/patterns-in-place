# Q6 Foundation Handoff — Infrastructure-to-Census-Place Overlap

You are extending the Infrastructure Engine after Geography publishes governed
Census Place analytical geometry.

## Read first

1. `AGENTS.md`
2. `metro-deep-dive-program/engines/infrastructure/CONTRACT.md`
3. `metro-deep-dive-program/engines/infrastructure/INFRASTRUCTURE_ENGINE_BUILD_PLAN.md`
4. `metro-deep-dive-program/engines/infrastructure/README.md`
5. `metro-deep-dive-program/engines/geography/CONTRACT.md`
6. `metro-deep-dive-program/analyses/explanation/q6_one_metro/EXPLANATION_Q6_ONE_METRO_SPEC.md`

## Mission

Publish a reusable, provenance-rich Census Place overlap interface for retained
Infrastructure line and polygon features. This is not a point assignment and
not an infrastructure score.

## Required deliverables

1. Require Geography’s `places_analysis` product and its declared analytical
   CRS. Do not use display geometry for measurements.
2. Materialize an auditable feature-overlap surface at least at:
   `source_run × source_record_key × Place × boundary vintage`.
3. For linear features, calculate the length of geometry clipped/intersected
   within the Place. For polygon features, calculate the intersected area.
   Retain the original feature classification, run identity, CRS, measurement
   method, and geometry/record status.
4. Publish a separate Place summary by feature group/type/form. Keep line
   length and polygon area separate; never add them together as “infrastructure
   present.”
5. Preserve a no-overlap result through coverage/QA, not by fabricating zero
   rows. Ensure an intersecting feature that crosses multiple Places contributes
   only its measured portion to each Place.
6. Validate accounting on a bounded Richmond run: geometry validity, overlap
   row counts, no unexpected duplicate keys, and reconciliation of clipped
   portions to source geometry within declared precision/tolerance.
7. Document that the interface provides physical context only. It does not
   identify barriers, connectivity, travel time, access, or anchor status.

## Current constraints

Infrastructure artifacts are serving candidates and need the Geography
analytical-boundary gate before consumer promotion. Do not use source points or
POI-like anchors as infrastructure features; POI owns those records.

## Done when

Q6 can show separately labeled road, rail, water-line, or water-surface context
by Census Place and trace every summary value to retained feature overlaps.
