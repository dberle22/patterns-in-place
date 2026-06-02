# Data Dictionary: silver.bea_regional_line_codes

## Overview
- **Table**: `silver.bea_regional_line_codes`
- **Purpose**: Silver layer analytical table.
- **Row count**: 6,057
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `line_code`.
- **Primary key candidate (recommended)**: (`line_code`)
  - `line_code` => rows=6057, distinct=393, duplicates=5664
  - `param_value` => rows=6057, distinct=0, duplicates=6057
- **Time coverage**: No standard time column detected.
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `param_value` | `VARCHAR` | 100.0000 | 0 |  | NULL (6057) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `line_code` | `VARCHAR` | 0.0000 | 393 | len 1-4 | 10 (95); 6 (82); 3 (81); 11 (73); 1 (71) | Description of the economic activity in the row (from BEA metadata). |
| `line_desc` | `VARCHAR` | 0.0000 | 6044 | len 17-163 | [CAINC4] Employer contributions for government social insurance (2); [CAINC5N] Employer contributions for government social insurance (2); [CAINC5S] Employer contributions for government social insurance (2); [SAINC35] Earned Income Tax Credit (EITC) (2); [SAINC4] Employer contributions for government social insurance (2) | Description of the economic activity in the row (from BEA metadata). |
| `table_name_ref` | `VARCHAR` | 0.0000 | 101 | len 5-13 | CAINC5N (237); SAINC5N (237); SAINC6N (225); CAINC6N (224); SAINC7N (220) | BEA table name reference (e.g., CAINC5N, SAINC5N, etc.). |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 3962 | len 7-154 | Employer contributions for government social insurance (30); Wages and salaries (20); Employer contributions for employee pension and insurance funds (19); Supplements to wages and salaries (19); Personal income (18) | Cleaned description of the economic activity in the row (from BEA metadata). |
| `dataset` | `VARCHAR` | 0.0000 | 1 | len 8-8 | Regional (6057) | The BEA dataset that the line code belongs to (in this case, all rows belong to the "Regional" dataset). |
## Data Quality Notes
- Columns with non-zero null rates: param_value=100%
- Key uniqueness check for recommended PK (`line_code`) found 5664 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/staging/get_bea.R:84:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_line_codes"),`

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
