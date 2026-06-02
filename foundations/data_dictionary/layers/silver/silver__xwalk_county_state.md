# Data Dictionary: silver.xwalk_county_state

## Overview
- **Table**: `silver.xwalk_county_state`
- **Purpose**: Silver layer analytical table.
- **Row count**: 3,235
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `county_geoid`.
- **Primary key candidate (recommended)**: (`county_geoid`)
  - `county_geoid` => rows=3235, distinct=3235, duplicates=0
  - `state_fip` => rows=3235, distinct=56, duplicates=3179
- **Time coverage**: `vintage` min=2023, max=2023
- **Geo coverage**: distinct_county_geoid=3235

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `state_fip` | `VARCHAR` | 0.0000 | 56 | len 2-2 | 48 (254); 13 (159); 51 (133); 21 (120); 29 (115) | 2-digit state FIPS code. Note: physical column name is `state_fip` (legacy singular naming), semantically equivalent to `state_fips` used in other tables. |
| `county_fip` | `VARCHAR` | 0.0000 | 333 | len 3-3 | 001 (49); 003 (49); 005 (49); 009 (48); 007 (47) | County FIPS code. |
| `county_geoid` | `VARCHAR` | 0.0000 | 3235 | len 5-5 | 01001 (1); 01003 (1); 01005 (1); 01007 (1); 01009 (1) | County GEOID, which is a concatenation of the state FIPS code and county FIPS code. |
| `county_name` | `VARCHAR` | 0.0000 | 1927 | len 3-30 | Washington (31); Franklin (26); Jefferson (26); Jackson (24); Lincoln (24) | County Name. |
| `county_name_long` | `VARCHAR` | 0.0000 | 1973 | len 4-46 | Washington County (30); Jefferson County (25); Franklin County (24); Jackson County (23); Lincoln County (23) | Long name of the county. |
| `state_abbr` | `VARCHAR` | 0.0000 | 56 | len 2-2 | TX (254); GA (159); VA (133); KY (120); MO (115) | State abbreviation. |
| `lsad` | `VARCHAR` | 0.0000 | 12 | len 2-2 | 06 (2999); 13 (78); 15 (64); 25 (40); 04 (13) | LSAD (Legal Statistical Area Description) code for the county. |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2023, max 2023 | 2023 (3235) | Year of the crosswalk data. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 6-6 | TIGRIS (3235) | Crosswalk source identifier, indicating the source and vintage of the county to state crosswalk data. In this case, TIGRIS indicates that the data is based on the U.S. Census Bureau's TIGER/Line Shapefiles. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`county_geoid`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/hud_fmr_silver.R:43:county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")`
   - `scripts/etl/silver/geo_crosswalks_silver.R:188:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_county_state"),`
   - `scripts/etl/silver/bps_silver.R:46:county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")`
   - `scripts/etl/silver/bls_laus_silver.R:41:county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")`
   - `scripts/etl/silver/irs_migration_silver.R:42:county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")`
2. **Downstream usage (examples)**:
   - `scripts/etl/staging/get_irs_migration.R:86:county_state_xwalk <- dbGetQuery(con, "SELECT * FROM silver.xwalk_county_state")`

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
