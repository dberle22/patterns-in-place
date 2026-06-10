# Data Dictionary: silver.social_infra_base

## Overview
- **Table**: `silver.social_infra_base`
- **Purpose**: Silver social infrastructure base table (`base` type).
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
| `hh_totalE` | `DOUBLE` | 0.0000 | 40,598 | min 0, max 129227496 | 0.0 (20641); 32.0 (1214); 43.0 (1176); 33.0 (1170); 45.0 (1163) | Total households. |
| `hh_familyE` | `DOUBLE` | 0.0000 | 32,194 | min 0, max 82990528 | 0.0 (25850); 17.0 (1791); 16.0 (1788); 15.0 (1751); 19.0 (1746) | Family households. |
| `hh_marriedE` | `DOUBLE` | 0.0000 | 27,245 | min 0, max 60637388 | 0.0 (29945); 17.0 (2370); 13.0 (2329); 15.0 (2329); 16.0 (2323) | Married-couple family households. |
| `hh_other_familyE` | `DOUBLE` | 0.0000 | 16,890 | min 0, max 22353140 | 0.0 (69103); 6.0 (6088); 8.0 (6067); 9.0 (6042); 7.0 (6019) | Other family households excluding married-couple families. |
| `hh_nonfamilyE` | `DOUBLE` | 0.0000 | 23,574 | min 0, max 46236968 | 0.0 (37068); 10.0 (3389); 16.0 (3349); 9.0 (3343); 15.0 (3306) | Nonfamily households. |
| `hh_nonfam_aloneE` | `DOUBLE` | 0.0000 | 20,960 | min 0, max 37140836 | 0.0 (41311); 9.0 (3958); 10.0 (3918); 11.0 (3871); 13.0 (3857) | Nonfamily households with one person living alone. |
| `hh_nonfam_not_aloneE` | `DOUBLE` | 0.0000 | 11,135 | min 0, max 9096132 | 0.0 (146205); 2.0 (14089); 6.0 (13756); 8.0 (13670); 5.0 (13393) | Nonfamily households with two or more people. |
| `family_with_children_married_coupleE` | `DOUBLE` | 0.0000 | 27,245 | min 0, max 60637388 | 0.0 (29945); 17.0 (2370); 13.0 (2329); 15.0 (2329); 16.0 (2323) | Married-couple families with own children of the householder under age 18. |
| `family_with_children_single_fatherE` | `DOUBLE` | 0.0000 | 9,090 | min 0, max 6572819 | 0.0 (157828); 8.0 (14265); 6.0 (14115); 9.0 (14054); 7.0 (13853) | Male-householder families with own children of the householder under age 18 and no spouse present. |
| `family_with_children_single_motherE` | `DOUBLE` | 0.0000 | 6,440 | min 0, max 2940092 | 0.0 (358350); 9.0 (22859); 10.0 (22288); 8.0 (22101); 7.0 (21473) | Female-householder families with own children of the householder under age 18 and no spouse present. |
| `ins_totalE` | `DOUBLE` | 0.0000 | 72,360 | min 0, max 329980753 | 0.0 (17427); 44.0 (490); 64.0 (489); 61.0 (486); 69.0 (480) | Total civilian noninstitutionalized population in the health insurance coverage universe. |
| `ins_u19_one_planE` | `DOUBLE` | 0.0000 | 30,345 | min 0, max 69406764 | 0.0 (48328); 9.0 (2280); 10.0 (2268); 14.0 (2225); 18.0 (2172) | Population under age 19 with one type of health insurance coverage. |
| `ins_u19_two_plansE` | `DOUBLE` | 0.0000 | 8,303 | min 0, max 5731722 | 0.0 (303605); 8.0 (16701); 10.0 (16446); 9.0 (16175); 6.0 (15964) | Population under age 19 with two or more types of health insurance coverage. |
| `ins_u19_uncoveredE` | `DOUBLE` | 0.0000 | 7,760 | min 0, max 4756380 | 0.0 (456681); 8.0 (17608); 9.0 (17533); 10.0 (17365); 6.0 (17283) | Population under age 19 without health insurance coverage. |
| `ins_19_34_one_planE` | `DOUBLE` | 0.0000 | 27,527 | min 0, max 55725308 | 0.0 (51129); 9.0 (3126); 12.0 (3097); 11.0 (3077); 10.0 (3027) | Population ages 19 to 34 with one type of health insurance coverage. |
| `ins_19_34_two_plansE` | `DOUBLE` | 0.0000 | 7,887 | min 0, max 4451439 | 0.0 (294480); 9.0 (19521); 2.0 (19451); 10.0 (19416); 8.0 (19291) | Population ages 19 to 34 with two or more types of health insurance coverage. |
| `ins_19_34_uncoveredE` | `DOUBLE` | 0.0000 | 12,954 | min 0, max 16531269 | 0.0 (170218); 9.0 (11307); 10.0 (11175); 8.0 (11076); 7.0 (11058) | Population ages 19 to 34 without health insurance coverage. |
| `ins_35_64_one_planE` | `DOUBLE` | 0.0000 | 36,270 | min 0, max 101334720 | 0.0 (28353); 15.0 (1581); 23.0 (1539); 34.0 (1531); 18.0 (1528) | Population ages 35 to 64 with one type of health insurance coverage. |
| `ins_35_64_two_plansE` | `DOUBLE` | 0.0000 | 12,207 | min 0, max 11317621 | 0.0 (90945); 6.0 (8938); 5.0 (8794); 8.0 (8774); 2.0 (8718) | Population ages 35 to 64 with two or more types of health insurance coverage. |
| `ins_35_64_uncoveredE` | `DOUBLE` | 0.0000 | 14,009 | min 0, max 18744797 | 0.0 (108093); 9.0 (9309); 8.0 (9263); 10.0 (9088); 12.0 (8992) | Population ages 35 to 64 without health insurance coverage. |
| `ins_65u_one_planE` | `DOUBLE` | 0.0000 | 14,324 | min 0, max 20831442 | 0.0 (69827); 8.0 (7102); 9.0 (6791); 6.0 (6756); 10.0 (6600) | Population age 65 and older with one type of health insurance coverage. |
| `ins_65u_two_plansE` | `DOUBLE` | 0.0000 | 20,426 | min 0, max 34932679 | 0.0 (43855); 9.0 (3534); 8.0 (3489); 10.0 (3469); 13.0 (3321) | Population age 65 and older with two or more types of health insurance coverage. |
| `ins_65u_uncoveredE` | `DOUBLE` | 0.0000 | 2,704 | min 0, max 475578 | 0.0 (1105800); 8.0 (13795); 9.0 (13462); 2.0 (13431); 7.0 (12429) | Population age 65 and older without health insurance coverage. |
## Data Quality Notes
- No columns with non-zero null rates in current snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_social_infra_silver.R:225-235` writes `silver.social_infra_base` from `staging.acs_social_infra_*` with CBSA rebasing from county data via `silver.xwalk_cbsa_county`.

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
