# Explanation Parcel Watch Build Plan

**Status:** Blocked — no parcel data source exists yet

This analysis cannot start until a parcel engine provides normalized data. Epic 1
is therefore partly a scoping exercise for that engine.

## How this plan works

**Epic 1 is an audit, and it comes first.** It audits prior art and scopes the
engine dependency. Epics 2–4 are written from expectation and should be
rewritten once the audit reports.

## Epic 1 — Audit Prior Art and Scope the Engine Dependency

- [ ] Confirm plainly that no parcel tables exist in the governed warehouse.
- [ ] Audit the legacy Jacksonville ROF parcel standardization work: what it
  acquired, what schema it produced, what screening logic it used, and what
  still runs.
- [ ] Determine what the Duval County assessor actually publishes: fields,
  format, refresh cadence, and licensing.
- [ ] Draft the normalized parcel schema from that evidence — the fields the
  engine must produce for this analysis to work.
- [ ] Separate what the engine owns from what this analysis owns.
- [ ] **Timeboxed side task:** price Regrid or a comparable national service —
  pricing, licensing, refresh cadence, field coverage against the draft schema,
  and redistribution terms. Report it as a comparison, not a recommendation to
  switch.
- [ ] Determine what a second county would require, to test whether the schema
  generalizes.
- [ ] Recommend whether the engine should be scaffolded, and with what scope.

**Done when:** the engine's first build has a concrete scope grounded in one
real county's data, and the free-versus-paid question has a costed answer. The
spec is rewritten against those findings.

Record the audit in `EXPLANATION_PARCEL_WATCH_AUDIT.md`.

## Epic 2 — Stand Up One County

*Provisional. Blocked on the engine. Rewrite after Epic 1.*

- [ ] Acquire and normalize Duval County parcels through the engine.
- [ ] Produce source and join QA.
- [ ] Produce the county parcel inventory.
- [ ] Confirm provenance and freshness fields are populated.

**Done when:** one county's parcels are queryable with visible provenance.

## Epic 3 — Build the Screen

*Provisional. Rewrite after Epic 1.*

- [ ] Define the eligible parcel universe.
- [ ] Define transparent underuse indicators as separate visible components.
- [ ] Build the countywide ranking.
- [ ] Add the area-of-interest filter without letting it define the universe.
- [ ] Add the candidate detail table.

**Done when:** the screen is reproducible and every component is inspectable.

## Epic 4 — Review and Generalize

*Provisional. Rewrite after Epic 1.*

- [ ] Test against a second county to see whether the schema holds.
- [ ] Decide whether scraped listings affect rank or only add context.
- [ ] Connect Catchment for point-level context on shortlisted parcels.
- [ ] Record what the engine's adapter contract should require.

**Done when:** the method survives a second county and the adapter contract is
written from experience.

## What not to do

- do not build the acquisition pipeline inside this analysis
- do not treat aggregate market series as parcel records
- do not hide the screen behind one composite score
- do not commit to a licensed source before costing the free path
