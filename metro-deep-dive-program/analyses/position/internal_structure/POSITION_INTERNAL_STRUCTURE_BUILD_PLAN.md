# Position Internal Structure Build Plan

**Status:** Parts 1–2 implemented for Richmond, VA (`40060`); ready for analyst review

Build two Marimo notebooks: Part 1 for market geography and zone anatomy, and
Part 2 for activity and physical structure. Corridor Intelligence is deprecated
and is not a notebook dependency.

## Dependencies and Pre-Build Checks

The required capabilities largely exist:

- Phase 7 supplies tract zone assignments, benchmarks, and the ZCTA rollup.
- Geography supplies CBSA, county, Place, tract, and ZCTA identities plus the
  allocation relationships needed for cross-geography summaries.
- Foundations supplies the small population and housing measures needed to
  establish area scale.
- existing D3 work supplies tract job-center evidence where its interface can
  be reused unchanged.
- POI and Infrastructure supply declared market runs and QA evidence.

Before building, confirm the exact fields, vintages, allocation bases, market
coverage, and display geometry needed by each view. Materialize Place or other
display geometry only when a planned map needs it. Do not open a new engine or
broad Foundations project for notebook-specific joins.

## Part 1 — Market Geography and Zone Structure

### Initial Richmond implementation

- [x] Add the read-only `POSITION_INTERNAL_STRUCTURE_NOTEBOOK.py` with
  Richmond, VA (`40060`) as the initial default.
- [x] Query governed CBSA/tract/Place/ZCTA identities, population-basis
  allocations, 2024 additive population and housing measures, and Phase 7
  tract and ZCTA outputs from their owning marts.
- [x] Add coverage, Place inventory, tract-share zone composition, two-way
  Place × Zone, selected-Place, ZCTA, and in-notebook QA surfaces.
- [x] Add hierarchy and tract-zone maps using the current latest Geography
  geometry products. The Geography contract update will document their
  approved consumer use.

### Epic 1 — Assemble the Market Anatomy Slice — complete

- Select the governed CBSA, county, Census Place, tract, and ZCTA identities
  and relationships for Richmond.
- Confirm how incorporated/CDP and unincorporated shares remain visible.
- Select a small set of additive population and housing scale fields with
  explicit vintages and allocation bases.
- Confirm the Phase 7 tract and ZCTA fields and national zone-composition
  baseline.
- Obtain only the market-scoped display geometry required by the planned maps.

**Done when:** Richmond loads as one reconciled, read-only geography and
zone slice with visible allocation, metric, and geometry coverage.

### Epic 2 — Build the Places and Zones Review — complete

- Add market controls and the coverage summary.
- Add the geography hierarchy map and Place inventory.
- Add the tract zone map and market composition comparison.
- Add the two-direction Place × Zone matrix and selected-Place profile.
- Add the supporting ZCTA view without presenting it as postal ZIP geography.

**Done when:** an analyst can explain how the metro's formal Places and Phase 7
zone types intersect without relying on corridors or POI overlays.

## Part 2 — Activity, Infrastructure, and Structural Patterns

### Initial Richmond implementation

- [x] Add `POSITION_INTERNAL_STRUCTURE_PART2_NOTEBOOK.py` with POI
  source/mapping/tract-assignment coverage, governed-category controls, zone
  composition, per-resident descriptive context, and source points.
- [x] Reuse the D3 tract workplace-jobs threshold against its current LODES
  input for descriptive employment-center orientation.
- [x] Discover the selected market's validated Infrastructure handoff directly
  from its versioned artifact and retain its source-run provenance.
- [x] Add an integrated tract-cluster, selected-POI, and selected-
  Infrastructure orientation map.
- [x] Add Richmond/Jacksonville input-coverage review and routing guidance.
- [x] Keep POI-by-Place unavailable until Geography publishes a direct
  point-to-Place assignment; do not allocate point counts with tract weights.

### Epic 3 — Add Activity and Physical Structure — complete

- Select governed POI categories and valid population/area denominators.
- Add POI count, normalized, and composition views by both Place and zone.
- Add a narrow major-anchor view and reuse existing D3 job-center evidence.
- Add approved Infrastructure groups and an integrated market map.
- Keep all source, mapping, assignment, and denominator limitations visible.

**Done when:** the analyst can see where activity and physical networks sit in
the Place/zone structure without the notebook implying access or causation.

### Epic 4 — Synthesize and Review Across Markets — complete

- Add a short market-structure summary and route unresolved questions to Q2,
  Q4, Q5, Q6, Regional Role, or later thematic work.
- Review Richmond first and Jacksonville second.
- Add one contrasting metro when input coverage permits.
- Check Place allocation, zone composition, POI normalization, and geometry
  joins across the reviewed markets.
- Return reusable data or method defects to their owning component rather than
  patching them locally.

**Done when:** the same workflow produces a legible broad review across
materially different market forms without market-specific notebook logic.

## Closeout

- [x] Run in-notebook grain, reconciliation, null, allocation, and coverage
  checks.
- [x] Record consumed interfaces: `mart_intelligence` Phase 7 zones,
  `mart_geography` allocation and current display geometry, `mart_poi` source
  and tract-assignment products, latest LODES workplace rows using the D3
  threshold, and the validated Infrastructure artifact.
- [x] Update this Position build-sequence status after both parts are
  implemented and validated for Richmond.
- [x] Defer causal claims, editorial Place/candidate names, issue styling, and
  final stat blocks.

The completed analysis uses two focused Marimo notebooks:
`POSITION_INTERNAL_STRUCTURE_NOTEBOOK.py` for Part 1 and
`POSITION_INTERNAL_STRUCTURE_PART2_NOTEBOOK.py` for Part 2.
