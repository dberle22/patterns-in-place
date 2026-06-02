# Data Dictionary: silver.migration_base

## Overview
- **Table**: `silver.migration_base`
- **Purpose**: Silver migration table (`base` type).
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
| `mig_totalE` | `DOUBLE` | 0.6159 | 79751 | min 0, max 331439980 | 0.0 (11125); NULL (6288); 69.0 (615); 113.0 (611); 64.0 (604) | ACS 2024 Geographical Mobility in the Past Year by Sex for Current Residence in the United States [B07003_001]: Total: (estimate). |
| `mig_same_houseE` | `DOUBLE` | 0.6159 | 72606 | min 0, max 290692800 | 0.0 (11810); NULL (6288); 108.0 (699); 69.0 (699); 96.0 (665) | ACS 2024 Geographical Mobility in the Past Year by Sex for Current Residence in the United States [B07003_004]: Total:, Same house 1 year ago: (estimate). |
| `mig_moved_same_cntyE` | `DOUBLE` | 0.6159 | 21356 | min 0, max 28002833 | 0.0 (132171); 2.0 (8813); 4.0 (8072); 3.0 (7840); 5.0 (7477) | ACS 2024 Geographical Mobility in the Past Year by Sex for Current Residence in the United States [B07003_007]: Total:, Moved within same county: (estimate). |
| `mig_moved_same_stE` | `DOUBLE` | 0.6159 | 14355 | min 0, max 10554284 | 0.0 (178966); 2.0 (12778); 4.0 (11241); 3.0 (11029); 5.0 (10208) | ACS 2024 Geographical Mobility in the Past Year by Sex for Current Residence in the United States [B07003_010]: Total:, Moved from different county within same state: (estimate). |
| `mig_moved_diff_stE` | `DOUBLE` | 0.6159 | 12533 | min 0, max 7641427 | 0.0 (258889); 2.0 (16765); 3.0 (14518); 4.0 (14179); 5.0 (12088) | ACS 2024 Geographical Mobility in the Past Year by Sex for Current Residence in the United States [B07003_013]: Total:, Moved from different state: (estimate). |
| `mig_moved_abroadE` | `DOUBLE` | 0.6159 | 6488 | min 0, max 2087731 | 0.0 (569337); 2.0 (15318); 3.0 (13625); 4.0 (11647); 1.0 (10827) | ACS 2024 Geographical Mobility in the Past Year by Sex for Current Residence in the United States [B07003_016]: Total:, Moved from abroad: (estimate). |
| `pop_nativity_totalE` | `DOUBLE` | 0.0000 | 80593 | min 0, max 334922500 | 0.0 (11017); 74.0 (610); 115.0 (607); 61.0 (603); 64.0 (602) | ACS 2024 Place of Birth by Nativity and Citizenship Status [B05002_001]: Total: (estimate). |
| `pop_nativeE` | `DOUBLE` | 0.0000 | 73407 | min 0, max 287573420 | 0.0 (11252); 64.0 (638); 130.0 (614); 101.0 (609); 115.0 (604) | ACS 2024 Place of Birth by Nativity and Citizenship Status [B05002_002]: Total:, Native: (estimate). |
| `pop_foreign_bornE` | `DOUBLE` | 0.0000 | 29590 | min 0, max 47349078 | 0.0 (196448); 2.0 (17844); 3.0 (14553); 4.0 (13138); 1.0 (11853) | ACS 2024 Place of Birth by Nativity and Citizenship Status [B05002_013]: Total:, Foreign-born: (estimate). |
| `pop_foreign_born_citizenE` | `DOUBLE` | 0.0000 | 20135 | min 0, max 24674406 | 0.0 (267024); 2.0 (20318); 3.0 (17064); 4.0 (14732); 1.0 (13381) | ACS 2024 Place of Birth by Nativity and Citizenship Status [B05002_014]: Total:, Foreign-born:, Naturalized U.S. citizen (estimate). |
## Data Quality Notes
- Columns with non-zero null rates: mig_totalE=0.6159%, mig_same_houseE=0.6159%, mig_moved_same_cntyE=0.6159%, mig_moved_same_stE=0.6159%, mig_moved_diff_stE=0.6159%, mig_moved_abroadE=0.6159%
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_migration_silver.R:153:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="migration_base"),`

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
