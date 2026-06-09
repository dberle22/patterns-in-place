# Data Dictionary: silver.social_infra_kpi

## Overview
- **Table**: `silver.social_infra_kpi`
- **Purpose**: Silver social infrastructure table (`kpi` type).
- **Row count**: 1,471,832
- **KPI applicability**: KPI table (or has KPI dictionary entries).

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1471832, distinct=1471832, duplicates=0
  - `geo_level + geo_id + year` => rows=1471832, distinct=1471832, duplicates=0
  - `geo_id + year` => rows=1471832, distinct=1453577, duplicates=18255
  - `geo_level` => rows=1471832, distinct=9, duplicates=1471823
- **Time coverage**: `year` min=2015, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=165557

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | tract (787324); zcta (333812); place (308527); county (32208); cbsa (9301) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 165,557 | len 1-11 | 1 (30); 01001 (20); 01003 (20); 01005 (20); 01007 (20) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 251,094 | len 4-81 | Alexandria city, Virginia (20); Baltimore city, Maryland (20); Bristol city, Virginia (20); Buena Vista city, Virginia (20); Carson City, Nevada (20) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 10 | min 2015, max 2024 | 2024 (154726); 2023 (154720); 2022 (154598); 2021 (154311); 2020 (153657) | Observation year or period year for the row. |
| `hh_total` | `DOUBLE` | 0.0000 | 40,598 | min 0, max 129227496 | 0.0 (20641); 32.0 (1214); 43.0 (1176); 33.0 (1170); 45.0 (1163) | Total households. |
| `hh_family` | `DOUBLE` | 0.0000 | 32,194 | min 0, max 82990528 | 0.0 (25850); 17.0 (1791); 16.0 (1788); 15.0 (1751); 19.0 (1746) | Family households. |
| `hh_married` | `DOUBLE` | 0.0000 | 27,245 | min 0, max 60637388 | 0.0 (29945); 17.0 (2370); 13.0 (2329); 15.0 (2329); 16.0 (2323) | Married-couple family households. |
| `hh_other_family` | `DOUBLE` | 0.0000 | 16,890 | min 0, max 22353140 | 0.0 (69103); 6.0 (6088); 8.0 (6067); 9.0 (6042); 7.0 (6019) | Other family households excluding married-couple families. |
| `hh_nonfamily` | `DOUBLE` | 0.0000 | 23,574 | min 0, max 46236968 | 0.0 (37068); 10.0 (3389); 16.0 (3349); 9.0 (3343); 15.0 (3306) | Nonfamily households. |
| `hh_nonfam_alone` | `DOUBLE` | 0.0000 | 20,960 | min 0, max 37140836 | 0.0 (41311); 9.0 (3958); 10.0 (3918); 11.0 (3871); 13.0 (3857) | Nonfamily households with one person living alone. |
| `hh_nonfam_not_alone` | `DOUBLE` | 0.0000 | 11,135 | min 0, max 9096132 | 0.0 (146205); 2.0 (14089); 6.0 (13756); 8.0 (13670); 5.0 (13393) | Nonfamily households with two or more people. |
| `single_households` | `DOUBLE` | 0.0000 | 20,960 | min 0, max 37140836 | 0.0 (41311); 9.0 (3958); 10.0 (3918); 11.0 (3871); 13.0 (3857) | Households with one person living alone. |
| `pct_hh_family` | `DOUBLE` | 1.4024 | 657,164 | min 0, max 1 | NULL (20641); 1.0 (16427); 0.0 (5209); 0.6666666666666666 (3283); 0.5 (2560) | Share of households that are family households. |
| `pct_hh_married` | `DOUBLE` | 1.4024 | 699,718 | min 0, max 1 | NULL (20641); 0.0 (9304); 1.0 (9151); 0.5 (4373); 0.6666666666666666 (1863) | Share of households that are married-couple family households. |
| `pct_hh_other_family` | `DOUBLE` | 1.4024 | 579,947 | min 0, max 1 | 0.0 (48462); NULL (20641); 0.16666666666666666 (1813); 0.2 (1710); 0.14285714285714285 (1689) | Share of households that are other family households. |
| `pct_hh_nonfamily` | `DOUBLE` | 1.4024 | 657,164 | min 0, max 1 | NULL (20641); 0.0 (16427); 1.0 (5209); 0.3333333333333333 (3283); 0.5 (2560) | Share of households that are nonfamily households. |
| `pct_single_households` | `DOUBLE` | 1.4024 | 625,029 | min 0, max 1 | 0.0 (20670); NULL (20641); 1.0 (3836); 0.3333333333333333 (3020); 0.25 (2736) | Share of households with one person living alone. |
| `pct_hh_single_person` | `DOUBLE` | 1.4024 | 625,029 | min 0, max 1 | 0.0 (20670); NULL (20641); 1.0 (3836); 0.3333333333333333 (3020); 0.25 (2736) | Alias for the share of households with one person living alone, named to match the household-structure Gold contract. |
| `pct_nonfamily_alone` | `DOUBLE` | 2.5185 | 280,781 | min 0, max 1 | 1.0 (109137); NULL (37068); 0.0 (4243); 0.8 (3893); 0.8333333333333334 (3722) | Share of nonfamily households that are one-person households. |
| `pct_nonfamily_not_alone` | `DOUBLE` | 2.5185 | 280,781 | min 0, max 1 | 0.0 (109137); NULL (37068); 1.0 (4243); 0.2 (3893); 0.16666666666666666 (3722) | Share of nonfamily households with two or more people. |
| `ins_total` | `DOUBLE` | 0.0000 | 72,360 | min 0, max 329980753 | 0.0 (17427); 44.0 (490); 64.0 (489); 61.0 (486); 69.0 (480) | Total civilian noninstitutionalized population in the health insurance coverage universe. |
| `ins_insured` | `DOUBLE` | 0.0000 | 68,197 | min 0, max 302245842 | 0.0 (17906); 76.0 (551); 93.0 (547); 50.0 (545); 94.0 (542) | Population with at least one form of health insurance coverage. |
| `ins_uninsured` | `DOUBLE` | 0.0000 | 20,920 | min 0, max 40446231 | 0.0 (69364); 9.0 (5173); 11.0 (5158); 10.0 (5141); 8.0 (5073) | Population without health insurance coverage. |
| `pct_health_insured` | `DOUBLE` | 1.1840 | 872,859 | min 0, max 1 | 1.0 (51937); NULL (17427); 0.9 (588); 0.8888888888888888 (563); 0.8571428571428571 (562) | Share of the health insurance universe with insurance coverage. |
| `pct_health_uninsured` | `DOUBLE` | 1.1840 | 872,859 | min 0, max 1 | 0.0 (51937); NULL (17427); 0.1 (588); 0.1111111111111111 (563); 0.14285714285714285 (562) | Share of the health insurance universe without health insurance coverage. |
| `ins_u19_total` | `DOUBLE` | 0.0000 | 32,449 | min 0, max 78612964 | 0.0 (44590); 12.0 (2001); 14.0 (1978); 8.0 (1971); 10.0 (1959) | Total population under age 19 in the health insurance coverage universe. |
| `ins_u19_covered` | `DOUBLE` | 0.0000 | 31,458 | min 0, max 74444233 | 0.0 (46502); 14.0 (2087); 12.0 (2083); 10.0 (2080); 9.0 (2079) | Population under age 19 with at least one form of health insurance coverage. |
| `ins_u19_uncovered` | `DOUBLE` | 0.0000 | 7,760 | min 0, max 4756380 | 0.0 (456681); 8.0 (17608); 9.0 (17533); 10.0 (17365); 6.0 (17283) | Population under age 19 without health insurance coverage. |
| `pct_u19_covered` | `DOUBLE` | 3.0296 | 321,354 | min 0, max 1 | 1.0 (412091); NULL (44590); 0.0 (1912); 0.9 (863); 0.875 (842) | Share of the under-19 insurance universe with insurance coverage. |
| `pct_u19_uncovered` | `DOUBLE` | 3.0296 | 321,354 | min 0, max 1 | 0.0 (412091); NULL (44590); 1.0 (1912); 0.1 (863); 0.125 (842) | Share of the under-19 insurance universe without health insurance coverage. |
| `ins_19_34_total` | `DOUBLE` | 0.0000 | 31,449 | min 0, max 72771471 | 0.0 (43408); 14.0 (2451); 13.0 (2393); 16.0 (2383); 12.0 (2382) | Total population ages 19 to 34 in the health insurance coverage universe. |
| `ins_19_34_covered` | `DOUBLE` | 0.0000 | 28,597 | min 0, max 60145366 | 0.0 (48968); 9.0 (2975); 12.0 (2889); 11.0 (2853); 14.0 (2820) | Population ages 19 to 34 with at least one form of health insurance coverage. |
| `ins_19_34_uncovered` | `DOUBLE` | 0.0000 | 12,954 | min 0, max 16531269 | 0.0 (170218); 9.0 (11307); 10.0 (11175); 8.0 (11076); 7.0 (11058) | Population ages 19 to 34 without health insurance coverage. |
| `pct_19_34_covered` | `DOUBLE` | 2.9492 | 413,696 | min 0, max 1 | 1.0 (126810); NULL (43408); 0.0 (5560); 0.75 (2285); 0.6666666666666666 (2261) | Share of the ages 19 to 34 insurance universe with insurance coverage. |
| `pct_19_34_uncovered` | `DOUBLE` | 2.9492 | 413,696 | min 0, max 1 | 0.0 (126810); NULL (43408); 1.0 (5560); 0.25 (2285); 0.3333333333333333 (2261) | Share of the ages 19 to 34 insurance universe without health insurance coverage. |
| `ins_35_64_total` | `DOUBLE` | 0.0000 | 41,153 | min 0, max 125637907 | 0.0 (24487); 34.0 (1221); 27.0 (1206); 22.0 (1184); 18.0 (1175) | Total population ages 35 to 64 in the health insurance coverage universe. |
| `ins_35_64_covered` | `DOUBLE` | 0.0000 | 38,305 | min 0, max 112652341 | 0.0 (26556); 18.0 (1432); 16.0 (1385); 22.0 (1365); 30.0 (1362) | Population ages 35 to 64 with at least one form of health insurance coverage. |
| `ins_35_64_uncovered` | `DOUBLE` | 0.0000 | 14,009 | min 0, max 18744797 | 0.0 (108093); 9.0 (9309); 8.0 (9263); 10.0 (9088); 12.0 (8992) | Population ages 35 to 64 without health insurance coverage. |
| `pct_35_64_covered` | `DOUBLE` | 1.6637 | 557,071 | min 0, max 1 | 1.0 (83606); NULL (24487); 0.0 (2069); 0.8333333333333334 (1306); 0.8571428571428571 (1297) | Share of the ages 35 to 64 insurance universe with insurance coverage. |
| `pct_35_64_uncovered` | `DOUBLE` | 1.6637 | 557,071 | min 0, max 1 | 0.0 (83606); NULL (24487); 1.0 (2069); 0.16666666666666666 (1306); 0.14285714285714285 (1297) | Share of the ages 35 to 64 insurance universe without health insurance coverage. |
| `ins_65u_total` | `DOUBLE` | 0.0000 | 25,137 | min 0, max 56239699 | 0.0 (34929); 9.0 (2436); 15.0 (2418); 17.0 (2409); 16.0 (2401) | Total population age 65 and older in the health insurance coverage universe. |
| `ins_65u_covered` | `DOUBLE` | 0.0000 | 25,001 | min 0, max 55764121 | 0.0 (35128); 9.0 (2467); 15.0 (2421); 17.0 (2410); 19.0 (2407) | Population age 65 and older with at least one form of health insurance coverage. |
| `ins_65u_uncovered` | `DOUBLE` | 0.0000 | 2,704 | min 0, max 475578 | 0.0 (1105800); 8.0 (13795); 9.0 (13462); 2.0 (13431); 7.0 (12429) | Population age 65 and older without health insurance coverage. |
| `pct_65u_covered` | `DOUBLE` | 2.3732 | 129,771 | min 0, max 1 | 1.0 (1070871); NULL (34929); 0.9545454545454546 (272); 0.9583333333333334 (269); 0.975 (269) | Share of the age 65 and older insurance universe with insurance coverage. |
| `pct_65u_uncovered` | `DOUBLE` | 2.3732 | 129,771 | min 0, max 1 | 0.0 (1070871); NULL (34929); 0.045454545454545456 (272); 0.025 (269); 0.041666666666666664 (269) | Share of the age 65 and older insurance universe without health insurance coverage. |
## Data Quality Notes
- Columns with non-zero null rates: pct_hh_family=1.4024%, pct_hh_married=1.4024%, pct_hh_other_family=1.4024%, pct_hh_nonfamily=1.4024%, pct_single_households=1.4024%, pct_nonfamily_alone=2.5185%, pct_nonfamily_not_alone=2.5185%, pct_health_insured=1.1840%, pct_health_uninsured=1.1840%, pct_u19_covered=3.0296%, ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_social_infra_silver.R:225-235` writes `silver.social_infra_kpi` from `staging.acs_social_infra_*` with CBSA rebasing from county data via `silver.xwalk_cbsa_county`.

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
