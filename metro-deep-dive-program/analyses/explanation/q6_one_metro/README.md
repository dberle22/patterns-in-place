# Q6 — One Metro?

**Build order:** E7 — applies Q2 physical proximity to Census Place anchors

**Status:** Epic 1 audit complete; implementation not started.

**Question:** Which Census Places anchor this metro, and how do its other Places
relate to those anchors?

Purpose:

- report the official OMB Central/Outlying county context
- rank and profile every covered Census Place in the CBSA
- identify whether one or several Places are supported as anchors
- use physical proximity and later relationship evidence to explain those roles

**Primary analytical unit:** Census Place within CBSA. County status is sourced
context, not an analytical unit to reclassify.

**National posture:** national method, local application. Prototype the Place
hierarchy consistently, then explain a selected market in depth.

## Sourced county context

`silver.xwalk_cbsa_county` already carries the OMB 2023 Central/Outlying county
designation. Q6 shows that context and focuses its method on Places rather than
rebuilding a government metro delineation.

## How the second question is answered

Start with the full Census Place inventory, profile Place population, income,
housing, and allocated workplace-job context, then associate candidates with
Q2's reviewed job-center components. Q6 adopts Q2's V0 Haversine distance as
physical proximity, not access, travel time, commuting behavior, or a
15-minute result. OD, POI, and Infrastructure are later relationship evidence.

## Guardrail

Treat direct Place measures, allocated workplace-job context, and relationship
evidence as distinct layers. Do not use any one layer as a hidden composite
anchor score.

## Open decisions for the spec

- minimum materiality rule for Census Place candidates
- Place metric contract, including direct versus allocated measures
- OD Place-to-Place flow coverage and direct POI/Infrastructure Place interfaces

See [EXPLANATION_Q6_ONE_METRO_SPEC.md](EXPLANATION_Q6_ONE_METRO_SPEC.md) for the
analysis boundary and inputs; the [Epic 1 audit](EXPLANATION_Q6_AUDIT.md) records
the evidence and decisions. The
[EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md](EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md)
holds the epic sequence.

Section 5.2 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
