# Q6 — One Metro?

**Build order:** E7 — re-runs the E3 access method with anchor cities as centers

**Status:** Spec and build plan drafted; Epic 1 audit not yet run.

**Question:** Is this really one metro — and if not, how many centers does it
have?

Purpose:

- test whether outlying counties belong to the same labor market
- test whether the metro has multiple anchor cities
- use the 15-minute concept as a proxy for the number of city centers

**Primary analytical unit:** county within CBSA for the integration read;
candidate centers and their access surfaces for the polycentricity read.

**National posture:** national method, local application. Prototype now; do not
claim integration until OD flow data exists.

## Two questions under one heading

The scope is deliberately wider than the original county-integration framing:

1. Do the CBSA's outlying counties belong to the same labor market, or are they
   administratively attached with weak integration?
2. **Does the metro have multiple anchor cities?** This is the more interesting
   half.

Widening the scope this way makes the question clearer, even though it is really
more than one question.

## How the second question is answered

Run Q2's access method with anchor cities and candidate downtowns as the center
input, and see how many coherent centers the metro actually supports. The
surfaces to work from — **commute flows, job corridors, and amenity clusters** —
are the same three that Q2 and Q4 produce. Q6 is largely a re-reading of those at
metro scale, asking whether they resolve into one center or several.

## Guardrail

Treat county economic role, employment-center distribution, industry similarity,
and polycentricity as **structural evidence, not a functional-integration
score.** Integration claims require OD flows; WAC/RAC alone cannot support them.

## Open decisions for the spec

- definition of the core
- numerator and denominator for commuting shares
- multidirectional versus core-directed integration
- treatment of cross-CBSA flows
- polycentricity measure and classification thresholds

See [EXPLANATION_Q6_ONE_METRO_SPEC.md](EXPLANATION_Q6_ONE_METRO_SPEC.md) for the
analysis boundary and inputs, and
[EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md](EXPLANATION_Q6_ONE_METRO_BUILD_PLAN.md) for
the epic sequence. Both are provisional: Epic 1 is an audit of what already
exists, and its findings are expected to reshape them.

Section 5.2 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
