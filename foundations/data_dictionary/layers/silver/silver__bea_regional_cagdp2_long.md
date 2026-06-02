# Data Dictionary: silver.bea_regional_cagdp2_long

## Overview
- **Table**: `silver.bea_regional_cagdp2_long`
- **Purpose**: Silver layer analytical table.
- **Row count**: 1,618,792
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period + metric_key`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `metric_key`)
  - `geo_level + geo_id + period` => rows=1618792, distinct=57814, duplicates=1560978
  - `geo_level + geo_id + period + metric_key` => rows=1618792, distinct=1618792, duplicates=0
  - `geo_level + geo_id + period + table + metric_key` => rows=1618792, distinct=1618792, duplicates=0
  - `geo_id + period` => rows=1618792, distinct=57786, duplicates=1561006
  - `table` => rows=1618792, distinct=1, duplicates=1618791
- **Time coverage**: `period` min=2001, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4089

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAGDP2 (1618792) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `code` | `VARCHAR` | 0.0000 | 28 | len 8-9 | CAGDP2-1 (57814); CAGDP2-10 (57814); CAGDP2-11 (57814); CAGDP2-12 (57814); CAGDP2-13 (57814) | BEA Table Code, used to link to BEA datasets and metadata. Examples include: CAGDP2-1, CAGDP2-10, CAINC1-1, etc. |
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (1222256); cbsa (357896); state (38640) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4089 | len 5-5 | 32000 (1036); 45000 (1036); 00000 (644); 01000 (644); 02000 (644) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 3976 | len 4-48 | Alamosa, CO (784); Alpena, MI (784); Andrews, TX (784); Ashland, OH (784); Atchison, KS (784) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 23 | min 2001, max 2023 | 2010 (114548); 2011 (114548); 2012 (114548); 2013 (114548); 2014 (114548) | Time period for the observation (usually calendar year). |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 28 | len 44-107 | Gross Domestic Product (GDP): Accommodation and food services (72) (57814); Gross Domestic Product (GDP): Administrative and support and waste management and remediation services (56) (57814); Gross Domestic Product (GDP): All industry total (57814); Gross Domestic Product (GDP): Arts, entertainment, and recreation (71) (57814); Gross Domestic Product (GDP): Construction (23) (57814) | Description of the economic activity in the row (from BEA metadata). |
| `metric_key` | `VARCHAR` | 0.0000 | 28 | len 9-41 | gdp_accomodation_food (57814); gdp_arts_entertainment (57814); gdp_construction (57814); gdp_durable_manufacturing (57814); gdp_education_all (57814) | Key for the economic activity in the row (from BEA metadata). |
| `value` | `DOUBLE` | 0.0000 | 582415 | min 0, max 27720709000000 | 0.0 (257676); 1000.0 (114); 4000.0 (110); 18000.0 (103); 2000.0 (103) | Numeric value for the metric in long-format records. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + period + metric_key`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/bea_cagdp2_silver.R:154:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cagdp2_long"),`

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
