# Regional Role

**Build order:** E4 — independent track; does not depend on the access spine

**Status:** Epics 1–5 complete. The V1 contract, Geography prerequisite, and
read-only evidence workbench are implemented; no Regional Role mart exists.

**Question:** How does this market fit into its broader region economically,
demographically, and functionally?

Purpose:

- define what "region" means for a given market, across several competing lenses
- establish the market's actual role within that region
- compare the market against the rest of the region and nearby metros

Regional Role should overlap with Position without duplicating it. Profile,
Peers, and Trajectory supply identity and comparative context; Regional Role adds
external relationships and division of labor.

**Primary analytical unit:** selected CBSA, its member counties, surrounding
counties and metros, read through several competing region definitions.

**National posture:** market scoped. Not a national build beyond confirming it
scales across markets.

Like Position, this is best treated as a **workbench** rather than a single fixed
analysis.

## Three parts, in order

**Part 1 — Define the region.** The biggest single piece of work and genuinely
unsettled. Four lenses, each acting as a filter, run to see how the read changes:

| Lens | Strength | Weakness |
|---|---|---|
| Census division | Easy to explain and produce | Edge markets fit badly |
| State | Clear and legible | States can be small |
| Primary state plus adjacent states | State-legible broader orbit | Requires a reusable land-adjacency relationship |
| 250-mile CBSA proximity | Transparent geographic-proximity challenger | Requires declared CBSA centroids |

Megaregions are deferred to V2. Functional labor sheds remain an output once
LODES OD exists, not an input lens.

Functional labor sheds are an **output** of this analysis, not an input lens.

**Part 2 — Establish how the market fits.** What it specializes in, how jobs and
workers balance, where people and money move, what function it serves that
neighbors do not. This is the substance and the basis of the role hypothesis.

**Part 3 — Compare.** Place the market against the region and nearby metros
through tables and maps. Closest to our Position products.

Region definition feeds back into Parts 2 and 3: each lens produces a different
comparison set, so the fit and comparison reads shift as the boundary moves. The
industry-role comparison is most sensitive to this, and showing how it changes
across lenses is a finding in its own right — but it supplements the role and
comparison work rather than replacing it.

## Build approach

Define components first and reuse what exists. Start with a single market and
build to see how it works. Consider splitting into a **setup notebook** that
defines region lenses and components, and a **run notebook** that executes the
analysis for a market.

## Guardrail

Do not label WAC/RAC balance as inflow/outflow; that claim requires flows.

## Open decisions for the spec

- the nearby-region construction rule (the X-mile border threshold)
- minimum migration-flow disclosure rule

V1 role labels remain analyst-authored rather than automatic classifications.

See [EXPLANATION_REGIONAL_ROLE_SPEC.md](EXPLANATION_REGIONAL_ROLE_SPEC.md) for the
analysis boundary and inputs, and
[EXPLANATION_REGIONAL_ROLE_BUILD_PLAN.md](EXPLANATION_REGIONAL_ROLE_BUILD_PLAN.md) for
the epic sequence. Both are provisional: Epic 1 is an audit of what already
exists, and its findings are expected to reshape them.

Section 5.1 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
