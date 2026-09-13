# Explanation Corridor Opportunity Read Spec

**Status:** Provisional — Epic 1 audit not yet run

**Build order:** E8 — closing synthesis; runs last

**Primary surface:** `EXPLANATION_CORRIDOR_OPPORTUNITY_NOTEBOOK.py` (not yet
written)

**Default market:** Richmond, VA (`40060`)

**Initial method:** `corridor_read_v1`

**Dependencies:** Q2, Q3, and Q4 outputs. **No engine dependency.**

## How to read this spec

**This spec is deliberately provisional.** Epic 1 is an audit that confirms what
already exists, and its findings are expected to reshape everything below it.
Where the audit contradicts this spec, the audit wins.

This spec is more provisional than most, because its primary inputs do not exist
yet. It cannot be meaningfully completed until Q2, Q3, and Q4 have produced
results. Treat it as a placeholder that records intent and constraints.

## Reframed: no engine dependency

This is **no longer a standalone analysis sitting on top of a Corridor
Intelligence engine.** That engine is a paused prototype whose Jacksonville and
Richmond artifacts are method reference only, not a consumer dependency.

Corridors now emerge organically from the 15-minute-city work — the access spine
in Q2, Q3, and Q4 keeps producing corridor-shaped results. This analysis
summarizes those.

Because of this, the previous gate — engine calibration, Richmond validation,
and a consumer handoff — no longer applies. What replaces it is a simpler and
more honest dependency: **there is nothing to synthesize until the upstream
analyses have run.**

## Goal

Taken together, what do the preceding analyses say about which corridors in this
market deserve deeper attention, and why?

## National posture: market scoped

## The central open question

**How is a corridor identified from upstream outputs, now that no engine
supplies membership?**

This is the question the analysis exists to answer and the one thing Epic 1
cannot resolve in advance. Candidate approaches, none yet tested:

- contiguous runs of high access from Q2's gradient
- POI cluster chains from Q4
- growth corridors from Q3's classification
- some combination, requiring a reconciliation rule

The answer should emerge from looking at real Q2/Q3/Q4 output, not from deciding
in advance.

## Inputs

All provisional; none exist yet.

| Input | Role |
|---|---|
| Q2 access, gradient, and affordability surfaces | Primary corridor evidence |
| Q4 POI clusters and daily-needs corridors | Amenity-based corridor evidence |
| Q3 growth-location classification | Trajectory evidence |
| Regional Role and Trajectory | Context where routed |
| Internal Structure market anatomy | Structural context |
| POI and Infrastructure governed handoffs | Physical context |
| Jacksonville/Richmond Corridor Intelligence artifacts | **Method reference only**, not a candidate source |

## V0 method

Synthesize across three evidence families:

1. structural role and connectivity
2. people, jobs, access, and housing conditions
3. current trajectory and issue relevance

## Minimum outputs

Comparison matrix across identified corridors, selected-corridor profile, map,
evidence-and-caveat table, one-sentence thesis candidates, and suggested
follow-on analyses.

## Guardrails

- do not create a canonical corridor boundary; this is analysis-local
- do not build one universal Investment Score before individual evidence
  families have been tested
- do not draw an investment conclusion from a corridor read
- do not revive Corridor Intelligence as a dependency
- do not start before the upstream analyses have real output

## Open decisions

- **how a corridor is identified from upstream outputs** — the central question
- comparison dimensions and evidence normalization
- selection versus ranking
- treatment of no-opportunity results
- handoff to issue-owned naming and stat blocks

## References

- Section 5.7 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- [EXPLANATION_CORRIDOR_OPPORTUNITY_READ_BUILD_PLAN.md](EXPLANATION_CORRIDOR_OPPORTUNITY_READ_BUILD_PLAN.md)
