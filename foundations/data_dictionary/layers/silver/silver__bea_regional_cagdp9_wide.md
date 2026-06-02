# Data Dictionary: silver.bea_regional_cagdp9_wide

## Overview
- **Table**: `silver.bea_regional_cagdp9_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 57,274
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=57274, distinct=57274, duplicates=0
  - `geo_id + period` => rows=57274, distinct=57246, duplicates=28
  - `geo_level` => rows=57274, distinct=3, duplicates=57271
- **Time coverage**: `period` min=2010, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4089

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (43652); cbsa (12782); state (840) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4089 | len 5-5 | 32000 (28); 45000 (28); 00000 (14); 01000 (14); 01001 (14) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 3976 | len 4-48 | Alamosa, CO (28); Alpena, MI (28); Andrews, TX (28); Ashland, OH (28); Atchison, KS (28) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 14 | min 2010, max 2023 | 2010 (4091); 2011 (4091); 2012 (4091); 2013 (4091); 2014 (4091) | Time period for the observation (usually calendar year). |
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAGDP9 (57274) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `real_gdp_total` | `DOUBLE` | 0.0000 | 48677 | min 0, max 22671096000000 | 0.0 (66); 1291355000.0 (5); 1047702000.0 (4); 1162632000.0 (4); 1232928000.0 (4) | Total Real GDP for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_utilities` | `DOUBLE` | 0.0000 | 28589 | min 0, max 342977000000 | 0.0 (9110); 2000.0 (28); 1000.0 (27); 82000.0 (22); 4000.0 (16) | Real GDP for Utilities for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_construction` | `DOUBLE` | 0.0000 | 39390 | min 0, max 887608000000 | 0.0 (4795); 5940000.0 (8); 10986000.0 (6); 15007000.0 (6); 56503000.0 (6) | Real GDP for Construction for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_manufacturing_all` | `DOUBLE` | 0.0000 | 41803 | min 0, max 2317923000000 | 0.0 (4905); 10000.0 (6); 8000.0 (6); 92000.0 (6); 10166000.0 (5) | Real GDP for Manufacturing (all sectors) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_durable_manufacturing` | `DOUBLE` | 0.0000 | 36815 | min 0, max 1293473000000 | 0.0 (8416); 6000.0 (19); 8000.0 (18); 23000.0 (17); 7000.0 (17) | Real GDP for Durable Manufacturing for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_private` | `DOUBLE` | 0.0000 | 48639 | min 0, max 20092919000000 | 0.0 (66); 1021736000.0 (4); 1395335000.0 (4); 1888236000.0 (4); 1970947000.0 (4) | Real GDP for Private Sector for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_nondurable_manufacturing` | `DOUBLE` | 0.0000 | 35776 | min 0, max 1036519000000 | 0.0 (8122); 1000.0 (18); 2000.0 (16); 5000.0 (15); 108000.0 (13) | Real GDP for Nondurable Manufacturing for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_agriculture` | `DOUBLE` | 0.0000 | 32902 | min 0, max 192667000000 | 0.0 (8852); 2486000.0 (10); 2528000.0 (9); 5359000.0 (9); 2228000.0 (8) | Real GDP for Agriculture for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_wholesale_trade` | `DOUBLE` | 0.0000 | 34529 | min 0, max 1205512000000 | 0.0 (11255); 5000.0 (10); 12859000.0 (6); 2000.0 (6); 26245000.0 (6) | Real GDP for Wholesale Trade for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_retail_trade` | `DOUBLE` | 0.0000 | 43415 | min 0, max 1317653000000 | 0.0 (1177); 127270000.0 (6); 100899000.0 (5); 106466000.0 (5); 11740000.0 (5) | Real GDP for Retail Trade for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_transportation` | `DOUBLE` | 0.0000 | 30295 | min 0, max 706954000000 | 0.0 (16203); 33334000.0 (7); 11350000.0 (6); 11528000.0 (6); 27792000.0 (6) | Real GDP for Transportation for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_information` | `DOUBLE` | 0.0000 | 30599 | min 0, max 1605851000000 | 0.0 (9231); 21000.0 (18); 1000.0 (17); 2000.0 (14); 4000.0 (14) | Real GDP for Information sector for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_finance_real_estate_all` | `DOUBLE` | 0.0000 | 44346 | min 0, max 4676163000000 | 0.0 (3212); 133025000.0 (6); 158049000.0 (5); 213742000.0 (5); 105518000.0 (4) | Real GDP for Finance, Insurance and Real Estate (Composite Sectors) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_finance_insurance` | `DOUBLE` | 0.0000 | 37563 | min 0, max 1625020000000 | 0.0 (6318); 30661000.0 (6); 41371000.0 (6); 52917000.0 (6); 80128000.0 (6) | Real GDP for Finance and Insurance for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_real_estate` | `DOUBLE` | 0.0000 | 40582 | min 0, max 3108447000000 | 0.0 (6784); 184420000.0 (6); 139043000.0 (5); 147494000.0 (5); 175504000.0 (5) | Real GDP for Real Estate for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_professional_all` | `DOUBLE` | 0.0000 | 37363 | min 0, max 3391773000000 | 0.0 (7546); 3186000.0 (7); 61478000.0 (7); 20461000.0 (6); 35481000.0 (6) | Real GDP for Professional, Scientific and Management Services (Composite) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_mining` | `DOUBLE` | 0.0000 | 24979 | min 0, max 336302000000 | 0.0 (10982); 28000.0 (27); 6000.0 (24); 15000.0 (23); 52000.0 (23) | Real GDP for Mining for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_professional_scientific` | `DOUBLE` | 0.0000 | 30885 | min 0, max 2116154000000 | 0.0 (13519); 2456000.0 (7); 3690000.0 (7); 4983000.0 (7); 1064000.0 (6) | Real GDP for Professional and Scientific Services for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_professional_management` | `DOUBLE` | 0.0000 | 17982 | min 0, max 536475000000 | 0.0 (29872); 9530000.0 (12); 2307000.0 (10); 2538000.0 (9); 2446000.0 (8) | Real GDP for Professional and Management Services for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_professional_admin_support` | `DOUBLE` | 0.0000 | 31223 | min 0, max 748330000000 | 0.0 (12487); 1612000.0 (7); 2128000.0 (7); 46000.0 (7); 65000.0 (7) | Real GDP for Administrative and Support Services for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_education_all` | `DOUBLE` | 0.0000 | 40771 | min 0, max 2021153000000 | 0.0 (4518); 174647000.0 (6); 176000.0 (6); 12100000.0 (5); 123207000.0 (5) | Real GDP for Educational and Health Services (All) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_education` | `DOUBLE` | 0.0000 | 21047 | min 0, max 263315000000 | 0.0 (16647); 19000.0 (79); 32000.0 (77); 41000.0 (74); 26000.0 (68) | Real GDP for Educational Services for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_health` | `DOUBLE` | 0.0000 | 30287 | min 0, max 1758316000000 | 0.0 (17713); 59645000.0 (6); 14746000.0 (5); 21698000.0 (5); 4943000.0 (5) | Real GDP for Health Care and Social Assistance for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_arts_food_all` | `DOUBLE` | 0.0000 | 37981 | min 0, max 889845000000 | 0.0 (3865); 31608000.0 (8); 29101000.0 (7); 6179000.0 (7); 6332000.0 (7) | Real GDP for Arts, Entertainment, Recreation, Accommodation and Food Services (Composite) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_arts_entertainment` | `DOUBLE` | 0.0000 | 23405 | min 0, max 243996000000 | 0.0 (10211); 3000.0 (32); 11000.0 (31); 13000.0 (29); 19000.0 (28) | Real GDP for Arts, Entertainment and Recreation for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_accomodation_food` | `DOUBLE` | 0.0000 | 33981 | min 0, max 647819000000 | 0.0 (10011); 19665000.0 (7); 109620000.0 (6); 16334000.0 (6); 20361000.0 (6) | Real GDP for Accommodation and Food Services for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_other` | `DOUBLE` | 0.0000 | 36560 | min 0, max 449026000000 | 0.0 (4748); 4758000.0 (8); 17880000.0 (7); 23550000.0 (7); 28627000.0 (7) | Real GDP for Other Services for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_gov_enterprises` | `DOUBLE` | 0.0000 | 46758 | min 0, max 2582255000000 | 0.0 (66); 118272000.0 (5); 182999000.0 (5); 217825000.0 (5); 408821000.0 (5) | Real GDP for Government Enterprises for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_natural_resources_all` | `DOUBLE` | 0.0000 | 35213 | min 0, max 533936920000 | 0.0 (10674); 11237000.0 (6); 13982000.0 (6); 14675000.0 (6); 18161000.0 (6) | Real GDP for Natural Resources (Composite Industries) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_trade_all` | `DOUBLE` | 0.0000 | 36600 | min 0, max 2484733900000 | 0.0 (11359); 118164000.0 (5); 141981000.0 (5); 52212000.0 (5); 102816000.0 (4) | Real GDP for Trade (Composite Industries) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_transport_utilities_all` | `DOUBLE` | 0.0000 | 26593 | min 0, max 1048186800000 | 0.0 (22610); 16658000.0 (6); 104358000.0 (4); 115820000.0 (4); 122539000.0 (4) | Real GDP for Transportation and Utilities (Composite Industries) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_manufacturing_info_all` | `DOUBLE` | 0.0000 | 38385 | min 0, max 3884821600000 | 0.0 (8876); 141305000.0 (5); 102106000.0 (4); 106205000.0 (4); 109276000.0 (4) | Real GDP Manufacturing and Information (Composite Industries) for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_private_goods_producing_industries` | `DOUBLE` | 0.0000 | 41804 | min 0, max 3678839000000 | 0.0 (7282); 126209000.0 (4); 165593000.0 (4); 178982000.0 (4); 213515000.0 (4) | Real GDP for Private Goods Producing Industries for the geographic unit and time period, from BEA CAGDP9 table. |
| `real_gdp_private_services_providing_industries` | `DOUBLE` | 0.0000 | 42165 | min 0, max 16416728000000 | 0.0 (7282); 1117267000.0 (4); 1573503000.0 (4); 1793678000.0 (4); 2565248000.0 (4) | Real GDP for Private Services Providing Industries for the geographic unit and time period, from BEA CAGDP9 table. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_industry.sql:54:from metro_deep_dive.silver.bea_regional_cagdp9_wide`
   - `scripts/etl/gold/gold_economy_industry.sql:142:from metro_deep_dive.silver.bea_regional_cagdp9_wide`
   - `scripts/etl/gold/gold_economy_gdp.sql:117:from metro_deep_dive.silver.bea_regional_cagdp9_wide`
   - `scripts/etl/gold/gold_economy_wide.sql:159:from metro_deep_dive.silver.bea_regional_cagdp9_wide`
   - `scripts/etl/silver/bea_cagdp9_silver.R:159:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cagdp9_wide"),`

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
