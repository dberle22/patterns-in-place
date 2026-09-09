# Position Internal Structure Build Plan

**Status:** Planned

Build one Marimo notebook in two parts. Start with the full market geography
and zone anatomy, then add activity, physical structure, and corridors. The
notebook should remain useful before Corridor Intelligence is implemented.

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
- Corridor Intelligence supplies only the later corridor/district section.

Before building, confirm the exact fields, vintages, allocation bases, market
coverage, and display geometry needed by each view. Materialize Place or other
display geometry only when a planned map needs it. Do not open a new engine or
broad Foundations project for notebook-specific joins.

## Part 1 — Market Geography and Zone Structure

### Epic 1 — Assemble the Market Anatomy Slice

- Select the governed CBSA, county, Census Place, tract, and ZCTA identities
  and relationships for Jacksonville.
- Confirm how incorporated/CDP and unincorporated shares remain visible.
- Select a small set of additive population and housing scale fields with
  explicit vintages and allocation bases.
- Confirm the Phase 7 tract and ZCTA fields and national zone-composition
  baseline.
- Obtain only the market-scoped display geometry required by the planned maps.

**Done when:** Jacksonville loads as one reconciled, read-only geography and
zone slice with visible allocation, metric, and geometry coverage.

### Epic 2 — Build the Places and Zones Review

- Add market controls and the coverage summary.
- Add the geography hierarchy map and Place inventory.
- Add the tract zone map and market composition comparison.
- Add the two-direction Place × Zone matrix and selected-Place profile.
- Add the supporting ZCTA view without presenting it as postal ZIP geography.

**Done when:** an analyst can explain how the metro's formal Places and Phase 7
zone types intersect without relying on corridors or POI overlays.

## Part 2 — Activity, Infrastructure, and Structural Patterns

### Epic 3 — Add Activity and Physical Structure

- Select governed POI categories and valid population/area denominators.
- Add POI count, normalized, and composition views by both Place and zone.
- Add a narrow major-anchor view and reuse existing D3 job-center evidence.
- Add approved Infrastructure groups and an integrated market map.
- Keep all source, mapping, assignment, and denominator limitations visible.

**Done when:** the analyst can see where activity and physical networks sit in
the Place/zone structure without the notebook implying access or causation.

### Epic 4 — Add the Corridor and District Section

- Consume one versioned Corridor Intelligence run when available.
- Add the candidate map, inventory, form, and core/bridge evidence review.
- Show which Places, centers, zones, and physical features each candidate
  crosses or connects.
- Confirm that hiding the corridor section leaves all earlier market-anatomy
  results unchanged.

**Done when:** corridors and districts add a useful structural lens without
becoming the organizing frame for the notebook or being edited locally.

### Epic 5 — Synthesize and Review Across Markets

- Add a short market-structure summary and route unresolved questions to Q2,
  Q4, Q5, Q6, Regional Role, or later thematic work.
- Review Jacksonville first and Richmond second.
- Add one contrasting metro when input coverage permits.
- Check Place allocation, zone composition, POI normalization, geometry joins,
  and Corridor portability across the reviewed markets.
- Return reusable data or method defects to their owning component rather than
  patching them locally.

**Done when:** the same workflow produces a legible broad review across
materially different market forms without market-specific notebook logic.

## Closeout

- Run in-notebook grain, reconciliation, null, allocation, and coverage checks.
- Record which engine and Foundations interfaces were consumed unchanged.
- Update Position and build-sequence status after each part is reviewed.
- Defer causal claims, editorial Place/candidate names, issue styling, and final
  stat blocks.

The completed analysis remains one Marimo notebook with two clearly labeled
parts unless interactive review demonstrates a concrete usability or
performance reason to split it further.
