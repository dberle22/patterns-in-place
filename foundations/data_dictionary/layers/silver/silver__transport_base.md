# Data Dictionary: silver.transport_base

## Overview
- **Table**: `silver.transport_base`
- **Purpose**: Silver transport table (`base` type).
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
| `commute_workers_totalE` | `DOUBLE` | 0.0069 | 51619 | min 0, max 159114090 | 0.0 (18087); 27.0 (1423); 41.0 (1393); 46.0 (1390); 28.0 (1377) | ACS 2024 Means of Transportation to Work [B08301_001]: Total: (estimate). |
| `commute_car_truck_vanE` | `DOUBLE` | 0.0069 | 46993 | min 0, max 130348040 | 0.0 (21870); 14.0 (1603); 27.0 (1575); 21.0 (1550); 12.0 (1539) | ACS 2024 Means of Transportation to Work [B08301_002]: Total:, Car, truck, or van: (estimate). |
| `commute_drove_aloneE` | `DOUBLE` | 0.0069 | 44049 | min 0, max 116584510 | 0.0 (23593); 14.0 (1778); 15.0 (1712); 12.0 (1699); 18.0 (1699) | ACS 2024 Means of Transportation to Work [B08301_003]: Total:, Car, truck, or van:, Drove alone (estimate). |
| `commute_carpoolE` | `DOUBLE` | 0.0069 | 15490 | min 0, max 14032099 | 0.0 (108075); 4.0 (9485); 6.0 (9410); 8.0 (9301); 2.0 (9229) | ACS 2024 Means of Transportation to Work [B08301_004]: Total:, Car, truck, or van:, Carpooled: (estimate). |
| `commute_public_transE` | `DOUBLE` | 0.0069 | 11105 | min 0, max 7641160 | 0.0 (581989); 2.0 (16192); 3.0 (13915); 1.0 (12467); 4.0 (11431) | ACS 2024 Means of Transportation to Work [B08301_010]: Total:, Public transportation: (estimate). |
| `commute_taxicabE` | `DOUBLE` | 0.0069 | 2532 | min 0, max 415878 | 0.0 (881462); 9.0 (4225); 8.0 (4087); 10.0 (3874); 11.0 (3650) | ACS 2024 Means of Transportation to Work [B08301_016]: Total:, Taxi or ride-hailing services (estimate). |
| `commute_motorcycleE` | `DOUBLE` | 0.0069 | 2493 | min 0, max 316992 | 0.0 (777305); 2.0 (10391); 3.0 (10266); 9.0 (8717); 8.0 (8614) | ACS 2024 Means of Transportation to Work [B08301_017]: Total:, Motorcycle (estimate). |
| `commute_bicycleE` | `DOUBLE` | 0.0069 | 4494 | min 0, max 877995 | 0.0 (728764); 2.0 (10125); 3.0 (9834); 4.0 (8276); 7.0 (7976) | ACS 2024 Means of Transportation to Work [B08301_018]: Total:, Bicycle (estimate). |
| `commute_walkedE` | `DOUBLE` | 0.0069 | 9157 | min 0, max 4073891 | 0.0 (301804); 2.0 (21683); 3.0 (18938); 4.0 (17386); 5.0 (16448) | ACS 2024 Means of Transportation to Work [B08301_019]: Total:, Walked (estimate). |
| `commute_otherE` | `DOUBLE` | 0.0069 | 5551 | min 0, max 1807557 | 0.0 (452073); 2.0 (22666); 3.0 (20297); 4.0 (17403); 5.0 (15488) | ACS 2024 Means of Transportation to Work [B08301_020]: Total:, Other means (estimate). |
| `commute_worked_homeE` | `DOUBLE` | 0.0069 | 13990 | min 0, max 24042489 | 0.0 (156507); 2.0 (16059); 3.0 (14367); 4.0 (14162); 5.0 (13102) | ACS 2024 Means of Transportation to Work [B08301_021]: Total:, Worked from home (estimate). |
| `veh_total_hhE` | `DOUBLE` | 0.0069 | 45115 | min 0, max 129227500 | 0.0 (15641); 33.0 (1475); 32.0 (1463); 39.0 (1453); 43.0 (1445) | ACS 2024 Household Size by Vehicles Available [B08201_001]: Total: (estimate). |
| `veh_0E` | `DOUBLE` | 0.0069 | 14095 | min 0, max 10793323 | 0.0 (167297); 2.0 (19638); 3.0 (16005); 4.0 (15406); 5.0 (14564) | ACS 2024 Household Size by Vehicles Available [B08201_002]: Total:, No vehicle available (estimate). |
| `veh_1E` | `DOUBLE` | 0.0069 | 25800 | min 0, max 42801892 | 0.0 (40851); 9.0 (4964); 10.0 (4829); 11.0 (4799); 8.0 (4714) | ACS 2024 Household Size by Vehicles Available [B08201_003]: Total:, 1 vehicle available (estimate). |
| `veh_2E` | `DOUBLE` | 0.0069 | 27085 | min 0, max 47334152 | 0.0 (33163); 9.0 (3756); 10.0 (3727); 11.0 (3590); 8.0 (3579) | ACS 2024 Household Size by Vehicles Available [B08201_004]: Total:, 2 vehicles available (estimate). |
| `veh_3E` | `DOUBLE` | 0.0069 | 17156 | min 0, max 18773476 | 0.0 (59849); 9.0 (7170); 10.0 (7011); 8.0 (7004); 11.0 (6866) | ACS 2024 Household Size by Vehicles Available [B08201_005]: Total:, 3 vehicles available (estimate). |
| `veh_4_plusE` | `DOUBLE` | 0.0069 | 11828 | min 0, max 9524653 | 0.0 (108276); 6.0 (11947); 8.0 (11838); 9.0 (11702); 7.0 (11666) | ACS 2024 Household Size by Vehicles Available [B08201_006]: Total:, 4 or more vehicles available (estimate). |
| `total_travel_timeE` | `DOUBLE` | 7.4595 | 127607 | min 0, max 3901729900 | NULL (76156); 2455.0 (236); 2725.0 (228); 1940.0 (225); 1980.0 (225) | ACS 2024 Aggregate Travel Time to Work (in Minutes) of Workers by Sex [B08013_001]: Aggregate travel time to work (in minutes): (estimate). |
## Data Quality Notes
- Columns with non-zero null rates: commute_workers_totalE=0.0069%, commute_car_truck_vanE=0.0069%, commute_drove_aloneE=0.0069%, commute_carpoolE=0.0069%, commute_public_transE=0.0069%, commute_taxicabE=0.0069%, commute_motorcycleE=0.0069%, commute_bicycleE=0.0069%, commute_walkedE=0.0069%, commute_otherE=0.0069% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_transport_silver.R:186:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="transport_base"),`

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
