# Data Dictionary: silver.metadata_topics

## Overview
- **Table**: `silver.metadata_topics`
- **Purpose**: Silver layer analytical table.
- **Row count**: 16
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `table_name`.
- **Primary key candidate (recommended)**: (`table_name`)
  - `table_name` => rows=16, distinct=16, duplicates=0
  - `table_schema` => rows=16, distinct=1, duplicates=15
- **Time coverage**: No standard time column detected.
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `table_schema` | `VARCHAR` | 0.0000 | 1 | len 6-6 | silver (16) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `table_name` | `VARCHAR` | 0.0000 | 16 | len 7-14 | age_base (1); age_kpi (1); education_base (1); education_kpi (1); housing_base (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `topic` | `VARCHAR` | 0.0000 | 8 | len 3-9 | age (2); education (2); housing (2); income (2); labor (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `table_type` | `VARCHAR` | 0.0000 | 2 | len 3-4 | base (8); kpi (8) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `row_count` | `DOUBLE` | 0.0000 | 1 | min 913388, max 913388 | 913388.0 (16) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `col_count` | `DOUBLE` | 0.0000 | 13 | min 13, max 54 | 14.0 (3); 22.0 (2); 13.0 (1); 23.0 (1); 26.0 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `min_year` | `INTEGER` | 0.0000 | 1 | min 2012, max 2012 | 2012 (16) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `max_year` | `INTEGER` | 0.0000 | 1 | min 2023, max 2023 | 2023 (16) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `geo_levels` | `VARCHAR` | 0.0000 | 16 | len 74-74 | c("US", "division", "place", "tract", "Region", "state", "county", "zcta") (1); c("US", "division", "place", "zcta", "state", "county", "Region", "tract") (1); c("US", "state", "county", "zcta", "Region", "division", "tract", "place") (1); c("division", "Region", "US", "place", "tract", "zcta", "state", "county") (1); c("division", "Region", "place", "zcta", "state", "county", "US", "tract") (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `last_refreshed` | `TIMESTAMP` | 0.0000 | 16 | len 24-26 | 2025-11-02 14:52:07.102005 (1); 2025-11-02 14:52:07.171306 (1); 2025-11-02 14:52:07.216115 (1); 2025-11-02 14:52:07.262194 (1); 2025-11-02 14:52:07.299466 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`table_name`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_metadata_silver.R:107:  DBI::Id(schema = "silver", table = "metadata_topics"),`

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
