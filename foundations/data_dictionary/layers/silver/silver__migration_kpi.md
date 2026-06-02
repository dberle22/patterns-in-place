# Data Dictionary: silver.migration_kpi

## Overview
- **Table**: `silver.migration_kpi`
- **Purpose**: Silver migration table (`kpi` type).
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
| `mig_total` | `DOUBLE` | 0.6159 | 79751 | min 0, max 331439980 | 0.0 (11125); NULL (6288); 69.0 (615); 113.0 (611); 64.0 (604) | Total Population, base for Migration Metrics from ACS. |
| `mig_same_house` | `DOUBLE` | 0.6159 | 72606 | min 0, max 290692800 | 0.0 (11810); NULL (6288); 108.0 (699); 69.0 (699); 96.0 (665) | Population count in same house as 1 year ago. Base for pct_same_house metric. |
| `mig_moved_same_cnty` | `DOUBLE` | 0.6159 | 21356 | min 0, max 28002833 | 0.0 (132171); 2.0 (8813); 4.0 (8072); 3.0 (7840); 5.0 (7477) | Population count that moved within same county. Base for pct_moved_same_cnty metric. |
| `mig_moved_same_st` | `DOUBLE` | 0.6159 | 14355 | min 0, max 10554284 | 0.0 (178966); 2.0 (12778); 4.0 (11241); 3.0 (11029); 5.0 (10208) | Population count that moved from different county within same state. Base for pct_moved_same_st metric. |
| `mig_moved_diff_st` | `DOUBLE` | 0.6159 | 12533 | min 0, max 7641427 | 0.0 (258889); 2.0 (16765); 3.0 (14518); 4.0 (14179); 5.0 (12088) | Population count that moved from different state. Base for pct_moved_diff_st metric. |
| `mig_moved_abroad` | `DOUBLE` | 0.6159 | 6488 | min 0, max 2087731 | 0.0 (569337); 2.0 (15318); 3.0 (13625); 4.0 (11647); 1.0 (10827) | Population count that moved from abroad. Base for pct_moved_abroad metric. |
| `pct_same_house` | `DOUBLE` | 0.6159 | 589475 |  | 1.0 (66372); -nan (11125); NULL (6288); 0.0 (685); 0.875 (632) | Percent of population in same house as 1 year ago. Share / percentage; denominator is mig_total. (from silver.kpi_dictionary). |
| `pct_moved_same_cnty` | `DOUBLE` | 0.6159 | 542541 |  | 0.0 (121046); -nan (11125); NULL (6288); 0.05263157894736842 (428); 0.0625 (415) | Percent of population that moved within same county. Share / percentage; denominator is mig_total. (from silver.kpi_dictionary). |
| `pct_moved_same_st` | `DOUBLE` | 0.6159 | 492089 |  | 0.0 (167841); -nan (11125); NULL (6288); 0.045454545454545456 (324); 0.02857142857142857 (315) | Percent of population that moved from different county within same state. Share / percentage; denominator is mig_total. (from silver.kpi_dictionary). |
| `pct_moved_diff_st` | `DOUBLE` | 0.6159 | 450141 |  | 0.0 (247764); -nan (11125); NULL (6288); 0.021739130434782608 (219); 0.02702702702702703 (213) | Percent of population that moved from different state. Share / percentage; denominator is mig_total. (from silver.kpi_dictionary). |
| `pct_moved_abroad` | `DOUBLE` | 0.6159 | 295986 |  | 0.0 (558212); -nan (11125); NULL (6288); 0.005952380952380952 (74); 0.005235602094240838 (66) | Percent of population that moved from abroad. Share / percentage; denominator is mig_total. (from silver.kpi_dictionary). |
| `pop_nativity_total` | `DOUBLE` | 0.0000 | 80593 | min 0, max 334922500 | 0.0 (11017); 74.0 (610); 115.0 (607); 61.0 (603); 64.0 (602) | Total:. |
| `pop_native` | `DOUBLE` | 0.0000 | 73407 | min 0, max 287573420 | 0.0 (11252); 64.0 (638); 130.0 (614); 101.0 (609); 115.0 (604) | Total population count that is native (born in the US). |
| `pop_foreign_born` | `DOUBLE` | 0.0000 | 29590 | min 0, max 47349078 | 0.0 (196448); 2.0 (17844); 3.0 (14553); 4.0 (13138); 1.0 (11853) | Total population count that is foreign-born. |
| `pop_foreign_born_citizen` | `DOUBLE` | 0.0000 | 20135 | min 0, max 24674406 | 0.0 (267024); 2.0 (20318); 3.0 (17064); 4.0 (14732); 1.0 (13381) | Total population count that is foreign-born and a naturalized U.S. citizen. |
| `pop_foreign_born_noncitizen` | `DOUBLE` | 0.0000 | 20916 | min 0, max 22674672 | 0.0 (296169); 2.0 (17590); 3.0 (15160); 4.0 (13081); 1.0 (11819) | Total population count that is foreign-born and not a naturalized U.S. citizen. |
| `pct_native` | `DOUBLE` | 0.0000 | 532833 |  | 1.0 (185431); -nan (11017); 0.96 (238); 0.9736842105263158 (236); 0.975609756097561 (236) | Percent of population that is native. Share / percentage; denominator is pop_nativity_total. (from silver.kpi_dictionary). |
| `pct_foreign_born` | `DOUBLE` | 0.0000 | 532833 |  | 0.0 (185431); -nan (11017); 0.04 (238); 0.024390243902439025 (236); 0.02631578947368421 (236) | Percent of population that is foreign-born. Share / percentage; denominator is pop_nativity_total. (from silver.kpi_dictionary). |
| `pct_non_citizen` | `DOUBLE` | 0.0000 | 476901 |  | 0.0 (285152); -nan (11017); 0.023809523809523808 (160); 0.04 (152); 0.016666666666666666 (147) | Percent of population that is not a naturalized U.S. citizen. Share / percentage; denominator is pop_nativity_total. (from silver.kpi_dictionary). |
## Data Quality Notes
- Columns with non-zero null rates: mig_total=0.6159%, mig_same_house=0.6159%, mig_moved_same_cnty=0.6159%, mig_moved_same_st=0.6159%, mig_moved_diff_st=0.6159%, mig_moved_abroad=0.6159%, pct_same_house=0.6159%, pct_moved_same_cnty=0.6159%, pct_moved_same_st=0.6159%, pct_moved_diff_st=0.6159% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_migration_silver.R:156:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="migration_kpi"),`

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
