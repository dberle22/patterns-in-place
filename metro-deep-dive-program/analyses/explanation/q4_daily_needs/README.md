# Q4 — Daily-Needs Access

**Build order:** E5 — re-runs the E3 access method with POI clusters as centers

**Status:** Spec and build plan drafted; Epic 1 audit not yet run.

**Question:** Which parts of a metro have practical proximity to a defensible
basket of everyday needs?

Purpose:

- define a narrow, defensible daily-needs basket
- apply Q2's access method with POI clusters as the center input
- produce another way of building corridors, this time from POI types rather than
  job centers

**Primary analytical unit:** tract, derived from governed POI points and an
explicitly defined reach method.

**National posture:** national method, local application. Market-pilot ready; not
nationally ready.

## What this analysis owns, and what it borrows

**Borrows from Q2:** the access method and the 15-minute operational definition.
Adopt it unchanged where possible; where you deliberately vary it, say so and
give the reason.

**Owns:** the amenity basket and the reach definition applied to it.

**Does not own:** POI source identity, provenance, classification, or assignment
— those stay with the POI Engine. POI counts are inputs, not access.

## Why this is a test of the shared method

Q4 is the first analysis to run Q2's method against a genuinely different center
construction. If POI-built clusters produce an incoherent result under that
method, that is a finding about the method itself, not only about Q4. Treat a bad
result here as informative rather than as a Q4 failure.

## V0 method

Use Richmond and Jacksonville to define the basket, coverage rules, and a simple
proximity/reach measure. Review category coverage and urban-form sensitivity
**before** acquiring or processing national POIs. Only after the basket and score
survive the two-market test should the method scale nationally.

The basket and category-coverage work can be designed in parallel with Q2, since
it does not depend on the access method.

## Open decisions for the spec

- basket categories and the multi-category sufficiency rule
- distance or reach method
- scoring and caps; population weighting
- urban/rural comparability
- treatment of barriers
- national source and run strategy

See [EXPLANATION_Q4_DAILY_NEEDS_SPEC.md](EXPLANATION_Q4_DAILY_NEEDS_SPEC.md) for the
analysis boundary and inputs, and
[EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md](EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md) for
the epic sequence. Both are provisional: Epic 1 is an audit of what already
exists, and its findings are expected to reshape them.

Section 5.6 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
