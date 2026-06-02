# Data Dictionary: silver.xwalk_tract_county

## Overview
- **Table**: `silver.xwalk_tract_county`
- **Purpose**: Silver layer analytical table.
- **Row count**: 10,573
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `state_fip`.
- **Primary key candidate (recommended)**: (`state_fip`)
  - `state_fip` => rows=10573, distinct=3, duplicates=10570
- **Time coverage**: `vintage` min=2023, max=2023
- **Geo coverage**: distinct_tract_geoid=10573

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `state_fip` | `VARCHAR` | 0.0000 | 3 | len 2-2 | 12 (5122); 13 (2791); 37 (2660) | State FIPS code. |
| `county_fip` | `VARCHAR` | 0.0000 | 161 | len 3-3 | 086 (706); 057 (431); 011 (425); 099 (386); 121 (342) | County FIPS code. |
| `tract_fip` | `VARCHAR` | 0.0000 | 5896 | len 6-6 | 950100 (27); 960200 (27); 960100 (26); 960300 (24); 970200 (24) | Tract FIPS code. |
| `tract_geoid` | `VARCHAR` | 0.0000 | 10573 | len 11-11 | 12001000201 (1); 12001000202 (1); 12001000301 (1); 12001000302 (1); 12001000400 (1) | Tract GEOID, which is a concatenation of the state FIPS code, county FIPS code, and tract FIPS code. |
| `tract_name` | `VARCHAR` | 0.0000 | 5896 | len 1-7 | 9501 (27); 9602 (27); 9601 (26); 9603 (24); 9702 (24) | Name of Tract, defined by the Census Bureau. Typically a 4-digit number, but can include a suffix (e.g. '9501.01' or '9601A'). |
| `tract_name_long` | `VARCHAR` | 0.0000 | 5896 | len 14-20 | Census Tract 9501 (27); Census Tract 9602 (27); Census Tract 9601 (26); Census Tract 9603 (24); Census Tract 9702 (24) | Long name of the tract. |
| `state_abbr` | `VARCHAR` | 0.0000 | 3 | len 2-2 | FL (5122); GA (2791); NC (2660) | State abbreviation. |
| `county_name` | `VARCHAR` | 0.0000 | 280 | len 10-20 | Miami-Dade County (706); Broward County (416); Palm Beach County (372); Hillsborough County (333); Fulton County (327) | Name of the county. |
| `state_name` | `VARCHAR` | 0.0000 | 3 | len 7-14 | Florida (5122); Georgia (2791); North Carolina (2660) | Full name of the state. |
| `lsad` | `VARCHAR` | 0.0000 | 1 | len 2-2 | CT (10573) | LSAD (Legal Statistical Area Description) code for the tract. |
| `vintage` | `INTEGER` | 0.0000 | 1 | min 2023, max 2023 | 2023 (10573) | Year of the crosswalk data. |
| `source` | `VARCHAR` | 0.0000 | 1 | len 6-6 | TIGRIS (10573) | Source of the crosswalk data. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`state_fip`) found 10570 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/geo_crosswalks_silver.R:94:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="xwalk_tract_county"),`
2. **Downstream usage (examples)**:
   - `notebooks/retail_opportunity_finder/legacy/retail_opportunity_finder_dash_v1.qmd:192:  FROM metro_deep_dive.silver.xwalk_tract_county`
   - `notebooks/retail_opportunity_finder/tract_universe.sql:18:  FROM metro_deep_dive.silver.xwalk_tract_county`
   - `notebooks/retail_opportunity_finder/tract_features.sql:25:  FROM metro_deep_dive.silver.xwalk_tract_county t`
   - `notebooks/retail_opportunity_finder/sections/01_setup/section_01_checks.R:54:    FROM metro_deep_dive.silver.xwalk_tract_county`
   - `notebooks/retail_opportunity_finder/sections/03_eligibility_scoring/section_03_build.R:267:    FROM metro_deep_dive.silver.xwalk_tract_county`
   - `notebooks/retail_opportunity_finder/sections/02_market_overview/section_02_build.R:310:    FROM metro_deep_dive.silver.xwalk_tract_county`

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
