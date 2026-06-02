# Data Dictionary: gold.economics_labor_wide

## Overview
- **Table**: `gold.economics_labor_wide`
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
| `working_age_pop` | `DOUBLE` | 0.0000 | 34061 | min 37, max 30431073 | 21747.0 (8); 12292.0 (7); 13684.0 (7); 18968.0 (7); 25771.0 (7) | Population of working age (16+), used as denominator for labor force participation rate. |
| `labor_force` | `DOUBLE` | 0.3530 | 29937 | min 0, max 19471001 | NULL (178); 0.0 (11); 2411.0 (9); 3502.0 (9); 3953.0 (9) | Total Labor Force (employed + unemployed), used as numerator for labor force participation rate. |
| `lfpr` | `DOUBLE` | 0.3530 | 43112 | min 0, max 4.4285714 | NULL (178); 0.0 (11); 0.6666666666666666 (5); 0.55 (4); 0.7155966420827244 (4) | Labor Force Participation Rate, share of population 16+ in labor force. Ratio of in labor force to pop 16plus. |
| `lfpr_growth_5yr` | `DOUBLE` | 41.9956 | 25138 | min -1, max 6.3809524 | NULL (21175); -1.0 (11); -0.00010886011528372146 (2); -0.00012137095340048361 (2); -0.000128185589388605 (2) | 5-year growth rate in labor force participation rate. |
| `lfpr_cagr_5yr` | `DOUBLE` | 41.9956 | 25138 | min -1, max 0.4914973 | NULL (21175); -1.0 (11); -0.00012799295947241163 (2); -0.0001326351003696491 (2); -0.00013381142043999983 (2) | 5-year compound annual growth rate (CAGR) in labor force participation rate. |
| `employed` | `DOUBLE` | 0.3530 | 29353 | min 0, max 18621929 | NULL (178); 0.0 (11); 2693.0 (10); 4535.0 (10); 3928.0 (9) | Total Employed Persons, used as numerator for employment-population ratio and unemployment rate in ACS. |
| `jobs_to_pop_ratio` | `DOUBLE` | 0.3530 | 43129 | min 0, max 3.962963 | NULL (178); 0.0 (11); 0.5 (8); 0.3333333333333333 (3); 0.3652448657187994 (3) | Ratio of employed to population (i.e., number of people with a job divided by total population). |
| `unemployed` | `DOUBLE` | 0.3530 | 10061 | min 0, max 1920778 | NULL (178); 23.0 (72); 30.0 (70); 49.0 (68); 38.0 (67) | Total Unemployed Persons, used as numerator for unemployment rate in ACS. |
| `pct_unemployment_rate` | `DOUBLE` | 0.3530 | 11991 |  | 0.035 (873); 0.036000000000000004 (845); 0.034 (839); 0.040999999999999995 (835); 0.037000000000000005 (831) | Percentage of the labor force that is unemployed. |
| `unemployment_rate_change_1yr` | `DOUBLE` | 8.8572 | 11478 |  | NULL (4466); 0.0 (1624); -0.0020000000000000018 (1544); -0.0010000000000000009 (1258); -0.0030000000000000027 (1116) | Unemployment rate change from previous year. |
## Data Quality Notes
- Columns with non-zero null rates: labor_force=0.353%, lfpr=0.353%, lfpr_growth_5yr=41.9956%, lfpr_cagr_5yr=41.9956%, employed=0.353%, jobs_to_pop_ratio=0.353%, unemployed=0.353%, pct_unemployment_rate=0.353%, unemployment_rate_change_1yr=8.8572%
- Key uniqueness check for recommended PK (`geo_level + geo_id + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_labor.sql:4:create or replace table metro_deep_dive.gold.economics_labor_wide as `

## Known Gaps / To-Dos
- Add business definitions for high-priority consumption columns.
- Add automated DQ thresholds for row-count drift and key integrity.
- Add explicit source provenance fields in Gold tables where needed.
