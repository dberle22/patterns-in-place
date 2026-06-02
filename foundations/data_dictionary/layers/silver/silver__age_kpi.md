# Data Dictionary: silver.age_kpi

## Overview
- **Table**: `silver.age_kpi`
- **Purpose**: Silver age table (`kpi` type).
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
| `pop_total` | `DOUBLE` | 0.0000 | 80593 | min 0, max 334922500 | 0.0 (11017); 74.0 (610); 115.0 (607); 61.0 (603); 64.0 (602) | Total population (all ages). |
| `median_age` | `DOUBLE` | 1.7624 | 5492 | min 0, max 105.1 | NULL (17993); 40.5 (5948); 40.8 (5846); 40.3 (5768); 40.6 (5615) | Median age of the population (years). |
| `age_0_4` | `DOUBLE` | 0.0000 | 18281 | min 0, max 20137884 | 0.0 (99942); 8.0 (6958); 4.0 (6920); 6.0 (6853); 10.0 (6794) | Population ages 0 to 4. |
| `age_5_14` | `DOUBLE` | 0.0000 | 26354 | min 0, max 41921255 | 0.0 (63240); 9.0 (4087); 8.0 (4031); 12.0 (4015); 10.0 (4010) | Population ages 5 to 14. |
| `age_15_17` | `DOUBLE` | 0.0000 | 14740 | min 0, max 13192298 | 0.0 (104795); 6.0 (9490); 2.0 (9233); 4.0 (9127); 8.0 (9001) | Population ages 15 to 17. |
| `age_18_24` | `DOUBLE` | 0.0000 | 24431 | min 0, max 31368674 | 0.0 (75273); 6.0 (5799); 8.0 (5719); 9.0 (5686); 11.0 (5648) | Population ages 18 to 24. |
| `age_25_34` | `DOUBLE` | 0.0000 | 27333 | min 0, max 45806540 | 0.0 (57934); 8.0 (4404); 9.0 (4403); 10.0 (4388); 13.0 (4327) | Population ages 25 to 34. |
| `age_35_44` | `DOUBLE` | 0.0000 | 26051 | min 0, max 44237292 | 0.0 (52919); 10.0 (4535); 12.0 (4332); 9.0 (4327); 11.0 (4289) | Population ages 35 to 44. |
| `age_45_54` | `DOUBLE` | 0.0000 | 25948 | min 0, max 44646979 | 0.0 (42724); 9.0 (3935); 13.0 (3880); 10.0 (3875); 14.0 (3831) | Population ages 45 to 54. |
| `age_55_64` | `DOUBLE` | 0.0000 | 25241 | min 0, max 42829413 | 0.0 (34730); 16.0 (3653); 9.0 (3623); 12.0 (3616); 14.0 (3596) | Population ages 55 to 64. |
| `age_65_74` | `DOUBLE` | 0.0000 | 21376 | min 0, max 34092907 | 0.0 (42026); 10.0 (4961); 9.0 (4931); 8.0 (4898); 16.0 (4708) | Population ages 65 to 74. |
| `age_75_84` | `DOUBLE` | 0.0000 | 15654 | min 0, max 17108680 | 0.0 (71196); 8.0 (8179); 10.0 (8085); 9.0 (8076); 7.0 (7858) | Population ages 75 to 84. |
| `age_85p` | `DOUBLE` | 0.0000 | 10469 | min 0, max 6621816 | 0.0 (157162); 2.0 (18137); 4.0 (15374); 3.0 (15332); 6.0 (14473) | Population ages 85 and older. |
| `age_25_54` | `DOUBLE` | 0.0000 | 47706 | min 0, max 130787630 | 0.0 (22503); 32.0 (1662); 19.0 (1646); 18.0 (1637); 45.0 (1637) | Population ages 25 to 54. |
| `pct_age_0_4` | `DOUBLE` | 0.0000 | 513048 |  | 0.0 (88925); -nan (11017); 0.0625 (680); 0.07142857142857142 (676); 0.058823529411764705 (675) | Share of total population ages 0 to 4 (0 to 1). |
| `pct_age_5_14` | `DOUBLE` | 0.0000 | 562848 |  | 0.0 (52223); -nan (11017); 0.14285714285714285 (1022); 0.125 (974); 0.1111111111111111 (943) | Share of total population ages 5 to 14 (0 to 1). |
| `pct_age_15_17` | `DOUBLE` | 0.0000 | 479966 |  | 0.0 (93778); -nan (11017); 0.04 (681); 0.041666666666666664 (668); 0.05263157894736842 (655) | Share of total population ages 15 to 17 (0 to 1). |
| `pct_age_18_24` | `DOUBLE` | 0.0000 | 542973 |  | 0.0 (64256); -nan (11017); 0.07692307692307693 (797); 0.07142857142857142 (786); 0.08333333333333333 (755) | Share of total population ages 18 to 24 (0 to 1). |
| `pct_age_25_34` | `DOUBLE` | 0.0000 | 565502 |  | 0.0 (46917); -nan (11017); 0.1111111111111111 (1029); 0.125 (1004); 0.14285714285714285 (943) | Share of total population ages 25 to 34 (0 to 1). |
| `pct_age_35_44` | `DOUBLE` | 0.0000 | 548915 |  | 0.0 (41902); -nan (11017); 0.1111111111111111 (1182); 0.125 (1159); 0.1 (1040) | Share of total population ages 35 to 44 (0 to 1). |
| `pct_age_45_54` | `DOUBLE` | 0.0000 | 558238 |  | 0.0 (31707); -nan (11017); 0.14285714285714285 (1218); 0.16666666666666666 (1207); 0.125 (1140) | Share of total population ages 45 to 54 (0 to 1). |
| `pct_age_55_64` | `DOUBLE` | 0.0000 | 568699 |  | 0.0 (23713); -nan (11017); 1.0 (1456); 0.16666666666666666 (1305); 0.14285714285714285 (1254) | Share of total population ages 55 to 64 (0 to 1). |
| `pct_age_65_74` | `DOUBLE` | 0.0000 | 565755 |  | 0.0 (31009); -nan (11017); 1.0 (1548); 0.1 (1036); 0.1111111111111111 (1011) | Share of total population ages 65 to 74 (0 to 1). |
| `pct_age_75_84` | `DOUBLE` | 0.0000 | 521545 |  | 0.0 (60179); -nan (11017); 0.07692307692307693 (739); 0.0625 (738); 0.08333333333333333 (719) | Share of total population ages 75 to 84 (0 to 1). |
| `pct_age_85p` | `DOUBLE` | 0.0000 | 453972 |  | 0.0 (146145); -nan (11017); 0.027777777777777776 (442); 0.02564102564102564 (414); 0.03225806451612903 (401) | Share of total population ages 85 and older (0 to 1). |
| `pct_age_25_54` | `DOUBLE` | 0.0000 | 603886 |  | 0.0 (11486); -nan (11017); 0.3333333333333333 (2431); 1.0 (1510); 0.4 (1262) | Share of total population ages 25 to 54 (0 to 1). |
| `aging_index` | `DOUBLE` | 9.7893 | 386143 | min 0, max 2811.2666667 | NULL (99942); 0.0 (5859); 2.0 (2834); 3.0 (2660); 4.0 (2217) | Ratio of population ages 65+ to population ages 0 to 4. |
| `youth_dependency` | `DOUBLE` | 2.2042 | 499204 | min 0, max 26.0833333 | 0.0 (31661); NULL (22503); 0.5 (3586); 0.3333333333333333 (1999); 1.0 (1699) | Ratio of population ages 0 to 14 to population ages 25 to 54 (prime working age population). |
| `old_age_dependency` | `DOUBLE` | 2.2042 | 541788 | min 0, max 426 | NULL (22503); 0.0 (17048); 0.5 (2444); 1.0 (2153); 0.3333333333333333 (1602) | Ratio of population ages 65+ to population ages 25 to 54. |
## Data Quality Notes
- Columns with non-zero null rates: median_age=1.7624%, aging_index=9.7893%, youth_dependency=2.2042%, old_age_dependency=2.2042%
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_industry.sql:12:from metro_deep_dive.silver.age_kpi `
   - `scripts/etl/gold/gold_population_wide.sql:61:FROM metro_deep_dive.silver.age_kpi `
   - `scripts/etl/gold/gold_economy_income.sql:16:from metro_deep_dive.silver.age_kpi `
   - `scripts/etl/gold/gold_economy_wide.sql:19:from metro_deep_dive.silver.age_kpi `
   - `scripts/etl/gold/gold_economy_gdp.sql:14:from metro_deep_dive.silver.age_kpi `
   - `scripts/etl/gold/gold_housing_core.sql:16:from metro_deep_dive.silver.age_kpi `
   - `scripts/etl/gold/gold_economy_labor.sql:14:from metro_deep_dive.silver.age_kpi `
   - `scripts/etl/silver/acs_age_silver.R:205:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="age_kpi"),`
2. **Downstream usage (examples)**:
   - `notebooks/national_analyses/real_personal_income/real_personal_income_base.sql:7:from metro_deep_dive.silver.age_kpi `
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.Rmd:43:from metro_deep_dive.silver.age_kpi `
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.nb.html:1878:from metro_deep_dive.silver.age_kpi `

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
