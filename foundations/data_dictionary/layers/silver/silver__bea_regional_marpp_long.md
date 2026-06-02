# Data Dictionary: silver.bea_regional_marpp_long

## Overview
- **Table**: `silver.bea_regional_marpp_long`
- **Purpose**: Silver layer analytical table.
- **Row count**: 55,808
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period + metric_key`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `metric_key`)
  - `geo_level + geo_id + period` => rows=55808, distinct=6976, duplicates=48832
  - `geo_level + geo_id + period + metric_key` => rows=55808, distinct=55808, duplicates=0
  - `geo_level + geo_id + period + table + code + line_code` => rows=55808, distinct=55808, duplicates=0
  - `geo_level + geo_id + period + table + metric_key` => rows=55808, distinct=55808, duplicates=0
  - `table + geo_level + geo_id + period + line_code` => rows=55808, distinct=55808, duplicates=0
- **Time coverage**: `period` min=2008, max=2023
- **Geo coverage**: distinct_geo_levels=2; distinct_geo_id=436

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `code` | `VARCHAR` | 0.0000 | 16 | len 7-7 | MARPP-1 (6144); MARPP-2 (6144); MARPP-3 (6144); MARPP-4 (6144); MARPP-5 (6144) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `table` | `VARCHAR` | 0.0000 | 2 | len 5-5 | MARPP (49152); SARPP (6656) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `geo_level` | `VARCHAR` | 0.0000 | 2 | len 4-5 | cbsa (49152); state (6656) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 436 | len 5-5 | 00000 (128); 01000 (128); 02000 (128); 04000 (128); 05000 (128) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 436 | len 4-78 | Abilene, TX (Metropolitan Statistical Area) (128); Akron, OH (Metropolitan Statistical Area) (128); Alabama (128); Alaska (128); Albany, GA (Metropolitan Statistical Area) (128) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 16 | min 2008, max 2023 | 2008 (3488); 2009 (3488); 2010 (3488); 2011 (3488); 2012 (3488) | Time period for the observation (usually calendar year). |
| `line_code` | `VARCHAR` | 0.0000 | 8 | len 1-1 | 1 (6976); 2 (6976); 3 (6976); 4 (6976); 5 (6976) | Line code for the metric in the row, from BEA metadata. Needs confirmation. |
| `unit_raw` | `VARCHAR` | 0.0000 | 3 | len 5-33 | Index (40192); Constant 2017 dollars (7808); Millions of constant 2017 dollars (7808) | Raw unit value for the metric in the row, from BEA metadata. |
| `unit_mult` | `INTEGER` | 0.0000 | 2 | min 0, max 6 | 0 (48000); 6 (7808) | Unit multiplier for the metric in the row, from BEA metadata. |
| `value_raw` | `DOUBLE` | 0.0000 | 37419 | min 0, max 19641720 | 0.0 (160); 95.902 (34); 97.109 (30); 94.361 (26); 97.839 (26) | Raw value for the metric in the row, from BEA metadata. |
| `value` | `DOUBLE` | 0.0000 | 37438 | min 0, max 19641720000000 | 0.0 (160); 95.902 (34); 97.109 (30); 94.361 (26); 97.839 (26) | Numeric value for the metric in long-format records. |
| `note_ref` | `VARCHAR` | 82.4255 | 8 | len 1-8 | NULL (46000); 2 (6928); 1 (832); 3 (832); 4 (832) | Reference number for the note in the BEA metadata. |
| `metric_key` | `VARCHAR` | 0.0000 | 10 | len 9-24 | rpp_all_items (6976); rpp_goods (6976); rpp_real_pc_income (6976); rpp_real_personal_income (6976); rpp_services_rents (6976) | Key for the metric in the row, from BEA metadata. |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 10 | len 11-49 | RPPs: All items (6976); RPPs: Goods (6976); RPPs: Services: Rents (6976); RPPs: Services: Utilities (6976); Real per capita personal income (6976) | Cleaned line description for the metric in the row, from BEA metadata. |
## Data Quality Notes
- Columns with non-zero null rates: note_ref=82.4255%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period + metric_key`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/bea_marpp_silver.R:87:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_marpp_long"),`

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
