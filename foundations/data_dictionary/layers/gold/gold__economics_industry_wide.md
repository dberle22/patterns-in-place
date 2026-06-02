# Data Dictionary: gold.economics_industry_wide

## Overview
- **Table**: `gold.economics_industry_wide`
- **Purpose**: Gold layer analytical output table.
- **Row count**: 57,274
- **KPI applicability**: Gold output table; may contain derived KPI fields.

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
| `real_gdp_total` | `DOUBLE` | 0.0000 | 48677 | min 0, max 22671096000000 | 0.0 (66); 1291355000.0 (5); 1047702000.0 (4); 1162632000.0 (4); 1232928000.0 (4) | Total real GDP for the geographic area and time period, from BEA regional data. |
| `real_gdp_natural_resources` | `DOUBLE` | 0.0000 | 35213 | min 0, max 533936920000 | 0.0 (10674); 11237000.0 (6); 13982000.0 (6); 14675000.0 (6); 18161000.0 (6) | Real GDP for the Natural Resources Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_manufacturing` | `DOUBLE` | 0.0000 | 41803 | min 0, max 2317923000000 | 0.0 (4905); 10000.0 (6); 8000.0 (6); 92000.0 (6); 10166000.0 (5) | Real GDP for the Manufacturing Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_construction` | `DOUBLE` | 0.0000 | 39390 | min 0, max 887608000000 | 0.0 (4795); 5940000.0 (8); 10986000.0 (6); 15007000.0 (6); 56503000.0 (6) | Real GDP for the Construction Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_trade` | `DOUBLE` | 0.0000 | 36600 | min 0, max 2484733900000 | 0.0 (11359); 118164000.0 (5); 141981000.0 (5); 52212000.0 (5); 102816000.0 (4) | Real GDP for the Wholesale and Retail Trade Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_transportation` | `DOUBLE` | 0.0000 | 30295 | min 0, max 706954000000 | 0.0 (16203); 33334000.0 (7); 11350000.0 (6); 11528000.0 (6); 27792000.0 (6) | Real GDP for the Transportation Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_information` | `DOUBLE` | 0.0000 | 30599 | min 0, max 1605851000000 | 0.0 (9231); 21000.0 (18); 1000.0 (17); 2000.0 (14); 4000.0 (14) | Real GDP for the Information Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_fire` | `DOUBLE` | 0.0000 | 42353 | min 0, max 4683675000000 | 0.0 (4983); 145390000.0 (5); 150642000.0 (5); 174069000.0 (5); 106141000.0 (4) | Real GDP for the Finance, Insurance, and Real Estate Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_professional` | `DOUBLE` | 0.0000 | 38332 | min 0, max 3397301000000 | 0.0 (3531); 3000.0 (7); 4383000.0 (7); 105000.0 (6); 13556000.0 (6) | Real GDP for the Professional, Scientific, and Management Services Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_edu_health` | `DOUBLE` | 0.0000 | 40771 | min 0, max 2021153000000 | 0.0 (4518); 174647000.0 (6); 176000.0 (6); 12100000.0 (5); 123207000.0 (5) | Real GDP for the Educational and Health Services Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_leisure` | `DOUBLE` | 0.0000 | 34819 | min 0, max 891815000000 | 0.0 (9469); 13000.0 (12); 16000.0 (11); 9000.0 (10); 1000.0 (9) | Real GDP for the Leisure and Hospitality Industry for the geographic area and time period, from BEA regional data. |
| `real_gdp_gov` | `DOUBLE` | 0.0000 | 46758 | min 0, max 2582255000000 | 0.0 (66); 118272000.0 (5); 182999000.0 (5); 217825000.0 (5); 408821000.0 (5) | Real GDP for the Government Industry for the geographic area and time period, from BEA regional data. |
| `sector_sum` | `DOUBLE` | 0.0000 | 48671 | min 0, max 22046660000000 | 0.0 (66); 1086191000.0 (4); 1239731000.0 (4); 1241494000.0 (4); 1474888000.0 (4) | Sum of all Real GDPs for the geographic area and time period, from BEA regional data. |
| `calc_real_gdp_other` | `DOUBLE` | 0.0000 | 46169 | min -3364944000, max 752181620000 | 0.0 (66); 25994000.0 (6); 45237000.0 (6); 63707000.0 (6); 72432000.0 (6) | Real GDP for the "Other Services" Industry for the geographic area and time period, calculated as the difference between real_gdp_total and sector_sum. |
| `pct_real_gdp_natural_resources` | `DOUBLE` | 0.0000 | 40090 |  | 0.0 (10608); -nan (66); 0.00023382027765575362 (2); 0.00025871421063795007 (2); 0.00027198913259063524 (2) | Percentage of Real GDP for the Natural Resources Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_manufacturing` | `DOUBLE` | 0.0000 | 44362 |  | 0.0 (4839); -nan (66); 0.0008406536318126004 (2); 0.0009340613774349977 (2); 0.001308300497051173 (2) | Percentage of Real GDP for the Manufacturing Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_construction` | `DOUBLE` | 0.0000 | 44462 |  | 0.0 (4729); -nan (66); 0.004587720523472292 (2); 0.006557404020111722 (2); 0.007438501252163227 (2) | Percentage of Real GDP for the Construction Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_trade` | `DOUBLE` | 0.0000 | 38905 |  | 0.0 (11293); -nan (66); 0.010340896770347193 (2); 0.011111784519859742 (2); 0.011181512453121984 (2) | Percentage of Real GDP for the Wholesale and Retail Trade Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_transportation` | `DOUBLE` | 0.0000 | 34553 |  | 0.0 (16137); -nan (66); 0.0003890499954895852 (2); 0.000993455780160484 (2); 0.0012708676693486715 (2) | Percentage of Real GDP for the Transportation Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_information` | `DOUBLE` | 0.0000 | 40041 |  | 0.0 (9165); -nan (66); 0.00046306403483129015 (2); 0.0005357101778224229 (2); 0.0006276552463660274 (2) | Percentage of Real GDP for the Information Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_fire` | `DOUBLE` | 0.0000 | 44132 |  | 0.0 (4917); -nan (66); 0.0025552374427359114 (2); 0.004607431619459697 (2); 0.007910972412065164 (2) | Percentage of Real GDP for the Finance, Insurance, Real Estate Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_professional` | `DOUBLE` | 0.0000 | 45656 |  | 0.0 (3465); -nan (66); 0.0015215332576264515 (2); 0.00154332518521149 (2); 0.00158115892246609 (2) | Percentage of Real GDP for the Professional, Scientific, and Technical Services Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_edu_health` | `DOUBLE` | 0.0000 | 44939 |  | 0.0 (4452); -nan (66); 0.0003859912123977272 (2); 0.0004003168214272374 (2); 0.00048537590222722844 (2) | Percentage of Real GDP for the Educational and Health Services Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_leisure` | `DOUBLE` | 0.0000 | 39851 |  | 0.0 (9403); -nan (66); 0.00028434582582030366 (2); 0.00237503957280735 (2); 0.0043289914145101015 (2) | Percentage of Real GDP for the Leisure and Hospitality Industry for the geographic area and time period, from BEA regional data. |
| `pct_real_gdp_gov` | `DOUBLE` | 0.0000 | 49033 |  | -nan (66); 0.011030856115526287 (2); 0.011315654411064822 (2); 0.014076266572605071 (2); 0.014709317237897535 (2) | Percentage of Real GDP for the Government Industry for the geographic area and time period, from BEA regional data. |
| `pct_calc_real_gdp_other` | `DOUBLE` | 0.0000 | 49033 |  | -nan (66); -0.00036832435458395693 (2); -0.00046048122843446036 (2); -0.0005418729995629883 (2); -0.0011061286166589085 (2) | Percentage of Real GDP for the Other Industry for the geographic area and time period, from BEA regional data. |
| `industry_concentration_hhi` | `DOUBLE` | 0.0000 | 49033 |  | -nan (66); 0.10219313942181639 (2); 0.10362014040034506 (2); 0.1037600528212887 (2); 0.10537338754516103 (2) | Industry Concentration HHI (Herfindahl-Hirschman Index) for the geographic area and time period, from BEA regional data. Higher values indicate more concentration (less diversity) of industry GDP contributions. |
| `sector_sum_ratio` | `DOUBLE` | 0.0000 | 49033 |  | -nan (66); 0.22286412120320354 (2); 0.22549197756467484 (2); 0.22628174300074494 (2); 0.2552024435855193 (2) | Ratio of the sum of all industry percentages to 100% for the geographic area and time period, from BEA regional data. |
| `sector_sum_ratio_quality_flag` | `VARCHAR` | 0.0000 | 2 | len 7-10 | Non Bug (57112); Sector Bug (162) | Quality flag indicating whether the sector sum ratio is within expected bounds (i.e., not a bug in the data processing). |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_industry.sql:5:create or replace table metro_deep_dive.gold.economics_industry_wide as `

## Known Gaps / To-Dos
- Add business definitions for high-priority consumption columns.
- Add automated DQ thresholds for row-count drift and key integrity.
- Add explicit source provenance fields in Gold tables where needed.
