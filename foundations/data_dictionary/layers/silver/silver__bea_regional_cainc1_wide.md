# Data Dictionary: silver.bea_regional_cainc1_wide

## Overview
- **Table**: `silver.bea_regional_cainc1_wide`
- **Purpose**: Silver layer analytical table.
- **Row count**: 98,712
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
  - `geo_level + geo_id + period` => rows=98712, distinct=98712, duplicates=0
  - `geo_id + period` => rows=98712, distinct=98664, duplicates=48
  - `geo_level` => rows=98712, distinct=3, duplicates=98709
- **Time coverage**: `period` min=2000, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4111

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (75360); cbsa (21912); state (1440) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4111 | len 5-5 | 32000 (48); 45000 (48); 00000 (24); 01000 (24); 01001 (24) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 4000 | len 4-48 | Alamosa, CO (48); Alpena, MI (48); Andrews, TX (48); Ashland, OH (48); Atchison, KS (48) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 24 | min 2000, max 2023 | 2000 (4113); 2001 (4113); 2002 (4113); 2003 (4113); 2004 (4113) | Time period for the observation (usually calendar year). |
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAINC1 (98712) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `pi_total` | `DOUBLE` | 0.0000 | 82990 | min 0, max 23380269000000 | 0.0 (663); 764792000.0 (5); 1011444000.0 (4); 1045353000.0 (4); 1092351000.0 (4) | Total Personal Income (PI) for the geographic unit and time period, from BEA CAINC1 table. |
| `population` | `DOUBLE` | 0.0000 | 60318 | min 0, max 334914900 | 0.0 (663); 14010.0 (9); 21763.0 (9); 25263.0 (9); 9260.0 (9) | Population for the geographic unit and time period, from BEA CAINC1 table. |
| `pi_per_capita` | `DOUBLE` | 0.0000 | 84029 |  | -nan (663); 100242.35461140468 (2); 101014.900783481 (2); 102019.27421379137 (2); 102125.82402697089 (2) | Personal Income (PI) per capita for the geographic unit and time period, calculated as pi_total / population. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + period`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_income.sql:58:from metro_deep_dive.silver.bea_regional_cainc1_wide cainc1`
   - `scripts/etl/gold/gold_economy_wide.sql:61:from metro_deep_dive.silver.bea_regional_cainc1_wide cainc1`
   - `scripts/etl/gold/gold_economy_wide.sql:269:from metro_deep_dive.silver.bea_regional_cainc1_wide inc`
   - `scripts/etl/silver/bea_cainc1_silver.R:185:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cainc1_wide"),`
2. **Downstream usage (examples)**:
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.Rmd:92:from metro_deep_dive.silver.bea_regional_cainc1_wide cainc`
   - `notebooks/national_analyses/real_personal_income/real_personal_income_base.sql:56:from metro_deep_dive.silver.bea_regional_cainc1_wide cainc`
   - `notebooks/national_analyses/real_personal_income/real_personal_income_analysis.nb.html:1927:from metro_deep_dive.silver.bea_regional_cainc1_wide cainc`

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
