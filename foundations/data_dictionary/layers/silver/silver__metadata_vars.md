# Data Dictionary: silver.metadata_vars

## Overview
- **Table**: `silver.metadata_vars`
- **Purpose**: Silver layer analytical table.
- **Row count**: 468
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `table_name`.
- **Primary key candidate (recommended)**: (`table_name`)
  - `table_name` => rows=468, distinct=16, duplicates=452
  - `table_schema` => rows=468, distinct=1, duplicates=467
- **Time coverage**: No standard time column detected.
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `table_schema` | `VARCHAR` | 0.0000 | 1 | len 6-6 | silver (468) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `table_name` | `VARCHAR` | 0.0000 | 16 | len 7-14 | age_base (54); labor_kpi (53); labor_base (48); housing_base (38); housing_kpi (37) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `column_name` | `VARCHAR` | 0.0000 | 407 | len 4-37 | geo_id (16); geo_level (16); geo_name (16); year (16); occ_totalE (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `ordinal_position` | `INTEGER` | 0.0000 | 54 | min 1, max 54 | 1 (16); 10 (16); 11 (16); 12 (16); 13 (16) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `data_type` | `VARCHAR` | 0.0000 | 3 | len 6-7 | DOUBLE (404); VARCHAR (48); INTEGER (16) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `topic` | `VARCHAR` | 0.0000 | 8 | len 3-9 | labor (101); age (84); housing (75); transport (53); education (43) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `is_key` | `BOOLEAN` | 0.0000 | 2 | len 4-5 | false (404); true (64) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `is_measure` | `BOOLEAN` | 0.0000 | 2 | len 4-5 | true (404); false (64) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `description` | `VARCHAR` | 0.0000 | 12 | len 23-80 | Metric from labor ACS table (93); Metric from age ACS table (76); Metric from housing ACS table (67); Metric from transport ACS table (45); Metric from education ACS table (35) | Definition not yet documented; inferred from column name. Needs confirmation. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`table_name`) found 452 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_metadata_silver.R:152:  DBI::Id(schema = "silver", table = "metadata_vars"),`
   - `scripts/etl/silver/acs_metadata_silver.R:160:  FROM silver.metadata_vars`

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
