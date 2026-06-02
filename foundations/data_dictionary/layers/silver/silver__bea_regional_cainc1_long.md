# Data Dictionary: silver.bea_regional_cainc1_long

## Overview
- **Table**: `silver.bea_regional_cainc1_long`
- **Purpose**: Silver layer analytical table.
- **Row count**: 296,136
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period + metric_key`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `metric_key`)
  - `geo_level + geo_id + period` => rows=296136, distinct=98712, duplicates=197424
  - `geo_level + geo_id + period + metric_key` => rows=296136, distinct=296136, duplicates=0
  - `geo_level + geo_id + period + table + metric_key` => rows=296136, distinct=296136, duplicates=0
  - `geo_id + period` => rows=296136, distinct=98664, duplicates=197472
  - `table` => rows=296136, distinct=1, duplicates=296135
- **Time coverage**: `period` min=2000, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4111

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAINC1 (296136) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `code` | `VARCHAR` | 0.0000 | 3 | len 8-8 | CAINC1-1 (98712); CAINC1-2 (98712); CAINC1-3 (98712) | BEA Table Code, used to link to BEA datasets and metadata. Examples include: CAGDP2-1, CAGDP2-10, CAINC1-1, etc. |
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (226080); cbsa (65736); state (4320) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4111 | len 5-5 | 32000 (144); 45000 (144); 00000 (72); 01000 (72); 01001 (72) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 4000 | len 4-48 | Alamosa, CO (144); Alpena, MI (144); Andrews, TX (144); Ashland, OH (144); Atchison, KS (144) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 24 | min 2000, max 2023 | 2000 (12339); 2001 (12339); 2002 (12339); 2003 (12339); 2004 (12339) | Time period for the observation (usually calendar year). |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 3 | len 10-26 | Per capita personal income (98712); Personal income (98712); Population (98712) | Description of the economic activity in the row (from BEA metadata). |
| `metric_key` | `VARCHAR` | 0.0000 | 3 | len 8-13 | pi_per_capita (98712); pi_total (98712); population (98712) | Key for the economic activity in the row (from BEA metadata). |
| `value` | `DOUBLE` | 0.0000 | 226772 |  | 0.0 (1326); -nan (663); 14010.0 (9); 21763.0 (9); 25263.0 (9) | Numeric value for the metric in long-format records. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + period + metric_key`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/bea_cainc1_silver.R:182:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cainc1_long"),`

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
