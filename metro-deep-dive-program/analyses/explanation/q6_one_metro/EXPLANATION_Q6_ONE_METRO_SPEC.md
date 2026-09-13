# Explanation Q6 — One Metro? Spec

**Status:** Provisional — Epic 1 audit not yet run

**Build order:** E7 — re-runs the E3 access method with anchor cities as centers

**Primary surface:** `EXPLANATION_Q6_NOTEBOOK.py` (not yet written)

**Default market:** Richmond, VA (`40060`)

**Initial method:** `q6_one_metro_v1`

**Dependencies:** Regional Role components, LODES WAC/RAC, Q2's access method.
LODES OD is required for the complete method and does not appear to exist.

## How to read this spec

**This spec is deliberately provisional.** Epic 1 is an audit that confirms what
already exists, and its findings are expected to reshape everything below it.
Where the audit contradicts this spec, the audit wins.

## Goal

Determine whether a CBSA is really one metro — and if not, how many centers it
has.

## Two questions under one heading

The scope is deliberately wider than the original county-integration framing:

1. Do the CBSA's outlying counties belong to the same labor market, or are they
   administratively attached with weak integration?
2. **Does the metro have multiple anchor cities?** This is the more interesting
   half.

Widening the scope this way makes the question clearer, even though it is really
more than one question. The two halves have different data readiness, and the
spec should not pretend otherwise.

## How the second question is answered

Run Q2's access method with anchor cities and candidate downtowns as the center
input, and see how many coherent centers the metro actually supports. The
surfaces to work from — **commute flows, job corridors, and amenity clusters** —
are the same three that Q2 and Q4 produce. Q6 is largely a re-reading of those
at metro scale, asking whether they resolve into one center or several.

This makes Q6 the third test of the shared access method, against a third center
construction.

## National posture: national method, local application

Prototype nationally; do not claim integration until OD exists.

## Preliminary read of what exists

**Provisional. Epic 1 must confirm or correct all of this.**

| Observation | Why it matters | What Epic 1 must settle |
|---|---|---|
| LODES WAC/RAC appear present at tract and county grain, 2023 only | County role, balance, and employment-center evidence are supported | Confirm grain and vintage |
| **No LODES OD table appears to exist anywhere in the warehouse** | The functional-integration half of this question is genuinely blocked | Confirm, and record it as the gating dependency |
| CBSA-to-county crosswalks appear present | Core and outlying counties can be identified | Confirm vintage and central/outlying flags |
| Phase 7 zone surfaces appear present | Polycentric form has interpretation context | Confirm what they carry at tract and ZCTA grain |
| Q2 will produce a center definition and access surfaces | The anchor-city half is supported once Q2 lands | Record exactly what Q6 adopts |

The honest reading is that **half this analysis is buildable now and half is
not.** The anchor-city question can proceed on WAC/RAC and Q2's method; the
integration question waits on OD. The spec should keep them visibly separate
rather than blending them into one weaker answer.

## Inputs

| Input | Role |
|---|---|
| Regional Role comparison surfaces | Regional context |
| County and tract LODES WAC/RAC | County role, balance, employment centers |
| County industry mix | Industry similarity |
| Q2 access method and center definition | The anchor-city read |
| Q4 amenity clusters | Supporting center evidence |
| Phase 7 / Internal Structure context | Polycentric form description |
| Required for the complete method: LODES OD | Functional integration — currently unavailable |

## V0 method

Prototype county economic role, employment-center distribution, industry
similarity, and polycentricity nationally. Treat these as **structural evidence,
not a functional-integration score.** Add OD shares when available, then test
how much each outlying county sends to the core and receives from the rest of
the CBSA.

## Minimum outputs

County role table, county integration matrix after OD, employment-center map,
core/outlying comparison, candidate anchor-city inventory with its access
surfaces, sensitivity table for the integration rule, and an explicit
`integrated`, `mixed`, `weak`, or `insufficient flow data` result.

## Guardrails

- do not claim commuting integration from WAC/RAC without OD
- keep the two halves of the question visibly separate
- return `insufficient flow data` honestly rather than substituting a weaker
  proxy and calling it integration
- do not silently diverge from Q2's access definition

## Open decisions

- definition of the core
- numerator and denominator for commuting shares
- multidirectional versus core-directed integration
- treatment of cross-CBSA flows
- polycentricity measure and classification thresholds

## References

- Section 5.2 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md](EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md)
