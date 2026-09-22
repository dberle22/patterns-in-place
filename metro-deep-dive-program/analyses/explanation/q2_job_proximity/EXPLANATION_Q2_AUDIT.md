# Explanation Q2 — Epic 1 Audit

**Status:** Complete

**Audit date:** 2026-09-13

**Warehouse reviewed:** `foundations/etl/data/duckdb/patterns_in_place.duckdb`

## Decision summary

Q2 can begin with a national 2023 workplace-job concentration study, followed
by Richmond-first local exploration using tract-centroid straight-line distance
and current ACS housing and household-income measures. It cannot honestly claim
a 15-minute travel-time result, a time series of job centers, worker origins,
or a worker-to-household affordability match. Those are later method decisions,
not gaps to conceal in V0.

V0 should use a national concentration notebook followed by two Richmond-first
notebooks. The national surface identifies tract concentration patterns without
ranking markets or selecting a rule. The market surface maps raw tract jobs and
compares local center/district candidates without selecting one automatically.
The evidence surface consumes an explicitly reviewed V0 rule to produce the
center inventory/map, distance curves, descriptive model results, and
separately labeled affordability context. Network routing and a final shared
15-minute definition remain out of scope until the first market result makes a
case for them.

## What exists in the live warehouse

### LODES workplace and residence evidence

`gold.economics_lodes_wide`, `silver.lehd_lodes_wac`, and
`silver.lehd_lodes_rac` are tract-first, 2023-only surfaces. The Gold table
retains workplace jobs, resident workers, workplace earnings bands, and the
jobs-to-workers measures at tract, county, CBSA, state, and division grain.
One year is sufficient to construct a current employment-location surface; it
is not sufficient to describe center formation, decline, or persistence.

For Richmond CBSA (`40060`), WAC has 330 populated tract rows in 2023. Job
counts range from 23 to 24,049; 60 tracts meet the Industry explorer's current
2,500-job display floor. WAC's known national coverage limitation remains
relevant to a later national run: 2023 workplace coverage excludes some Alaska
and Michigan geography, while RAC is broader.

**V0 decision:** use WAC to identify workplace concentrations. RAC is context
only; it does not supply origin-destination flows and must not be used to infer
commutes.

### Existing D3 job-center work

The Industry explorer's D3 page is useful prior art, but not a reusable center
definition. It reads the latest WAC tract surface, applies an adjustable
default `D3_DEFAULT_TRACT_JOBS_FLOOR = 2500`, and ranks qualifying tracts by
total jobs, jobs-to-workers, or a selected-sector measure. The page does not
merge adjacent tracts, identify contiguous clusters, justify the default floor,
or define a reach threshold. The floor exists to keep small tracts from
dominating a display ranking and its origin is not documented.

**V0 decision:** retain D3's 2,500-job floor only as one named sensitivity
candidate. Do not promote its tract ranking or its default value as the Q2
center rule.

### Geometry and distance

`geo.tracts_all_us` contains tract identifiers, land area, `geom_wkb`, and a
DuckDB `GEOMETRY` column. The Industry explorer loads DuckDB Spatial before
calculating geometry centroids. The table contract does not state a distance
projection or CRS policy, so V0 must not use raw planar coordinate distance.

**V0 decision:** decode the governed WKB, calculate tract centroids, and use a
documented Haversine/great-circle calculation in miles. This is a physical
proximity measure, not a route, time, or barrier-aware access measure.

### Housing, income, and burden

`staging.acs_housing_tract` and `staging.acs_income_tract` provide 2012–2024
tract rows. Their needed V0 fields are median home value, median gross rent,
housing units, rent-burden counts, and median household income. In Richmond,
the 2024 housing table has 332 rows: 321 values for median home value, 307 for
median rent, 332 for housing units and rent burden, and 327 joined values for
median household income. Missing values must remain visible in the notebook's
coverage table and models.

Q1 has already materialized the current 2024 tract housing surface in
`mart_explanation_q1.supply_demand_base`, including annualized median rent,
median household income, rent-to-income, median home value, housing units, and
rent burden. It is the appropriate V0 housing input; Q2 should not recreate
those transformations. It does not contain a job-center construction or
distance field.

### Wage context and affordability limits

`silver.bls_oews` has 2025 CBSA and state occupational rows; Richmond has 621
CBSA rows. It has no tract geography, so it is metro-level occupational context
only. LODES workplace earnings are three worker-count bands, not a tract wage
estimate and not a household-income measure.

**V0 decision:** show local housing-cost-to-household-income and nearby-center
earnings-band composition in separate panels. Do not calculate an affordability
"mismatch" or call it an affordability conclusion until a household/worker
unit, earnings-band interpretation, and comparison standard are explicitly
chosen.

### Price series

There is no managed tract-level home-price or rent series for V0. A tract FHFA
HPI table is staged (1975–2025) but is not a managed Gold/Silver price surface
and is an appreciation index, not a housing-price level. It is out of scope for
the initial gradient. Q2's tract cost outcomes are ACS levels, not market-price
trends.

## V0 readiness and constraints

| Need | Audit finding | V0 disposition |
|---|---|---|
| Job locations | 2023 tract WAC is populated for Richmond | Use as one current snapshot. |
| Center method | D3 supplies a display threshold only | Define and test Q2 candidates; do not inherit D3. |
| Distance | Governed geometry exists; projection contract is absent | Use centroid-to-centroid Haversine miles. |
| Housing outcomes | Current tract ACS/Q1 fields are populated but not complete | Publish coverage and use complete-case models only. |
| Household affordability | Q1 supplies rent-to-income and burden | Show as a separate resident-household result. |
| Job earnings | LODES bands plus CBSA-only OEWS | Context only; no household-worker bridge. |
| 15-minute access | No routing or travel-time input audited | Explicitly deferred. |
| National calibration | WAC has one vintage and known coverage exceptions | Explicitly deferred from V0. |

## Required spec and build-plan changes

1. Reframe V0 as straight-line job proximity, not a 15-minute definition.
2. Replace the former broad minimum-output list with a national concentration
   surface, a Richmond-first local exploration surface, and a later evidence
   surface; defer national proximity calibration and network routing.
3. Reuse Q1's 2024 tract housing surface rather than rebuilding ACS measures.
4. Treat the D3 2,500-job floor as a sensitivity case, not a center rule.
5. Keep affordability context separate from workplace earnings until a later
   standard supports a defensible comparison.
