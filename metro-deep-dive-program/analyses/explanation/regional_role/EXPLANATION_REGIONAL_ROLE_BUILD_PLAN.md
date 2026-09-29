# Explanation Regional Role Build Plan

**Status:** Epics 1–5 complete. The baseline dependencies, workbench, and
market-role evidence surfaces are implemented; review begins in Epic 6.

## How this plan works

**Epic 1 is an audit, and it comes first.** Its findings now define the V1
contract in `EXPLANATION_REGIONAL_ROLE_SPEC.md`. The reusable Geography work is
an explicit prerequisite rather than analysis-local notebook logic.

## Epic 1 — Audit the Region Inputs

- [x] Confirm the state/region/division crosswalk and what fields it carries.
- [x] Confirm CBSA-to-state and CBSA-to-county relationships and their vintages.
- [x] Confirm that `gold.dim_geo.state_fips` defines primary state as the first
  state in the official CBSA name, not county count or population.
- [x] Determine that no reusable adjacency or distance relation exists; both
  require the new Geography interfaces.
- [x] Confirm IRS migration flow grain, 2012–2022 coverage, and null/suppression
  behavior. Gold already exposes county/CBSA/state inflow, outflow, and net
  summaries; detailed county flows can be rolled to CBSA pairs for partners.
- [x] Confirm 2023 LODES WAC/RAC grain and coverage.
- [x] **Confirm plainly that no LODES OD table exists.** Commute-shed content is
  deferred to V2.
- [x] Confirm industry mix and specialization measures in Gold and Position.
- [x] Defer megaregions from V1 because no governed source layer exists.
- [x] Review Position Profile, Peers, and Trajectory outputs for reuse.

**Done when:** each of the four lenses is either confirmed buildable with named
sources, or recorded as blocked with the reason. The spec is rewritten against
those findings.

Findings are recorded in `EXPLANATION_REGIONAL_ROLE_AUDIT.md`.

## Epic 2 — Reconcile Benchmarking Primary-State Membership

Benchmarking's existing `state_primary` build derives primary state from the
state with the most member counties. Geography's governed rule uses the first
state named in the official CBSA label. Regional Role requires the Geography
rule, so reconcile the reusable Benchmarking contract before a consumer relies
on a primary-state benchmark.

- [x] Replace the county-count primary-state derivation in Benchmarking's set
  and membership builders with `gold.dim_geo.state_fips` for CBSA rows.
- [x] Update the Benchmarking contract, notes, and comparison descriptions to
  name the first-state-in-official-CBSA-label rule.
- [x] Rebuild `mart_benchmarking.benchmark_sets` and
  `mart_benchmarking.benchmark_set_members` sequentially.
- [x] Add a regression check for at least one multi-state CBSA, confirming that
  the stored `state_primary` set and its members use the same state as
  `gold.dim_geo.state_fips`.
- [x] Confirm national, division, peer, and `state_member` memberships retain
  their existing counts or explain any intentional change.

**Done when:** the governed Geography primary-state identity and Benchmarking
`state_primary` comparison set agree for every covered metropolitan CBSA.

**Completed 2026-09-21:** `state_primary` now uses
`gold.dim_geo.state_fips` / the first state in the official CBSA label.
Rebuilding produced 393 primary-state sets, one for every covered metro CBSA;
zero stored-state mismatches remain. Wheeling, WV-OH resolves to West Virginia.
Other set types remained materialized in the same sequential build.

## Epic 3 — Build reusable Region Lenses in Geography

This work is owned by the Geography engine. See Epic 9 in
`engines/geography/GEOGRAPHY_ENGINE_BUILD_PLAN.md`.

- [x] Publish approved analytical state and CBSA geometry.
- [x] Build land-only state adjacency using a shared border line of nonzero
  length; rivers count, while ocean, Great Lake, and point-only contact do not.
  Build declared CBSA centroids.
- [x] Materialize membership for the division, primary-state, primary-state-plus-
  adjacent-states, and centroid-radius lenses.
- [x] Validate Richmond and a multi-state CBSA, including the first-named-state
  primary-state rule.

**Done when:** each Regional Role lens is available as a versioned,
provenance-bearing Geography surface, not a notebook-only calculation.

**Completed 2026-09-21:** Geography now exposes 51 full-TIGER state/DC and 935
CBSA analytical geometries, 220 symmetric adjacency edges, 935 declared CBSA
centroids, and 76,128 membership rows. Richmond has 9 primary-state members,
52 primary-state-plus-adjacent-state members, and 48 members at the 250-mile
radius; membership keys are unique and every target/lens has exactly one target
row.

## Epic 4 — Build the Regional Role workbench

- [x] Build the setup notebook: membership provenance, overlap, sensitivity, and
  boundary map.
- [x] Build the run notebook with a national metro baseline, persistent
  all-lens panel, and active-lens controls.
- [x] Consume Geography membership for Regional Role lenses; Benchmarking's
  reconciled `state_primary` set is available for its separate comparison use.
- [x] Build the active regional comparison table and map.

**Done when:** an analyst can verify the selected region before interpreting a
market's role inside it.

**Completed 2026-09-21:**
`EXPLANATION_REGIONAL_ROLE_SETUP_NOTEBOOK.py` exposes governed membership,
radius sensitivity, pairwise lens overlap, provenance, and a display-only
active-lens map. `EXPLANATION_REGIONAL_ROLE_NOTEBOOK.py` exposes the national
metro baseline, persistent four-lens KPI panel, and active-lens CBSA comparison
table/map. Both notebooks read named SQL surfaces only; neither writes a
Regional Role mart or recreates Geography relationships.

## Epic 5 — Establish the Market's Role

- [x] Build the industry role comparison against each lens.
- [x] Build the descriptive jobs-versus-workers balance.
- [x] Build IRS migration at both existing CBSA-summary and rolled CBSA-pair
  grain, retaining within-CBSA moves, non-CBSA county endpoints, and
  nearby/distant partner context.
- [x] Add the market-scoped Infrastructure context map after the Geography
  analytical boundary promotes the existing serving candidate.
- [x] Assemble manual evidence for a market-role hypothesis.

**Done when:** the analysis says something about what the market does within its
region, not only where it ranks.

**Completed 2026-09-21:** The run notebook now provides industry share/LQ
evidence, descriptive 2023 LODES jobs-versus-resident-workers evidence, and
2022 IRS county-flow rolls to partner-CBSA exchange with inside/outside-lens,
within-target, and non-CBSA county categories. Richmond's cached OSM source
run was rebuilt and revalidated against `geo.cbsas_analysis`; the unchanged
validated handoff now supplies a contextual road/rail/water map. A free-text
manual hypothesis surface retains analyst authorship and caveats.

## Epic 6 — Review and Split the Notebooks

- [ ] Test on a second market with a different regional character.
- [ ] Review the setup/run notebook boundary after both surfaces are in use.
- [ ] Record which Geography interfaces are ready for Q6 reuse.
- [ ] Record what Q6 can reuse.

**Done when:** the workbench is reusable across markets and its long-term
geography ownership is written down.

## What not to do

- do not present WAC/RAC balance as commuting flows
- do not block the whole analysis on megaregions
- do not rebuild Position's identity or peer logic
- do not let the lens comparison crowd out the role and comparison work
