# Data Dictionary: silver.labor_kpi

## Overview
- **Table**: `silver.labor_kpi`
- **Purpose**: Silver labor table (`kpi` type).
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
| `pop_16plus` | `DOUBLE` | 0.0069 | 70459 | min 0, max 270181640 | 0.0 (11027); 65.0 (746); 80.0 (741); 77.0 (739); 47.0 (734) | Total Population, Age 16 and Up. Considered the denominator for ACS Labor Metrics. |
| `in_labor_force` | `DOUBLE` | 0.0069 | 54423 | min 0, max 171493280 | 0.0 (17145); 53.0 (1241); 49.0 (1240); 38.0 (1237); 46.0 (1234) | Total Population in Labor Force, used as basis for labor force participation rate and unemployment rate in ACS. |
| `in_lf_civilian` | `DOUBLE` | 0.0069 | 54223 | min 0, max 170199520 | 0.0 (17517); 53.0 (1253); 38.0 (1241); 49.0 (1239); 30.0 (1235) | Total Population in Civilian Labor Force. |
| `in_lf_armed_forces` | `DOUBLE` | 0.0069 | 52125 | min 0, max 161297160 | 0.0 (18242); 46.0 (1392); 27.0 (1364); 28.0 (1363); 41.0 (1337) | Total Population in Armed Forces Labor Force. |
| `not_in_labor_force` | `DOUBLE` | 0.0069 | 13916 | min 0, max 15249189 | 0.0 (128203); 2.0 (13467); 3.0 (12219); 4.0 (11942); 5.0 (11384) | Total Population Not in Labor Force, used as numerator for not in labor force rate in ACS. |
| `employed` | `DOUBLE` | 0.0069 | 39939 | min 0, max 98688351 | 0.0 (17315); 35.0 (1752); 39.0 (1740); 28.0 (1731); 34.0 (1718) | Total Employed Persons, used as numerator for employment-population ratio and unemployment rate in ACS. |
| `unemployed` | `DOUBLE` | 0.0069 | 41915 | min -320178, max 72804934 | 0.0 (13505); 1.0 (2554); 4.0 (2496); 12.0 (2468); 3.0 (2454) | Total Unemployed Persons, used as numerator for unemployment rate in ACS. |
| `lfpr` | `DOUBLE` | 0.0069 | 604128 |  | -nan (11027); 1.0 (6288); 0.0 (6118); 0.5 (2478); 0.6666666666666666 (1857) | Labor Force Participation Rate, share of population 16+ in labor force. Ratio of in labor force to pop 16plus. |
| `unemp_rate` | `DOUBLE` | 1.6862 | 604126 | min -5066, max 1 | NULL (17215); 1.0 (6288); 0.0 (2478); 0.5 (1857); 0.3333333333333333 (1248) | Unemployment Rate, derived from ACS counts. Unemployment / In Labor Force. Note some values are >1 due to data quality issues in source ACS tables. |
| `emp_pop_ratio` | `DOUBLE` | 0.0069 | 604128 |  | -nan (11027); 0.0 (6288); 1.0 (6118); 0.5 (2478); 0.3333333333333333 (1857) | Ratio of Employed Persons to Population 16 and Up, used as employment-population ratio in ACS. |
| `unemp_rate_civ` | `DOUBLE` | 1.7226 | 604769 | min -5066, max 1060.4285714 | NULL (17587); 1.0 (5696); 0.0 (2475); 0.5 (1830); 0.3333333333333333 (1245) | Unemployment Rate for Civilian Labor Force, derived from ACS counts. Unemployed / In LF Civilian. Note some values are >1 due to data quality issues in source ACS tables. Also note some values are >100% due to data quality issues in source ACS tables. Consider using unemp_rate instead of this metric for analysis given the data quality issues with this one. |
| `occ_total_emp` | `DOUBLE` | 0.0069 | 52125 | min 0, max 161297160 | 0.0 (18242); 46.0 (1392); 27.0 (1364); 28.0 (1363); 41.0 (1337) | Total Population, Occupational Eployment. Considered the denominator for ACS Occupational Employment Metrics. |
| `occ_mgmt_business_sci_arts` | `DOUBLE` | 0.0069 | 31419 | min 0, max 68788669 | 0.0 (41659); 9.0 (4620); 10.0 (4577); 8.0 (4513); 7.0 (4426) | Population count for Management, Business, Science, and Arts Occupations. |
| `occ_service` | `DOUBLE` | 0.0069 | 21410 | min 0, max 27489501 | 0.0 (59347); 9.0 (6327); 8.0 (6273); 10.0 (6200); 6.0 (6062) | Population count for Services Occupations. |
| `occ_sales_office` | `DOUBLE` | 0.0069 | 23651 | min 0, max 35440563 | 0.0 (53449); 9.0 (5732); 10.0 (5681); 8.0 (5672); 6.0 (5620) | Population count for Sales and Office Occupations. |
| `occ_nat_resources_const_maint` | `DOUBLE` | 0.0069 | 15213 | min 0, max 13773265 | 0.0 (73460); 8.0 (8155); 9.0 (8106); 10.0 (7966); 7.0 (7695) | Population count for Natural Resources, Construction, and Maintenance Occupations. |
| `occ_prod_transp_material` | `DOUBLE` | 0.0069 | 18399 | min 0, max 20842673 | 0.0 (68973); 9.0 (6860); 8.0 (6645); 10.0 (6633); 7.0 (6406) | Population count for Production, Transportation, and Material Moving Occupations. |
| `pct_occ_mgmt_business_sci_arts` | `DOUBLE` | 0.0069 | 500650 |  | 0.0 (23417); -nan (18242); 1.0 (4910); 0.3333333333333333 (2839); 0.25 (2516) | Percent of Occupational Employment in Management, Business, Science, and Arts Occupations. Share / percentage; denominator is occ_total_emp. (from silver.kpi_dictionary). |
| `pct_occ_service` | `DOUBLE` | 0.0069 | 454403 |  | 0.0 (41105); -nan (18242); 0.2 (2330); 1.0 (2245); 0.16666666666666666 (2194) | Percent of Occupational Employment in Service Occupations. Share / percentage; denominator is occ_total_emp. (from silver.kpi_dictionary). |
| `pct_occ_sales_office` | `DOUBLE` | 0.0069 | 444401 |  | 0.0 (35207); -nan (18242); 0.2 (2697); 0.25 (2677); 0.16666666666666666 (2056) | Percent of Occupational Employment in Sales and Office Occupations. Share / percentage; denominator is occ_total_emp. (from silver.kpi_dictionary). |
| `pct_occ_nat_resources_const_maint` | `DOUBLE` | 0.0069 | 437451 |  | 0.0 (55218); -nan (18242); 0.16666666666666666 (1902); 0.14285714285714285 (1841); 0.2 (1739) | Percent of Occupational Employment in Natural Resources, Construction, and Maintenance Occupations. Share / percentage; denominator is occ_total_emp. (from silver.kpi_dictionary). |
| `pct_occ_prod_transp_material` | `DOUBLE` | 0.0069 | 463988 |  | 0.0 (50731); -nan (18242); 0.25 (1982); 0.2 (1950); 1.0 (1881) | Percent of Occupational Employment in Production, Transportation, and Material Moving Occupations. Share / percentage; denominator is occ_total_emp. (from silver.kpi_dictionary). |
| `ind_total_emp` | `DOUBLE` | 0.0069 | 52125 | min 0, max 161297160 | 0.0 (18242); 46.0 (1392); 27.0 (1364); 28.0 (1363); 41.0 (1337) | Total Population, Industry Employment. Considered the denominator for ACS Industry Employment Metrics. Note this is the same as occ_total_emp, just from a different source table in ACS |
| `ind_ag_mining` | `DOUBLE` | 0.0069 | 6514 | min 0, max 2852402 | 0.0 (289212); 2.0 (17358); 3.0 (15525); 4.0 (15459); 9.0 (15364) | Population count for Agriculture, Mining, Quarrying, Oil and Gas Extraction industries. From the ACS table IND_AG_Mining, which is the sum of the following ACS industry categories: Agriculture, Forestry, Fishing and Hunting; Mining, Quarrying, and Oil and Gas Extraction. |
| `ind_construction` | `DOUBLE` | 0.0069 | 13062 | min 0, max 11167040 | 0.0 (109876); 4.0 (10921); 6.0 (10902); 5.0 (10828); 8.0 (10705) | Population count for Construction. From the ACS table IND_CONSTRUCTION, which corresponds to the ACS industry category Construction. |
| `ind_manufacturing` | `DOUBLE` | 0.0069 | 16549 | min 0, max 15940000 | 0.0 (108029); 6.0 (8366); 8.0 (8334); 4.0 (8212); 2.0 (8136) | Population count for Manufacturing. From the ACS table IND_MANUFACTURING, which corresponds to the ACS industry category Manufacturing. |
| `ind_wholesale` | `DOUBLE` | 0.0069 | 8641 | min 0, max 4042867 | 0.0 (253072); 2.0 (21822); 3.0 (18910); 4.0 (17507); 5.0 (16223) | Population count for Wholesale Industries. From the ACS table IND_WHOLESALE, which corresponds to the ACS industry category Wholesale Trade. |
| `ind_retail` | `DOUBLE` | 0.0069 | 17285 | min 0, max 17463378 | 0.0 (86509); 6.0 (8387); 8.0 (8298); 7.0 (8203); 9.0 (8161) | Population count for Retail Industries. From the ACS table IND_RETAIL, which corresponds to the ACS industry category Retail Trade. |
| `ind_transport_util` | `DOUBLE` | 0.0069 | 11871 | min 0, max 9568767 | 0.0 (130157); 2.0 (13584); 4.0 (13074); 6.0 (13065); 3.0 (13025) | Population count for Transportation, Warehousing, and Utilities industries (IND_TRANSPORT_UTIL), combining ACS categories Transportation and Warehousing; Utilities. |
| `ind_information` | `DOUBLE` | 0.0069 | 7783 | min 0, max 3173300 | 0.0 (343828); 2.0 (24563); 3.0 (21058); 4.0 (18722); 5.0 (16944) | Population count for Information Industry. From the ACS table IND_INFORMATION, which corresponds to the ACS industry category Information. |
| `ind_finance_real` | `DOUBLE` | 0.0069 | 13121 | min 0, max 10783159 | 0.0 (170331); 2.0 (17522); 3.0 (15222); 4.0 (15063); 5.0 (13828) | Population count for Finance, Insurance, Real Estate, and Rental and Leasing industries (IND_FINANCE_REAL), combining ACS categories Finance and Insurance; Real Estate and Rental and Leasing. |
| `ind_professional` | `DOUBLE` | 0.0069 | 17003 | min 0, max 20282450 | 0.0 (124747); 2.0 (14700); 3.0 (12764); 4.0 (12737); 5.0 (11905) | Population count for Professional, Scientific, Management, Administrative, and Waste Management industries (IND_PROFESSIONAL). |
| `ind_educ_health` | `DOUBLE` | 0.0069 | 24226 | min 0, max 37913663 | 0.0 (51451); 9.0 (5539); 8.0 (5378); 10.0 (5297); 6.0 (5228) | Population count for Education and Health Services industries (IND_EDUC_HEALTH), combining ACS categories Educational Services; Health Care and Social Assistance. |
| `ind_arts_accomm_food` | `DOUBLE` | 0.0069 | 15972 | min 0, max 14962299 | 0.0 (118324); 2.0 (12409); 3.0 (11659); 4.0 (11444); 5.0 (11108) | Population count for Arts, Entertainment, Recreation, Accommodation, and Food Services industries (IND_ARTS_ACCOMM_FOOD), combining ACS categories Arts, Entertainment, and Recreation; Accommodation and Food Services. |
| `ind_other_services` | `DOUBLE` | 0.0069 | 11420 | min 0, max 7588496 | 0.0 (146740); 2.0 (16720); 3.0 (14852); 4.0 (14508); 5.0 (13908) | Population count for Other Services. From the ACS table IND_OTHER_SERVICES, which corresponds to the ACS industry category Other Services (except Public Administration). |
| `ind_public_admin` | `DOUBLE` | 0.0069 | 11649 | min 0, max 7624243 | 0.0 (146953); 2.0 (16572); 3.0 (14799); 4.0 (14675); 5.0 (14017) | Population count for Public Administration. From the ACS table IND_PUBLIC_ADMIN, which corresponds to the ACS industry category Public Administration. Note this industry category includes public administration jobs in various government departments and agencies, so may be less useful for analysis focused on specific types of government jobs (e.g. education administration jobs, public health administration jobs, etc.). Consider using more specific industry categories from source ACS tables if analysis focused on specific types of government jobs. Also note this industry category includes public administration jobs at all levels of government (federal, state, local), so may be less useful for analysis focused on specific levels of government jobs. Consider using more specific industry categories from source ACS tables if analysis focused on specific levels of government jobs. Also note this industry category includes some non-government public administration jobs (e.g. public administration jobs in non-profits), so may be less useful for analysis focused specifically on government jobs. Consider using more specific industry categories from source ACS tables if analysis focused specifically on government jobs. |
| `pct_ind_ag_mining` | `DOUBLE` | 0.0069 | 329223 |  | 0.0 (270970); -nan (18242); 1.0 (1417); 0.125 (776); 0.1 (758) | Percent of Industry Employment in Agriculture, Mining, Quarrying, Oil and Gas Extraction Industries. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_construction` | `DOUBLE` | 0.0069 | 404911 |  | 0.0 (91634); -nan (18242); 0.09090909090909091 (1307); 0.1 (1290); 0.07692307692307693 (1273) | Percent of Industry Employment in Construction. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_manufacturing` | `DOUBLE` | 0.0069 | 451740 |  | 0.0 (89787); -nan (18242); 0.16666666666666666 (1383); 0.2 (1371); 0.14285714285714285 (1308) | Percent of Industry Employment in Manufacturing. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_wholesale` | `DOUBLE` | 0.0069 | 326846 |  | 0.0 (234830); -nan (18242); 0.03333333333333333 (643); 0.038461538461538464 (631); 0.037037037037037035 (627) | Percent of Industry Employment in Wholesale. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_retail` | `DOUBLE` | 0.0069 | 416487 |  | 0.0 (68267); -nan (18242); 0.125 (1829); 0.1111111111111111 (1667); 0.14285714285714285 (1637) | Percent of Industry Employment in Retail. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_transport_util` | `DOUBLE` | 0.0069 | 381118 |  | 0.0 (111915); -nan (18242); 0.07142857142857142 (1168); 0.08333333333333333 (1161); 0.07692307692307693 (1144) | Percent of Industry Employment in Transportation and Utilities. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_information` | `DOUBLE` | 0.0069 | 300029 |  | 0.0 (325586); -nan (18242); 0.02564102564102564 (406); 0.02702702702702703 (399); 0.022222222222222223 (398) | Percent of Industry Employment in Information. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_finance_real` | `DOUBLE` | 0.0069 | 385772 |  | 0.0 (152089); -nan (18242); 0.05555555555555555 (892); 0.0625 (871); 0.05263157894736842 (851) | Percent of Industry Employment in Finance and Real Estate. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_professional` | `DOUBLE` | 0.0069 | 421673 |  | 0.0 (106505); -nan (18242); 0.07692307692307693 (1033); 0.06666666666666667 (1023); 0.08333333333333333 (1016) | Percent of Industry Employment in Professional and Business Services. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_educ_health` | `DOUBLE` | 0.0069 | 457769 |  | 0.0 (33209); -nan (18242); 0.25 (2744); 1.0 (2593); 0.2 (2529) | Percent of Industry Employment in Education and Health Services. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_arts_accomm_food` | `DOUBLE` | 0.0069 | 417545 |  | 0.0 (100082); -nan (18242); 0.07692307692307693 (1106); 0.08333333333333333 (1099); 0.1 (1093) | Percent of Industry Employment in Arts, Entertainment, and Recreation. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_other_services` | `DOUBLE` | 0.0069 | 362395 |  | 0.0 (128498); -nan (18242); 0.05263157894736842 (1076); 0.05555555555555555 (1038); 0.045454545454545456 (1037) | Percent of Industry Employment in Other Services. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
| `pct_ind_public_admin` | `DOUBLE` | 0.0069 | 382246 |  | 0.0 (128711); -nan (18242); 0.06666666666666667 (896); 0.058823529411764705 (882); 0.043478260869565216 (877) | Percent of Industry Employment in Public Administration. Share / percentage; denominator is ind_total_emp. (from silver.kpi_dictionary). |
## Data Quality Notes
- Columns with non-zero null rates: pop_16plus=0.0069%, in_labor_force=0.0069%, in_lf_civilian=0.0069%, in_lf_armed_forces=0.0069%, not_in_labor_force=0.0069%, employed=0.0069%, unemployed=0.0069%, lfpr=0.0069%, unemp_rate=1.6862%, emp_pop_ratio=0.0069% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_labor_silver.R:270:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="labor_kpi"),`

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
