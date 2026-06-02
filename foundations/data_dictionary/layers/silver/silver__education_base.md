# Data Dictionary: silver.education_base

## Overview
- **Table**: `silver.education_base`
- **Purpose**: Silver education table (`base` type).
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
| `edu_total_25pE` | `DOUBLE` | 0.0000 | 63573 | min 0, max 230807300 | 0.0 (11750); 62.0 (876); 76.0 (852); 54.0 (851); 38.0 (847) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_001]: Total: (estimate). |
| `edu_no_schoolingE` | `DOUBLE` | 0.0000 | 7960 | min 0, max 4534710 | 0.0 (326572); 2.0 (28603); 3.0 (23193); 4.0 (19194); 1.0 (19180) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_002]: Total:, No schooling completed (estimate). |
| `edu_nurseryE` | `DOUBLE` | 0.0000 | 1151 | min 0, max 65861 | 0.0 (942899); 8.0 (3709); 9.0 (3518); 2.0 (3455); 7.0 (3345) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_003]: Total:, Nursery school (estimate). |
| `edu_kindergartenE` | `DOUBLE` | 0.0000 | 1232 | min 0, max 64338 | 0.0 (939655); 2.0 (3872); 9.0 (3521); 3.0 (3513); 8.0 (3490) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_004]: Total:, Kindergarten (estimate). |
| `edu_grade1E` | `DOUBLE` | 0.0000 | 1911 | min 0, max 145745 | 0.0 (898346); 2.0 (5108); 3.0 (4878); 4.0 (4729); 5.0 (4303) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_005]: Total:, 1st grade (estimate). |
| `edu_grade2E` | `DOUBLE` | 0.0000 | 2607 | min 0, max 319316 | 0.0 (845732); 3.0 (6340); 2.0 (6088); 4.0 (5791); 5.0 (5443) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_006]: Total:, 2nd grade (estimate). |
| `edu_grade3E` | `DOUBLE` | 0.0000 | 3590 | min 0, max 670157 | 0.0 (743068); 2.0 (10201); 3.0 (10009); 4.0 (9253); 5.0 (8378) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_007]: Total:, 3rd grade (estimate). |
| `edu_grade4E` | `DOUBLE` | 0.0000 | 3280 | min 0, max 548838 | 0.0 (757801); 2.0 (9855); 3.0 (9583); 4.0 (9124); 5.0 (8255) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_008]: Total:, 4th grade (estimate). |
| `edu_grade5E` | `DOUBLE` | 0.0000 | 3771 | min 0, max 761051 | 0.0 (695904); 2.0 (11922); 3.0 (11610); 4.0 (10734); 5.0 (9558) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_009]: Total:, 5th grade (estimate). |
| `edu_grade6E` | `DOUBLE` | 0.0000 | 7071 | min 0, max 2829818 | 0.0 (531774); 2.0 (17410); 3.0 (15655); 4.0 (13459); 5.0 (12438) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_010]: Total:, 6th grade (estimate). |
| `edu_grade7E` | `DOUBLE` | 0.0000 | 4247 | min 0, max 1119030 | 0.0 (554897); 2.0 (19337); 3.0 (17200); 4.0 (15300); 5.0 (13922) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_011]: Total:, 7th grade (estimate). |
| `edu_grade8E` | `DOUBLE` | 0.0000 | 6780 | min 0, max 3230578 | 0.0 (283839); 2.0 (23857); 3.0 (20235); 4.0 (18822); 5.0 (17499) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_012]: Total:, 8th grade (estimate). |
| `edu_grade9E` | `DOUBLE` | 0.0000 | 7753 | min 0, max 3638277 | 0.0 (282390); 2.0 (24376); 3.0 (19654); 4.0 (18459); 5.0 (17358) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_013]: Total:, 9th grade (estimate). |
| `edu_grade10E` | `DOUBLE` | 0.0000 | 8310 | min 0, max 4519562 | 0.0 (210129); 2.0 (21285); 3.0 (18281); 4.0 (17180); 5.0 (16366) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_014]: Total:, 10th grade (estimate). |
| `edu_grade11E` | `DOUBLE` | 0.0000 | 8873 | min 0, max 5004410 | 0.0 (197768); 2.0 (20270); 3.0 (17258); 4.0 (16658); 5.0 (15910) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_015]: Total:, 11th grade (estimate). |
| `edu_grade12_no_diplomaE` | `DOUBLE` | 0.0000 | 8556 | min 0, max 4494501 | 0.0 (220655); 2.0 (26491); 3.0 (22431); 4.0 (20503); 5.0 (18422) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_016]: Total:, 12th grade, no diploma (estimate). |
| `edu_hs_diplomaE` | `DOUBLE` | 0.0000 | 29000 | min 0, max 51011337 | 0.0 (27815); 9.0 (2461); 15.0 (2460); 19.0 (2445); 17.0 (2436) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_017]: Total:, Regular high school diploma (estimate). |
| `edu_ged_alt_credentialE` | `DOUBLE` | 0.0000 | 12545 | min 0, max 9083379 | 0.0 (104286); 2.0 (11812); 4.0 (11738); 6.0 (11662); 5.0 (11520) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_018]: Total:, GED or alternative credential (estimate). |
| `edu_some_college_lt1yrE` | `DOUBLE` | 0.0000 | 15558 | min 0, max 14727607 | 0.0 (78064); 8.0 (9156); 9.0 (8990); 7.0 (8969); 6.0 (8954) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_019]: Total:, Some college, less than 1 year (estimate). |
| `edu_some_college_ge1yrE` | `DOUBLE` | 0.0000 | 22666 | min 0, max 31493074 | 0.0 (45093); 9.0 (5291); 8.0 (5258); 10.0 (5250); 11.0 (5137) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_020]: Total:, Some college, 1 or more years, no degree (estimate). |
| `edu_associatesE` | `DOUBLE` | 0.0000 | 17753 | min 0, max 20322913 | 0.0 (68319); 6.0 (7505); 9.0 (7441); 7.0 (7337); 8.0 (7321) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_021]: Total:, Associate's degree (estimate). |
| `edu_bachelorsE` | `DOUBLE` | 0.0000 | 26841 | min 0, max 49868171 | 0.0 (60062); 8.0 (6690); 7.0 (6556); 9.0 (6516); 5.0 (6491) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_022]: Total:, Bachelor's degree (estimate). |
| `edu_mastersE` | `DOUBLE` | 0.0000 | 17997 | min 0, max 23264421 | 0.0 (121033); 2.0 (14861); 3.0 (12919); 4.0 (12366); 5.0 (11709) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_023]: Total:, Master's degree (estimate). |
| `edu_professionalE` | `DOUBLE` | 0.0000 | 9436 | min 0, max 5354651 | 0.0 (345066); 2.0 (22152); 3.0 (19483); 4.0 (16448); 5.0 (14585) | ACS 2024 Educational Attainment for the Population 25 Years and Over [B15003_024]: Total:, Professional school degree (estimate). |
| `edu_doctorateE` | `DOUBLE` | 0.0000 | 8307 | min 0, max 3875973 | 0.0 (408900); 2.0 (21038); 3.0 (18976); 4.0 (16243); 5.0 (14346) | Rate derived from ACS counts. (from silver.kpi_dictionary). |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_edu_silver.R:152:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="education_base"),`

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
