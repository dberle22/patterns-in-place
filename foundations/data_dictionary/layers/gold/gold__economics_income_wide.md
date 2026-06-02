# Data Dictionary: gold.economics_income_wide

## Overview
- **Table**: `gold.economics_income_wide`
- **Purpose**: Gold layer analytical output table.
- **Row count**: 50,422
- **KPI applicability**: Gold output table; may contain derived KPI fields.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
  - `geo_level + geo_id + year` => rows=50422, distinct=50422, duplicates=0
  - `geo_id + year` => rows=50422, distinct=50422, duplicates=0
  - `geo_level` => rows=50422, distinct=3, duplicates=50419
- **Time coverage**: `year` min=2012, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4221

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (38648); cbsa (11150); state (624) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4221 | len 2-5 | 01 (12); 01001 (12); 01003 (12); 01005 (12); 01007 (12) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 4222 | len 4-59 | Abbeville County, South Carolina (12); Aberdeen, SD (12); Aberdeen, WA (12); Abilene, TX (12); Acadia Parish, Louisiana (12) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 12 | min 2012, max 2023 | 2022 (4209); 2023 (4209); 2012 (4201); 2013 (4201); 2020 (4201) | Observation year or period year for the row. |
| `pop_total` | `DOUBLE` | 0.0000 | 35702 | min 43, max 39455353 | 25477.0 (8); 3389.0 (7); 14335.0 (6); 16211.0 (6); 16511.0 (6) | Total population (all ages). |
| `median_hh_income` | `DOUBLE` | 0.0139 | 31076 |  | 48750.0 (24); 47500.0 (20); 51250.0 (18); 55000.0 (18); 50000.0 (16) | Median household income in the past 12 months. |
| `acs_income_pc` | `DOUBLE` | 0.0020 | 24931 |  | 21716.0 (13); 22589.0 (13); 23895.0 (13); 24864.0 (12); 21109.0 (11) | Per capita income calculated from ACS data as total income divided by total population. |
| `pov_rate` | `DOUBLE` | 0.0020 | 43244 |  | 0.1 (7); 0.1111111111111111 (6); 0.16666666666666666 (4); 0.05128205128205128 (3); 0.07547169811320754 (3) | Poverty Rate, dervied from pov_below and pov_universe. (from silver.kpi_dictionary). |
| `gini_index` | `DOUBLE` | 0.0020 | 7358 |  | 0.4401 (73); 0.4291 (72); 0.4434 (71); 0.4439 (71); 0.4286 (70) | Ratio of Gini Index, a meaure of economic equality (0=perfect equality, 1=perfect inequality). |
| `pi_total` | `DOUBLE` | 4.7916 | 40797 | min 1899000, max 1785029500000 | NULL (2416); 1148796000.0 (4); 1295315000.0 (4); 2049858000.0 (4); 2626563000.0 (4) | Total Personal Income (PI) in current dollars, from BEA regional data. |
| `calc_income_pc` | `DOUBLE` | 4.7916 | 41021 | min 5462.2932196, max 469206.3960956 | NULL (2416); 100136.09954304376 (2); 100162.93746414228 (2); 101283.17448680352 (2); 101436.26774999069 (2) | Per capita income calculated from BEA data as total personal income divided by total population. |
| `income_pc_growth_1yr` | `DOUBLE` | 12.7325 | 37600 | min -0.3994802, max 1.668498 | NULL (6420); -0.0001637248831747089 (2); -0.00016717833333474574 (2); -0.00022681130625706815 (2); -0.00024762434264891884 (2) | 1-year per capita income growth rate (i.e., the percentage change in per capita income from the previous year). |
| `income_pc_growth_5yr` | `DOUBLE` | 44.4925 | 23914 | min -0.4960392, max 10.8340128 | NULL (22434); -0.0007341448860337595 (2); -0.001203074428835366 (2); -0.003120363183548495 (2); -0.003277103487806 (2) | 5-year per capita income growth rate (i.e., the percentage change in per capita income over 5 years). |
| `income_pc_cagr_5yr` | `DOUBLE` | 44.4925 | 23914 | min -0.1280745, max 0.6391791 | NULL (22434); -0.00014687211370634223 (2); -0.00024073076046715602 (2); -0.0006248530315473566 (2); -0.0006562815433468483 (2) | 5-year per capita income compound annual growth rate (CAGR). |
| `income_pc_growth_10yr` | `DOUBLE` | 84.1696 | 6818 | min -0.4028209, max 7.1505763 | NULL (42440); -0.04109279445095245 (2); -0.08132703657943609 (2); -0.15179582742610864 (2); -0.17648823954399873 (2) | 10-year per capita income growth rate (i.e., the percentage change in per capita income over 10 years). |
| `income_pc_cagr_10yr` | `DOUBLE` | 84.1696 | 6818 | min -0.0502475, max 0.2334423 | NULL (42440); -0.004187305731515378 (2); -0.008446633167005335 (2); -0.016328609317201592 (2); -0.0192304347718929 (2) | 10-year per capita income compound annual growth rate (CAGR). |
| `pi_wages_salary` | `DOUBLE` | 17.6034 | 39235 | min 823000, max 967137050000 | NULL (8876); 208158000.0 (4); 113541000.0 (3); 11481000.0 (3); 161140000.0 (3) | Personal Income from Wages and Salaries, from BEA regional data. |
| `pi_wage_share` | `DOUBLE` | 17.6907 | 39894 | min 0.0673574, max 8.0698739 | NULL (8920); 0.19686943960018466 (2); 0.19739961855332705 (2); 0.20343434031821442 (2); 0.2045612824028012 (2) | Share of total personal income that is from Wages and Salaries. |
## Data Quality Notes
- Columns with non-zero null rates: median_hh_income=0.0139%, acs_income_pc=0.002%, pov_rate=0.002%, gini_index=0.002%, pi_total=4.7916%, calc_income_pc=4.7916%, income_pc_growth_1yr=12.7325%, income_pc_growth_5yr=44.4925%, income_pc_cagr_5yr=44.4925%, income_pc_growth_10yr=84.1696% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_income.sql:7:create or replace table metro_deep_dive.gold.economics_income_wide as `
   - `scripts/etl/gold/gold_housing_core.sql:58:DESCRIBE metro_deep_dive.gold.economics_income_wide; -- Contains Incomes`

## Known Gaps / To-Dos
- Add business definitions for high-priority consumption columns.
- Add automated DQ thresholds for row-count drift and key integrity.
- Add explicit source provenance fields in Gold tables where needed.
