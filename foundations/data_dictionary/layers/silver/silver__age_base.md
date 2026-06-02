# Data Dictionary: silver.age_base

## Overview
- **Table**: `silver.age_base`
- **Purpose**: Silver age table (`base` type).
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
| `pop_totalE` | `DOUBLE` | 0.0000 | 80593 | min 0, max 334922500 | 0.0 (11017); 74.0 (610); 115.0 (607); 61.0 (603); 64.0 (602) | ACS 2024 Sex by Age [B01001_001]: Total: (estimate). |
| `median_age.E` | `DOUBLE` | 1.7624 | 5492 | min 0, max 105.1 | NULL (17993); 40.5 (5948); 40.8 (5846); 40.3 (5768); 40.6 (5615) | ACS 2024 Median Age by Sex [B01002_001]: Total (estimate). |
| `pop_male_totalE` | `DOUBLE` | 0.0000 | 53318 | min 0, max 165808020 | 0.0 (12980); 62.0 (1151); 44.0 (1138); 55.0 (1135); 32.0 (1133) | ACS 2024 Sex by Age [B01001_002]: Total:, Male: (estimate). |
| `pop_age_male_under5E` | `DOUBLE` | 0.0000 | 13301 | min 0, max 10291124 | 0.0 (143218); 2.0 (11221); 4.0 (10812); 5.0 (10631); 6.0 (10600) | ACS 2024 Sex by Age [B01001_003]: Total:, Male:, Under 5 years (estimate). |
| `pop_age_male_5_9E` | `DOUBLE` | 0.0000 | 13473 | min 0, max 10476978 | 0.0 (132439); 2.0 (10853); 4.0 (10712); 6.0 (10581); 5.0 (10309) | ACS 2024 Sex by Age [B01001_004]: Total:, Male:, 5 to 9 years (estimate). |
| `pop_age_male_10_14E` | `DOUBLE` | 0.0000 | 13686 | min 0, max 11101231 | 0.0 (124397); 2.0 (10732); 4.0 (10658); 6.0 (10307); 5.0 (9955) | ACS 2024 Sex by Age [B01001_005]: Total:, Male:, 10 to 14 years (estimate). |
| `pop_age_male_15_17E` | `DOUBLE` | 0.0000 | 10805 | min 0, max 6756663 | 0.0 (160440); 2.0 (15127); 4.0 (13788); 3.0 (13701); 6.0 (13322) | ACS 2024 Sex by Age [B01001_006]: Total:, Male:, 15 to 17 years (estimate). |
| `pop_age_male_18_19E` | `DOUBLE` | 0.0000 | 9725 | min 0, max 4641564 | 0.0 (231605); 2.0 (20553); 3.0 (18489); 4.0 (17240); 5.0 (15902) | ACS 2024 Sex by Age [B01001_007]: Total:, Male:, 18 and 19 years (estimate). |
| `pop_age_male_20E` | `DOUBLE` | 0.0000 | 7248 | min 0, max 2454800 | 0.0 (380108); 2.0 (19279); 3.0 (19205); 4.0 (16721); 5.0 (15173) | ACS 2024 Sex by Age [B01001_008]: Total:, Male:, 20 years (estimate). |
| `pop_age_male_21E` | `DOUBLE` | 0.0000 | 7195 | min 0, max 2400843 | 0.0 (383328); 2.0 (19649); 3.0 (19010); 4.0 (16803); 5.0 (15329) | ACS 2024 Sex by Age [B01001_009]: Total:, Male:, 21 years (estimate). |
| `pop_age_male_22_24E` | `DOUBLE` | 0.0000 | 11494 | min 0, max 6799319 | 0.0 (193290); 2.0 (16858); 3.0 (15309); 4.0 (14742); 5.0 (13530) | ACS 2024 Sex by Age [B01001_010]: Total:, Male:, 22 to 24 years (estimate). |
| `pop_age_male_25_29E` | `DOUBLE` | 0.0000 | 14162 | min 0, max 11850355 | 0.0 (133909); 2.0 (12170); 4.0 (11630); 3.0 (11377); 5.0 (11213) | ACS 2024 Sex by Age [B01001_011]: Total:, Male:, 25 to 29 years (estimate). |
| `pop_age_male_30_34E` | `DOUBLE` | 0.0000 | 13816 | min 0, max 11829461 | 0.0 (125924); 2.0 (12273); 4.0 (11800); 3.0 (11515); 5.0 (11437) | ACS 2024 Sex by Age [B01001_012]: Total:, Male:, 30 to 34 years (estimate). |
| `pop_age_male_35_39E` | `DOUBLE` | 0.0000 | 13437 | min 0, max 11367389 | 0.0 (123256); 2.0 (12613); 5.0 (11667); 4.0 (11624); 3.0 (11447) | ACS 2024 Sex by Age [B01001_013]: Total:, Male:, 35 to 39 years (estimate). |
| `pop_age_male_40_44E` | `DOUBLE` | 0.0000 | 13250 | min 0, max 10914858 | 0.0 (117490); 2.0 (12409); 4.0 (11764); 5.0 (11692); 6.0 (11398) | ACS 2024 Sex by Age [B01001_014]: Total:, Male:, 40 to 44 years (estimate). |
| `pop_age_male_45_49E` | `DOUBLE` | 0.0000 | 13253 | min 0, max 11079384 | 0.0 (108852); 2.0 (11838); 6.0 (11244); 4.0 (11016); 3.0 (10913) | ACS 2024 Sex by Age [B01001_015]: Total:, Male:, 45 to 49 years (estimate). |
| `pop_age_male_50_54E` | `DOUBLE` | 0.0000 | 13406 | min 0, max 11051409 | 0.0 (94838); 6.0 (11011); 7.0 (10758); 5.0 (10653); 4.0 (10636) | ACS 2024 Sex by Age [B01001_016]: Total:, Male:, 50 to 54 years (estimate). |
| `pop_age_male_55_59E` | `DOUBLE` | 0.0000 | 13209 | min 0, max 10781599 | 0.0 (85918); 6.0 (10758); 8.0 (10698); 9.0 (10566); 5.0 (10546) | ACS 2024 Sex by Age [B01001_017]: Total:, Male:, 55 to 59 years (estimate). |
| `pop_age_male_60_61E` | `DOUBLE` | 0.0000 | 8592 | min 0, max 4304343 | 0.0 (164725); 2.0 (22182); 3.0 (19048); 4.0 (18583); 5.0 (17455) | ACS 2024 Sex by Age [B01001_018]: Total:, Male:, 60 and 61 years (estimate). |
| `pop_age_male_62_64E` | `DOUBLE` | 0.0000 | 9859 | min 0, max 6138005 | 0.0 (125314); 2.0 (17774); 4.0 (16099); 3.0 (15730); 5.0 (15222) | ACS 2024 Sex by Age [B01001_019]: Total:, Male:, 62 to 64 years (estimate). |
| `pop_age_male_65_66E` | `DOUBLE` | 0.0000 | 7892 | min 0, max 3767554 | 0.0 (176876); 2.0 (24224); 3.0 (20740); 4.0 (19832); 5.0 (18620) | ACS 2024 Sex by Age [B01001_020]: Total:, Male:, 65 and 66 years (estimate). |
| `pop_age_male_67_69E` | `DOUBLE` | 0.0000 | 8868 | min 0, max 5119378 | 0.0 (144249); 2.0 (20602); 3.0 (18018); 4.0 (17875); 5.0 (16678) | ACS 2024 Sex by Age [B01001_021]: Total:, Male:, 67 to 69 years (estimate). |
| `pop_age_male_70_74E` | `DOUBLE` | 0.0000 | 10073 | min 0, max 7171219 | 0.0 (114306); 2.0 (16287); 4.0 (15538); 3.0 (15149); 5.0 (14963) | ACS 2024 Sex by Age [B01001_022]: Total:, Male:, 70 to 74 years (estimate). |
| `pop_age_male_75_79E` | `DOUBLE` | 0.0000 | 8370 | min 0, max 4746871 | 0.0 (154195); 2.0 (21712); 3.0 (18705); 4.0 (18408); 5.0 (17382) | ACS 2024 Sex by Age [B01001_023]: Total:, Male:, 75 to 79 years (estimate). |
| `pop_age_male_80_84E` | `DOUBLE` | 0.0000 | 6878 | min 0, max 2836327 | 0.0 (219797); 2.0 (27430); 3.0 (22386); 4.0 (21068); 6.0 (19146) | ACS 2024 Sex by Age [B01001_024]: Total:, Male:, 80 to 84 years (estimate). |
| `pop_age_male_85_plusE` | `DOUBLE` | 0.0000 | 6405 | min 0, max 2364441 | 0.0 (278295); 2.0 (28726); 3.0 (23321); 4.0 (21092); 5.0 (18970) | ACS 2024 Sex by Age [B01001_025]: Total:, Male:, 85 years and over (estimate). |
| `pop_female_totalE` | `DOUBLE` | 0.0000 | 54213 | min 0, max 169114480 | 0.0 (13706); 49.0 (1212); 43.0 (1209); 56.0 (1203); 31.0 (1168) | ACS 2024 Sex by Age [B01001_026]: Total:, Female: (estimate). |
| `pop_age_female_under5E` | `DOUBLE` | 0.0000 | 13066 | min 0, max 9846760 | 0.0 (147463); 2.0 (11783); 4.0 (11517); 6.0 (10917); 5.0 (10844) | ACS 2024 Sex by Age [B01001_027]: Total:, Female:, Under 5 years (estimate). |
| `pop_age_female_5_9E` | `DOUBLE` | 0.0000 | 13266 | min 0, max 10031835 | 0.0 (136264); 2.0 (11460); 4.0 (11096); 6.0 (10776); 5.0 (10555) | ACS 2024 Sex by Age [B01001_028]: Total:, Female:, 5 to 9 years (estimate). |
| `pop_age_female_10_14E` | `DOUBLE` | 0.0000 | 13364 | min 0, max 10572886 | 0.0 (129090); 2.0 (11188); 4.0 (10783); 6.0 (10528); 5.0 (10273) | ACS 2024 Sex by Age [B01001_029]: Total:, Female:, 10 to 14 years (estimate). |
| `pop_age_female_15_17E` | `DOUBLE` | 0.0000 | 10554 | min 0, max 6435635 | 0.0 (166672); 2.0 (15811); 4.0 (14408); 3.0 (14178); 6.0 (13704) | ACS 2024 Sex by Age [B01001_030]: Total:, Female:, 15 to 17 years (estimate). |
| `pop_age_female_18_19E` | `DOUBLE` | 0.0000 | 9726 | min 0, max 4424350 | 0.0 (256063); 2.0 (20999); 3.0 (19323); 4.0 (17676); 5.0 (16376) | ACS 2024 Sex by Age [B01001_031]: Total:, Female:, 18 and 19 years (estimate). |
| `pop_age_female_20E` | `DOUBLE` | 0.0000 | 7141 | min 0, max 2335348 | 0.0 (405040); 2.0 (18951); 3.0 (18842); 4.0 (16840); 5.0 (15000) | ACS 2024 Sex by Age [B01001_032]: Total:, Female:, 20 years (estimate). |
| `pop_age_female_21E` | `DOUBLE` | 0.0000 | 7111 | min 0, max 2283357 | 0.0 (403686); 2.0 (19556); 3.0 (18804); 4.0 (16548); 5.0 (15135) | ACS 2024 Sex by Age [B01001_033]: Total:, Female:, 21 years (estimate). |
| `pop_age_female_22_24E` | `DOUBLE` | 0.0000 | 11175 | min 0, max 6467461 | 0.0 (200589); 2.0 (16877); 3.0 (15391); 4.0 (14867); 6.0 (13671) | ACS 2024 Sex by Age [B01001_034]: Total:, Female:, 22 to 24 years (estimate). |
| `pop_age_female_25_29E` | `DOUBLE` | 0.0000 | 13908 | min 0, max 11411800 | 0.0 (135576); 2.0 (12746); 4.0 (11935); 6.0 (11727); 3.0 (11633) | ACS 2024 Sex by Age [B01001_035]: Total:, Female:, 25 to 29 years (estimate). |
| `pop_age_female_30_34E` | `DOUBLE` | 0.0000 | 13677 | min 0, max 11590116 | 0.0 (126996); 2.0 (12563); 4.0 (11645); 5.0 (11618); 3.0 (11435) | ACS 2024 Sex by Age [B01001_036]: Total:, Female:, 30 to 34 years (estimate). |
| `pop_age_female_35_39E` | `DOUBLE` | 0.0000 | 13389 | min 0, max 11174476 | 0.0 (123534); 2.0 (12896); 4.0 (11747); 5.0 (11473); 3.0 (11418) | ACS 2024 Sex by Age [B01001_037]: Total:, Female:, 35 to 39 years (estimate). |
| `pop_age_female_40_44E` | `DOUBLE` | 0.0000 | 13317 | min 0, max 10780569 | 0.0 (117924); 2.0 (12707); 4.0 (11876); 3.0 (11475); 6.0 (11432) | ACS 2024 Sex by Age [B01001_038]: Total:, Female:, 40 to 44 years (estimate). |
| `pop_age_female_45_49E` | `DOUBLE` | 0.0000 | 13390 | min 0, max 11352936 | 0.0 (108061); 2.0 (11831); 4.0 (11522); 3.0 (11106); 5.0 (10960) | ACS 2024 Sex by Age [B01001_039]: Total:, Female:, 45 to 49 years (estimate). |
| `pop_age_female_50_54E` | `DOUBLE` | 0.0000 | 13645 | min 0, max 11475456 | 0.0 (93680); 6.0 (10851); 2.0 (10837); 4.0 (10776); 5.0 (10640) | ACS 2024 Sex by Age [B01001_040]: Total:, Female:, 50 to 54 years (estimate). |
| `pop_age_female_55_59E` | `DOUBLE` | 0.0000 | 13589 | min 0, max 11202165 | 0.0 (84223); 6.0 (11044); 7.0 (10990); 8.0 (10645); 4.0 (10530) | ACS 2024 Sex by Age [B01001_041]: Total:, Female:, 55 to 59 years (estimate). |
| `pop_age_female_60_61E` | `DOUBLE` | 0.0000 | 8870 | min 0, max 4492270 | 0.0 (159856); 2.0 (22201); 3.0 (18911); 4.0 (18558); 5.0 (17196) | ACS 2024 Sex by Age [B01001_042]: Total:, Female:, 60 and 61 years (estimate). |
| `pop_age_female_62_64E` | `DOUBLE` | 0.0000 | 10320 | min 0, max 6528522 | 0.0 (122587); 2.0 (17360); 4.0 (15954); 3.0 (15708); 5.0 (15353) | ACS 2024 Sex by Age [B01001_043]: Total:, Female:, 62 to 64 years (estimate). |
| `pop_age_female_65_66E` | `DOUBLE` | 0.0000 | 8288 | min 0, max 4112705 | 0.0 (170127); 2.0 (24204); 3.0 (20458); 4.0 (19416); 5.0 (18055) | ACS 2024 Sex by Age [B01001_044]: Total:, Female:, 65 and 66 years (estimate). |
| `pop_age_female_67_69E` | `DOUBLE` | 0.0000 | 9411 | min 0, max 5713148 | 0.0 (138698); 2.0 (20026); 3.0 (17605); 4.0 (17371); 5.0 (16066) | ACS 2024 Sex by Age [B01001_045]: Total:, Female:, 67 to 69 years (estimate). |
| `pop_age_female_70_74E` | `DOUBLE` | 0.0000 | 10836 | min 0, max 8208903 | 0.0 (111400); 2.0 (15216); 4.0 (14261); 3.0 (14182); 5.0 (13912) | ACS 2024 Sex by Age [B01001_046]: Total:, Female:, 70 to 74 years (estimate). |
| `pop_age_female_75_79E` | `DOUBLE` | 0.0000 | 9326 | min 0, max 5750350 | 0.0 (141296); 2.0 (19316); 4.0 (17126); 3.0 (16911); 5.0 (15984) | ACS 2024 Sex by Age [B01001_047]: Total:, Female:, 75 to 79 years (estimate). |
| `pop_age_female_80_84E` | `DOUBLE` | 0.0000 | 8090 | min 0, max 3775132 | 0.0 (186236); 2.0 (24077); 3.0 (19876); 4.0 (19125); 5.0 (17735) | ACS 2024 Sex by Age [B01001_048]: Total:, Female:, 80 to 84 years (estimate). |
| `pop_age_female_85_plusE` | `DOUBLE` | 0.0000 | 8608 | min 0, max 4262925 | 0.0 (206103); 2.0 (24026); 3.0 (19148); 4.0 (18478); 5.0 (16505) | ACS 2024 Sex by Age [B01001_049]: Total:, Female:, 85 years and over (estimate). |
## Data Quality Notes
- Columns with non-zero null rates: median_age.E=1.7624%
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_age_silver.R:202:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="age_base"),`

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
