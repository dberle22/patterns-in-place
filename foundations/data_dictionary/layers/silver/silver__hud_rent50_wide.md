# Data Dictionary: silver.hud_rent50_wide

## Overview
- **Table**: `silver.hud_rent50_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 5,749
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=5749, distinct=4213, duplicates=1536
  - `geo_id + period` => rows=5749, distinct=4213, duplicates=1536
  - `geo_level` => rows=5749, distinct=3, duplicates=5746
- **Time coverage**: `period` min=2023, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4212

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | County (4764); CBSA (929); State (56) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0174 | 4212 | len 2-5 | 23003 (71); 23019 (67); 25027 (60); 25017 (54); 23029 (48) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0174 | 4211 | len 2-46 | Aroostook County, ME (71); Penobscot County, ME (67); Worcester County, MA (60); Middlesex County, MA (54); Washington County, ME (48) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 1 | min 2023, max 2023 | 2023 (5749) | Time period for the observation (usually calendar year). |
| `rent50_0br` | `DOUBLE` | 0.0000 | 879 | min 405, max 2443 | 2181.0 (114); 579.0 (104); 661.0 (80); 590.0 (78); 596.0 (65) | 50th percentile (median) rent for 0-bedroom units. |
| `rent50_1br` | `DOUBLE` | 0.0000 | 909 | min 421, max 3000 | 666.0 (164); 2368.0 (114); 706.0 (84); 776.0 (66); 804.0 (64) | 50th percentile (median) rent for 1-bedroom units. |
| `rent50_2br` | `DOUBLE` | 0.0000 | 927 | min 475, max 3590 | 877.0 (425); 2838.0 (114); 815.0 (96); 883.0 (82); 845.0 (78) | 50th percentile (median) rent for 2-bedroom units. |
| `rent50_3br` | `DOUBLE` | 0.0000 | 1129 | min 630, max 4406 | 3454.0 (114); 1246.0 (97); 1172.0 (91); 1267.0 (76); 1067.0 (69) | 50th percentile (median) rent for 3-bedroom units. |
| `rent50_4br` | `DOUBLE` | 0.0000 | 1224 | min 638, max 4823 | 3812.0 (114); 1329.0 (77); 1494.0 (70); 1421.0 (58); 1322.0 (54) | 50th percentile (median) rent for 4-bedroom units. |
## Data Quality Notes
- Columns with non-zero null rates: geo_id=0.0174%, geo_name=0.0174%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) found 1536 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/hud_fmr_silver.R:165:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="hud_rent50_wide"),`

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
