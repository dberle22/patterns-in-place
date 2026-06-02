# Data Dictionary: silver.xwalk_zcta_county

## Overview
- **Table**: `silver.xwalk_zcta_county`
- **Purpose**: Silver layer analytical table.
- **Row count**: 54,559
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `county_geoid`.
- **Primary key candidate (recommended)**: (`county_geoid`)
  - `county_geoid` => rows=54559, distinct=3229, duplicates=51330
  - `zip_geoid` => rows=54559, distinct=39485, duplicates=15074
- **Time coverage**: `vintage` min=2025, max=2025
- **Geo coverage**: distinct_county_geoid=3229; distinct_zip_geoid=39485

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `zip_geoid` | `VARCHAR` | 0.0000 | 39485 | len 5-5 | 00926 (7); 40361 (7); 30534 (6); 39573 (6); 40351 (6) | ZIP Code GEOID, represented as a 5-digit string. Note that some ZIP Codes have leading zeros, which are preserved in the geoid (e.g. '00926'). |
| `county_geoid` | `VARCHAR` | 0.0000 | 3229 | len 5-5 | 06037 (491); 48201 (229); 17031 (228); 11001 (221); 04013 (195) | County GEOID, represented as a 5-digit string combining state FIPS and county FIPS (e.g. '06037' for Los Angeles County, CA). |
| `zip_pref_city` | `VARCHAR` | 0.0000 | 18501 | len 3-27 | WASHINGTON (264); HOUSTON (187); NEW YORK (128); ATLANTA (112); SPRINGFIELD (107) | Preferred city name for the ZIP Code. |
| `zip_pref_state` | `VARCHAR` | 0.0000 | 55 | len 2-2 | TX (3407); CA (2653); PA (2563); NY (2522); IL (2275) | State abbreviation for the ZIP Code. |
| `rel_weight_pop` | `DOUBLE` | 0.0000 | 23775 | min 0, max 1 | 1.0 (24650); 0.0 (3864); 0.5 (11); 0.8571428571428571 (11); 0.14285714285714285 (10) | Relative weight of the ZIP Code's population within the county. |
| `rel_weight_bus` | `DOUBLE` | 0.0000 | 7018 | min 0, max 1 | 1.0 (29290); 0.0 (10335); 0.5 (229); 0.3333333333333333 (145); 0.25 (138) | Relative weight of the ZIP Code's business count within the county. |
| `rel_weight_hu` | `DOUBLE` | 0.0000 | 24283 | min 2.7079723e-05, max 1 | 1.0 (28118); 0.5 (11); 0.014705882352941176 (9); 0.02564102564102564 (9); 0.027777777777777776 (9) | Relative weight of the ZIP Code's housing units within the county. |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2025, max 2025 | 2025 (54559) | Year of the crosswalk data. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 21-21 | HUD_ZIP_COUNTY_2025Q1 (54559) | Source of the crosswalk data. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`county_geoid`) found 51330 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/geo_crosswalks_silver.R:120:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_zcta_county"),`

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
