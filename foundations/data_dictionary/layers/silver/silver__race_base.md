# Data Dictionary: silver.race_base

## Overview
- **Table**: `silver.race_base`
- **Purpose**: Silver race table (`base` type).
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
| `pop_total_b03002E` | `DOUBLE` | 0.0000 | 80593 | min 0, max 334922500 | 0.0 (11017); 74.0 (610); 115.0 (607); 61.0 (603); 64.0 (602) | ACS 2024 Hispanic or Latino Origin by Race [B03002_001]: Total: (estimate). |
| `white_nonhispE` | `DOUBLE` | 0.0000 | 60752 | min 0, max 197362670 | 0.0 (21708); 10.0 (945); 9.0 (934); 14.0 (914); 16.0 (914) | ACS 2024 Hispanic or Latino Origin by Race [B03002_003]: Total:, Not Hispanic or Latino:, White alone (estimate). |
| `black_nonhispE` | `DOUBLE` | 0.0000 | 29524 | min 0, max 40196302 | 0.0 (326848); 2.0 (13278); 1.0 (11953); 3.0 (11022); 4.0 (10083) | ACS 2024 Hispanic or Latino Origin by Race [B03002_004]: Total:, Not Hispanic or Latino:, Black or African American alone (estimate). |
| `amind_nonhispE` | `DOUBLE` | 0.0000 | 6670 | min 0, max 2160378 | 0.0 (561086); 2.0 (15941); 1.0 (15412); 3.0 (15052); 4.0 (14321) | ACS 2024 Hispanic or Latino Origin by Race [B03002_005]: Total:, Not Hispanic or Latino:, American Indian and Alaska Native alone (estimate). |
| `asian_nonhispE` | `DOUBLE` | 0.0000 | 19094 | min 0, max 19678814 | 0.0 (436671); 2.0 (13764); 3.0 (12663); 4.0 (11921); 1.0 (11610) | ACS 2024 Hispanic or Latino Origin by Race [B03002_006]: Total:, Not Hispanic or Latino:, Asian alone (estimate). |
| `pacisl_nonhispE` | `DOUBLE` | 0.0000 | 3737 | min 0, max 566450 | 0.0 (862772); 5.0 (4944); 6.0 (4887); 4.0 (4828); 3.0 (4814) | ACS 2024 Hispanic or Latino Origin by Race [B03002_007]: Total:, Not Hispanic or Latino:, Native Hawaiian and Other Pacific Islander alone (estimate). |
| `other_nonhispE` | `DOUBLE` | 0.0000 | 4723 | min 0, max 1868910 | 0.0 (715624); 3.0 (7067); 2.0 (6764); 8.0 (6750); 4.0 (6629) | ACS 2024 Hispanic or Latino Origin by Race [B03002_008]: Total:, Not Hispanic or Latino:, Some other race alone (estimate). |
| `two_plus_nonhispE` | `DOUBLE` | 0.0000 | 12942 | min 0, max 14240018 | 0.0 (228417); 2.0 (15031); 3.0 (14014); 4.0 (13263); 5.0 (12426) | ACS 2024 Hispanic or Latino Origin by Race [B03002_009]: Total:, Not Hispanic or Latino:, Two or more races: (estimate). |
| `hispanic_anyE` | `DOUBLE` | 0.0000 | 36687 | min 0, max 64759370 | 0.0 (190506); 2.0 (10753); 3.0 (10064); 4.0 (9394); 5.0 (8510) | ACS 2024 Hispanic or Latino Origin by Race [B03002_012]: Total:, Hispanic or Latino: (estimate). |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_race_silver.R:148:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="race_base"),`

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
