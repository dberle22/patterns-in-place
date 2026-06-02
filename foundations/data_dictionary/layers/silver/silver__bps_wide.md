# Data Dictionary: silver.bps_wide

## Overview
- **Table**: `silver.bps_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 998,801
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=998801, distinct=374406, duplicates=624395
  - `geo_id + period` => rows=998801, distinct=374226, duplicates=624575
  - `geo_level` => rows=998801, distinct=6, duplicates=998795
- **Time coverage**: `period` min=1980, max=2024
- **Geo coverage**: distinct_geo_levels=6; distinct_geo_id=18057

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 6 | len 4-8 | Place (857644); County (106162); CBSA (32075); State (2335); Division (405) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0035 | 18057 | len 1-7 | 42NA (65695); 36NA (40280); 55NA (29139); 26NA (27552); 39NA (26340) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0035 | 21928 | len 3-58 | Washington township (1388); Jackson township (1222); Washington County (1130); Franklin township (1030); Franklin County (1025) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 45 | min 1980, max 2024 | 2013 (24536); 2014 (24497); 2022 (24155); 2015 (24142); 2017 (24139) | Time period for the observation (usually calendar year). |
| `total_bldgs` | `DOUBLE` | 0.0000 | 8791 | min 0, max 846071 | 0.0 (230817); 1.0 (81903); 2.0 (59407); 3.0 (45222); 4.0 (36346) | Total Buildings in the geography and time period. |
| `total_units` | `DOUBLE` | 0.0000 | 10366 | min 0, max 1039044 | 0.0 (230814); 1.0 (77465); 2.0 (56303); 3.0 (42461); 4.0 (34629) | Total Units in the geography and time period. |
| `total_value` | `DOUBLE` | 0.0000 | 411653 | min 0, max 17670518000 | 0.0 (230760); 100000.0 (4040); 200000.0 (3865); 150000.0 (3813); 50000.0 (2949) | Total Value of all units in the geography and time period. |
| `bldgs_1_unit` | `DOUBLE` | 0.0000 | 8602 | min 0, max 826793 | 0.0 (239225); 1.0 (83693); 2.0 (60267); 3.0 (45549); 4.0 (36593) | Number of buildings with 1 unit in the geography and time period. |
| `bldgs_2_units` | `DOUBLE` | 0.0000 | 1298 | min 0, max 16090 | 0.0 (834822); 1.0 (50825); 2.0 (25842); 3.0 (15441); 4.0 (10594) | Number of buildings with 2 units in the geography and time period. |
| `bldgs_3_4_units` | `DOUBLE` | 0.0000 | 979 | min 0, max 10566 | 0.0 (886690); 1.0 (37954); 2.0 (17098); 3.0 (10121); 4.0 (7208) | Number of buildings with 3-4 units in the geography and time period. |
| `bldgs_5_units` | `DOUBLE` | 0.0000 | 1445 | min 0, max 25284 | 0.0 (852404); 1.0 (39215); 2.0 (18117); 3.0 (11343); 4.0 (8892) | Number of Buildings with 5+ units in the geography and time period. |
| `units_1_unit` | `DOUBLE` | 0.0000 | 8602 | min 0, max 826793 | 0.0 (239225); 1.0 (83693); 2.0 (60267); 3.0 (45549); 4.0 (36593) | Count of Units in 1 Unit buildings. Directly from BPS Survey |
| `units_2_units` | `DOUBLE` | 0.0000 | 1302 | min 0, max 32180 | 0.0 (834822); 2.0 (50824); 4.0 (25843); 6.0 (15441); 8.0 (10594) | Count of Units in 2 Unit buildings. Directly from BPS Survey |
| `units_3_4_units` | `DOUBLE` | 0.0000 | 1799 | min 0, max 40042 | 0.0 (886615); 4.0 (24237); 3.0 (13757); 8.0 (9282); 12.0 (5895) | Count of Units in 3-4 Unit buildings. Directly from BPS Survey |
| `units_5_units` | `DOUBLE` | 0.0000 | 5966 | min 0, max 348020 | 0.0 (852404); 6.0 (5600); 5.0 (5329); 8.0 (5192); 24.0 (4648) | Count of Units in 5+ Unit buildings. Directly from BPS Survey |
| `value_1_unit` | `DOUBLE` | 0.0000 | 397739 | min 0, max 15718555000 | 0.0 (238782); 100000.0 (4124); 200000.0 (3896); 150000.0 (3867); 50000.0 (3087) | Total value of 1 Unit buildings in the geography and time period. |
| `value_2_units` | `DOUBLE` | 0.0000 | 61225 | min 0, max 795796610 | 0.0 (834717); 100000.0 (1966); 200000.0 (1851); 150000.0 (1694); 60000.0 (1516) | Total value of 2 Unit buildings in the geography and time period. |
| `value_3_4_units` | `DOUBLE` | 0.0000 | 46132 | min 0, max 584622570 | 0.0 (887611); 200000.0 (1348); 300000.0 (1161); 100000.0 (1159); 150000.0 (1108) | Total value of 3-4 Unit buildings in the geography and time period. |
| `value_5_units` | `DOUBLE` | 0.0000 | 76546 | min 0, max 8573074500 | 0.0 (852064); 400000.0 (881); 500000.0 (880); 300000.0 (867); 600000.0 (797) | Total value of 5+ Unit buildings in the geography and time period. |
| `units_multifam` | `DOUBLE` | 0.0000 | 6396 | min 0, max 419894 | 0.0 (746854); 2.0 (29731); 4.0 (20554); 6.0 (11424); 8.0 (10369) | Count of Multifamily Units (2+ units). Sum of units in 2 Unit, 3-4 Unit, and 5+ Unit buildings. Directly from BPS Survey |
| `bldgs_multifam` | `DOUBLE` | 0.0000 | 2082 | min 0, max 51766 | 0.0 (746885); 1.0 (62437); 2.0 (31970); 3.0 (20394); 4.0 (15398) | Count of Multifamily Buildings (2+ units). Sum of 2 Unit, 3-4 Unit, and 5+ Unit buildings. Directly from BPS Survey |
| `value_multifam` | `DOUBLE` | 0.0000 | 118685 | min 0, max 8886951700 | 0.0 (747441); 200000.0 (2087); 100000.0 (1928); 150000.0 (1844); 300000.0 (1664) | Total value of Multifamily buildings (2+ units) in the geography and time period. |
| `avg_units_per_bldg` | `DOUBLE` | 23.1094 | 61891 | min 1, max 583 | 1.0 (516043); NULL (230817); 2.0 (4929); 1.5 (3944); 1.3333333333333333 (3190) | Average Units per Building (calculated as total_units / total_bldgs) |
| `avg_units_per_mf_bldg` | `DOUBLE` | 74.7782 | 24854 | min 1, max 676 | NULL (746885); 2.0 (62537); 4.0 (16505); 3.0 (10899); 5.0 (6671) | Average Units per Multifamily Building (calculated as total_multifam_units / total_multifam_bldgs) |
| `share_multifam_units` | `DOUBLE` | 23.1091 | 60583 | min 0, max 1 | 0.0 (516040); NULL (230814); 1.0 (8411); 0.6666666666666666 (4142); 0.5 (3956) | Share of total units that are in Multifamily buildings (2+ units) in the geography and time period. |
| `share_units_5_plus` | `DOUBLE` | 23.1091 | 54781 | min 0, max 1 | 0.0 (621590); NULL (230814); 1.0 (2885); 0.5 (871); 0.6666666666666666 (841) | Share of total units that are in 5+ Unit buildings in the geography and time period. |
| `share_units_1_unit` | `DOUBLE` | 23.1091 | 60583 | min 0, max 1 | 1.0 (516040); NULL (230814); 0.0 (8411); 0.3333333333333333 (4142); 0.5 (3956) | Share of total units that are in 1 Unit buildings in the geography and time period. |
| `structure_mix` | `VARCHAR` | 0.0000 | 3 | len 15-21 | mostly_single_family (917120); mostly_large_multifam (47855); mostly_multifam (33826) | Metadata column categorizing the structure mix of the geography and time period, based on share of units in 1 Unit, 2-4 Unit, and 5+ Unit buildings. |
## Data Quality Notes
- Columns with non-zero null rates: geo_id=0.0035%, geo_name=0.0035%, avg_units_per_bldg=23.1094%, avg_units_per_mf_bldg=74.7782%, share_multifam_units=23.1091%, share_units_5_plus=23.1091%, share_units_1_unit=23.1091%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) found 624395 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_housing_core.sql:71:FROM metro_deep_dive.silver.bps_wide bw `
   - `scripts/etl/silver/bps_silver.R:415:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bps_wide"),`
2. **Downstream usage (examples)**:
   - `notebooks/retail_opportunity_finder/tract_features.sql:43:  FROM metro_deep_dive.silver.bps_wide`
   - `notebooks/retail_opportunity_finder/cbsa_features.sql:88:  FROM metro_deep_dive.silver.bps_wide`

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
