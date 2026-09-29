# Tract Commute Sheds Contract

## Purpose

Materialize reusable, CBSA-scoped tract-to-tract work relationships in DuckDB
without creating a national tract-pair mart.

## Outputs

- `silver.lehd_lodes_od_tract_metro`: one aggregated flow per CBSA, declared
  relationship scope, endpoint tracts/statuses, source asset, year, job type,
  and segment.
- `silver.lehd_lodes_od_tract_metro_coverage`: one row per source asset used
  by a metro build, including source/reconciliation counts and unavailable
  providers.

## Relationship scope

- `workplace_side`: retains every flow with a workplace tract in the selected
  CBSA. It is bounded to the state(s) containing CBSA workplaces and captures
  all inbound workers for those jobs.
- `either_endpoint`: retains flows where either tract is in the CBSA. It is the
  complete residence-and-work relationship scope, but must examine `aux` files
  for every available workplace state to find residents who work elsewhere.

Neither scope measures travel time, routes, access, or causality. `main` and
`aux` are retained separately; 2023 Alaska and Michigan availability is
recorded as coverage, never zero.
