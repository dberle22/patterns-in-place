# Data Dictionary: silver.xwalk_state_region

## Overview
- **Table**: `silver.xwalk_state_region`
- **Purpose**: Silver layer analytical table.
- **Row count**: 51
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `state_fips`.
- **Primary key candidate (recommended)**: (`state_fips`)
  - `state_fips` => rows=51, distinct=51, duplicates=0
- **Time coverage**: No standard time column detected.
- **Geo coverage**: distinct_state_fips=51

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `state_fips` | `VARCHAR` | 0.0000 | 51 | len 2-2 | 01 (1); 02 (1); 04 (1); 05 (1); 06 (1) | State FIPS code. |
| `state_abbr` | `VARCHAR` | 0.0000 | 51 | len 2-2 | AK (1); AL (1); AR (1); AZ (1); CA (1) | State abbreviation. |
| `state_name` | `VARCHAR` | 0.0000 | 51 | len 4-20 | Alabama (1); Alaska (1); Arizona (1); Arkansas (1); California (1) | Full name of the state. |
| `census_region` | `VARCHAR` | 0.0000 | 4 | len 4-9 | South (17); West (13); Midwest (12); Northeast (9) | Census region of the state. |
| `census_division` | `VARCHAR` | 0.0000 | 9 | len 7-18 | South Atlantic (9); Mountain (8); West North Central (7); New England (6); East North Central (5) | Census division of the state. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`state_fips`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/geo_crosswalks_silver.R:261:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_state_region"),`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Add explicit business definitions for columns flagged as needs confirmation.
- Add enforced lineage metadata entries in `silver.metadata_topics` / `silver.metadata_vars` where missing.

## How To Extend (Next Table)
1. Run table-existence and row-count checks from DuckDB.
2. Pull schema from `information_schema.columns` and compute per-column profile metrics.
3. Run uniqueness checks for plausible key combinations.
4. Locate ETL lineage with `rg -n "<table_name>|dbWriteTable|CREATE TABLE" scripts notebooks documents`.
5. Write `data_dictionary/layers/<layer>/<schema>__<table>.md` and `.yml` artifacts.
6. Mark inferred statements explicitly and set `needs_confirmation` where definitions are unclear.
