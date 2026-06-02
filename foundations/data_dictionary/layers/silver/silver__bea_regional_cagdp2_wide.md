# Data Dictionary: silver.bea_regional_cagdp2_wide

## Overview
- **Table**: `silver.bea_regional_cagdp2_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 57,814
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=57814, distinct=57814, duplicates=0
  - `geo_id + period` => rows=57814, distinct=57786, duplicates=28
  - `geo_level` => rows=57814, distinct=3, duplicates=57811
- **Time coverage**: `period` min=2001, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4089

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (43652); cbsa (12782); state (1380) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4089 | len 5-5 | 32000 (37); 45000 (37); 00000 (23); 01000 (23); 02000 (23) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 3976 | len 4-48 | Alamosa, CO (28); Alpena, MI (28); Andrews, TX (28); Ashland, OH (28); Atchison, KS (28) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 23 | min 2001, max 2023 | 2010 (4091); 2011 (4091); 2012 (4091); 2013 (4091); 2014 (4091) | Time period for the observation (usually calendar year). |
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAGDP2 (57814) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `gdp_total` | `DOUBLE` | 0.0000 | 49263 | min 0, max 27720709000000 | 0.0 (66); 2502608000.0 (4); 851888000.0 (4); 9628476000.0 (4); 1055378000.0 (3) | Total GDP for the geography and time period. |
| `gdp_utilities` | `DOUBLE` | 0.0000 | 29474 | min 0, max 446515000000 | 0.0 (9110); 1000.0 (28); 2000.0 (25); 32000.0 (18); 75000.0 (17) | GDP from Utilities sector for the geography and time period. |
| `gdp_construction` | `DOUBLE` | 0.0000 | 40046 | min 0, max 1220566000000 | 0.0 (4795); 14330000.0 (7); 23978000.0 (6); 31309000.0 (6); 33736000.0 (6) | GDP from Construction sector for the geography and time period. |
| `gdp_manufacturing_all` | `DOUBLE` | 0.0000 | 42350 | min 0, max 2840447000000 | 0.0 (4905); 8000.0 (7); 5000.0 (6); 1083000.0 (5); 11000.0 (5) | GDP from Manufacturing sector for the geography and time period. |
| `gdp_durable_manufacturing` | `DOUBLE` | 0.0000 | 37382 | min 0, max 1511940000000 | 0.0 (8416); 6000.0 (21); 14000.0 (18); 4000.0 (17); 58000.0 (17) | GDP from Durable Manufacturing sector for the geography and time period. |
| `gdp_private` | `DOUBLE` | 0.0000 | 49224 | min 0, max 24615614000000 | 0.0 (66); 1073669000.0 (4); 1125102000.0 (4); 1166129000.0 (4); 1263812000.0 (4) | GDP from Private sector for the geography and time period. |
| `gdp_nondurable_manufacturing` | `DOUBLE` | 0.0000 | 36386 | min 0, max 1328506000000 | 0.0 (8122); 1000.0 (18); 2000.0 (17); 5000.0 (16); 110000.0 (13) | GDP from Nondurable Manufacturing sector for the geography and time period. |
| `gdp_wholesale_trade` | `DOUBLE` | 0.0000 | 35181 | min 0, max 1653014000000 | 0.0 (11255); 10000.0 (7); 5000.0 (7); 10607000.0 (6); 12407000.0 (6) | GDP from Wholesale Trade sector for the geography and time period. |
| `gdp_retail_trade` | `DOUBLE` | 0.0000 | 44178 | min 0, max 1772380000000 | 0.0 (1177); 59502000.0 (7); 106515000.0 (5); 23396000.0 (5); 2356000.0 (5) | GDP from Retail Trade sector for the geography and time period. |
| `gdp_transportation` | `DOUBLE` | 0.0000 | 31017 | min 0, max 943734000000 | 0.0 (16203); 11725000.0 (6); 14043000.0 (6); 19227000.0 (6); 8748000.0 (6) | GDP from Transportation sector for the geography and time period. |
| `gdp_information` | `DOUBLE` | 0.0000 | 31267 | min 0, max 1477938000000 | 0.0 (9231); 1000.0 (17); 10000.0 (16); 18000.0 (14); 2000.0 (14) | GDP from Information sector for the geography and time period. |
| `gdp_finance_insurance` | `DOUBLE` | 0.0000 | 37886 | min 0, max 2015595000000 | 0.0 (6318); 18423000.0 (7); 40318000.0 (7); 100385000.0 (6); 2000.0 (6) | GDP from Financial and Insurance sector for the geography and time period. |
| `gdp_real_estate` | `DOUBLE` | 0.0000 | 41134 | min 0, max 3796022000000 | 0.0 (6784); 166591000.0 (5); 60446000.0 (5); 100251000.0 (4); 100274000.0 (4) | GDP from Real Estate sector for the geography and time period. |
| `gdp_professional_scientific` | `DOUBLE` | 0.0000 | 31332 | min 0, max 2221972000000 | 0.0 (13519); 21247000.0 (8); 3720000.0 (8); 3777000.0 (8); 12504000.0 (7) | GDP from Professional Scientific sector for the geography and time period. |
| `gdp_professional_management` | `DOUBLE` | 0.0000 | 18496 | min 0, max 503129000000 | 0.0 (29872); 2314000.0 (12); 2224000.0 (10); 2640000.0 (10); 3893000.0 (8) | GDP from Professional Management sector for the geography and time period. |
| `gdp_professional_admin_support` | `DOUBLE` | 0.0000 | 31691 | min 0, max 886601000000 | 0.0 (12487); 101000.0 (7); 102000.0 (7); 1803000.0 (7); 1941000.0 (7) | GDP from Professional Admin Support sector for the geography and time period. |
| `gdp_education_all` | `DOUBLE` | 0.0000 | 41420 | min 0, max 2350905000000 | 0.0 (4518); 1118000.0 (5); 1205000.0 (5); 124444000.0 (5); 15753000.0 (5) | GDP from Education sector for the geography and time period. |
| `gdp_health` | `DOUBLE` | 0.0000 | 30870 | min 0, max 2038867000000 | 0.0 (17713); 4217000.0 (5); 59000.0 (5); 100000.0 (4); 100507000.0 (4) | GDP from Health sector for the geography and time period. |
| `gdp_arts_entertainment` | `DOUBLE` | 0.0000 | 23922 | min 0, max 299724000000 | 0.0 (10211); 18000.0 (35); 4000.0 (34); 11000.0 (33); 15000.0 (31) | GDP from Arts and Entertainment sector for the geography and time period. |
| `gdp_accomodation_food` | `DOUBLE` | 0.0000 | 34486 | min 0, max 911750000000 | 0.0 (10011); 1757000.0 (7); 22835000.0 (7); 1700000.0 (6); 18219000.0 (6) | GDP from Accommodation and Food sector for the geography and time period. |
| `gdp_other` | `DOUBLE` | 0.0000 | 37291 | min 0, max 589391000000 | 0.0 (4748); 16096000.0 (7); 32488000.0 (7); 4501000.0 (7); 8493000.0 (7) | GDP from Other sector for the geography and time period. |
| `gdp_gov_enterprises` | `DOUBLE` | 0.0000 | 47271 | min 0, max 3105093000000 | 0.0 (66); 243122000.0 (6); 142179000.0 (5); 224036000.0 (5); 102684000.0 (4) | GDP from Government Enterprises sector for the geography and time period. |
| `gdp_natural_resources_all` | `DOUBLE` | 0.0000 | 36174 | min 0, max 750558000000 | 0.0 (10674); 8950000.0 (8); 23306000.0 (7); 10358000.0 (6); 14629000.0 (6) | GDP from Natural Resources (composite) sector for the geography and time period. |
| `gdp_trade_all` | `DOUBLE` | 0.0000 | 37225 | min 0, max 3425394000000 | 0.0 (11359); 100033000.0 (5); 109225000.0 (5); 40383000.0 (5); 52843000.0 (5) | GDP from Trade (composite) sector for the geography and time period. |
| `gdp_transport_utilities_all` | `DOUBLE` | 0.0000 | 27120 | min 0, max 1390249000000 | 0.0 (22610); 138896000.0 (6); 28702000.0 (6); 10318000.0 (5); 11978000.0 (5) | GDP from Transport and Utilities (composite) sector for the geography and time period. |
| `gdp_manufacturing_info_all` | `DOUBLE` | 0.0000 | 38898 | min 0, max 4318385000000 | 0.0 (8876); 10086000.0 (5); 10186000.0 (4); 104837000.0 (4); 1075000.0 (4) | GDP from Manufacturing and Information (composite) sector for the geography and time period. |
| `gdp_private_goods_producing_industries` | `DOUBLE` | 0.0000 | 42384 | min 0, max 4746944000000 | 0.0 (7282); 409152000.0 (5); 140159000.0 (4); 150497000.0 (4); 159444000.0 (4) | GDP from Private Goods Producing Industries sector for the geography and time period. |
| `gdp_private_services_providing_industries` | `DOUBLE` | 0.0000 | 42719 | min 0, max 19868671000000 | 0.0 (7282); 1428569000.0 (4); 2957115000.0 (4); 442437000.0 (4); 505882000.0 (4) | GDP from Private Services Providing Industries sector for the geography and time period. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_gdp.sql:75:from metro_deep_dive.silver.bea_regional_cagdp2_wide`
   - `scripts/etl/gold/gold_economy_wide.sql:117:from metro_deep_dive.silver.bea_regional_cagdp2_wide`
   - `scripts/etl/silver/bea_cagdp2_silver.R:157:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cagdp2_wide"),`

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
