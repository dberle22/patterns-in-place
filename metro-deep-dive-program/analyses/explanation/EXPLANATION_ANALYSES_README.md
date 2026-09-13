# Explanation Analyses

`explanation/` holds the question notebooks that test *why* a metro sits where
it does.

Position analyses say where a metro sits. Explanation analyses examine variation
and relationships below the CBSA level to explain it. Their primary evidence is
usually tract, county, Place, ZCTA, point, corridor, or parcel grain, even when
the result is summarized for national comparison.

These are reusable research instruments. They can feed Act 2, Act 3, or Act 4,
but no single act owns them.

**Planning source:** [EXPLANATION_ANALYSES_PLAN.md](EXPLANATION_ANALYSES_PLAN.md)
is authoritative for this family — scope, sequence, and the decisions each spec
must lock. [EXPLANATION_ANALYSES_FEEDBACK.md](EXPLANATION_ANALYSES_FEEDBACK.md)
is the review that shaped the current version of that plan.

## Status

**All nine analyses have a provisional spec and build plan.** No notebooks or
queries exist yet. No Epic 1 audit has been run.

Specs are written in two stages: a general shape with inputs and epics, then an
**Epic 1 audit that confirms what already exists** before the method is locked.
Audit findings are expected to reshape the spec that precedes them. A spec is
provisional until its audit has run.

Readiness differs sharply across the nine, and the specs say so rather than
implying uniform readiness:

| Analysis | Readiness |
|---|---|
| Catchment (E1) | Method largely exists; likely a repoint rather than a rewrite |
| Q1 (E2) | Inputs strong; prior art exists in a publisher-owned mart to reconcile |
| Q2 (E3) | Buildable; carries the shared spine, so its definition work gates three analyses |
| Regional Role (E4) | Three of four lenses supported; commute-shed content deferred |
| Q4 (E5) | Two-market pilot supported; not nationally ready |
| Q3 (E6) | Harmonization is the real dependency; crosswalk prior art exists |
| Q6 (E7) | Half buildable now; the integration half is blocked on OD flow data |
| Corridor Opportunity Read (E8) | Not startable until Q2, Q3, Q4 produce output |
| Parcel Watch (E9) | Blocked; no parcel data exists and the engine is unscaffolded |

## The shared access spine

Most of the numbered questions run on the same shape:

> define centers → measure distance or access from them → measure what varies
> across that gradient

What changes between questions is the input used to build the centers and the
variable measured across the gradient.

**Q2 defines that method once.** It establishes the operational 15-minute-city
definition — what a center is, how reach is measured, what counts as access —
using job centers as the center input. Q3, Q4, Q6, and Catchment then re-run the
same method with different center inputs.

| Analysis | Center input | Measured across the gradient |
|---|---|---|
| Q2 | Job centers from LODES WAC/RAC | Housing cost and housing units |
| Q3 | Prior built footprint and existing centers | Growth: population, units, permits |
| Q4 | POI clusters by category | Daily-needs access |
| Q6 | Anchor cities / candidate downtowns | Whether the metro has one center or several |
| Catchment | A declared point | Whatever the point question asks |

This is deliberate and is itself a test: re-running one method against several
center constructions tells us whether the definition holds up generally or only
works for job centers. If Q4's POI-built centers produce an incoherent result,
that is a finding about the method, not only about Q4.

It is also the one deliberate exception to the promotion rule. Five consumers are
known before any is written, so the method is specified once in Q2 rather than
discovered on the third notebook.

**Consequence:** Q2 must be specced and built before Q3, Q4, and Q6.

## Build Rule

Follow the same folder shape Position uses, with Explanation naming:

```text
<analysis>/
├── README.md
├── EXPLANATION_<ANALYSIS>_SPEC.md
├── EXPLANATION_<ANALYSIS>_NOTEBOOK.py
├── queries/
└── figures/
    └── <scope-or-market>/
```

A separate headless runner (`<analysis>.py`) should be added only when the method
has stable expectations worth testing outside Marimo. Unlike Position, it is not
required to start every exploratory notebook here.

DuckDB is the data layer, SQL files define reusable surfaces, Marimo notebooks
load and explore them, and saved files at this layer are QA visuals rather than
substitute marts. Visuals here are for inspection, not publication.

## National posture

The governing rule is **one national method**, then run it for individual
markets. That is not the same as every analysis producing a national analysis.
Each analysis declares its posture in its spec:

| Posture | Meaning | Analyses |
|---|---|---|
| National analysis | The national run is itself a result worth reading | Q1 |
| National method, local application | Uniform method; the national run tests and calibrates it rather than being the finding | Q2, Q3, Q4, Q6 |
| Market or point scoped | No national run expected; reuse comes from consistent method and QA | Regional Role, Corridor Opportunity Read, Parcel Watch, Catchment |

An analysis whose posture does not call for national coverage tables,
distributions, or threshold sensitivity should say so in its spec and omit them
rather than build scaffolding it will not use.

## Analyses and build order

Order follows the E-sequence in [`docs/build_sequence.md`](../../docs/build_sequence.md),
which this plan drives.

| Order | Folder | Analysis | Why here |
|---|---|---|---|
| E1 | [`catchment/`](catchment/) | Catchment | Fastest path to a working notebook; the method already exists in Place Intelligence |
| E2 | [`q1_supply_or_demand/`](q1_supply_or_demand/) | Q1 Supply or Demand | Strongest national-ready data base; the family's one true national analysis |
| E3 | [`q2_job_proximity/`](q2_job_proximity/) | Q2 Job Proximity, Housing, and Affordability | **Carries the shared access spine**; gates E5, E6, E7 |
| E4 | [`regional_role/`](regional_role/) | Regional Role | Independent track; a workbench rather than a fixed analysis |
| E5 | [`q4_daily_needs/`](q4_daily_needs/) | Q4 Daily-Needs Access | Re-runs E3 with POI clusters as centers |
| E6 | [`q3_where_growth_lands/`](q3_where_growth_lands/) | Q3 Where Growth Lands | Re-runs E3 against the prior built footprint |
| E7 | [`q6_one_metro/`](q6_one_metro/) | Q6 One Metro? | Re-runs E3 with anchor cities as centers |
| E8 | [`corridor_opportunity_read/`](corridor_opportunity_read/) | Corridor Opportunity Read | Closing synthesis of E3, E5, E6 |
| E9 | [`parcel_watch/`](parcel_watch/) | Parcel Watch | Gated on the proposed parcel engine |

Q5 "Afford to Live Near Jobs" is **not** in this list. It merged into Q2: the two
shared inputs and outputs and differed only in dependent variable. Two
publication hooks remain available, but that is an issue-layer decision.

## Two structural decisions worth knowing

**Corridor Intelligence is not a dependency.** It is a paused prototype whose
Jacksonville and Richmond artifacts are method reference only. Corridors now
emerge from the Q2/Q3/Q4 access work, and Corridor Opportunity Read is a
synthesis of those rather than a consumer of an engine.

**Parcel Watch sits on a proposed parcel engine.** Assessor acquisition,
per-county adapters, scraped listings, and the normalized schema are engine
work. The analysis owns only the underuse heuristic, ranking, and
interpretation. The engine is proposed, not scaffolded — see Section 12 of the
plan.

## What Not To Do Here

- do not locally rewrite source taxonomy, geography identities, Phase 7 zones, or
  Time-Series results
- do not let each question grow its own 15-minute definition; adopt Q2's, and say
  so explicitly when you deliberately vary it
- do not infer travel, access, or commuting flows from straight-line proximity
- do not treat ZCTAs as postal delivery ZIPs
- do not allocate a non-additive measure without a declared method
- do not claim commuting integration from WAC/RAC without OD
- do not silently narrow the universe; report missing coverage and excluded
  markets
- do not polish validation visuals as if they were final issue charts
