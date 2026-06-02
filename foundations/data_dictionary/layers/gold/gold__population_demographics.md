# Data Dictionary: gold.population_demographics

## Overview
- **Table**: `gold.population_demographics`
- **Purpose**: Gold layer analytical output table.
- **Row count**: 1,020,930
- **KPI applicability**: Gold output table; may contain derived KPI fields.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
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
| `pop_growth_1yr` | `DOUBLE` | 12.4866 | 571936 | min -1, max 402.5 | NULL (127479); 0.0 (5701); -1.0 (1409); -0.14285714285714285 (378); -0.2 (373) | 1-year population growth rate (i.e., the percentage change in population from the previous year). |
| `pop_growth_3yr` | `DOUBLE` | 28.8685 | 520706 | min -1, max 1089 | NULL (294727); -1.0 (2554); 0.0 (2164); -0.3333333333333333 (316); -0.25 (313) | 3-year population growth rate (i.e., the percentage change in population over 3 years). |
| `pop_growth_5yr` | `DOUBLE` | 45.1145 | 427209 | min -1, max 1556 | NULL (460587); -1.0 (2606); 0.0 (1158); -0.3333333333333333 (226); -0.5 (206) | 5-year population growth rate (i.e., the percentage change in population over 5 years). |
| `pop_growth_10yr` | `DOUBLE` | 81.7148 | 158448 | min -1, max 423 | NULL (834251); -1.0 (1056); 0.0 (336); -0.5 (80); -0.3333333333333333 (77) | 10-year compound annual growth rate (CAGR) in population. |
| `pop_cagr_3yr` | `DOUBLE` | 28.8685 | 520706 | min -1, max 3.0502824 | NULL (294727); -1.0 (2554); 0.0 (2164); -0.07789208851827223 (316); -0.05591248870509802 (313) | 3-year compound annual growth rate (CAGR) in population. |
| `pop_cagr_5yr` | `DOUBLE` | 45.1145 | 427209 | min -1, max 3.3496842 | NULL (460587); -1.0 (2606); 0.0 (1158); -0.07789208851827223 (226); -0.12944943670387588 (206) | 5-year compound annual growth rate (CAGR) in population. |
| `pop_cagr_10yr` | `DOUBLE` | 81.7148 | 157517 |  | NULL (834251); -1.0 (794); inf (401); 0.0 (346); -nan (262) | 10-year compound annual growth rate (CAGR) in population. |
| `median_age` | `DOUBLE` | 1.7624 | 5492 | min 0, max 105.1 | NULL (17993); 40.5 (5948); 40.8 (5846); 40.3 (5768); 40.6 (5615) | Median age of the population. |
| `pct_age_under_18` | `DOUBLE` | 0.0000 | 601926 |  | 0.0 (33984); -nan (11017); 0.25 (1448); 0.2 (1318); 0.16666666666666666 (957) | Percent of population that is under age 18. |
| `pct_age_18_64` | `DOUBLE` | 0.0000 | 607480 |  | -nan (11017); 1.0 (7291); 0.0 (3902); 0.5 (2440); 0.6666666666666666 (1519) | Percent of population that is 18 to 64 years old. |
| `pct_age_over_64` | `DOUBLE` | 0.0000 | 611443 |  | 0.0 (19532); -nan (11017); 1.0 (3808); 0.2 (1211); 0.25 (1197) | Percent of population that is over age 64. |
| `dependents_per_worker` | `DOUBLE` | 0.0000 | 567895 |  | -nan (13006); inf (9497); 0.0 (5302); 1.0 (3859); 2.0 (1379) | Number of dependents (ages 0-17 and ages 65+) per worker (ages 18-64). |
| `youth_dependency` | `DOUBLE` | 2.2042 | 499204 | min 0, max 26.0833333 | 0.0 (31661); NULL (22503); 0.5 (3586); 0.3333333333333333 (1999); 1.0 (1699) | Ratio of population ages 0 to 14 to population ages 25 to 54 (prime working age population). |
| `old_age_dependency` | `DOUBLE` | 2.2042 | 541788 | min 0, max 426 | NULL (22503); 0.0 (17048); 0.5 (2444); 1.0 (2153); 0.3333333333333333 (1602) | Ratio of population ages 65+ to population ages 25 to 54 (prime working age population). |
| `aging_index` | `DOUBLE` | 0.0000 | 483880 |  | 0.0 (32540); -nan (21043); inf (9506); 1.0 (3592); 0.5 (1832) | Ratio of population ages 65+ to population ages 0 to 14 (child dependency ratio). |
| `pct_white_nh` | `DOUBLE` | 0.0000 | 651344 |  | 1.0 (70841); -nan (11017); 0.0 (10691); 0.9 (383); 0.8333333333333334 (363) | Percent of population that is White alone, Not Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `pct_black_nh` | `DOUBLE` | 0.0000 | 517321 |  | 0.0 (315831); -nan (11017); 1.0 (1106); 0.012987012987012988 (94); 0.015151515151515152 (93) | Percent of population that is Black or African American alone, Not Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `pct_aian_nh` | `DOUBLE` | 0.0000 | 291020 |  | 0.0 (550069); -nan (11017); 1.0 (1206); 0.007751937984496124 (86); 0.0125 (85) | Percent of population that is American Indian and Alaska Native alone, Not Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `pct_asian_nh` | `DOUBLE` | 0.0000 | 398671 |  | 0.0 (425654); -nan (11017); 0.012658227848101266 (108); 0.0136986301369863 (100); 0.015151515151515152 (99) | Percent of population that is Asian alone, Not Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `pct_nhpi_nh` | `DOUBLE` | 0.0000 | 129237 |  | 0.0 (851755); -nan (11017); 0.003787878787878788 (22); 0.0032679738562091504 (20); 0.004524886877828055 (18) | Percent of population that is Native Hawaiian and Other Pacific Islander alone, Not Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `pct_other_nh` | `DOUBLE` | 0.0000 | 229053 |  | 0.0 (704607); -nan (11017); 0.009174311926605505 (47); 0.006211180124223602 (38); 0.0037174721189591076 (36) | Percent of population that is Some other race alone, Not Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `pct_two_plus_nh` | `DOUBLE` | 0.0000 | 460891 |  | 0.0 (217400); -nan (11017); 0.03125 (264); 0.038461538461538464 (256); 0.024390243902439025 (249) | Percent of population that is Two or more races, Not Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `pct_hispanic` | `DOUBLE` | 0.0000 | 562059 |  | 0.0 (179489); -nan (11017); 1.0 (5431); 0.043478260869565216 (230); 0.05263157894736842 (218) | Percent of population that is Hispanic or Latino. Share / percentage; denominator is race_total. (from silver.kpi_dictionary). |
| `diversity_index` | `DOUBLE` | 0.0000 | 840718 |  | 0.0 (78740); -nan (11017); 0.4444444444444444 (216); 0.375 (190); 0.31999999999999984 (165) | Diversity index, calculated as 1 - sum of squares of percent of races, lower score means less diversity, higher score means more diversity. |
| `pct_hs_or_less` | `DOUBLE` | 0.0000 | 641733 |  | -nan (11750); 0.0 (8892); 1.0 (7464); 0.5 (2973); 0.6666666666666666 (915) | Percent of population age 25+ with high school education or less. Share / percentage; denominator is education_total. (from silver.kpi_dictionary). |
| `pct_ba` | `DOUBLE` | 0.0000 | 544390 |  | 0.0 (48312); -nan (11750); 0.125 (1100); 0.1111111111111111 (1008); 0.16666666666666666 (984) | Percent of population age 25+ with Bachelor's degree or higher. Share / percentage; denominator is education_total. (from silver.kpi_dictionary). |
| `pct_ba_plus` | `DOUBLE` | 0.0000 | 611757 |  | 0.0 (34980); -nan (11750); 1.0 (1985); 0.14285714285714285 (1103); 0.125 (1011) | Percent of population age 25+ with Graduate degree or higher. Share / percentage; denominator is education_total. (from silver.kpi_dictionary). |
| `pct_grad_plus` | `DOUBLE` | 0.0000 | 506098 |  | 0.0 (93456); -nan (11750); 0.05555555555555555 (662); 0.058823529411764705 (643); 0.06666666666666667 (641) | Percent of population age 25+ with Graduate degree or higher. Share / percentage; denominator is education_total. (from silver.kpi_dictionary). |
## Data Quality Notes
- Columns with non-zero null rates: pop_growth_1yr=12.4866%, pop_growth_3yr=28.8685%, pop_growth_5yr=45.1145%, pop_growth_10yr=81.7148%, pop_cagr_3yr=28.8685%, pop_cagr_5yr=45.1145%, pop_cagr_10yr=81.7148%, median_age=1.7624%, youth_dependency=2.2042%, old_age_dependency=2.2042%
- Key uniqueness check for recommended PK (`geo_level + geo_id + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_population_wide.sql:6:create or replace table metro_deep_dive.gold.population_demographics as `
   - `scripts/etl/gold/gold_housing_core.sql:49:from metro_deep_dive.gold.population_demographics pd `
   - `scripts/etl/gold/gold_housing_core.sql:56:DESCRIBE metro_deep_dive.gold.population_demographics; -- Contains year, pop, growth`

## Known Gaps / To-Dos
- Add business definitions for high-priority consumption columns.
- Add automated DQ thresholds for row-count drift and key integrity.
- Add explicit source provenance fields in Gold tables where needed.
