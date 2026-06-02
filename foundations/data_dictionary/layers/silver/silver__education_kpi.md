# Data Dictionary: silver.education_kpi

## Overview
- **Table**: `silver.education_kpi`
- **Purpose**: Silver education table (`kpi` type).
- **Row count**: 1,020,930
- **KPI applicability**: KPI table (or has KPI dictionary entries).

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1020930, distinct=1020930, duplicates=0
  - `geo_level + geo_id + year` => rows=1020930, distinct=1020930, duplicates=0
  - `geo_id + year` => rows=1020930, distinct=998787, duplicates=22143
  - `geo_level` => rows=1020930, distinct=9, duplicates=1020921
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=115976

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | zcta (433172); place (397094); tract (135851); county (41870); cbsa (12085) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 115976 | len 1-11 | 1 (39); 2 (26); 3 (26); 4 (26); 01001 (25) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 97125 | len 4-66 | Alexandria city, Virginia (26); Baltimore city, Maryland (26); Bristol city, Virginia (26); Buena Vista city, Virginia (26); Carson City, Nevada (26) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 13 | min 2012, max 2024 | 2024 (82276); 2023 (82271); 2022 (82134); 2021 (81848); 2020 (81194) | Observation year or period year for the row. |
| `edu_total_25p` | `DOUBLE` | 0.0000 | 63573 | min 0, max 230807300 | 0.0 (11750); 62.0 (876); 76.0 (852); 54.0 (851); 38.0 (847) | Total Population Aged 25+, base unit for Education metrics. |
| `lt_hs_25p` | `DOUBLE` | 0.0000 | 22049 | min 0, max 29179819 | 0.0 (60004); 10.0 (6818); 8.0 (6642); 7.0 (6552); 9.0 (6497) | Population count for less than high school 25+. |
| `hs_ged_25p` | `DOUBLE` | 0.0000 | 31522 | min 0, max 60094716 | 0.0 (24955); 15.0 (2202); 17.0 (2190); 27.0 (2151); 9.0 (2129) | Population count for High School or GED 25+. |
| `somecol_assoc_25p` | `DOUBLE` | 0.0000 | 32415 | min 0, max 64656741 | 0.0 (25668); 8.0 (2773); 15.0 (2736); 14.0 (2731); 17.0 (2723) | Population count for Some College or Associate's degree 25+. |
| `ba_25p` | `DOUBLE` | 0.0000 | 26841 | min 0, max 49868171 | 0.0 (60062); 8.0 (6690); 7.0 (6556); 9.0 (6516); 5.0 (6491) | Total: Population count for Bachelor's degree 25+. |
| `ma_plus_25p` | `DOUBLE` | 0.0000 | 21512 | min 0, max 32495045 | 0.0 (105206); 2.0 (13141); 3.0 (11469); 4.0 (11165); 5.0 (10667) | Total: Population count for Master's or higher degree 25+. |
| `pct_lt_hs_25p` | `DOUBLE` | 0.0000 | 542847 |  | 0.0 (48254); -nan (11750); 1.0 (1258); 0.2 (1010); 0.16666666666666666 (1001) | Percentage of population aged 25+ with less than high school education. |
| `pct_hs_ged_25p` | `DOUBLE` | 0.0000 | 578769 |  | 0.0 (13205); -nan (11750); 0.5 (2851); 1.0 (2750); 0.3333333333333333 (2161) | Percentage of population aged 25+ with High School or GED education. |
| `pct_somecol_assoc_25p` | `DOUBLE` | 0.0000 | 551761 |  | 0.0 (13918); -nan (11750); 1.0 (2557); 0.3333333333333333 (2538); 0.25 (1766) | Percentage of population aged 25+ with Some College or Associate's degree. |
| `pct_ba_25p` | `DOUBLE` | 0.0000 | 544390 |  | 0.0 (48312); -nan (11750); 0.125 (1100); 0.1111111111111111 (1008); 0.16666666666666666 (984) | Percentage of population aged 25+ with Bachelor's degree. |
| `pct_ma_plus_25p` | `DOUBLE` | 0.0000 | 506098 |  | 0.0 (93456); -nan (11750); 0.05555555555555555 (662); 0.058823529411764705 (643); 0.06666666666666667 (641) | Percentage of population aged 25+ with Master's or higher degree. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_population_wide.sql:92:FROM metro_deep_dive.silver.education_kpi `
   - `scripts/etl/silver/acs_edu_silver.R:155:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="education_kpi"),`

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
