# Explanation Parcel Watch Spec

**Status:** Provisional — blocked on a parcel engine that does not exist

**Build order:** E9 — gated on the proposed parcel engine, **not** on a corridor

**Primary surface:** `EXPLANATION_PARCEL_WATCH_NOTEBOOK.py` (not yet written)

**First county:** Duval County, FL (Jacksonville) — where prior art exists

**Initial method:** `parcel_watch_v1`

**Dependencies:** A proposed parcel engine (Section 12 of the family plan).
Nothing under `engines/` has been created for it.

## How to read this spec

**This spec is deliberately provisional.** Epic 1 is an audit that confirms what
already exists, and its findings are expected to reshape everything below it.
Where the audit contradicts this spec, the audit wins.

This analysis is additionally **blocked**: its data source does not exist in the
warehouse yet. Epic 1 is therefore partly a scoping exercise for the engine.

## Split into an engine and an analysis

The bulk of this work — acquiring county assessor records, scraping listings,
normalizing them into a standard schema — is ingestion and normalization, not
analysis. It is a repeated per-county pipeline with a contract, which is
engine-shaped.

| | Owns |
|---|---|
| **Parcel engine** (proposed) | Assessor acquisition and per-county adapters, the scraped listings watch list, the normalized schema (pricing, land use, sale history, ownership, geometry), provenance and freshness |
| **This analysis** | The underuse heuristic, ranking, and interpretation |

The engine should not encode a view about which parcels are interesting.

## Goal

Identify which parcels in a selected county appear underused or otherwise worth
monitoring, and how they relate to an area of interest.

## National posture: county scoped

## Source strategy

**Free county or state assessor records are the default.** A paid source would
require its own engine to build, so it is not the starting assumption — but if
Regrid or a similar national service turns out to be low cost, it is worth a
look. Keep that a short, timeboxed exploratory task during engine construction,
not a prerequisite.

Free sources mean **a per-county adapter permanently** — there is no vendor
normalizing them for us. That recurring cost is the accepted price of avoiding a
licensed source, and it is exactly the kind of cost an engine exists to contain.

**Start with a manual file and a manual universe.** Do not wait for a general
acquisition pipeline. Try assessor data first; where unavailable, a scraped list
from Zillow, brokers, or foreclosure listings is an acceptable starting
universe.

## Preliminary read of what exists

**Provisional. Epic 1 must confirm or correct all of this.**

| Observation | Why it matters | What Epic 1 must settle |
|---|---|---|
| **No parcel tables appear to exist anywhere in the warehouse** | This analysis has no data source today | Confirm, and record it as the gating dependency |
| A Jacksonville parcel standardization and screening path appears to exist in legacy ROF work | There is prior art for one county | Audit what it does, what schema it produced, and what survives |
| Zillow ZHVI/ZORI exist but are aggregate market series | They are not parcel records and cannot substitute | Confirm they stay out of the base ranking |
| Catchment (E1) will produce a point-centered contribution table | Supplies the "what is within X of this parcel" read | Record what Parcel Watch consumes |

## Inputs

All supplied by the parcel engine once it exists.

| Input | Role |
|---|---|
| Free county or state assessor records | System of record |
| Parcel polygons and durable identifiers | Geometry and joins |
| Land use, land and improvement value, building area, parcel area, ownership, last sale, situs address | Underuse indicators |
| Geography assignment | Area-of-interest filters |
| Legacy Jacksonville ROF standardization logic | Prior art |
| Scraped listing evidence | Dated enrichment layer only |
| Catchment contribution table | Point context |

## V0 method

Take one county's normalized parcels, define an eligible universe, derive
transparent underuse indicators, and rank within county.

The heuristic is a candidate-for-purchase screen: is it beneath a certain cost,
has it not sold in X years, does it have a qualifying land use, is it within X
distance of things we care about. **Keep component measures visible instead of
hiding logic behind one score.**

Countywide-first ranking is intentional: a countywide percentile makes the
result reusable and keeps an area filter from defining the comparison universe
after the fact. The area filter is any selected area, including one identified
by Q2/Q4 access work — not a Corridor Intelligence candidate.

## Minimum outputs

Source and join QA, county parcel inventory, component ranking table, county
map, selected-area filter, candidate detail table, and data-freshness and
provenance fields.

## Relationship to Catchment

Catchment is a separate analytical process. It does not build on Parcel Watch,
but the two are used closely together — Catchment supplies the "what is within X
of this parcel" read.

## Guardrails

- do not treat Zillow aggregate series as parcel records
- do not require scraped listings to reproduce the base ranking
- do not hide the screen behind one composite score
- do not let an area filter define the comparison universe
- do not commit to a licensed source before a free path is tried and costed

## Open decisions

- eligible land uses
- underutilization definition and its thresholds
- required versus optional fields; missing-value behavior
- score weights or ranking rule
- treatment of parcel assemblages
- refresh cadence
- whether scraped listings affect rank or only add context

## References

- Section 5.8 of [EXPLANATION_ANALYSES_PLAN.md](../EXPLANATION_ANALYSES_PLAN.md)
- Section 12 of the same plan for the proposed engine
- [EXPLANATION_PARCEL_WATCH_BUILD_PLAN.md](EXPLANATION_PARCEL_WATCH_BUILD_PLAN.md)
