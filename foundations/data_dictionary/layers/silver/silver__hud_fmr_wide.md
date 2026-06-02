# Data Dictionary: silver.hud_fmr_wide

## Overview
- **Table**: `silver.hud_fmr_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 33,080
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=33080, distinct=29074, duplicates=4006
  - `geo_id + period` => rows=33080, distinct=27443, duplicates=5637
  - `geo_level` => rows=33080, distinct=4, duplicates=33076
- **Time coverage**: `period` min=2023, max=2023
- **Geo coverage**: distinct_geo_levels=4; distinct_geo_id=27442

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 4 | len 4-8 | Zip Code (27331); County (4764); CBSA (929); State (56) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0030 | 27442 | len 2-5 | 23003 (72); 23019 (67); 25027 (60); 25017 (54); 23029 (48) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0030 | 29072 | len 2-46 | Aroostook County, ME (71); Penobscot County, ME (67); Worcester County, MA (60); Middlesex County, MA (54); Washington County, ME (48) | Geographic name (from ACS NAME) |
| `period` | `DOUBLE` | 0.0000 | 1 | min 2023, max 2023 | 2023.0 (33080) | Time period for the observation (usually calendar year). |
| `fmr_0br` | `DOUBLE` | 0.0000 | 1063 | min 360, max 3280 | 660.0 (642); 690.0 (589); 630.0 (559); 710.0 (538); 620.0 (517) | Fair Market Rent (40th Percentile) for 0-bedroom units. |
| `fmr_1br` | `DOUBLE` | 0.0000 | 1124 | min 390, max 4000 | 740.0 (536); 720.0 (507); 790.0 (503); 680.0 (497); 760.0 (482) | Fair Market Rent (40th Percentile) for 1-bedroom units. |
| `fmr_2br` | `DOUBLE` | 0.0000 | 1207 | min 440, max 4780 | 830.0 (663); 930.0 (461); 860.0 (442); 910.0 (441); 880.0 (438) | Fair Market Rent (40th Percentile) for 2-bedroom units. |
| `fmr_3br` | `DOUBLE` | 0.0000 | 1452 | min 550, max 5870 | 1170.0 (414); 1110.0 (386); 1160.0 (354); 1250.0 (339); 1180.0 (323) | Fair Market Rent (40th Percentile) for 3-bedroom units. |
| `fmr_4br` | `DOUBLE` | 0.0000 | 1604 | min 596, max 6420 | 1410.0 (354); 1310.0 (351); 1320.0 (307); 1500.0 (288); 1380.0 (282) | Fair Market Rent (40th Percentile) for 4-bedroom units. |
## Data Quality Notes
- Columns with non-zero null rates: geo_id=0.003%, geo_name=0.003%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) found 4006 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/hud_fmr_silver.R:109:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="hud_fmr_wide"),`

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
