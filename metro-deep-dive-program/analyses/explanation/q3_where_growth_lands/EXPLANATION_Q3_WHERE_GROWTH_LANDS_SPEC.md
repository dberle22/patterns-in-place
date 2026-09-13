# Explanation Q3 — Where Growth Lands Spec

**Status:** Provisional — Epic 1 audit not yet run

**Build order:** E6 — re-runs the E3 access method against the prior built
footprint

**Primary surface:** `EXPLANATION_Q3_NOTEBOOK.py` (not yet written)

**Default market:** Richmond, VA (`40060`)

**Initial method:** `q3_growth_location_v1`

**Dependencies:** Tract population and housing histories, temporal crosswalks,
tract geometry, Q2's access method.

## How to read this spec

**This spec is deliberately provisional.** Epic 1 is an audit that confirms what
already exists, and its findings are expected to reshape everything below it.
Where the audit contradicts this spec, the audit wins.

## Goal

Determine whether recent population and housing growth is landing in infill
areas, greenfield edges, already-developed outer centers, or nowhere.

## National posture: national method, local application

## Two prerequisites before the analysis proper

This analysis has more upfront method work than most. Both prerequisites are
real work, not setup.

**1. Tract harmonization.** Restate comparable population and housing-unit
counts on a declared tract vintage. The 2010-to-2020 boundary change is the
central problem and is best opened as its own vertical slice.

**2. An infill/greenfield standard.** `Infill` and `greenfield` must be
**measured conditions**, not labels inferred from whether a tract looks central
on a map. Without an operational standard, the classification is just a vibe.

Only then does the analysis — how growth rates and permits compare against that
standard — become tractable.

## Relationship to the access spine

Q3 is close kin to Q2 but measures growth against historic density and built
environment rather than cost against distance. It reads growth against Q2's
access surfaces: what are the new 15-minute areas, and is growth happening
inside them or outside them?

## Preliminary read of what exists

**Provisional. Epic 1 must confirm or correct all of this.**

| Observation | Why it matters | What Epic 1 must settle |
|---|---|---|
| A temporal crosswalk surface appears to exist with weight basis, change type, and allocation weights | Harmonization may be substantially supported already | Confirm it covers the tract vintages Q3 needs, and what its weight basis is |
| An allocation-edges surface and containment crosswalk appear present | Cross-vintage and cross-grain allocation has prior art | Determine quality flags and whether they are fit for count restatement |
| Tract population and housing histories appear present 2012–2024 | The change measures are supported | Confirm which fields are populated at tract grain across the full window |
| **Permits appear absent at tract and ZCTA grain** and present at Place, county, and CBSA | Permits stay a separate labeled lens; they cannot be assigned to tracts | Confirm the non-null pattern by grain |
| Structure, density, and vacancy context appear present at tract grain | The prior-built-footprint read is supported | Confirm which fields best express prior density |

## Inputs

| Input | Role |
|---|---|
| Tract population and housing-unit histories | Change measures |
| Temporal and allocation crosswalks | Harmonization |
| Tract geometry | Footprint and edge logic |
| Housing structure, density, vacancy context | Prior built condition |
| Permit evidence at Place/county grain | Supporting context only |
| Q2 access surfaces | Reading growth against access |
| Phase 7 zone types and Infrastructure | Interpretation layers only |

## V0 method

First restate comparable population and housing-unit counts on a declared tract
vintage. Then classify growing tracts from their prior density, location
relative to the existing developed footprint, and change in housing units and
population.

## Minimum outputs

Harmonization QA, national growth-location distribution, CBSA summary,
selected-market tract classification map, population-versus-unit change table,
and a residual/unclassified group.

## Guardrails

- do not assign county or Place permits to tracts
- do not infer infill or greenfield from map appearance
- do not hide harmonization error; report it as QA
- do not drop tracts that fail classification; keep a residual group

## Open decisions

- comparison years and harmonization basis
- growth floor
- developed-footprint baseline
- infill/greenfield/outer-center rules
- treatment of large rural tracts
- negative and no-growth classes

## References

- Section 5.5 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_Q3_WHERE_GROWTH_LANDS_BUILD_PLAN.md](EXPLANATION_Q3_WHERE_GROWTH_LANDS_BUILD_PLAN.md)
