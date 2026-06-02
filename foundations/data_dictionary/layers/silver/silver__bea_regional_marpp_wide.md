# Data Dictionary: silver.bea_regional_marpp_wide

## Overview
- **Table**: `silver.bea_regional_marpp_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 6,976
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=6976, distinct=6976, duplicates=0
  - `geo_id + period` => rows=6976, distinct=6976, duplicates=0
  - `geo_level` => rows=6976, distinct=2, duplicates=6974
- **Time coverage**: `period` min=2008, max=2023
- **Geo coverage**: distinct_geo_levels=2; distinct_geo_id=436

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 2 | len 4-5 | cbsa (6144); state (832) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 436 | len 5-5 | 00000 (16); 01000 (16); 02000 (16); 04000 (16); 05000 (16) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 436 | len 4-78 | Abilene, TX (Metropolitan Statistical Area) (16); Akron, OH (Metropolitan Statistical Area) (16); Alabama (16); Alaska (16); Albany, GA (Metropolitan Statistical Area) (16) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 16 | min 2008, max 2023 | 2008 (436); 2009 (436); 2010 (436); 2011 (436); 2012 (436) | Time period for the observation (usually calendar year). |
| `table` | `VARCHAR` | 0.0000 | 2 | len 5-5 | MARPP (6144); SARPP (832) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `rpp_real_personal_income` | `DOUBLE` | 0.0000 | 6883 | min 0, max 19641720000000 | 0.0 (20); 4493600000.0 (3); 7074800000.0 (3); 10054700000.0 (2); 11261400000.0 (2) | Regional Price Parities (RPP) real personal income, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_real_pc_income` | `DOUBLE` | 0.0000 | 6130 | min 0, max 129989 | 0.0 (20); 41060.0 (4); 42768.0 (4); 46715.0 (4); 47569.0 (4) | Regional Price Parities (RPP) real per capita income, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_all_items` | `DOUBLE` | 0.0000 | 5859 | min 0, max 122.74 | 0.0 (20); 100.0 (16); 92.94 (5); 95.232 (5); 95.33 (5) | Regional Price Parities (RPP) all items price index, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_goods` | `DOUBLE` | 0.0000 | 3047 | min 0, max 117.799 | 94.361 (25); 96.177 (24); 96.206 (24); 104.493 (23); 104.56 (23) | Regional Price Parities (RPP) goods price index, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_services_rents` | `DOUBLE` | 0.0000 | 6629 | min 0, max 246.696 | 0.0 (20); 101.48 (3); 62.815 (3); 66.015 (3); 66.607 (3) | Regional Price Parities (RPP) services and rents price index, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_services_utilities` | `DOUBLE` | 0.0000 | 6372 | min 0, max 265.981 | 0.0 (20); 103.509 (4); 89.077 (4); 89.152 (4); 90.525 (4) | Regional Price Parities (RPP) services and utilities price index, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_services_other` | `DOUBLE` | 11.9266 | 2645 | min 0, max 111.307 | NULL (832); 95.902 (32); 104.294 (24); 95.265 (23); 97.839 (23) | Regional Price Parities (RPP) other services price index, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_price_deflator` | `DOUBLE` | 11.9266 | 5559 | min 0, max 142.45 | NULL (832); 0.0 (20); 89.335 (4); 96.673 (4); 100.206 (3) | Regional Price Parities (RPP) price deflator index, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_real_consumption` | `DOUBLE` | 88.0734 | 831 | min 21817000000, max 15621697000000 | NULL (6144); 45151600000.0 (2); 1013265900000.0 (1); 102073700000.0 (1); 102529100000.0 (1) | Regional Price Parities (RPP) real consumption, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
| `rpp_real_pc_consumption` | `DOUBLE` | 88.0734 | 806 | min 29978, max 68937 | NULL (6144); 34043.0 (2); 34563.0 (2); 34595.0 (2); 34783.0 (2) | Regional Price Parities (RPP) real per capita consumption, in chained 2012 dollars. RPPs are price indices that measure the differences in price levels across regions, and are used to adjust nominal personal income to reflect differences in purchasing power across regions. |
## Data Quality Notes
- Columns with non-zero null rates: rpp_services_other=11.9266%, rpp_price_deflator=11.9266%, rpp_real_consumption=88.0734%, rpp_real_pc_consumption=88.0734%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_wide.sql:270:left join metro_deep_dive.silver.bea_regional_marpp_wide rpp `
   - `scripts/etl/gold/gold_economy_wide.sql:281:from metro_deep_dive.silver.bea_regional_marpp_wide`
   - `scripts/etl/silver/bea_marpp_silver.R:90:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_marpp_wide"),`
2. **Downstream usage (examples)**:
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.Rmd:108:from metro_deep_dive.silver.bea_regional_marpp_wide `
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.Rmd:120:from metro_deep_dive.silver.bea_regional_marpp_wide `
   - `notebooks/national_analyses/real_personal_income/real_personal_income_base.sql:72:from metro_deep_dive.silver.bea_regional_marpp_wide `
   - `notebooks/national_analyses/real_personal_income/real_personal_income_base.sql:84:from metro_deep_dive.silver.bea_regional_marpp_wide `
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.nb.html:1943:from metro_deep_dive.silver.bea_regional_marpp_wide `
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.nb.html:1955:from metro_deep_dive.silver.bea_regional_marpp_wide `

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
