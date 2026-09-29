# Notes

## Audit Snapshot

Originally reviewed on `2026-09-02`; current-state notes refreshed on
`2026-09-08`.

## Current Framework Surfaces

Promoted into DuckDB under `mart_intelligence`:

- `intelligence_character`
- `intelligence_livability`
- `intelligence_opportunity`
- `intelligence_cross_frame`
- `intelligence_zones`
- `intelligence_zones_zcta`

Observed current row counts:

- `396` rows in each CBSA-grain table
- one row per `cbsa_code` in the promoted frame marts

## What Looks Stable

- frame-level labels and percentile ranks
- promoted top-10 peer fields
- cross-frame overlap and divergence fields
- tract and ZCTA zone surfaces

## What Still Needs Cleanup

- `intelligence_cross_frame` mixes flattened aliases with many prefixed source
  fields, which makes it harder to treat as a clean notebook surface
- the Phase 7 consumer contract still needs to point to the current model build
  and vintage evidence; row-level fields can wait until multiple runs require
  them
- no locked fingerprint mart yet; early Act 1 fingerprint work still needs a
  curated join across frame tables

## Existing Research Tool Consumers

The legacy Research Tool usage split across:

- Phase 2 to 5 promoted static frame outputs
- Phase 6 trajectory files
- Phase 7 zone outputs

Current consumers should distinguish:

- `queryable now in DuckDB`
- `legacy comparison evidence only`

Trajectory is no longer file-backed for current consumers. The Time-Series
engine owns the canonical `mart_intelligence.intelligence_trajectory_*`
tables, while the old Phase 6 files remain available only for comparison.

## Clarifications From This Review

- The current promoted peer set is top `10` only.
- A cross-frame divergence surface is already promoted via
  `frame_percentile_gap`, `top_frame`, `bottom_frame`, `overlap_profile`, and
  related fields in `intelligence_cross_frame`.
- The broader Phase 6 candidate shortlist also exists, but only as file output
  today, not as a `mart_intelligence` table.

## Promotion Candidates

- flatten and normalize the cross-frame column surface
- keep trajectory governance in the separate Time-Series engine contract
- promote a locked fingerprint asset once `Profile` stabilizes its selected KPI
  set
