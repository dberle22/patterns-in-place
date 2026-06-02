# Data Dictionary: silver.bea_regional_tables

## Overview
- **Table**: `silver.bea_regional_tables`
- **Purpose**: Silver layer analytical table.
- **Row count**: 101
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `table_key`.
- **Primary key candidate (recommended)**: (`table_key`)
  - `table_key` => rows=101, distinct=101, duplicates=0
  - `param_value` => rows=101, distinct=0, duplicates=101
- **Time coverage**: No standard time column detected.
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `param_value` | `VARCHAR` | 100.0000 | 0 |  | NULL (101) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `table_key` | `VARCHAR` | 0.0000 | 101 | len 5-13 | CAGDP1 (1); CAGDP11 (1); CAGDP2 (1); CAGDP8 (1); CAGDP9 (1) | Table Key from BEA, used to link to BEA datasets and metadata. Examples include: CAGDP1, CAINC1, etc. |
| `table_desc` | `VARCHAR` | 0.0000 | 77 | len 8-130 | Contributions to percent change in real GDP (4); Compensation of employees by NAICS industry (3); Compensation of employees by SIC industry (3); Personal income by major component and earnings by NAICS industry (3); Personal income by major component and earnings by SIC industry (3) | Description of the BEA table, e.g., "Contributions to percent change in real GDP" |
| `dataset` | `VARCHAR` | 0.0000 | 1 | len 8-8 | Regional (101) | The dataset that the BEA table belongs to (e.g., "Regional") |
## Data Quality Notes
- Columns with non-zero null rates: param_value=100%
- Key uniqueness check for recommended PK (`table_key`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/staging/get_bea.R:81:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_tables"),`

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
