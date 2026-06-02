# Data Dictionary: silver.kpi_dictionary

## Overview
- **Table**: `silver.kpi_dictionary`
- **Purpose**: Silver layer analytical table.
- **Row count**: 404
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `table_name`.
- **Primary key candidate (recommended)**: (`table_name`)
  - `table_name` => rows=404, distinct=16, duplicates=388
  - `topic` => rows=404, distinct=8, duplicates=396
- **Time coverage**: No standard time column detected.
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `topic` | `VARCHAR` | 0.0000 | 8 | len 3-9 | labor (93); age (76); housing (67); transport (45); education (35) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `table_name` | `VARCHAR` | 0.0000 | 16 | len 7-14 | age_base (50); labor_kpi (49); labor_base (44); housing_base (34); housing_kpi (33) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `kpi_name` | `VARCHAR` | 0.0000 | 403 | len 4-37 | occ_totalE (2); age_0_4 (1); age_15_24 (1); age_25_34 (1); age_25_54 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `business_definition` | `VARCHAR` | 0.0000 | 3 | len 29-53 | Measure derived from ACS Silver table. (324); Share / percentage; denominator defined in KPI logic. (72); Rate derived from ACS counts. (8) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `source` | `VARCHAR` | 0.0000 | 3 | len 10-34 | ACS 5-year (305); ACS Housing (B2500x) (67); ACS Income/Poverty (B19xxx/B17xxx) (32) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `denominator_hint` | `VARCHAR` | 91.3366 | 7 | len 8-32 | NULL (369); ind_total_emp (13); households (topic-specific) (9); commute_workers_total (5); occ_total_emp (5) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `data_type` | `VARCHAR` | 0.0000 | 1 | len 6-6 | DOUBLE (404) | Definition not yet documented; inferred from column name. Needs confirmation. |
## Data Quality Notes
- Columns with non-zero null rates: denominator_hint=91.3366%
- Key uniqueness check for recommended PK (`table_name`) found 388 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_metadata_silver.R:203:  DBI::Id(schema = "silver", table = "kpi_dictionary"),`

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
