# Data Dictionary: silver.housing_base

## Overview
- **Table**: `silver.housing_base`
- **Purpose**: Silver housing table (`base` type).
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
| `hu_totalE` | `DOUBLE` | 0.0000 | 48279 | min 0, max 143775360 | 0.0 (12518); 46.0 (1194); 50.0 (1174); 71.0 (1166); 52.0 (1159) | ACS 2024 Housing Units [B25001_001]: Total (estimate). |
| `occ_totalE` | `DOUBLE` | 0.0000 | 48279 | min 0, max 143775360 | 0.0 (12518); 46.0 (1194); 50.0 (1174); 71.0 (1166); 52.0 (1159) | ACS 2024 Occupancy Status [B25002_001]: Total: (estimate). |
| `occ_occupiedE` | `DOUBLE` | 0.0000 | 45115 | min 0, max 129227500 | 0.0 (15641); 33.0 (1475); 32.0 (1463); 39.0 (1453); 43.0 (1445) | ACS 2024 Occupancy Status [B25002_002]: Total:, Occupied (estimate). |
| `occ_vacantE` | `DOUBLE` | 0.0000 | 17020 | min 0, max 16672938 | 0.0 (67178); 9.0 (6089); 14.0 (5988); 13.0 (5927); 15.0 (5907) | ACS 2024 Occupancy Status [B25002_003]: Total:, Vacant (estimate). |
| `tenure_totalE` | `DOUBLE` | 0.0000 | 45115 | min 0, max 129227500 | 0.0 (15641); 33.0 (1475); 32.0 (1463); 39.0 (1453); 43.0 (1445) | ACS 2024 Tenure [B25003_001]: Total: (estimate). |
| `owner_occupiedE` | `DOUBLE` | 0.0000 | 35573 | min 0, max 84210142 | 0.0 (22036); 25.0 (1920); 26.0 (1879); 27.0 (1854); 17.0 (1851) | ACS 2024 Tenure [B25003_002]: Total:, Owner occupied (estimate). |
| `renter_occupiedE` | `DOUBLE` | 0.0000 | 27966 | min 0, max 45017354 | 0.0 (59306); 9.0 (6033); 8.0 (5878); 10.0 (5806); 7.0 (5801) | ACS 2024 Tenure [B25003_003]: Total:, Renter occupied (estimate). |
| `median_gross_rentE` | `DOUBLE` | 17.7859 | 7772 | min 99, max 3501 | NULL (181582); 675.0 (3799); 625.0 (3687); 725.0 (3579); 775.0 (3366) | ACS 2024 Median Gross Rent (Dollars) [B25064_001]: Median gross rent (estimate). |
| `median_home_valueE` | `DOUBLE` | 6.8108 | 18205 | min 9999, max 2000001 | NULL (69534); 85000.0 (1928); 112500.0 (1924); 75000.0 (1878); 95000.0 (1737) | ACS 2024 Median Value (Dollars) [B25077_001]: Median value (dollars) (estimate). |
| `rent_burden_totalE` | `DOUBLE` | 0.0069 | 27966 | min 0, max 45017354 | 0.0 (59283); 9.0 (6033); 8.0 (5877); 10.0 (5804); 7.0 (5801) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_001]: Total: (estimate). |
| `rent_lt_10E` | `DOUBLE` | 0.0069 | 5666 | min 0, max 1730092 | 0.0 (418608); 2.0 (22622); 3.0 (19922); 4.0 (18214); 5.0 (16707) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_002]: Total:, Less than 10.0 percent (estimate). |
| `rent_10_14E` | `DOUBLE` | 0.0069 | 8272 | min 0, max 3706926 | 0.0 (292256); 2.0 (21083); 3.0 (18184); 4.0 (17214); 5.0 (16423) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_003]: Total:, 10.0 to 14.9 percent (estimate). |
| `rent_15_19E` | `DOUBLE` | 0.0069 | 9817 | min 0, max 5254304 | 0.0 (263880); 2.0 (20563); 3.0 (16706); 4.0 (16015); 5.0 (15281) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_004]: Total:, 15.0 to 19.9 percent (estimate). |
| `rent_20_24E` | `DOUBLE` | 0.0069 | 9884 | min 0, max 5274812 | 0.0 (277367); 2.0 (20222); 3.0 (17108); 4.0 (16172); 5.0 (15283) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_005]: Total:, 20.0 to 24.9 percent (estimate). |
| `rent_25_29E` | `DOUBLE` | 0.0069 | 9454 | min 0, max 4820123 | 0.0 (304224); 2.0 (20642); 3.0 (16863); 4.0 (15610); 5.0 (14557) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_006]: Total:, 25.0 to 29.9 percent (estimate). |
| `rent_30_34E` | `DOUBLE` | 0.0069 | 8538 | min 0, max 3872456 | 0.0 (344207); 2.0 (21019); 3.0 (17442); 4.0 (15901); 5.0 (14996) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_007]: Total:, 30.0 to 34.9 percent (estimate). |
| `rent_35_39E` | `DOUBLE` | 0.0069 | 7466 | min 0, max 2838920 | 0.0 (399811); 2.0 (20690); 3.0 (18334); 4.0 (15860); 5.0 (14348) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_008]: Total:, 35.0 to 39.9 percent (estimate). |
| `rent_40_49E` | `DOUBLE` | 0.0069 | 8587 | min 0, max 3858845 | 0.0 (348019); 2.0 (21492); 3.0 (18364); 4.0 (16146); 5.0 (14990) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_009]: Total:, 40.0 to 49.9 percent (estimate). |
| `rent_50_plusE` | `DOUBLE` | 0.0069 | 14027 | min 0, max 10852194 | 0.0 (217364); 2.0 (18637); 3.0 (15279); 4.0 (14894); 5.0 (13847) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_010]: Total:, 50.0 percent or more (estimate). |
| `rent_not_computedE` | `DOUBLE` | 0.0069 | 7827 | min 0, max 3206218 | 0.0 (197080); 2.0 (20641); 3.0 (18320); 4.0 (17877); 5.0 (17211) | ACS 2024 Gross Rent as a Percentage of Household Income in the Past 12 Months [B25070_011]: Total:, Not computed (estimate). |
| `median_owner_costs_totalE` | `DOUBLE` | 6.7597 | 8334 | min 99, max 4001 | NULL (69012); 650.0 (3098); 550.0 (3086); 750.0 (2679); 600.0 (2635) | ACS 2024 Median Selected Monthly Owner Costs (Dollars) by Mortgage Status [B25088_001]: Median selected monthly owner costs (dollars) --, Total: (estimate). |
| `median_owner_costs_mortgageE` | `DOUBLE` | 10.0527 | 8122 | min 99, max 4001 | NULL (102631); 4001.0 (9584); 1125.0 (4185); 950.0 (4175); 850.0 (3548) | ACS 2024 Median Selected Monthly Owner Costs (Dollars) by Mortgage Status [B25088_002]: Median selected monthly owner costs (dollars) --, Housing units with a mortgage (dollars) (estimate). |
| `median_owner_costs_no_mortgageE` | `DOUBLE` | 8.1629 | 5842 | min 99, max 1501 | NULL (83338); 1501.0 (8670); 1001.0 (6039); 375.0 (5993); 450.0 (5319) | ACS 2024 Median Selected Monthly Owner Costs (Dollars) by Mortgage Status [B25088_003]: Median selected monthly owner costs (dollars) --, Housing units without a mortgage (dollars) (estimate). |
| `struct_totalE` | `DOUBLE` | 0.0000 | 48279 | min 0, max 143775360 | 0.0 (12518); 46.0 (1194); 50.0 (1174); 71.0 (1166); 52.0 (1159) | ACS 2024 Units in Structure [B25024_001]: Total: (estimate). |
| `struct_1_detE` | `DOUBLE` | 0.0000 | 37660 | min 0, max 88075458 | 0.0 (17114); 39.0 (1548); 48.0 (1530); 43.0 (1518); 45.0 (1516) | ACS 2024 Units in Structure [B25024_002]: Total:, 1, detached (estimate). |
| `struct_1_attE` | `DOUBLE` | 0.0000 | 12687 | min 0, max 8955086 | 0.0 (351732); 2.0 (22108); 3.0 (18733); 4.0 (15979); 5.0 (13889) | ACS 2024 Units in Structure [B25024_003]: Total:, 1, attached (estimate). |
| `struct_2_unitsE` | `DOUBLE` | 0.0000 | 10034 | min 0, max 5004472 | 0.0 (383610); 2.0 (13654); 3.0 (12302); 4.0 (12236); 5.0 (11547) | ACS 2024 Units in Structure [B25024_004]: Total:, 2 (estimate). |
| `struct_3_4_unitsE` | `DOUBLE` | 0.0000 | 11041 | min 0, max 6214115 | 0.0 (381874); 2.0 (10406); 6.0 (10054); 4.0 (9845); 9.0 (9770) | ACS 2024 Units in Structure [B25024_005]: Total:, 3 or 4 (estimate). |
| `struct_5_9_unitsE` | `DOUBLE` | 0.0000 | 11481 | min 0, max 6483370 | 0.0 (437110); 5.0 (8539); 4.0 (8529); 7.0 (8452); 3.0 (8324) | ACS 2024 Units in Structure [B25024_006]: Total:, 5 to 9 (estimate). |
| `struct_10_19E` | `DOUBLE` | 0.0000 | 11327 | min 0, max 6141784 | 0.0 (517677); 3.0 (8680); 2.0 (8058); 4.0 (7590); 6.0 (7366) | ACS 2024 Units in Structure [B25024_007]: Total:, 10 to 19 (estimate). |
| `struct_20_49E` | `DOUBLE` | 0.0000 | 10275 | min 0, max 5407809 | 0.0 (558946); 3.0 (7573); 9.0 (6596); 2.0 (6595); 4.0 (6447) | ACS 2024 Units in Structure [B25024_008]: Total:, 20 to 49 (estimate). |
| `struct_50_plusE` | `DOUBLE` | 0.0000 | 12776 | min 0, max 9451738 | 0.0 (628358); 3.0 (6660); 4.0 (5754); 8.0 (5586); 2.0 (5502) | ACS 2024 Units in Structure [B25024_009]: Total:, 50 or more (estimate). |
| `struct_mobileE` | `DOUBLE` | 0.0000 | 11835 | min 0, max 8583843 | 0.0 (204491); 9.0 (11188); 8.0 (11171); 10.0 (10724); 7.0 (10578) | ACS 2024 Units in Structure [B25024_010]: Total:, Mobile home (estimate). |
| `struct_otherE` | `DOUBLE` | 0.0000 | 1703 | min 0, max 186040 | 0.0 (864362); 2.0 (7377); 3.0 (6925); 8.0 (6318); 9.0 (6165) | ACS 2024 Units in Structure [B25024_011]: Total:, Boat, RV, van, etc. (estimate). |
## Data Quality Notes
- Columns with non-zero null rates: median_gross_rentE=17.7859%, median_home_valueE=6.8108%, rent_burden_totalE=0.0069%, rent_lt_10E=0.0069%, rent_10_14E=0.0069%, rent_15_19E=0.0069%, rent_20_24E=0.0069%, rent_25_29E=0.0069%, rent_30_34E=0.0069%, rent_35_39E=0.0069% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_housing_silver.R:210:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="housing_base"),`

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
