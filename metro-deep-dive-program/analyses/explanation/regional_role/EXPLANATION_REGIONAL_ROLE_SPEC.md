# Explanation Regional Role Spec

**Status:** Provisional — Epic 1 audit not yet run

**Build order:** E4 — independent track; does not depend on the access spine

**Primary surface:** `EXPLANATION_REGIONAL_ROLE_NOTEBOOK.py` (not yet written)

**Default market:** Richmond, VA (`40060`)

**Initial method:** `regional_role_v1`

**Dependencies:** Position outputs, Benchmarking, Geography, LODES WAC/RAC, IRS
migration. No new engine required for the first build.

## How to read this spec

**This spec is deliberately provisional.** Epic 1 is an audit that confirms what
already exists, and its findings are expected to reshape everything below it.
Where the audit contradicts this spec, the audit wins.

## Goal

Establish how a market fits into its broader region economically,
demographically, and functionally — read through several competing definitions
of what "region" means.

Regional Role should overlap with Position without duplicating it. Profile,
Peers, and Trajectory supply identity and comparative context; Regional Role
adds external relationships and division of labor.

Like Position, this is best treated as a **workbench** rather than a single
fixed analysis.

## National posture: market scoped

Not a national build beyond confirming it scales across markets. Do not build
national coverage tables or national distributions here.

## Three parts, in order

The analysis has three subjects and all three matter. Region definition comes
first because everything downstream depends on it, but it is the setup, not the
point.

**Part 1 — Define the region.** The biggest single piece of work and genuinely
unsettled. Each definition acts as a filter; the analysis runs under each to see
how the read changes.

| # | Lens | Strength | Weakness |
|---|---|---|---|
| 1 | Census division | Easy to explain, understand, and produce | Edge markets fit badly — does Richmond belong to the South Atlantic, or to the DC/Maryland/Delaware orbit? |
| 2 | State | Clear and legible | States can be small; a Delaware metro's state context is thin |
| 3 | Nearby counties and metros | Often the most meaningful | Needs a real construction rule. Candidate: find state borders within X miles, then take CBSAs and counties from those states — using both state boundaries, which maps read well, and physical proximity |
| 4 | Megaregions | Genuinely interesting framing; the eleven US megaregions | New to the repo, manual to bring in, only works for markets inside one. Include as a labeled lens; do not block on it |

**Functional labor sheds are an output of this analysis, not an input lens.**
They belong on the output side, produced once LODES OD exists.

**Part 2 — Establish how the market fits.** With a region defined, characterize
the market's actual role within it: what it specializes in, how jobs and workers
balance, where people and money move to and from, and what function it serves
that its neighbors do not. This is the substance and the basis of the role
hypothesis.

**Part 3 — Compare.** Place the market against the rest of the region and
against nearby metros, through tables and maps. Closest to our Position
products.

Region definition feeds back into Parts 2 and 3: each lens produces a different
comparison set, so the fit and comparison reads shift as the boundary moves. The
industry-role comparison is most sensitive to this, and showing how it changes
across lenses is a finding in its own right — but it supplements the role and
comparison work rather than replacing it.

## Preliminary read of what exists

**Provisional. Epic 1 must confirm or correct all of this.**

| Observation | Why it matters | What Epic 1 must settle |
|---|---|---|
| A state-to-region/division crosswalk appears to exist covering all states | Lenses 1 and 2 look directly supported | Confirm it carries both census region and division |
| CBSA-to-state and CBSA-to-county crosswalks appear present | Lens 3 has a starting point | Confirm whether any distance or adjacency relation exists, or must be derived from geometry |
| County and state IRS migration flows appear present for 2012–2022 | Origin/destination migration is supported | Confirm grain, disclosure suppression, and how flows are keyed |
| LODES WAC/RAC appear present at tract and county grain, 2023 only | Jobs/workers balance is supported | Confirm; and confirm no OD table exists anywhere |
| **No LODES OD table appears to exist** | Commute sheds and true functional integration are not yet possible | Confirm, and label all commute-shed content as deferred |
| No megaregion layer appears to exist in the repo | Lens 4 needs manual sourcing | Decide whether it is in scope for v0 at all |

## Inputs

| Input | Role |
|---|---|
| Position Profile, Peers, Trajectory outputs | Identity and comparative context |
| Benchmarking and Geography identities/rollups | Comparison surfaces and relationships |
| State/region/division and CBSA/county crosswalks | Lens construction |
| LODES WAC/RAC jobs, workers, earnings bands, industry mix | Jobs/workers balance and industry role |
| IRS county migration origins, destinations, people, AGI | Migration exchange |
| Infrastructure context | Interregional connections where useful |
| Later: LODES OD | Commute shed — deferred until the source exists |

## Output analyses, each run with the defined region as input

- **Regional comparison** — comparison table and map placing the market in
  context. Select KPIs for the table and for map color.
- **Job/worker balance** — map of inflows and outflows. May or may not amount to
  much; worth testing.
- **Industry role comparison** — what the market specializes in versus the rest
  of the region. Most sensitive to region definition.
- **IRS and LODES origin/destination** — maps of how people move in and out,
  separating more permanent moves (IRS) from commuting patterns (LODES).
- **Nearby metro comparison** — an extension of the benchmarks.
- **Infrastructure map** — built environment and network comparison.
- **Market role hypothesis** — written up manually from the above.

## Build approach

Define components first and reuse what exists. Start with a single market and
build to see how it works. Consider splitting into a **setup notebook** that
defines region lenses and components, and a **run notebook** that executes the
analysis for a market.

## Guardrails

- do not label WAC/RAC balance as inflow/outflow; that claim requires flows
- do not claim functional integration without OD
- do not let region definition become the whole analysis; Parts 2 and 3 are the
  payload
- do not build national scaffolding this posture does not need

## Open decisions

- the nearby-region construction rule (the X-mile border threshold)
- whether megaregions are in scope for v0
- base/traded industry treatment
- minimum migration-flow disclosure rule
- what evidence qualifies a role label

## References

- Section 5.1 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_REGIONAL_ROLE_BUILD_PLAN.md](EXPLANATION_REGIONAL_ROLE_BUILD_PLAN.md)
