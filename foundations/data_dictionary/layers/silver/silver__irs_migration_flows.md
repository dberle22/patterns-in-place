# Data Dictionary: silver.irs_migration_flows

## Overview
- **Table**: `silver.irs_migration_flows`
- **Purpose**: Standardized IRS migration origin-destination flow table for county and state geographies.
- **Row count**: 654,225
- **Time coverage**: 2012-2022

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + origin_geo_id + dest_geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `origin_geo_id`, `dest_geo_id`, `year`)
- **Observed geo coverage**: `county` and `state`
- **Key QA**: live duplicate check on `geo_level + flow_id + year` returned zero duplicates after Silver deduping.

## Columns

| Column | Type | Null % | Definition |
|---|---|---:|---|
| `geo_level` | `VARCHAR` | 0.0000 | Geographic level shared by the origin and destination IDs in the flow row (`county` or `state`). |
| `flow_id` | `VARCHAR` | 0.0000 | Derived flow identifier composed from destination year, origin geography ID, and destination geography ID. |
| `year` | `INTEGER` | 0.0000 | Destination tax year and canonical analysis year for the migration flow. |
| `origin_year` | `INTEGER` | 0.0000 | Prior-year residence tax year carried from the IRS source file. |
| `dest_year` | `INTEGER` | 0.0000 | Destination-year label from the IRS source file. |
| `origin_geo_id` | `VARCHAR` | 0.0000 | Origin geography identifier for the flow row. County rows use 5-digit county FIPS; state rows use 2-digit state FIPS. |
| `origin_geo_name` | `VARCHAR` | 0.0000 | Name of the origin geography for the flow row. |
| `origin_state_fips` | `VARCHAR` | 0.0000 | 2-digit state FIPS code for the flow origin. |
| `origin_state_abbr` | `VARCHAR` | 0.0000 | USPS state abbreviation for the flow origin. |
| `origin_county_fips` | `VARCHAR` | 4.2875 | 3-digit county FIPS code for county-level origin rows; null for state-level rows. |
| `dest_geo_id` | `VARCHAR` | 0.0000 | Destination geography identifier for the flow row. County rows use 5-digit county FIPS; state rows use 2-digit state FIPS. |
| `dest_geo_name` | `VARCHAR` | 0.0000 | Name of the destination geography for the flow row. |
| `dest_state_fips` | `VARCHAR` | 0.0000 | 2-digit state FIPS code for the flow destination. |
| `dest_state_abbr` | `VARCHAR` | 0.0000 | USPS state abbreviation for the flow destination. |
| `dest_county_fips` | `VARCHAR` | 4.2875 | 3-digit county FIPS code for county-level destination rows; null for state-level rows. |
| `n_returns` | `DOUBLE` | 0.0130 | Number of tax returns moving from the origin geography to the destination geography. |
| `n_exemptions` | `DOUBLE` | 0.0130 | Number of claimed exemptions or people associated with the migrating tax returns. |
| `agi_thousands` | `DOUBLE` | 0.1029 | Adjusted gross income associated with the flow, reported in thousands of dollars. |
| `agi` | `DOUBLE` | 0.1029 | Adjusted gross income associated with the flow, scaled into dollars from the IRS thousand-dollar source field. |

## Data Quality Notes
- Exact duplicate staging flow rows were removed during Silver modeling; row count dropped from 655,232 to 654,225.
- `origin_county_fips` and `dest_county_fips` are null only on `state` rows.
- `agi_thousands` and `agi` retain nulls where the IRS source suppressed or omitted income values.

## Lineage
1. `foundations/etl/staging/get_irs_migration.R` downloads annual IRS county inflow CSVs, normalizes county and state inflow staging tables, converts suppressed negative measures to nulls, and scales AGI into dollars.
2. `foundations/etl/silver/irs_migration_silver.R` joins county/state naming metadata, deduplicates exact staging repeats, and writes `silver.irs_migration_flows`.

## Known Gaps / To-Dos
- The current provider coverage is inflow-based only; there is no separate outbound raw source table.
- Historical county FIPS changes are handled by a best-available name reference built from current crosswalks plus staged destination county names.

## How To Extend (Next Table)
1. Query the live DuckDB table and confirm row count and candidate keys.
2. Profile each column for null rates, distinct counts, and representative top values.
3. Trace the ETL path from staging source script to Silver write target.
4. Update the `.yml` contract first, then sync the `.md` companion.
