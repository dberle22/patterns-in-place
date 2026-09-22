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

**All nine analyses have a spec and build plan.** Regional Role's, Q4's, and
Q6's Epic 1 audits are complete; the remaining analysis audits retain their
current status in their own folders.

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
| Q2 (E3) | Buildable; supplies reviewed job-center physical-proximity evidence to Q3/Q6 and a comparison layer to Q4 |
| Regional Role (E4) | Two identity lenses supported; Geography must build adjacency and centroid interfaces for the other two; commute-shed content deferred |
| Q4 (E5) | POI-first Richmond/Jacksonville pilot supported; cluster method and reusable serving interface remain to be built |
| Q3 (E6) | Harmonization is the real dependency; crosswalk prior art exists |
| Q6 (E7) | Place hierarchy and anchor analysis can use Q2 physical proximity; OD/POI/Infrastructure add later relationship evidence |
| Corridor Opportunity Read (E8) | Not startable until Q2, Q3, Q4 produce output |
| Parcel Watch (E9) | Blocked; no parcel data exists and the engine is unscaffolded |

## Spatial methods and the Q4 POI workbench

Several questions use a related gradient shape:

> define centers → measure distance or access from them → measure what varies
> across that gradient

What changes between them is the input used to construct the origin or center
and the variable measured across the gradient.

**Q2 publishes job-center physical proximity.** Its current Haversine surface
is not travel time, access, or a 15-minute-city definition. Q3 and Catchment
may adopt transparent spatial-method conventions where their own specs support
them; Q4 does not rerun Q2's method.

| Analysis | Center input | Measured across the gradient |
|---|---|---|
| Q2 | Job centers from LODES WAC/RAC | Housing cost and housing units |
| Q3 | Prior built footprint and existing centers | Growth: population, units, permits |
| Catchment | A declared point | Whatever the point question asks |

**Q4 has a distinct POI-first shape:** governed POI points → spatial amenity
hubs → composition-based typologies → tract context and employment comparison.
It is the family's introductory 15-minute-city workbench, not a resident-access
claim. A later network/barrier method may connect these surfaces, but no current
analysis should imply that it already exists.

Q6 is adjacent to this work: it uses
Census Places as anchor candidates and Q2's physical-proximity/job-center
evidence to classify whether one or several anchors are supported.

**Consequence:** Q4 can build its POI workbench independently of Q2. Q6 requires
Q2's published job-center/proximity surfaces, but does not call them access.

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
| National method, local application | Uniform method; the national run tests and calibrates it rather than being the finding | Q2, Q3, Q6 |
| Two-market pilot | A declared method is tested on governed pilot markets before any broader scale-out | Q4 |
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
| E3 | [`q2_job_proximity/`](q2_job_proximity/) | Q2 Job Proximity, Housing, and Affordability | Publishes reviewed job-center physical proximity for its own outcomes and Q6/Q4 comparison |
| E4 | [`regional_role/`](regional_role/) | Regional Role | Independent track; a workbench rather than a fixed analysis |
| E5 | [`q4_daily_needs/`](q4_daily_needs/) | Q4 Livability Amenities and POI Clusters | POI-first workbench; produces amenity hubs, typologies, and tract context |
| E6 | [`q3_where_growth_lands/`](q3_where_growth_lands/) | Q3 Where Growth Lands | Builds its growth classification and may compare it with E3 physical proximity |
| E7 | [`q6_one_metro/`](q6_one_metro/) | Q6 One Metro? | Uses E3 job-center/proximity evidence to evaluate Census Place anchors |
| E8 | [`corridor_opportunity_read/`](corridor_opportunity_read/) | Corridor Opportunity Read | Closing synthesis of E3, E5, E6 |
| E9 | [`parcel_watch/`](parcel_watch/) | Parcel Watch | Gated on the proposed parcel engine |

Q5 "Afford to Live Near Jobs" is **not** in this list. It merged into Q2: the two
shared inputs and outputs and differed only in dependent variable. Two
publication hooks remain available, but that is an issue-layer decision.

## Two structural decisions worth knowing

**Corridor Intelligence is not a dependency.** It is a paused prototype whose
Jacksonville and Richmond artifacts are method reference only. Corridor
Opportunity Read can synthesize Q2/Q3 results with Q4's reviewed amenity hubs,
rather than treating any of them as an access result or a consumer of an engine.

**Parcel Watch sits on a proposed parcel engine.** Assessor acquisition,
per-county adapters, scraped listings, and the normalized schema are engine
work. The analysis owns only the underuse heuristic, ranking, and
interpretation. The engine is proposed, not scaffolded — see Section 12 of the
plan.

## What Not To Do Here

- do not locally rewrite source taxonomy, geography identities, Phase 7 zones, or
  Time-Series results
- do not call physical proximity, POI concentration, or tract context a
  15-minute-access result without a declared network and barrier method
- do not infer travel, access, or commuting flows from straight-line proximity
- do not treat ZCTAs as postal delivery ZIPs
- do not allocate a non-additive measure without a declared method
- do not claim commuting integration from WAC/RAC without OD
- do not silently narrow the universe; report missing coverage and excluded
  markets
- do not polish validation visuals as if they were final issue charts
