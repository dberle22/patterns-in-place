# Data Dictionary: silver.xwalk_cbsa_primary_city

## Overview
- **Table**: `silver.xwalk_cbsa_primary_city`
- **Purpose**: Silver layer analytical table.
- **Row count**: 1,294
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `cbsa_code`.
- **Primary key candidate (recommended)**: (`cbsa_code`)
  - `cbsa_code` => rows=1294, distinct=935, duplicates=359
- **Time coverage**: `vintage` min=2023, max=2023
- **Geo coverage**: distinct_state_fips=52; distinct_cbsa_code=935

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `cbsa_code` | `VARCHAR` | 0.0000 | 935 | len 5-5 | 31080 (19); 33100 (13); 41860 (12); 33460 (10); 47900 (10) | GEOID for Core Based Statistical Areas (CBSAs). |
| `cbsa_name` | `VARCHAR` | 0.0000 | 935 | len 7-46 | Los Angeles-Long Beach-Anaheim, CA (19); Miami-Fort Lauderdale-West Palm Beach, FL (13); San Francisco-Oakland-Fremont, CA (12); Minneapolis-St. Paul-Bloomington, MN-WI (10); Washington-Arlington-Alexandria, DC-VA-MD-WV (10) | Name of Core Based Statistical Areas (CBSAs). |
| `cbsa_type` | `VARCHAR` | 0.0000 | 2 | len 29-29 | Metropolitan Statistical Area (726); Micropolitan Statistical Area (568) | Type of Core Based Statistical Area (CBSA). Metropolitan Statistical Areas have an urban core population of 50,000 or more, while Micropolitan Statistical Areas have an urban core population of at least 10,000 but less than 50,000. |
| `primary_city` | `VARCHAR` | 0.0000 | 1153 | len 3-57 | Auburn (5); Columbus (5); Springfield (5); Greenville (4); Jackson (4) | Primary city within a Core Based Statistical Area (CBSA). |
| `state_fips` | `VARCHAR` | 0.0000 | 52 | len 2-2 | 06 (95); 48 (94); 12 (67); 37 (48); 39 (47) | FIPS code for the state within a Core Based Statistical Area (CBSA). |
| `place_fips` | `VARCHAR` | 0.0000 | 1168 | len 5-5 | 01000 (5); 37000 (5); 53000 (5); 65000 (5); 67000 (5) | FIPS code for the place within a Core Based Statistical Area (CBSA). |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2023, max 2023 | 2023 (1294) | The vintage year of the crosswalk data. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 8-8 | OMB_2023 (1294) | Crosswalk source identifier, indicating the source and vintage of the CBSA to primary city crosswalk data. In this case, OMB_2023 indicates that the data is based on the Office of Management and Budget's 2023 delineations of CBSAs. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`cbsa_code`) found 359 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/geo_crosswalks_silver.R:69:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_cbsa_primary_city"),`

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
