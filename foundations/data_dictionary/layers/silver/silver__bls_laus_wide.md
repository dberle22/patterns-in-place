# Data Dictionary: silver.bls_laus_wide

## Overview
- **Table**: `silver.bls_laus_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 63,125
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=63125, distinct=63125, duplicates=0
  - `geo_id + period` => rows=63125, distinct=63125, duplicates=0
  - `geo_level` => rows=63125, distinct=3, duplicates=63122
- **Time coverage**: `period` min=2010, max=2024
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4209

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (48305); CBSA (14040); State (780) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0238 | 4209 | len 2-5 | 01 (15); 01001 (15); 01003 (15); 01005 (15); 01007 (15) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0238 | 4208 | len 2-50 | Carson City, NV (30); AK (15); AL (15); AR (15); AZ (15) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 15 | min 2010, max 2024 | 2020 (4209); 2021 (4209); 2022 (4209); 2023 (4209); 2024 (4209) | Time period for the observation (usually calendar year). |
| `labor_force` | `DOUBLE` | 0.1236 | 35271 | min 0, max 19644057 | NULL (78); 0.0 (11); 1032.0 (10); 19238.0 (10); 3953.0 (10) | Population in Labor Force (employed + unemployed). |
| `employed` | `DOUBLE` | 0.1236 | 34503 | min 0, max 18621929 | NULL (78); 0.0 (11); 1993.0 (10); 2193.0 (10); 2693.0 (10) | Population Employed. |
| `unemployed` | `DOUBLE` | 0.1236 | 11898 | min 0, max 2267409 | 23.0 (79); 30.0 (78); NULL (78); 38.0 (75); 20.0 (74) | Population Unemployed. |
| `unemployment_rate_percent` | `DOUBLE` | 0.1236 | 15056 |  | 3.5 (1032); 3.7 (1009); 3.6 (1008); 3.4 (991); 4.1 (983) | Unemployment Rate (calculated as unemployed / labor_force * 100) |
## Data Quality Notes
- Columns with non-zero null rates: geo_id=0.0238%, geo_name=0.0238%, labor_force=0.1236%, employed=0.1236%, unemployed=0.1236%, unemployment_rate_percent=0.1236%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_gdp.sql:130:from metro_deep_dive.silver.bls_laus_wide`
   - `scripts/etl/gold/gold_economy_wide.sql:172:from metro_deep_dive.silver.bls_laus_wide`
   - `scripts/etl/gold/gold_economy_labor.sql:27:from metro_deep_dive.silver.bls_laus_wide`
   - `scripts/etl/silver/bls_laus_silver.R:110:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bls_laus_wide"),`

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
