# Q6 Foundation Handoff — Direct POI-to-Census-Place Assignment

You are extending the POI Engine after Geography publishes a governed Census
Place analytical geometry product.

## Read first

1. `AGENTS.md`
2. `metro-deep-dive-program/engines/poi/CONTRACT.md`
3. `metro-deep-dive-program/engines/poi/POI_ENGINE_BUILD_PLAN.md`
4. `metro-deep-dive-program/engines/poi/DATA_SHAPE.md`
5. `metro-deep-dive-program/engines/geography/CONTRACT.md`
6. `metro-deep-dive-program/analyses/explanation/q6_one_metro/EXPLANATION_Q6_ONE_METRO_SPEC.md`

## Mission

Publish direct, boundary-vintaged Census Place assignments for retained POI
records in `mart_poi.poi_geography_assignment`. This is a reusable POI
geography interface, not a Q6-only output.

## Current state

- `mart_poi.poi_source_place` preserves geometry plus validated representative
  longitude/latitude.
- `mart_poi.poi_geography_assignment` already holds governed tract and county
  assignments. Current runs have 148,446 assigned tract rows and the same
  number of county rows.
- Richmond’s retained POI records have valid representative points and existing
  tract/county assignments. Address and postal fields are retained as source
  evidence.
- The POI contract requires Geography assignment to preserve level, ID,
  boundary vintage, assignment method, and assignment status.

## Required deliverables

1. Require the new Geography `places_analysis` interface; stop with a clear
   dependency message if it is unavailable. Do not use `geo.places_display`.
2. Assign every retained, valid representative POI point directly to a Census
   Place polygon. Write `geo_level = 'place'`, its Census Place ID, analytical
   boundary vintage, declared predicate/method, and status to
   `mart_poi.poi_geography_assignment`.
3. Preserve explicit outcomes for `assigned`, `no_census_place` (including
   unincorporated territory), `boundary_ambiguous`, and invalid/unassignable
   points. Do not silently discard any record.
4. Define a deterministic boundary policy. It must not turn an ambiguous point
   into an arbitrary Place without recording why.
5. Add assignment QA by source run, market, governed category/mapping status,
   and result status. Check row accounting against retained valid POIs and
   report coverage separately from a true zero count.
6. Run Richmond smoke tests that compare Place assignment to the existing tract
   assignment for review only; a tract-to-Place allocation must not be used to
   assign an individual POI.
7. Update POI contract/build-plan/data-shape documentation and publish a small
   consumer example for Q6.

## Address-field decision

Do **not** assign a POI from its provider-supplied city/address string. Mailing
city names are not reliable Census Place identifiers, may be stale or omitted,
and cannot represent unincorporated territory consistently. Address-city text
may be retained as QA evidence for an unexpected geometric result.

## Guardrails

- Do not change source taxonomy or Q4 amenity-basket membership.
- Do not allocate individual POIs fractionally through a tract-to-Place edge.
- Do not treat `no_census_place` as an error or zero POI coverage.

## Done when

A Q6 consumer can count or inspect POIs by Census Place using a direct point
assignment, while clearly retaining unincorporated and ambiguous records.
