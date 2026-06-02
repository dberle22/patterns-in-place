# Data Dictionary: gold.economics_gdp_wide

## Overview
- **Table**: `gold.economics_gdp_wide`
- **Purpose**: Gold layer analytical output table.
- **Row count**: 50,446
- **KPI applicability**: Gold output table; may contain derived KPI fields.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
  - `geo_level + geo_id + year` => rows=50446, distinct=50422, duplicates=24
  - `geo_id + year` => rows=50446, distinct=50422, duplicates=24
  - `geo_level` => rows=50446, distinct=3, duplicates=50443
- **Time coverage**: `year` min=2012, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4221

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (38648); cbsa (11174); state (624) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4221 | len 2-5 | 32000 (24); 45000 (24); 01 (12); 01001 (12); 01003 (12) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 4222 | len 4-59 | Marion, NC (24); Susanville, CA (24); Abbeville County, South Carolina (12); Aberdeen, SD (12); Aberdeen, WA (12) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 12 | min 2012, max 2023 | 2022 (4211); 2023 (4211); 2012 (4203); 2013 (4203); 2020 (4203) | Observation year or period year for the row. |
| `pop_total` | `DOUBLE` | 0.0000 | 35702 | min 43, max 39455353 | 25477.0 (8); 3389.0 (7); 14335.0 (6); 16211.0 (6); 16511.0 (6) | Total population (all ages). |
| `nominal_gdp_total` | `DOUBLE` | 4.7893 | 40782 | min 6288000, max 2296930200000 | NULL (2416); 2502608000.0 (4); 851888000.0 (4); 9628476000.0 (4); 1057030000.0 (3) | Total Nominal GDP, in current dollars. |
| `nominal_gdp_growth_5yr` | `DOUBLE` | 44.4753 | 23943 | min -0.8650248, max 5.4349737 | NULL (22436); -0.00027760493945340546 (2); -0.001396598414595962 (2); -0.001642857589528592 (2); -0.0019435866936867753 (2) | 5-year nominal GDP growth rate (i.e., the percentage change in GDP over 5 years). |
| `nominal_gdp_cagr_5yr` | `DOUBLE` | 44.4753 | 23943 | min -0.3300371, max 0.4511401 | NULL (22436); -0.00027947585277199316 (2); -0.00032878764946953076 (2); -0.00038901989397022163 (2); -0.0004116872184751763 (2) | 5-year nominal GDP compound annual growth rate (CAGR). |
| `nominal_gdp_pc` | `DOUBLE` | 4.7893 | 41021 | min 3077.142552, max 189548060 | NULL (2416); 29081.956995948894 (3); 31344.865426822224 (3); 31603.362764940062 (3); 31777.2061849609 (3) | Per capita nominal GDP (i.e., total nominal GDP divided by total population). |
| `nominal_gdp_pc_growth_5yr` | `DOUBLE` | 44.4753 | 23950 | min -0.845072, max 13.9307821 | NULL (22436); -0.00015571105356292886 (2); -0.0003731373655807843 (2); -0.0006511156453991608 (2); -0.000827836192526019 (2) | 5-year per capita nominal GDP growth rate (i.e., the percentage change in per capita nominal GDP over 5 years). |
| `nominal_gdp_pc_cagr_5yr` | `DOUBLE` | 44.4753 | 23950 | min -0.3113065, max 0.7171827 | NULL (22436); -0.00013025705846259061 (2); -0.00016562209077364276 (2); -0.0002766813159467141 (2); -0.0004395352584974921 (2) | 5-year per capita nominal GDP compound annual growth rate (CAGR). |
| `real_gdp_total` | `DOUBLE` | 4.7893 | 40782 | min 5420000, max 1903894600000 | NULL (2416); 1047702000.0 (4); 1232928000.0 (4); 1418863000.0 (4); 1660722000.0 (4) | Real GDP total (i.e., total real GDP for a given geographic area). |
| `real_gdp_growth_5yr` | `DOUBLE` | 44.4753 | 23943 | min -0.9953508, max 222.2084522 | NULL (22436); -0.00010551862403714256 (2); -0.0001212878821323432 (2); -0.00014708462254922302 (2); -0.00016798244391700285 (2) | 5-year real GDP growth rate (i.e., the percentage change in real GDP over 5 years). |
| `real_gdp_cagr_5yr` | `DOUBLE` | 44.4753 | 23943 | min -0.6584335, max 1.9494574 | NULL (22436); -0.000109358698214157 (2); -0.00011862043601318373 (2); -0.00012327797834754683 (2); -0.00012478084946743184 (2) | 5-year real GDP compound annual growth rate (CAGR). |
| `real_gdp_pc` | `DOUBLE` | 4.7893 | 41046 | min 2714.0161464, max 153650350 | NULL (2416); 100231.46067415731 (2); 100303.92273321211 (2); 101201.9748751094 (2); 103223.47555591779 (2) | Per capita real GDP (i.e., total real GDP divided by population). |
| `real_gdp_pc_growth_5yr` | `DOUBLE` | 44.4753 | 23950 | min -0.9954697, max 218.0774814 | NULL (22436); -0.00019170347304418907 (2); -0.00023468766132942687 (2); -0.0002524549904455399 (2); -0.0003592372424745634 (2) | 5-year per capita real GDP growth rate (i.e., the percentage change in per capita real GDP over 5 years). |
| `real_gdp_pc_cagr_5yr` | `DOUBLE` | 44.4753 | 23950 | min -0.6601982, max 1.9384584 | NULL (22436); -0.00012867418838524713 (2); -0.00015046421351283534 (2); -0.00015842086240158704 (2); -0.00016815093520128332 (2) | 5-year per capita real GDP compound annual growth rate (CAGR). |
| `employed` | `DOUBLE` | 0.3529 | 29353 | min 0, max 18621929 | NULL (178); 0.0 (11); 2693.0 (10); 4535.0 (10); 3928.0 (9) | Total Employed Persons, used as numerator for employment-population ratio and unemployment rate in ACS. |
| `productivity_index` | `DOUBLE` | 4.9479 | 40964 | min 5240.4740614, max 169901260 | NULL (2496); 100006.25818658128 (2); 100016.08815426998 (2); 100063.6855036855 (2); 100076.1421319797 (2) | Productivity index calculated as real GDP per employed person |
| `productivity_growth_5yr` | `DOUBLE` | 44.5546 | 23910 | min -0.9950743, max 249.1911089 | NULL (22476); -0.0002034254487034615 (2); -0.00022242355705629204 (2); -0.00023024883582251426 (2); -0.00024384894788505925 (2) | 5-year real GDP per employed person growth rate (i.e., the percentage change in real GDP per employed person over 5 years). |
| `productivity_cagr_5yr` | `DOUBLE` | 44.5546 | 23910 | min -0.6544641, max 2.0175493 | NULL (22476); -0.00010690502710763994 (2); -0.00010798777299925177 (2); -0.00012156872454915923 (2); -0.00012527641972370773 (2) | 5-year real GDP per employed person compound annual growth rate (CAGR). |
## Data Quality Notes
- Columns with non-zero null rates: nominal_gdp_total=4.7893%, nominal_gdp_growth_5yr=44.4753%, nominal_gdp_cagr_5yr=44.4753%, nominal_gdp_pc=4.7893%, nominal_gdp_pc_growth_5yr=44.4753%, nominal_gdp_pc_cagr_5yr=44.4753%, real_gdp_total=4.7893%, real_gdp_growth_5yr=44.4753%, real_gdp_cagr_5yr=44.4753%, real_gdp_pc=4.7893% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + year`) found 24 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_gdp.sql:4:create or replace table metro_deep_dive.gold.economics_gdp_wide as `

## Known Gaps / To-Dos
- Add business definitions for high-priority consumption columns.
- Add automated DQ thresholds for row-count drift and key integrity.
- Add explicit source provenance fields in Gold tables where needed.
