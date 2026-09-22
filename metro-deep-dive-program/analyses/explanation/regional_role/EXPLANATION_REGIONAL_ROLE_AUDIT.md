# Regional Role — Epic 1 Audit

**Completed:** 2026-09-20

**Scope:** Read-only audit of the current warehouse, Geography, Benchmarking,
Position, Infrastructure, and documented source contracts. No Regional Role
notebook, query, or mart was built in this epic.

## Decision summary

| Requirement | Finding | V1 disposition |
|---|---|---|
| Census division lens | `gold.dim_geo` carries CBSA Census division identity. | Buildable from governed identity. |
| Primary-state lens | `gold.dim_geo.state_fips` uses the first state named in the official CBSA label for multi-state CBSAs. | Buildable from governed identity. |
| Benchmarking primary-state set | Current Benchmarking SQL derives `state_primary` from the state with the most member counties. | Do not reuse for Regional Role until it adopts Geography's first-named-state rule. |
| Adjacent-state lens | No reusable state-adjacency surface exists. Existing geometry is display-only and cannot establish adjacency. | Build in Geography Epic 9 using land-only analytical state geometry. |
| 250-mile CBSA lens | No declared CBSA centroid or distance surface exists. | Build in Geography Epic 9 from approved analytical CBSA geometry. |
| Megaregion lens | No governed source or membership layer exists. | Defer to V2. |
| IRS migration summary | `gold.migration_wide` and `silver.irs_migration_summary` provide county, CBSA, and state inflow, outflow, and net totals for 2012–2022. | Use in V1. |
| IRS partner-metro exchange | `silver.irs_migration_flows` is county OD data for 2012–2022. County endpoints can join to CBSA membership and aggregate to CBSA pairs; within-CBSA moves remain observable. | Use in V1 as an explicit rolled query surface. |
| LODES WAC/RAC | 2023 WAC/RAC surfaces exist at tract, county, CBSA, state, and division grain. | Use in V1 for descriptive jobs-versus-workers and industry composition. |
| LODES OD | National available-state 2023 county-pair OD is materialized with provider coverage metadata; Alaska and Michigan are unavailable. | V2 can build a declared commute-shed or functional-integration method without treating missing coverage as zero. |
| Industry role | `gold.economics_industry_wide` exposes broad-sector employment, LQs, concentration, wages, establishments, and GDP context. | Use in V1. |
| National metro baseline | `mart_benchmarking` already has national metropolitan-CBSA comparison membership and metric surfaces. | Include above regional lenses in V1. |
| Infrastructure context | Market-scoped Infrastructure serving candidates and a read-only handoff exist for Richmond/Jacksonville. They await an approved analytical CBSA boundary, not national scaling. | Include a contextual V1 map after Geography Epic 9 supplies that boundary. |
| Position reuse | Profile provides governed KPIs and identity, Peers provides similarity peers, and Trajectory provides stored trend context. | Consume, do not rebuild. |

## Evidence details

- `silver.xwalk_cbsa_county` and `silver.xwalk_county_state` are current 2023
  relationships. `gold.dim_geo` is the current serving dimension.
- The primary-state derivation in `foundations/etl/gold/gold_dim_geo.sql`
  extracts the first state abbreviation after the comma in the CBSA name and
  resolves it to its governed state fields. It does not use county count.
- `silver.irs_migration_flows` has county and state origin-destination rows.
  County flow keys are suitable for joining both endpoints to
  `silver.xwalk_cbsa_county` before aggregating to a CBSA pair. Its IRS
  measures are returns, exemptions/people, and AGI, with suppressed/missing
  values retained as null.
- The LODES source contract confirms that WAC/RAC are the current managed
  scope and OD is deferred. WAC/RAC must never be labelled as flows.
- The Geography contract permits existing cartographic layers for display, but
  prohibits their use for distance, area, or relationship construction. The
  new regional-lens interfaces therefore require approved analytical state and
  CBSA geometry.

## Audit-driven specification changes

- Use four V1 lenses: Census division, primary state, primary state plus
  land-adjacent states, and declared CBSA-centroid radius.
- Treat megaregions, functional labor sheds, LODES OD, national infrastructure
  comparison, travel-time lenses, and automated role labels as V2. When OD
  opens, prefer a scoped, on-demand CBSA helper over a national OD mart.
- Add a national metro baseline above the division and active regional lenses.
- Use CBSA-level IRS totals for broad context and roll detailed IRS county flows
  to CBSA-pair exchange for partner-metro analysis.
- Add Geography Epic 9 as the V1 prerequisite for state adjacency, CBSA
  centroids, regional-lens membership, and analytical CBSA geometry needed by
  the Infrastructure handoff.

## References

- [Regional Role Spec](EXPLANATION_REGIONAL_ROLE_SPEC.md)
- [Regional Role Build Plan](EXPLANATION_REGIONAL_ROLE_BUILD_PLAN.md)
- [Geography Engine Build Plan](../../../engines/geography/GEOGRAPHY_ENGINE_BUILD_PLAN.md)
