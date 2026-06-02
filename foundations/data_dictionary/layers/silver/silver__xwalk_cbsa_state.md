# Data Dictionary: silver.xwalk_cbsa_state

## Overview
- **Table**: `silver.xwalk_cbsa_state`
- **Purpose**: Silver layer analytical table.
- **Row count**: 1,002
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `cbsa_code`.
- **Primary key candidate (recommended)**: (`cbsa_code`)
  - `cbsa_code` => rows=1002, distinct=935, duplicates=67
- **Time coverage**: `vintage` min=2023, max=2023
- **Geo coverage**: distinct_state_fips=52; distinct_cbsa_code=935

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `cbsa_code` | `VARCHAR` | 0.0000 | 935 | len 5-5 | 37980 (4); 47900 (4); 17140 (3); 26580 (3); 32820 (3) | GEOID for Core Based Statistical Areas (CBSAs). |
| `cbsa_name` | `VARCHAR` | 0.0000 | 935 | len 7-46 | Philadelphia-Camden-Wilmington, PA-NJ-DE-MD (4); Washington-Arlington-Alexandria, DC-VA-MD-WV (4); Cincinnati, OH-KY-IN (3); Huntington-Ashland, WV-KY-OH (3); Memphis, TN-MS-AR (3) | Name of Core Based Statistical Areas (CBSAs). |
| `state_fips` | `VARCHAR` | 0.0000 | 52 | len 2-2 | 48 (67); 39 (44); 18 (40); 13 (39); 37 (39) | FIPS code for the state within a Core Based Statistical Area (CBSA). |
| `state_name` | `VARCHAR` | 0.0000 | 52 | len 4-20 | Texas (67); Ohio (44); Indiana (40); Georgia (39); North Carolina (39) | Name of the state within a Core Based Statistical Area (CBSA). |
| `counties` | `INTEGER` | 0.0000 | 18 | min 1, max 40 | 1 (655); 2 (165); 3 (77); 4 (37); 5 (25) | Number of counties within a Core Based Statistical Area (CBSA). |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2023, max 2023 | 2023 (1002) | Year of the crosswalk data. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 30-30 | DERIVED_FROM_CBSA_COUNTY_XWALK (1002) | Crosswalk source identifier, indicating that the data was derived from a crosswalk of CBSA to county FIPS codes. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`cbsa_code`) found 67 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/geo_crosswalks_silver.R:201:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_cbsa_state"),`

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
