# Data Dictionary: silver.housing_kpi

## Overview
- **Table**: `silver.housing_kpi`
- **Purpose**: Silver housing table (`kpi` type).
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
| `hu_total` | `DOUBLE` | 0.0000 | 48279 | min 0, max 143775360 | 0.0 (12518); 46.0 (1194); 50.0 (1174); 71.0 (1166); 52.0 (1159) | Total Housing Units. |
| `occ_total` | `DOUBLE` | 0.0000 | 48279 | min 0, max 143775360 | 0.0 (12518); 46.0 (1194); 50.0 (1174); 71.0 (1166); 52.0 (1159) | Total Housing Units used in Occupied Metrics. |
| `occ_occupied` | `DOUBLE` | 0.0000 | 45115 | min 0, max 129227500 | 0.0 (15641); 33.0 (1475); 32.0 (1463); 39.0 (1453); 43.0 (1445) | Total Housing Units Occupied. |
| `occ_vacant` | `DOUBLE` | 0.0000 | 17020 | min 0, max 16672938 | 0.0 (67178); 9.0 (6089); 14.0 (5988); 13.0 (5927); 15.0 (5907) | Total Housing Units Vacant. |
| `vacancy_rate` | `DOUBLE` | 0.0000 | 489853 |  | 0.0 (54660); -nan (12518); 1.0 (3123); 0.2 (1392); 0.25 (1260) | Housing Vacancy Rates Derived from ACS counts. (from silver.kpi_dictionary). |
| `occupancy_rate` | `DOUBLE` | 0.0000 | 489853 |  | 1.0 (54660); -nan (12518); 0.0 (3123); 0.8 (1392); 0.75 (1260) | Housing Occupancy Rate derived from ACS counts. (from silver.kpi_dictionary). |
| `tenure_total` | `DOUBLE` | 0.0000 | 45115 | min 0, max 129227500 | 0.0 (15641); 33.0 (1475); 32.0 (1463); 39.0 (1453); 43.0 (1445) | Total Units used in Tenure as base. |
| `owner_occupied` | `DOUBLE` | 0.0000 | 35573 | min 0, max 84210142 | 0.0 (22036); 25.0 (1920); 26.0 (1879); 27.0 (1854); 17.0 (1851) | Total Housing Units Owner occupied. |
| `renter_occupied` | `DOUBLE` | 0.0000 | 27966 | min 0, max 45017354 | 0.0 (59306); 9.0 (6033); 8.0 (5878); 10.0 (5806); 7.0 (5801) | Total Housing Units Renter occupied. |
| `owner_occ_rate` | `DOUBLE` | 0.0000 | 491434 |  | 1.0 (43665); -nan (15641); 0.0 (6395); 0.75 (2069); 0.8 (1924) | Rate of Owner Occupied Housing Units derived from ACS counts. (from silver.kpi_dictionary). |
| `renter_occ_rate` | `DOUBLE` | 0.0000 | 491434 |  | 0.0 (43665); -nan (15641); 1.0 (6395); 0.25 (2069); 0.2 (1924) | Rate of Renter Occupied Housing Units derived from ACS counts. (from silver.kpi_dictionary). |
| `median_gross_rent` | `DOUBLE` | 17.7859 | 7772 | min 99, max 3501 | NULL (181582); 675.0 (3799); 625.0 (3687); 725.0 (3579); 775.0 (3366) | Median gross rent (monthly dollar figures, multiply by 12 for yearly rent). |
| `median_home_value` | `DOUBLE` | 6.8108 | 18205 | min 9999, max 2000001 | NULL (69534); 85000.0 (1928); 112500.0 (1924); 75000.0 (1878); 95000.0 (1737) | Median Home Value (dollars). |
| `median_owner_costs_mortgage` | `DOUBLE` | 10.0527 | 8122 | min 99, max 4001 | NULL (102631); 4001.0 (9584); 1125.0 (4185); 950.0 (4175); 850.0 (3548) | Median selected monthly owner costs (dollars) --, Housing units with a mortgage (dollars). |
| `median_owner_costs_no_mortgage` | `DOUBLE` | 8.1629 | 5842 | min 99, max 1501 | NULL (83338); 1501.0 (8670); 1001.0 (6039); 375.0 (5993); 450.0 (5319) | Median selected monthly owner costs (dollars) --, Housing units without a mortgage (dollars). |
| `rent_burden_total` | `DOUBLE` | 0.0069 | 27966 | min 0, max 45017354 | 0.0 (59283); 9.0 (6033); 8.0 (5877); 10.0 (5804); 7.0 (5801) | Total base for Rent Burden metrics. |
| `rent_burden_30plus` | `DOUBLE` | 0.0069 | 19315 | min 0, max 21422415 | 0.0 (142921); 2.0 (12978); 4.0 (11276); 3.0 (11044); 5.0 (10797) | Population count for rent burden 30plus, meaning renter spends 30% or more of income on rent. |
| `rent_burden_50plus` | `DOUBLE` | 0.0069 | 14027 | min 0, max 10852194 | 0.0 (217364); 2.0 (18637); 3.0 (15279); 4.0 (14894); 5.0 (13847) | Population count for rent burden 50plus, meaning renter spends 50% or more of income on rent. |
| `pct_rent_burden_30plus` | `DOUBLE` | 7.7844 | 265882 | min 0, max 1 | NULL (79473); 0.0 (63518); 1.0 (33514); 0.5 (9481); 0.3333333333333333 (6279) | Share of renters spending 30% or more of income on rent; denominator defined in KPI logic. (from silver.kpi_dictionary). |
| `pct_rent_burden_50plus` | `DOUBLE` | 7.7844 | 251044 | min 0, max 1 | 0.0 (137961); NULL (79473); 1.0 (12922); 0.3333333333333333 (4686); 0.25 (4453) | Share of renters spending 50% or more of income on rent; denominator defined in KPI logic. (from silver.kpi_dictionary). |
| `struct_total` | `DOUBLE` | 0.0000 | 48279 | min 0, max 143775360 | 0.0 (12518); 46.0 (1194); 50.0 (1174); 71.0 (1166); 52.0 (1159) | Total number of structures, used as base in structure metrics. |
| `struct_1_unit` | `DOUBLE` | 0.0000 | 39239 | min 0, max 97030544 | 0.0 (16152); 39.0 (1502); 43.0 (1487); 49.0 (1472); 48.0 (1465) | Total count for 1 unit structures, including detached and attached. |
| `struct_sf_det` | `DOUBLE` | 0.0000 | 37660 | min 0, max 88075458 | 0.0 (17114); 39.0 (1548); 48.0 (1530); 43.0 (1518); 45.0 (1516) | Total count for single family detached structures. |
| `struct_small_mf` | `DOUBLE` | 0.0000 | 14790 | min 0, max 11031346 | 0.0 (283163); 2.0 (11365); 4.0 (10206); 5.0 (9739); 3.0 (9608) | Total count for small multifamily structures, defined as 2-4 units. |
| `struct_mid_mf` | `DOUBLE` | 0.0000 | 15751 | min 0, max 12625154 | 0.0 (386411); 2.0 (8300); 3.0 (8228); 4.0 (8195); 5.0 (8077) | Total count for mid-size multifamily structures, defined as 5-19 units. |
| `struct_large_mf` | `DOUBLE` | 0.0000 | 16162 | min 0, max 14859547 | 0.0 (508544); 3.0 (8680); 2.0 (8316); 4.0 (7240); 6.0 (6757) | Total count for large multifamily structures, defined as 20 or more units. |
| `struct_mobile` | `DOUBLE` | 0.0000 | 11835 | min 0, max 8583843 | 0.0 (204491); 9.0 (11188); 8.0 (11171); 10.0 (10724); 7.0 (10578) | Total count of mobile homes or trailers. |
| `pct_struct_1_unit` | `DOUBLE` | 0.0000 | 525556 |  | 1.0 (55027); -nan (12518); 0.0 (3634); 0.75 (1363); 0.6666666666666666 (1272) | Share of 1 unit structures out of total structures. |
| `pct_struct_sf_det` | `DOUBLE` | 0.0000 | 534108 |  | 1.0 (44541); -nan (12518); 0.0 (4596); 0.75 (1412); 0.8 (1371) | Share of 1 unit dettached structures out of total structures. |
| `pct_struct_small_mf` | `DOUBLE` | 0.0000 | 398117 |  | 0.0 (270645); -nan (12518); 0.058823529411764705 (451); 0.09090909090909091 (418); 0.05263157894736842 (408) | Share of small multifamily structures out of total structures. |
| `pct_struct_mid_mf` | `DOUBLE` | 0.0000 | 386198 |  | 0.0 (373893); -nan (12518); 1.0 (241); 0.047619047619047616 (237); 0.0625 (235) | Share of mid-size multifamily structures out of total structures. |
| `pct_struct_large_mf` | `DOUBLE` | 0.0000 | 344904 |  | 0.0 (496026); -nan (12518); 1.0 (419); 0.01818181818181818 (109); 0.034482758620689655 (105) | Share of large multifamily structures out of total structures. |
| `pct_struct_mobile` | `DOUBLE` | 0.0000 | 421125 |  | 0.0 (191973); -nan (12518); 1.0 (1726); 0.2 (991); 0.3333333333333333 (927) | Share of mobile homes or trailers out of total structures. |
## Data Quality Notes
- Columns with non-zero null rates: median_gross_rent=17.7859%, median_home_value=6.8108%, median_owner_costs_mortgage=10.0527%, median_owner_costs_no_mortgage=8.1629%, rent_burden_total=0.0069%, rent_burden_30plus=0.0069%, rent_burden_50plus=0.0069%, pct_rent_burden_30plus=7.7844%, pct_rent_burden_50plus=7.7844%
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_housing_core.sql:43:from metro_deep_dive.silver.housing_kpi `
   - `scripts/etl/silver/acs_housing_silver.R:213:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="housing_kpi"),`
2. **Downstream usage (examples)**:
   - `notebooks/retail_opportunity_finder/tract_features.sql:94:  FROM metro_deep_dive.silver.housing_kpi`
   - `notebooks/retail_opportunity_finder/cbsa_features.sql:58:  FROM metro_deep_dive.silver.housing_kpi`

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
