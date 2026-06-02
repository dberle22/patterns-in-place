# Data Dictionary: silver.tx_tea_district_metrics

## Overview
- **Table**: `silver.tx_tea_district_metrics`
- **Purpose**: Silver layer analytical table.
- **Row count**: 1,218
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `county_number`.
- **Primary key candidate (recommended)**: (`county_number`)
  - `county_number` => rows=1218, distinct=253, duplicates=965
- **Time coverage**: `year` min=2024, max=2024
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `county_number` | `VARCHAR` | 0.0000 | 253 | len 3-3 | 101 (60); 057 (43); 015 (39); 220 (26); 227 (26) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `county_name` | `VARCHAR` | 0.0000 | 253 | len 10-20 | HARRIS COUNTY (60); DALLAS COUNTY (43); BEXAR COUNTY (39); TARRANT COUNTY (26); TRAVIS COUNTY (26) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `esc_region_served` | `VARCHAR` | 0.0000 | 20 | len 2-2 | 10 (113); 07 (101); 11 (95); 04 (91); 20 (86) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_number` | `VARCHAR` | 0.0000 | 1218 | len 6-6 | 001902 (1); 001903 (1); 001904 (1); 001906 (1); 001907 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_name` | `VARCHAR` | 0.0000 | 1207 | len 7-48 | BIG SANDY ISD (2); CENTERVILLE ISD (2); CHAPEL HILL ISD (2); DAWSON ISD (2); EDGEWOOD ISD (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_city` | `VARCHAR` | 0.0000 | 917 | len 3-22 | HOUSTON (49); SAN ANTONIO (39); AUSTIN (20); DALLAS (18); FORT WORTH (13) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_zip` | `VARCHAR` | 0.0000 | 1168 | len 5-10 | 77077 (6); 78212 (6); 77004 (4); 75217 (3); 76401 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_type` | `VARCHAR` | 0.0000 | 5 | len 4-11 | INDEPENDENT (1020); CHARTER (189); COMMON (6); TSD/TSBVI (2); TJJD (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `nces_district_id` | `VARCHAR` | 0.0000 | 1209 | len 0-7 | NULL (10); 4800001 (1); 4800002 (1); 4800003 (1); 4800004 (1) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `district_enrollment_as_of_oct_2024` | `DOUBLE` | 0.0000 | 989 | min 0, max 176727 | 0.0 (18); 343.0 (6); 141.0 (5); 227.0 (5); 119.0 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `number_of_schools` | `INTEGER` | 0.0000 | 73 | min 1, max 274 | 1 (280); 3 (209); 2 (149); 4 (140); 5 (95) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `avg_school_enrollment` | `DOUBLE` | 0.0000 | 990 | min -1, max 3075.25 | 0.0 (18); 141.0 (6); 119.0 (4); 129.0 (4); 163.0 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `lea_name` | `VARCHAR` | 16.5025 | 1006 | len 30-68 | NULL (201); Big Sandy Independent School District (2); Centerville Independent School District (2); Chapel Hill Independent School District (2); Dawson Independent School District (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `allocations` | `DOUBLE` | 16.5025 | 988 | min 0, max 169760890 | NULL (201); 0.0 (19); 21534.039622084958 (3); 104270.0865911482 (2); 107670.19811042478 (2) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `year` | `INTEGER` | 0.0000 | 1 | min 2024, max 2024 | 2024 (1218) | Observation year or period year for the row. |
| `charter_status` | `VARCHAR` | 1.7241 | 2 | len 19-23 | TRADITIONAL ISD/CSD (1020); OPEN ENROLLMENT CHARTER (177); NULL (21) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `total_count` | `DOUBLE` | 1.7241 | 987 | min -999, max 176727 | NULL (21); 343.0 (6); 141.0 (5); 227.0 (5); 119.0 (4) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `not_economically_disadvantaged_percent` | `DOUBLE` | 15.3530 | 945 | min 0, max 100 | NULL (187); 0.0 (9); 34.78 (3); 36.14 (3); 50.81 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
| `economically_disadvantaged_percent` | `DOUBLE` | 15.3530 | 945 | min 0, max 100 | NULL (187); 100.0 (9); 39.36 (3); 49.19 (3); 63.86 (3) | Definition not yet documented; inferred from column name. Needs confirmation. |
## Data Quality Notes
- Columns with non-zero null rates: lea_name=16.5025%, allocations=16.5025%, charter_status=1.7241%, total_count=1.7241%, not_economically_disadvantaged_percent=15.353%, economically_disadvantaged_percent=15.353%
- Key uniqueness check for recommended PK (`county_number`) found 965 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_tx_school_district.sql:26:from metro_deep_dive.silver.tx_tea_district_metrics `

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
