# Data Dictionary: silver.irs_migration_summary

## Overview
- **Table**: `silver.irs_migration_summary`
- **Purpose**: Geography-level IRS migration summary table for counties, CBSAs, and states.
- **Row count**: 42,575
- **Time coverage**: 2012-2022

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**: `county`, `cbsa`, and `state`
- **Key QA**: live duplicate check on `geo_level + geo_id + year` returned zero duplicates.

## Columns

| Column | Type | Null % | Definition |
|---|---|---:|---|
| `geo_level` | `VARCHAR` | 0.0000 | Geographic level for the summary row (`county`, `cbsa`, or `state`). |
| `geo_id` | `VARCHAR` | 0.0000 | Geographic identifier for the summary row. County rows use county FIPS, CBSA rows use CBSA code, and state rows use state FIPS. |
| `geo_name` | `VARCHAR` | 0.0000 | Geographic name for the summary row. |
| `state_fips` | `VARCHAR` | 23.7346 | State FIPS code for county and state rows. Null for CBSA rows because metros can span multiple states. |
| `state_abbr` | `VARCHAR` | 23.7346 | USPS state abbreviation for county and state rows. Null for CBSA rows. |
| `year` | `INTEGER` | 0.0000 | Destination tax year and canonical analysis year for the summary row. |
| `inflow_returns` | `DOUBLE` | 0.0000 | Sum of IRS returns moving into the geography during the year. CBSA rows exclude within-CBSA county moves. |
| `outflow_returns` | `DOUBLE` | 0.0000 | Sum of IRS returns moving out of the geography during the year. CBSA rows exclude within-CBSA county moves. |
| `net_returns` | `DOUBLE` | 0.0000 | Net IRS migration returns calculated as `inflow_returns - outflow_returns`. |
| `inflow_exemptions` | `DOUBLE` | 0.0000 | Sum of exemptions or people associated with incoming IRS migration returns. |
| `outflow_exemptions` | `DOUBLE` | 0.0000 | Sum of exemptions or people associated with outgoing IRS migration returns. |
| `net_exemptions` | `DOUBLE` | 0.0000 | Net exemptions or people calculated as `inflow_exemptions - outflow_exemptions`. |
| `inflow_agi_thousands` | `DOUBLE` | 0.0188 | Sum of incoming adjusted gross income, in thousands of dollars. |
| `outflow_agi_thousands` | `DOUBLE` | 0.0117 | Sum of outgoing adjusted gross income, in thousands of dollars. |
| `net_agi_thousands` | `DOUBLE` | 0.0305 | Net adjusted gross income calculated as `inflow_agi_thousands - outflow_agi_thousands`. |
| `inflow_agi` | `DOUBLE` | 0.0188 | Sum of incoming adjusted gross income, in dollars. |
| `outflow_agi` | `DOUBLE` | 0.0117 | Sum of outgoing adjusted gross income, in dollars. |
| `net_agi` | `DOUBLE` | 0.0305 | Net adjusted gross income calculated as `inflow_agi - outflow_agi`. |

## Data Quality Notes
- CBSA rows intentionally leave `state_fips` and `state_abbr` null because a metro can span multiple states.
- Missing-sided summary rows are now zero-filled before netting, so `net_returns` and `net_exemptions` no longer go null just because one side had no observed rows.
- Small remaining null rates on AGI summary columns trace to suppressed or missing income values in the staged IRS source.

## Lineage
1. `foundations/etl/staging/get_irs_migration.R` creates the county and state inflow staging tables used as the Silver summary source.
2. `foundations/etl/silver/irs_migration_silver.R` aggregates county inflows and outflows, rebases county flows to CBSA while excluding within-CBSA moves, preserves state interstate totals, and writes `silver.irs_migration_summary`.

## Known Gaps / To-Dos
- County and CBSA summaries remain domestic-only and do not introduce a separate foreign-migration bucket.
- State summary rows are interstate-only because they come from the staged state inflow slice rather than county-to-county rebasing.

## How To Extend (Next Table)
1. Confirm live row counts and key uniqueness in DuckDB.
2. Profile all metric columns after the transform stabilizes.
3. Record lineage from staging family through Silver script and any crosswalk rebasing steps.
4. Update the `.yml` contract first, then sync the `.md` companion.
