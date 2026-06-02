# Data Dictionary: silver.xwalk_zcta_tract

## Overview
- **Table**: `silver.xwalk_zcta_tract`
- **Purpose**: Silver layer analytical table.
- **Row count**: 189,302
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `zip_geoid`.
- **Primary key candidate (recommended)**: (`zip_geoid`)
  - `zip_geoid` => rows=189302, distinct=39367, duplicates=149935
- **Time coverage**: `vintage` min=2025, max=2025
- **Geo coverage**: distinct_zip_geoid=39367; distinct_tract_geoid=84933

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `zip_geoid` | `VARCHAR` | 0.0000 | 39367 | len 5-5 | 00926 (64); 00959 (54); 60647 (53); 00957 (52); 11236 (48) | ZIP Code GEOID, represented as a 5-digit string. Note that some ZIP Codes have leading zeros, which are preserved in the geoid (e.g. '00926'). |
| `tract_geoid` | `VARCHAR` | 0.0000 | 84933 | len 11-11 | 11001980000 (46); 11001010700 (30); 11001010202 (27); 54011000600 (25); 11001005802 (24) | Census Tract GEOID, represented as an 11-digit string combining state FIPS, county FIPS, and tract code (e.g. '11001000100' for Census Tract 1 in Washington, D.C.). |
| `zip_pref_city` | `VARCHAR` | 0.0000 | 18479 | len 3-27 | HOUSTON (1444); LOS ANGELES (1206); CHICAGO (1179); BROOKLYN (1153); MIAMI (893) | Preferred city name for the ZIP Code. |
| `zip_pref_state` | `VARCHAR` | 0.0000 | 54 | len 2-2 | CA (16068); TX (13839); NY (11310); FL (9166); PA (8912) | Preferred state abbreviation for the ZIP Code. |
| `rel_weight_pop` | `DOUBLE` | 0.0000 | 155149 | min 0, max 1 | 0.0 (11105); 1.0 (9692); 0.5 (39); 0.3333333333333333 (30); 0.09090909090909091 (26) | Relative weight of the ZIP Code's population within the tract. |
| `rel_weight_bus` | `DOUBLE` | 0.0000 | 75588 | min 0, max 1 | 0.0 (31508); 1.0 (14017); 0.5 (689); 0.3333333333333333 (434); 0.25 (391) | Relative weight of the ZIP Code's business count within the tract. |
| `rel_weight_hu` | `DOUBLE` | 0.0000 | 162415 | min 1.6992642e-05, max 1 | 1.0 (12769); 0.5 (105); 0.3333333333333333 (55); 0.6666666666666666 (41); 0.25 (38) | Relative weight of the ZIP Code's housing units within the tract. |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2025, max 2025 | 2025 (189302) | Year of the crosswalk data. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 20-20 | HUD_ZIP_TRACT_2025Q1 (189302) | Source of the crosswalk data. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`zip_geoid`) found 149935 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/geo_crosswalks_silver.R:166:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_zcta_tract"),`

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
