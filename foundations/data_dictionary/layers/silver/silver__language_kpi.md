# Data Dictionary: silver.language_kpi

## Overview
- **Table**: `silver.language_kpi`
- **Purpose**: Silver language KPI table (`kpi` type).
- **Row count**: 1,331,868
- **KPI applicability**: KPI table (or has KPI dictionary entries).

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1331868, distinct=1331868, duplicates=0
  - `geo_level + geo_id + year` => rows=1331868, distinct=1331868, duplicates=0
  - `geo_id + year` => rows=1331868, distinct=1315425, duplicates=16443
  - `geo_level` => rows=1331868, distinct=9, duplicates=1331859
- **Time coverage**: `year` min=2016, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=165549

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | tract (714268); zcta (300692); place (278953); county (28988); cbsa (8373) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 165,549 | len 1-11 | 1 (27); 01001 (18); 01003 (18); 01005 (18); 01007 (18) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 251,070 | len 4-81 | Alexandria city, Virginia (18); Baltimore city, Maryland (18); Bristol city, Virginia (18); Buena Vista city, Virginia (18); Carson City, Nevada (18) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 9 | min 2016, max 2024 | 2024 (154726); 2023 (154720); 2022 (154598); 2021 (154311); 2020 (153657) | Observation year or period year for the row. |
| `language_total` | `DOUBLE` | 99.3355 | 478 | min 0, max 316142548 | NULL (1323018); 0.0 (8373); 1000367.0 (1); 1001567.0 (1); 1002024.0 (1) | Total population age 5 and older in the language-spoken-at-home universe. |
| `language_english_only` | `DOUBLE` | 99.3355 | 478 | min 0, max 245767039 | NULL (1323018); 0.0 (8373); 1002753.0 (1); 1012068.0 (1); 1014495.0 (1) | Population age 5 and older who speak only English at home. |
| `language_non_english` | `DOUBLE` | 99.3355 | 478 | min 0, max 70375509 | NULL (1323018); 0.0 (8373); 100557.0 (1); 1016077.0 (1); 103247.0 (1) | Population age 5 and older who speak a language other than English at home. |
| `language_limited_english` | `DOUBLE` | 99.3355 | 478 | min 0, max 27139643 | NULL (1323018); 0.0 (8373); 100442.0 (1); 100626.0 (1); 100828.0 (1) | Population age 5 and older who speak a language other than English at home and speak English less than very well. |
| `language_spanish` | `DOUBLE` | 99.3355 | 478 | min 0, max 42869908 | NULL (1323018); 0.0 (8373); 10407915.0 (1); 10446277.0 (1); 10462968.0 (1) | Population age 5 and older who speak Spanish at home. |
| `language_other_indo_european` | `DOUBLE` | 99.3355 | 478 | min 0, max 12249474 | NULL (1323018); 0.0 (8373); 100325.0 (1); 100733.0 (1); 100894.0 (1) | Population age 5 and older who speak a non-Spanish Indo-European language at home. |
| `language_asian_pacific` | `DOUBLE` | 99.3355 | 477 | min 0, max 11320253 | NULL (1323018); 0.0 (8373); 4681.0 (2); 10096.0 (1); 10172370.0 (1) | Population age 5 and older who speak an Asian or Pacific language at home. |
| `language_middle_eastern_african` | `DOUBLE` | 99.3355 | 476 | min 0, max 3292109 | NULL (1323018); 0.0 (8373); 12844.0 (2); 5851.0 (2); 100358.0 (1) | Population age 5 and older who speak an Arabic, Afro-Asiatic, or African language at home. |
| `language_native_north_american` | `DOUBLE` | 99.3355 | 437 | min 0, max 359459 | NULL (1323018); 0.0 (8380); 58.0 (4); 1072.0 (3); 608.0 (3) | Population age 5 and older who speak a Native North American language at home. |
| `language_other_unspecified` | `DOUBLE` | 99.3355 | 463 | min 0, max 330049 | NULL (1323018); 0.0 (8373); 1082.0 (2); 1509.0 (2); 1567.0 (2) | Population age 5 and older who speak another or unspecified language at home. |
| `pct_english_only` | `DOUBLE` | 99.9642 | 477 | min 0.0452772129635245, max 0.975544437972141 | NULL (1331391); 0.04527721296352453 (1); 0.0489460993763958 (1); 0.05048354093441852 (1); 0.05146574370331206 (1) | Share of the language-spoken-at-home universe that speaks only English at home. |
| `pct_non_english` | `DOUBLE` | 99.9642 | 477 | min 0.0244555620278594, max 0.954722787036476 | NULL (1331391); 0.024455562027859448 (1); 0.02458062516490974 (1); 0.02470040858963384 (1); 0.024780273366929458 (1) | Share of the language-spoken-at-home universe that speaks a language other than English at home. |
| `pct_limited_english` | `DOUBLE` | 99.9642 | 477 | min 0.00647606957617462, max 0.781100784498445 | NULL (1331391); 0.006476069576174622 (1); 0.006673140021496572 (1); 0.006675723472574382 (1); 0.007002849178139894 (1) | Share of the language-spoken-at-home universe that speaks English less than very well. |
| `pct_spanish` | `DOUBLE` | 99.9642 | 477 | min 0.00872932049975187, max 0.953219334842106 | NULL (1331391); 0.008729320499751872 (1); 0.00883735040655288 (1); 0.009022143824563539 (1); 0.009035964098973805 (1) | Share of the language-spoken-at-home universe that speaks Spanish at home. |
| `pct_other_indo_european` | `DOUBLE` | 99.9642 | 477 | min 0.000911773949187724, max 0.0926083202886948 | NULL (1331391); 0.0009117739491877244 (1); 0.0009413334439908197 (1); 0.0009424144456511605 (1); 0.0009495559383465998 (1) | Share of the language-spoken-at-home universe that speaks a non-Spanish Indo-European language at home. |
| `pct_asian_pacific` | `DOUBLE` | 99.9642 | 477 | min 0.000366446522109685, max 0.222495072199404 | NULL (1331391); 0.000366446522109685 (1); 0.000422218037319137 (1); 0.00042696079521448106 (1); 0.00042702713248029064 (1) | Share of the language-spoken-at-home universe that speaks an Asian or Pacific language at home. |
| `pct_middle_eastern_african` | `DOUBLE` | 99.9642 | 477 | min 0.000119164879977446, max 0.0269652611931325 | NULL (1331391); 0.00011916487997744647 (1); 0.00013191701119405643 (1); 0.00015955039547871792 (1); 0.0001601516693279485 (1) | Share of the language-spoken-at-home universe that speaks an Arabic, Afro-Asiatic, or African language at home. |
| `pct_native_north_american` | `DOUBLE` | 99.9642 | 471 | min 0, max 0.0498142384438085 | NULL (1331391); 0.0 (7); 0.00010027406251818886 (1); 0.00010137373448882232 (1); 0.00010245545002111222 (1) | Share of the language-spoken-at-home universe that speaks a Native North American language at home. |
| `pct_other_unspecified` | `DOUBLE` | 99.9642 | 477 | min 1.881550736486e-05, max 0.0100992872081796 | NULL (1331391); 0.00010302769048049181 (1); 0.0001076229207501997 (1); 0.00013677657956415054 (1); 0.00013732476714912737 (1) | Share of the language-spoken-at-home universe that speaks another or unspecified language at home. |
## Data Quality Notes
- Columns with non-zero null rates: language_total=99.3355%, language_english_only=99.3355%, language_non_english=99.3355%, language_limited_english=99.3355%, language_spanish=99.3355%, language_other_indo_european=99.3355%, language_asian_pacific=99.3355%, language_middle_eastern_african=99.3355%, language_native_north_american=99.3355%, language_other_unspecified=99.3355%, ...
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `foundations/etl/silver/acs_language_silver.R writes silver.language_kpi from staging.acs_language_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Re-run the landed profile after major ACS topic changes and sync both this `.md` file and the companion `.yml` artifact.
