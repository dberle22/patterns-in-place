# Data Dictionary: silver.xwalk_zcta_cbsa

## Overview
- **Table**: `silver.xwalk_zcta_cbsa`
- **Purpose**: Silver layer analytical table.
- **Row count**: 47,633
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `zip_geoid`.
- **Primary key candidate (recommended)**: (`zip_geoid`)
  - `zip_geoid` => rows=47633, distinct=39482, duplicates=8151
- **Time coverage**: `vintage` min=2025, max=2025
- **Geo coverage**: distinct_zip_geoid=39482

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `zip_geoid` | `VARCHAR` | 0.0000 | 39482 | len 5-5 | 37144 (5); 47240 (5); 03280 (4); 17021 (4); 17814 (4) | ZIP Code, represented as a 5-digit string. Note that some ZIP Codes have leading zeros, which are preserved in the geoid (e.g. '03280'). |
| `cbsa_geoid` | `VARCHAR` | 0.0000 | 936 | len 5-5 | 99999 (11192); 35620 (1072); 47900 (683); 31080 (632); 37980 (489) | CBSA (Core Based Statistical Area) GEOID. Note that some ZIP Codes are not assigned to a CBSA, and in those cases the geoid is '99999'. |
| `zip_pref_city` | `VARCHAR` | 0.0000 | 18498 | len 3-27 | WASHINGTON (262); HOUSTON (178); NEW YORK (127); SPRINGFIELD (105); MIAMI (99) | Preferred city name for the ZIP Code. |
| `zip_pref_state` | `VARCHAR` | 0.0000 | 54 | len 2-2 | TX (2894); CA (2602); PA (2397); NY (2394); IL (1960) | State abbreviation for the ZIP Code. |
| `rel_weight_pop` | `DOUBLE` | 0.0000 | 14192 | min 0, max 1 | 1.0 (28858); 0.0 (3705); 0.007042253521126761 (7); 0.0033112582781456954 (6); 0.045454545454545456 (6) | Relative weight of the ZIP Code's population within the CBSA. |
| `rel_weight_bus` | `DOUBLE` | 0.0000 | 3844 | min 0, max 1 | 1.0 (32103); 0.0 (7079); 0.5 (131); 0.25 (84); 0.6666666666666666 (82) | Relative weight of the ZIP Code's business count within the CBSA. |
| `rel_weight_hu` | `DOUBLE` | 0.0000 | 14367 | min 2.7079723e-05, max 1 | 1.0 (32443); 0.01282051282051282 (7); 0.014705882352941176 (6); 0.04878048780487805 (6); 0.06666666666666667 (6) | Relative weight of the ZIP Code's housing units within the CBSA. |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2025, max 2025 | 2025 (47633) | Year of the crosswalk data. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 19-19 | HUD_ZIP_CBSA_2025Q1 (47633) | Source of the crosswalk data. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`zip_geoid`) found 8151 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/geo_crosswalks_silver.R:143:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_zcta_cbsa"),`

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
