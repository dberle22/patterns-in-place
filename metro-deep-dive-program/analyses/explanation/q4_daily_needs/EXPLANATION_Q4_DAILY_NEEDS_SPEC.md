# Explanation Q4 — Daily-Needs Access Spec

**Status:** Provisional — Epic 1 audit not yet run

**Build order:** E5 — re-runs the E3 access method with POI clusters as centers

**Primary surface:** `EXPLANATION_Q4_NOTEBOOK.py` (not yet written)

**Pilot markets:** Richmond, VA (`40060`) and Jacksonville, FL (`27260`)

**Initial method:** `q4_daily_needs_v1`

**Dependencies:** Q2's access method, governed POI runs, tract geometry and
population. No new engine required for the first build.

## How to read this spec

**This spec is deliberately provisional.** Epic 1 is an audit that confirms what
already exists, and its findings are expected to reshape everything below it.
Where the audit contradicts this spec, the audit wins.

## Goal

Establish which parts of a metro have practical proximity to a defensible basket
of everyday needs — and, in doing so, test whether Q2's access method survives a
different center construction.

## What this analysis owns, and what it borrows

**Borrows from Q2:** the access method and the 15-minute operational definition.
Adopt it unchanged where possible; where you deliberately vary it, say so and
give the reason.

**Owns:** the amenity basket and the reach definition applied to it.

**Does not own:** POI source identity, provenance, classification, or
assignment. Those stay with the POI Engine. **POI counts are inputs, not
access.**

## Why this is a test of the shared method

Q4 is the first analysis to run Q2's method against a genuinely different center
construction. If POI-built clusters produce an incoherent result under that
method, that is a finding about the method itself, not only about Q4. Treat a
bad result here as informative rather than as a Q4 failure, and report it back
to the shared definition.

## National posture: national method, local application

Market-pilot ready; **not nationally ready.** Review category coverage and
urban-form sensitivity before acquiring or processing national POIs. Only after
the basket and score survive the two-market test should the method scale
nationally.

## Preliminary read of what exists

**Provisional. Epic 1 must confirm or correct all of this.**

| Observation | Why it matters | What Epic 1 must settle |
|---|---|---|
| Governed POI runs appear to exist for exactly two markets — Richmond and Jacksonville | The two-market pilot is supported; national is not | Confirm coverage and that both runs are governed, not provisional |
| A POI geography assignment surface appears to carry tract, county, and ZIP assignments | Tract-grain access work is supported | Confirm assignment method and status fields, and how unassigned records behave |
| A taxonomy hierarchy profile surface appears to exist with mapping status | Basket construction has prior art | Determine what `mapping_status` means and which categories are reliably mapped |
| A meaningful share of classified places appear to carry a null primary taxonomy | Basket coverage may be weaker than raw counts suggest | Quantify the null and low-confidence share by category |
| Category mix looks dominated by non-daily-needs types in places | The basket must be deliberately narrow | Review actual category frequencies before choosing basket members |

## Inputs

| Input | Role |
|---|---|
| Declared POI Engine runs and governed taxonomy mappings | Amenity source |
| POI geography assignment | Tract assignment |
| Tract identity and geometry | Access base |
| Population and selected demographic denominators | Normalization |
| Q2 access method and 15-minute definition | The reach method |
| Place Intelligence method references | Prior art |
| Infrastructure | Only if the access method names a barrier requirement |

## V0 method

Use Richmond and Jacksonville to define a narrow daily-needs basket, coverage
rules, and a simple proximity/reach measure. Apply Q2's access method with POI
clusters as the center input. Review category coverage and urban-form
sensitivity before any national scale-out.

The basket and category-coverage work can be designed in parallel with Q2, since
it does not depend on the access method.

## Minimum outputs

Category and mapping coverage, amenity inventory, tract access components,
selected-market access map and distribution, national comparison after
scale-out, sensitivity to basket and reach choices, and an explicit
`unavailable` result where source coverage is inadequate.

## Guardrails

- POI counts are inputs, not access
- do not rewrite POI taxonomy, provenance, or assignment locally
- do not grow a second 15-minute definition; adopt Q2's and document any
  deliberate variation
- do not scale nationally before the two-market review passes
- report inadequate coverage as `unavailable` rather than producing a weak score

## Open decisions

- basket categories and the multi-category sufficiency rule
- distance or reach method
- scoring and caps; population weighting
- urban/rural comparability
- treatment of barriers
- national source and run strategy

## References

- Section 5.6 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md](EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md)
