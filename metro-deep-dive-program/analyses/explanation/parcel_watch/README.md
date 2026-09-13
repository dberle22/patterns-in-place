# Parcel Watch

**Build order:** E9 — gated on the proposed parcel engine, **not** on a corridor

**Status:** Spec and build plan drafted; blocked on a parcel engine that does not
exist.

**Question:** Which parcels in a selected county appear underused or otherwise
worth monitoring, and how do they relate to an area of interest?

Purpose:

- define an eligible parcel universe within a county
- derive transparent underuse indicators and rank within county
- expose area-of-interest filters without letting them define the comparison
  universe

**Primary analytical unit:** standardized parcel, ranked within county first and
optionally filtered or re-ranked within an area of interest.

**National posture:** county scoped.

## Split into an engine and an analysis

The bulk of this work — acquiring county assessor records, scraping listings,
normalizing them into a standard schema — is ingestion and normalization, not
analysis. It is a repeated per-county pipeline with a contract, which is
engine-shaped.

| | Owns |
|---|---|
| **Parcel engine** (proposed) | Assessor acquisition and per-county adapters, the scraped listings watch list, the normalized schema (pricing, land use, sale history, ownership, geometry), provenance and freshness |
| **This analysis** | The underuse heuristic, ranking, and interpretation |

The engine is **proposed, not scaffolded.** See Section 12 of the plan for what
it would need. Nothing under `engines/` has been created for it.

## Source strategy

Free county or state assessor records are the default. A paid source would
require its own engine to build, so it is not the starting assumption — but if
Regrid or a similar national service turns out to be low cost, it is worth a
look. That stays a short exploratory task during engine construction, not a
prerequisite.

**Start with a manual file and a manual universe.** Do not wait for a general
acquisition pipeline. Try assessor data first; where unavailable, a scraped list
from Zillow, brokers, or foreclosure listings is an acceptable starting universe.

Free sources mean a per-county adapter permanently — there is no vendor
normalizing them for us. That recurring cost is the accepted price of avoiding a
licensed source, and it is exactly the kind of cost an engine exists to contain.

## The heuristic

A candidate-for-purchase screen: is it beneath a certain cost, has it not sold in
X years, does it have a qualifying land use, is it within X distance of things we
care about. Keep component measures visible instead of hiding logic behind one
score.

## Relationship to Catchment

Catchment is a separate analytical process. It does not build on Parcel Watch,
but the two are used closely together — Catchment supplies the "what is within X
of this parcel" read.

## Open decisions for the spec

- eligible land uses
- underutilization definition and its thresholds
- required versus optional fields; missing-value behavior
- score weights or ranking rule
- treatment of parcel assemblages
- refresh cadence
- whether scraped listings affect rank or only add context

See [EXPLANATION_PARCEL_WATCH_SPEC.md](EXPLANATION_PARCEL_WATCH_SPEC.md) for the
analysis boundary and inputs, and
[EXPLANATION_PARCEL_WATCH_BUILD_PLAN.md](EXPLANATION_PARCEL_WATCH_BUILD_PLAN.md) for
the epic sequence. Both are provisional: Epic 1 is an audit of what already
exists, and its findings are expected to reshape them.

Section 5.8 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
holds the family-level framing.
