# Data Dictionary: silver.transport_kpi

## Overview
- **Table**: `silver.transport_kpi`
- **Purpose**: Silver transport table (`kpi` type).
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
| `commute_workers_total` | `DOUBLE` | 0.0069 | 51619 | min 0, max 159114090 | 0.0 (18087); 27.0 (1423); 41.0 (1393); 46.0 (1390); 28.0 (1377) | Total number of workers in the Commute universe. |
| `commute_drove_alone` | `DOUBLE` | 0.0069 | 44049 | min 0, max 116584510 | 0.0 (23593); 14.0 (1778); 15.0 (1712); 12.0 (1699); 18.0 (1699) | Population count of commuters that drove alone to work. Total drove alone. |
| `commute_carpool` | `DOUBLE` | 0.0069 | 15490 | min 0, max 14032099 | 0.0 (108075); 4.0 (9485); 6.0 (9410); 8.0 (9301); 2.0 (9229) | Population count of commuters that carpooled to work. Total carpool. |
| `commute_public_trans` | `DOUBLE` | 0.0069 | 11105 | min 0, max 7641160 | 0.0 (581989); 2.0 (16192); 3.0 (13915); 1.0 (12467); 4.0 (11431) | Population count of commuters that took public transportation to work. Total public transportation. |
| `commute_taxicab` | `DOUBLE` | 0.0069 | 2532 | min 0, max 415878 | 0.0 (881462); 9.0 (4225); 8.0 (4087); 10.0 (3874); 11.0 (3650) | Population count of commuters that used taxi or ride-hailing services to work. Total taxi or ride-hailing services. |
| `commute_motorcycle` | `DOUBLE` | 0.0069 | 2493 | min 0, max 316992 | 0.0 (777305); 2.0 (10391); 3.0 (10266); 9.0 (8717); 8.0 (8614) | Population count of commuters that rode a motorcycle to work. Total motorcycle. |
| `commute_bicycle` | `DOUBLE` | 0.0069 | 4494 | min 0, max 877995 | 0.0 (728764); 2.0 (10125); 3.0 (9834); 4.0 (8276); 7.0 (7976) | Population count of commuters that rode a bicycle to work. Total bicycle. |
| `commute_walked` | `DOUBLE` | 0.0069 | 9157 | min 0, max 4073891 | 0.0 (301804); 2.0 (21683); 3.0 (18938); 4.0 (17386); 5.0 (16448) | Population count of commuters that walked to work. Total walked. |
| `commute_other` | `DOUBLE` | 0.0069 | 5551 | min 0, max 1807557 | 0.0 (452073); 2.0 (22666); 3.0 (20297); 4.0 (17403); 5.0 (15488) | Population count of commuters that used other means to work. Total other means. |
| `commute_worked_home` | `DOUBLE` | 0.0069 | 13990 | min 0, max 24042489 | 0.0 (156507); 2.0 (16059); 3.0 (14367); 4.0 (14162); 5.0 (13102) | Population count of commuters that worked from home. Total worked from home. |
| `pct_commute_drive_alone` | `DOUBLE` | 0.0069 | 473061 |  | 1.0 (37150); -nan (18087); 0.0 (5506); 0.8 (2053); 0.75 (2034) | Percent of commuters that drove alone to work. Share / percentage; denominator is commute_workers_total. |
| `pct_commute_carpool` | `DOUBLE` | 0.0069 | 418584 |  | 0.0 (89988); -nan (18087); 0.1111111111111111 (1369); 0.125 (1345); 0.09090909090909091 (1317) | Percent of commuters that carpooled to work. Share / percentage; denominator is commute_workers_total. |
| `pct_commute_transit` | `DOUBLE` | 0.0069 | 266533 |  | 0.0 (563902); -nan (18087); 0.019230769230769232 (134); 0.02127659574468085 (132); 0.02 (128) | Percent of commuters that took public transportation to work. Share / percentage; denominator is commute_workers_total. |
| `pct_commute_walk` | `DOUBLE` | 0.0069 | 323493 |  | 0.0 (283717); -nan (18087); 1.0 (730); 0.047619047619047616 (548); 0.0625 (546) | Percent of commuters that walked to work. Share / percentage; denominator is commute_workers_total. |
| `pct_commute_wfh` | `DOUBLE` | 0.0069 | 406748 |  | 0.0 (138420); -nan (18087); 1.0 (1170); 0.08333333333333333 (856); 0.058823529411764705 (855) | Percent of commuters that worked from home. Share / percentage; denominator is commute_workers_total. |
| `veh_total_hh` | `DOUBLE` | 0.0069 | 45115 | min 0, max 129227500 | 0.0 (15641); 33.0 (1475); 32.0 (1463); 39.0 (1453); 43.0 (1445) | Total Count of Vehicle Households. Base for Vehicle KPIs. |
| `veh_0` | `DOUBLE` | 0.0069 | 14095 | min 0, max 10793323 | 0.0 (167297); 2.0 (19638); 3.0 (16005); 4.0 (15406); 5.0 (14564) | Total Household count with no vehicles available. |
| `veh_1` | `DOUBLE` | 0.0069 | 25800 | min 0, max 42801892 | 0.0 (40851); 9.0 (4964); 10.0 (4829); 11.0 (4799); 8.0 (4714) | Total Household count with 1 vehicle available. |
| `veh_2` | `DOUBLE` | 0.0069 | 27085 | min 0, max 47334152 | 0.0 (33163); 9.0 (3756); 10.0 (3727); 11.0 (3590); 8.0 (3579) | Total Household count with 2 vehicles available. |
| `veh_3` | `DOUBLE` | 0.0069 | 17156 | min 0, max 18773476 | 0.0 (59849); 9.0 (7170); 10.0 (7011); 8.0 (7004); 11.0 (6866) | Total Household count with 3 vehicles available. |
| `veh_4_plus` | `DOUBLE` | 0.0069 | 11828 | min 0, max 9524653 | 0.0 (108276); 6.0 (11947); 8.0 (11838); 9.0 (11702); 7.0 (11666) | Total Household count with 4 or more vehicles available. |
| `pct_hh_0_vehicles` | `DOUBLE` | 0.0069 | 378975 |  | 0.0 (151656); -nan (15641); 1.0 (1097); 0.06666666666666667 (853); 0.05555555555555555 (843) | Percent of Households with no vehicles available. Share / percentage; denominator is veh_total_hh. |
| `pct_hh_1_vehicles` | `DOUBLE` | 0.0069 | 469272 |  | 0.0 (25210); -nan (15641); 1.0 (4039); 0.3333333333333333 (3209); 0.25 (2725) | Percent of Households with 1 vehicle available. Share / percentage; denominator is veh_total_hh. |
| `pct_hh_2_vehicles` | `DOUBLE` | 0.0069 | 452285 |  | 0.0 (17522); -nan (15641); 1.0 (5620); 0.3333333333333333 (3547); 0.5 (3329) | Percent of Households with 2 vehicles available. Share / percentage; denominator is veh_total_hh. |
| `pct_hh_3_vehicles` | `DOUBLE` | 0.0069 | 428986 |  | 0.0 (44208); -nan (15641); 0.2 (2358); 0.25 (2274); 0.16666666666666666 (2163) | Percent of Households with 3 vehicles available. Share / percentage; denominator is veh_total_hh. |
| `pct_hh_4p_vehicles` | `DOUBLE` | 0.0069 | 388725 |  | 0.0 (92635); -nan (15641); 0.1111111111111111 (1411); 0.1 (1378); 0.14285714285714285 (1375) | Percent of Households with 4 or more vehicles available. Share / percentage; denominator is veh_total_hh. |
| `total_travel_time` | `DOUBLE` | 7.4595 | 127607 | min 0, max 3901729900 | NULL (76156); 2455.0 (236); 2725.0 (228); 1940.0 (225); 1980.0 (225) | Aggregate travel time to work (in minutes):. |
| `mean_travel_time` | `DOUBLE` | 7.4595 | 705675 |  | NULL (76156); 20.0 (729); 25.0 (720); 30.0 (457); 15.0 (451) | Aggregate travel time to work (in minutes) divided by total commuters (commute_workers_total). |
## Data Quality Notes
- Columns with non-zero null rates: commute_workers_total=0.0069%, commute_drove_alone=0.0069%, commute_carpool=0.0069%, commute_public_trans=0.0069%, commute_taxicab=0.0069%, commute_motorcycle=0.0069%, commute_bicycle=0.0069%, commute_walked=0.0069%, commute_other=0.0069%, commute_worked_home=0.0069% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_transport_silver.R:189:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="transport_kpi"),`
2. **Downstream usage (examples)**:
   - `notebooks/retail_opportunity_finder/tract_features.sql:103:  FROM metro_deep_dive.silver.transport_kpi`
   - `notebooks/retail_opportunity_finder/cbsa_features.sql:72:  FROM metro_deep_dive.silver.transport_kpi`

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
