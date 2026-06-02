# Data Dictionary: silver.bea_regional_cagdp9_long

## Overview
- **Table**: `silver.bea_regional_cagdp9_long`
- **Purpose**: Silver layer analytical table.
- **Row count**: 1,947,316
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period + metric_key`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `metric_key`)
  - `geo_level + geo_id + period` => rows=1947316, distinct=57274, duplicates=1890042
  - `geo_level + geo_id + period + metric_key` => rows=1947316, distinct=1947316, duplicates=0
  - `geo_level + geo_id + period + table + metric_key` => rows=1947316, distinct=1947316, duplicates=0
  - `geo_id + period` => rows=1947316, distinct=57246, duplicates=1890070
  - `table` => rows=1947316, distinct=1, duplicates=1947315
- **Time coverage**: `period` min=2010, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=4089

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAGDP9 (1947316) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `code` | `VARCHAR` | 0.0000 | 34 | len 8-9 | CAGDP9-1 (57274); CAGDP9-10 (57274); CAGDP9-11 (57274); CAGDP9-12 (57274); CAGDP9-13 (57274) | BEA Table Code, used to link to BEA datasets and metadata. Examples include: CAGDP2-1, CAGDP2-10, CAINC1-1, etc. |
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (1484168); cbsa (434588); state (28560) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 4089 | len 5-5 | 32000 (952); 45000 (952); 00000 (476); 01000 (476); 01001 (476) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 3976 | len 4-48 | Alamosa, CO (952); Alpena, MI (952); Andrews, TX (952); Ashland, OH (952); Atchison, KS (952) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 14 | min 2010, max 2023 | 2010 (139094); 2011 (139094); 2012 (139094); 2013 (139094); 2014 (139094) | Time period for the observation (usually calendar year). |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 34 | len 24-87 | Real GDP: Accommodation and food services (72) (57274); Real GDP: Administrative and support and waste management and remediation services (56) (57274); Real GDP: Agriculture, forestry, fishing and hunting (11) (57274); Real GDP: All industry total (57274); Real GDP: Arts, entertainment, and recreation (71) (57274) | Description of the economic activity in the row (from BEA metadata). |
| `metric_key` | `VARCHAR` | 0.0000 | 34 | len 14-46 | real_gdp_accomodation_food (57274); real_gdp_agriculture (57274); real_gdp_arts_entertainment (57274); real_gdp_arts_food_all (57274); real_gdp_construction (57274) | Key for the economic activity in the row (from BEA metadata). |
| `value` | `DOUBLE` | 0.0000 | 618487 | min 0, max 22671096000000 | 0.0 (308780); 1000.0 (180); 6000.0 (176); 19000.0 (172); 3000.0 (170) | Numeric value for the metric in long-format records. |
## Data Quality Notes
- No nulls observed in this snapshot.
- Key uniqueness check for recommended PK (`geo_level + geo_id + period + metric_key`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/bea_cagdp9_silver.R:156:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cagdp9_long"),`

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
