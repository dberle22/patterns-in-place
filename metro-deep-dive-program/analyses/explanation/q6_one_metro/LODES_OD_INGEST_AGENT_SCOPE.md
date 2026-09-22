# LODES OD Ingestion — Agent Scope

## Objective

Add the smallest validated shared LODES OD surface that lets Q6 describe
Place-to-Place work relationships inside and beyond a selected CBSA. This is
Foundations data-layer work, not a Q6 notebook implementation.

## Starting facts

- The managed LODES path includes 2023 county-pair OD with `JT00` and `JT02`
  measures; Alaska and Michigan are explicit provider gaps.
- Census publishes OD as state-based, block-to-block files split into `main`
  (in-state home/work pairs) and `aux` (workplace state with an out-of-state
  home).
- A flow is keyed by workplace block (`w_geocode`) and home block (`h_geocode`).
  Q6 needs that direction preserved.
- Do not persist a national block-to-block table by default.

## Required work

1. Read the current LODES source contract and WAC/RAC staging/silver path.
2. Profile one state’s 2023 `JT02` / `S000` OD `main` and `aux` files: schema,
   rows, compressed/uncompressed size, source coverage, block-to-Place match
   rate, and duplicate behavior.
3. Estimate the national Place-to-Place row count and storage footprint after
   aggregating each source state/part. Record whether this is a safe durable
   Silver surface or whether a parameterized on-demand helper is required.
4. Propose the layer contract before coding: staging grain, Silver grain,
   keys, measures, direction fields, provenance, null/suppression treatment,
   and coverage flags. The preferred target is a home-Place × work-Place × year
   flow surface for 2023 `JT02` / `S000`. Explain whether a county companion is
   low-cost enough to retain for other consumers.
5. Implement only after the contract is reviewed. Process state files
   sequentially; validate that `main` plus `aux` have no accidental overlap,
   retain cross-state destinations, and reconcile Place totals to the source
   within declared coverage limits.
6. Update the source documentation, table contracts, and Q6/Regional Role
   dependency notes. Do not build a Q6 score, notebook, or classification.

## Acceptance criteria

- A selected CBSA can inspect flows between its Places and from those Places to
  external destinations, with all known destinations retained in the relevant
  denominator.
- The data layer distinguishes incomplete provider coverage from a zero flow.
- Source state, OD part, year, job type, segment, and transformation version
  are traceable.
- No flow alone is treated as an anchor-city classification.

## Explicit non-goals

- No block-level persisted mart unless the profiling decision records why it is
  essential.
- No historical panel, travel-time/access model, worker demographic analysis,
  or national Q6 ranking.
- No parallel DuckDB writes.
