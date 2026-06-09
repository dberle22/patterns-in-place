# Data Dictionary: silver.disability_kpi

## Overview
- **Table**: `silver.disability_kpi`
- **Purpose**: Silver disability KPI table (`kpi` type).
- **Row count**: 1,891,571
- **KPI applicability**: KPI table (or has KPI dictionary entries).

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1891571, distinct=1891571, duplicates=0
  - `geo_level + geo_id + year` => rows=1891571, distinct=1891571, duplicates=0
  - `geo_id + year` => rows=1891571, distinct=1869428, duplicates=22143
  - `geo_level` => rows=1891571, distinct=9, duplicates=1891562
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=198456

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | tract (1006492); zcta (433172); place (397094); county (41870); cbsa (12085) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 198,456 | len 1-11 | 1 (39); 2 (26); 3 (26); 4 (26); 01001 (25) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 251,188 | len 4-81 | Alexandria city, Virginia (26); Baltimore city, Maryland (26); Bristol city, Virginia (26); Buena Vista city, Virginia (26); Carson City, Nevada (26) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 13 | min 2012, max 2024 | 2024 (154726); 2023 (154720); 2022 (154598); 2021 (154311); 2020 (153657) | Observation year or period year for the row. |
| `disability_total` | `DOUBLE` | 0.0000 | 80,081 | min 0, max 329980753 | 0.0 (21493); 61.0 (627); 74.0 (623); 64.0 (614); 69.0 (609) | Total civilian noninstitutionalized population in the disability-status universe. |
| `disability_with` | `DOUBLE` | 0.0000 | 26,141 | min 0, max 43869797 | 0.0 (40822); 10.0 (3575); 14.0 (3451); 8.0 (3446); 9.0 (3444) | Population with a disability. |
| `disability_without` | `DOUBLE` | 0.0000 | 74,148 | min 0, max 286110956 | 0.0 (23189); 58.0 (750); 56.0 (728); 35.0 (727); 87.0 (726) | Population without a disability. |
| `disability_male_total` | `DOUBLE` | 0.0000 | 52,594 | min 0, max 162271028 | 0.0 (23807); 42.0 (1180); 32.0 (1174); 44.0 (1171); 41.0 (1170) | Male civilian noninstitutionalized population in the disability-status universe. |
| `disability_male_with` | `DOUBLE` | 0.0000 | 18,268 | min 0, max 21240802 | 0.0 (57511); 9.0 (6358); 8.0 (6344); 12.0 (6212); 10.0 (6201) | Male population with a disability. |
| `disability_female_total` | `DOUBLE` | 0.0000 | 53,981 | min 0, max 167709725 | 0.0 (24132); 49.0 (1240); 43.0 (1227); 56.0 (1215); 31.0 (1198) | Female civilian noninstitutionalized population in the disability-status universe. |
| `disability_female_with` | `DOUBLE` | 0.0000 | 18,920 | min 0, max 22628995 | 0.0 (62219); 8.0 (6946); 9.0 (6785); 10.0 (6679); 11.0 (6504) | Female population with a disability. |
| `disability_under_5_total` | `DOUBLE` | 0.0000 | 18,334 | min 0, max 20135140 | 0.0 (118227); 8.0 (7474); 10.0 (7320); 4.0 (7275); 9.0 (7243) | Population under age 5 in the disability-status universe. |
| `disability_under_5_with` | `DOUBLE` | 0.0000 | 1,969 | min 0, max 161265 | 0.0 (1639628); 9.0 (9500); 3.0 (9480); 4.0 (9323); 8.0 (9236) | Population under age 5 with a disability. |
| `disability_5_17_total` | `DOUBLE` | 0.0000 | 30,226 | min 0, max 54684151 | 0.0 (65130); 12.0 (3645); 10.0 (3600); 14.0 (3460); 9.0 (3444) | Population ages 5 to 17 in the disability-status universe. |
| `disability_5_17_with` | `DOUBLE` | 0.0000 | 7,816 | min 0, max 3449147 | 0.0 (440130); 9.0 (28016); 8.0 (27665); 10.0 (27392); 11.0 (26303) | Population ages 5 to 17 with a disability. |
| `disability_18_34_total` | `DOUBLE` | 0.0000 | 36,360 | min 0, max 74890315 | 0.0 (51987); 16.0 (2972); 12.0 (2941); 15.0 (2928); 9.0 (2922) | Population ages 18 to 34 in the disability-status universe. |
| `disability_18_34_with` | `DOUBLE` | 0.0000 | 9,758 | min 0, max 6058471 | 0.0 (278492); 2.0 (23168); 9.0 (21423); 8.0 (21379); 10.0 (20965) | Population ages 18 to 34 with a disability. |
| `disability_35_64_total` | `DOUBLE` | 0.0000 | 45,863 | min 0, max 125637907 | 0.0 (30041); 27.0 (1518); 34.0 (1515); 22.0 (1486); 37.0 (1482) | Population ages 35 to 64 in the disability-status universe. |
| `disability_35_64_with` | `DOUBLE` | 0.0000 | 16,651 | min 0, max 15837938 | 0.0 (80755); 10.0 (8218); 8.0 (8161); 9.0 (8140); 11.0 (7911) | Population ages 35 to 64 with a disability. |
| `disability_65_74_total` | `DOUBLE` | 0.0000 | 21,281 | min 0, max 33677758 | 0.0 (56978); 8.0 (5232); 10.0 (5212); 9.0 (5155); 12.0 (4966) | Population ages 65 to 74 in the disability-status universe. |
| `disability_65_74_with` | `DOUBLE` | 0.0000 | 11,150 | min 0, max 8071051 | 0.0 (131989); 9.0 (15461); 8.0 (15379); 10.0 (15215); 6.0 (14709) | Population ages 65 to 74 with a disability. |
| `disability_75_plus_total` | `DOUBLE` | 0.0000 | 18,064 | min 0, max 22561941 | 0.0 (77997); 9.0 (7285); 10.0 (7283); 8.0 (7240); 11.0 (6924) | Population age 75 and older in the disability-status universe. |
| `disability_75_plus_with` | `DOUBLE` | 0.0000 | 12,938 | min 0, max 10416723 | 0.0 (119822); 9.0 (12415); 8.0 (12409); 10.0 (12269); 6.0 (12024) | Population age 75 and older with a disability. |
| `disability_under_18_total` | `DOUBLE` | 0.0000 | 35,667 | min 0, max 74105940 | 0.0 (57492); 12.0 (2772); 10.0 (2704); 14.0 (2641); 9.0 (2621) | Population under age 18 in the disability-status universe. |
| `disability_under_18_with` | `DOUBLE` | 0.0000 | 7,958 | min 0, max 3578121 | 0.0 (425396); 9.0 (27340); 8.0 (26990); 10.0 (26689); 11.0 (25730) | Population under age 18 with a disability. |
| `disability_18_64_total` | `DOUBLE` | 0.0000 | 60,628 | min 0, max 200303569 | 0.0 (25612); 37.0 (1051); 40.0 (1022); 57.0 (1022); 36.0 (1011) | Population ages 18 to 64 in the disability-status universe. |
| `disability_18_64_with` | `DOUBLE` | 0.0000 | 18,970 | min 0, max 21803902 | 0.0 (68117); 10.0 (6651); 9.0 (6639); 8.0 (6567); 7.0 (6381) | Population ages 18 to 64 with a disability. |
| `disability_65_plus_total` | `DOUBLE` | 0.0000 | 27,878 | min 0, max 56239699 | 0.0 (44262); 19.0 (3189); 15.0 (3182); 17.0 (3159); 16.0 (3143) | Population age 65 and older in the disability-status universe. |
| `disability_65_plus_with` | `DOUBLE` | 0.0000 | 16,794 | min 0, max 18487774 | 0.0 (75057); 8.0 (7781); 9.0 (7722); 10.0 (7498); 11.0 (7209) | Population age 65 and older with a disability. |
| `pct_disabled` | `DOUBLE` | 1.1363 | 1,077,258 | min 0, max 1 | NULL (21493); 0.0 (19329); 1.0 (1696); 0.2 (1388); 0.16666666666666666 (1335) | Share of the disability-status universe with a disability. |
| `pct_disabled_male` | `DOUBLE` | 1.2586 | 726,820 | min 0, max 1 | 0.0 (33704); NULL (23807); 1.0 (3244); 0.16666666666666666 (2310); 0.2 (2208) | Share of the male disability-status universe with a disability. |
| `pct_disabled_female` | `DOUBLE` | 1.2758 | 741,320 | min 0, max 1 | 0.0 (38087); NULL (24132); 1.0 (2805); 0.16666666666666666 (2198); 0.14285714285714285 (2156) | Share of the female disability-status universe with a disability. |
| `pct_disabled_under_5` | `DOUBLE` | 6.2502 | 80,643 | min 0, max 1 | 0.0 (1521401); NULL (118227); 1.0 (464); 0.1111111111111111 (441); 0.08333333333333333 (436) | Share of the under-5 disability-status universe with a disability. |
| `pct_disabled_5_17` | `DOUBLE` | 3.4432 | 292,414 | min 0, max 1 | 0.0 (375000); NULL (65130); 0.08333333333333333 (2090); 0.1 (2088); 0.09090909090909091 (2057) | Share of the ages 5 to 17 disability-status universe with a disability. |
| `pct_disabled_18_34` | `DOUBLE` | 2.7484 | 365,337 | min 0, max 1 | 0.0 (226505); NULL (51987); 1.0 (2934); 0.1 (2200); 0.1111111111111111 (2172) | Share of the ages 18 to 34 disability-status universe with a disability. |
| `pct_disabled_35_64` | `DOUBLE` | 1.5882 | 656,093 | min 0, max 1 | 0.0 (50714); NULL (30041); 1.0 (2908); 0.16666666666666666 (2475); 0.2 (2466) | Share of the ages 35 to 64 disability-status universe with a disability. |
| `pct_disabled_65_74` | `DOUBLE` | 3.0122 | 271,299 | min 0, max 1 | 0.0 (75011); NULL (56978); 1.0 (14076); 0.3333333333333333 (9247); 0.5 (8477) | Share of the ages 65 to 74 disability-status universe with a disability. |
| `pct_disabled_75_plus` | `DOUBLE` | 4.1234 | 228,262 | min 0, max 1 | NULL (77997); 1.0 (50792); 0.0 (41825); 0.5 (19820); 0.6666666666666666 (9171) | Share of the age 75 and older disability-status universe with a disability. |
| `pct_disabled_under_18` | `DOUBLE` | 3.0394 | 329,768 | min 0, max 1 | 0.0 (367904); NULL (57492); 0.05263157894736842 (1573); 0.06666666666666667 (1535); 0.07692307692307693 (1535) | Share of the under-18 disability-status universe with a disability. |
| `pct_disabled_18_64` | `DOUBLE` | 1.3540 | 823,722 | min 0, max 1 | 0.0 (42505); NULL (25612); 1.0 (1792); 0.14285714285714285 (1714); 0.16666666666666666 (1658) | Share of the ages 18 to 64 disability-status universe with a disability. |
| `pct_disabled_65_plus` | `DOUBLE` | 2.3400 | 396,800 | min 0, max 1 | NULL (44262); 0.0 (30795); 1.0 (13536); 0.5 (8932); 0.3333333333333333 (7521) | Share of the age 65 and older disability-status universe with a disability. |
## Data Quality Notes
- Columns with non-zero null rates: pct_disabled=1.1363%, pct_disabled_male=1.2586%, pct_disabled_female=1.2758%, pct_disabled_under_5=6.2502%, pct_disabled_5_17=3.4432%, pct_disabled_18_34=2.7484%, pct_disabled_35_64=1.5882%, pct_disabled_65_74=3.0122%, pct_disabled_75_plus=4.1234%, pct_disabled_under_18=3.0394%, ...
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `foundations/etl/silver/acs_disability_silver.R writes silver.disability_kpi from staging.acs_disability_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Re-run the landed profile after major ACS topic changes and sync both this `.md` file and the companion `.yml` artifact.
