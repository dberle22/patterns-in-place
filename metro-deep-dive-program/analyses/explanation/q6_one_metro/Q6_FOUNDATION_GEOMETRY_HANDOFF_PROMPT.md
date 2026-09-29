# Q6 Foundation Handoff — Census Place Analytical Geometry

**Status: completed 2026-09-22.** Geography now publishes national 2024
`geo.places_analysis` (32,041 Places across all 50 states and DC), cataloged as
`consumer_ready_analysis`. The downstream POI and Infrastructure handoffs now
depend on this product; they remain responsible for publishing their own
assignment or overlap interfaces.

You are extending the Geography Engine so downstream analyses can make
reproducible spatial assignments and overlaps against Census Places.

## Read first

1. `AGENTS.md`
2. `metro-deep-dive-program/engines/geography/CONTRACT.md`
3. `metro-deep-dive-program/engines/geography/GEOGRAPHY_ENGINE_BUILD_PLAN.md`
4. `metro-deep-dive-program/engines/geography/geo_spec.md`
5. `metro-deep-dive-program/analyses/explanation/q6_one_metro/EXPLANATION_Q6_ONE_METRO_SPEC.md`
6. `metro-deep-dive-program/analyses/explanation/q6_one_metro/EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md`

## Mission

Publish a governed, versioned Census Place **analytical** geometry product. It
must be usable for point-in-Place assignment and line/polygon overlap. It is
not a replacement for the existing `geo.places_display` cartographic layer.

The immediate consumers are Q6, the POI Engine, and the Infrastructure Engine.
Do not broaden this work into a generic geometry migration for all geography
levels.

## Current state

- `geo.places_display` exists and is appropriate for map display only.
- The Geography contract already separates `geo.<level>_display` from
  `geo.<level>_analysis`; only the Place analytical product is missing.
- `silver.block_registry` and `silver.xwalk_place_membership` are governed
  identity/allocation products. Do not derive polygon boundaries from blocks.
- Q6 uses Census Place as its candidate unit. Its display map must never use
  display geometry to establish analytical membership.

## Required deliverables

1. Materialize a Census Place analytical geometry table, preferably
   `geo.places_analysis`, from a declared Census TIGER/Line source and boundary
   vintage. Retain the Place key, source/boundary metadata, geometry role, and
   WKB/geometry fields consistent with other Geography products.
2. Add it to the Geography geometry catalog and expose it through the
   appropriate read-only `mart_geography` discovery/interface surface.
3. Define and document the spatial-operation policy:
   - use a declared analytical CRS for length/area operations;
   - preserve WGS84 geometry for interchange where that is the current engine
     convention;
   - specify how a point on a boundary, invalid geometry, overlapping match,
     and no-Place match are represented.
4. Add a state-scoped or otherwise bounded build path before considering a
   national materialization. A national product is appropriate only after the
   build is validated and its operational cost is known.
5. Add structural QA: unique Place identity/vintage, geometry validity,
   expected source coverage, and Richmond (`40060`) smoke checks. Confirm that
   the product can be used in a point-in-polygon query and a line-intersection
   query without substituting display geometry.
6. Update the Geography contract, usage documentation, and build plan with the
   new product and its consumer-ready status.

## Guardrails

- Do not use cartographic/display boundaries for analytical point assignment,
  intersections, area, or length.
- Do not imply Census Places exactly partition a CBSA; unincorporated territory
  must remain a valid no-Place outcome.
- Do not alter current Place-to-CBSA weighted membership semantics.
- Do not make Q6-specific business decisions in Geography.

## Done when

The POI and Infrastructure agents can name one governed Place geometry product,
one boundary vintage, one analytical CRS policy, and explicit no-match/boundary
statuses—without creating their own geometry download or relying on
`geo.places_display`.
