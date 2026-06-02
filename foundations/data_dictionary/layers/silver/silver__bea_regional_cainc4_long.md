# Data Dictionary: silver.bea_regional_cainc4_long

## Overview
- **Table**: `silver.bea_regional_cainc4_long`
- **Purpose**: Silver layer analytical table.
- **Row count**: 1,097,160
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + period + metric_key`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `metric_key`)
  - `geo_level + geo_id + period` => rows=1097160, distinct=86040, duplicates=1011120
  - `geo_level + geo_id + period + metric_key` => rows=1097160, distinct=1097160, duplicates=0
  - `geo_level + geo_id + period + table + code + line_code` => rows=1097160, distinct=1097160, duplicates=0
  - `geo_level + geo_id + period + table + metric_key` => rows=1097160, distinct=1097160, duplicates=0
  - `table + geo_level + geo_id + period + line_code` => rows=1097160, distinct=1097160, duplicates=0
- **Time coverage**: `period` min=2000, max=2023
- **Geo coverage**: distinct_geo_levels=3; distinct_geo_id=3585

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `code` | `VARCHAR` | 0.0000 | 13 | len 9-9 | CAINC4-11 (86040); CAINC4-35 (86040); CAINC4-42 (86040); CAINC4-45 (86040); CAINC4-46 (86040) | BEA Table Code, used to link to BEA datasets and metadata. Examples include: CAGDP2-1, CAGDP2-10, CAINC1-1, etc. |
| `table` | `VARCHAR` | 0.0000 | 1 | len 6-6 | CAINC4 (1097160) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `geo_level` | `VARCHAR` | 0.0000 | 3 | len 4-6 | county (979680); cbsa (101640); state (15840) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 3585 | len 5-5 | 01001 (312); 01003 (312); 01005 (312); 01007 (312); 01009 (312) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 3585 | len 4-78 | Abbeville, SC (312); Acadia, LA (312); Accomack, VA (312); Ada, ID (312); Adair, IA (312) | Geographic name (from ACS NAME) |
| `period` | `INTEGER` | 0.0000 | 24 | min 2000, max 2023 | 2000 (45715); 2001 (45715); 2002 (45715); 2003 (45715); 2004 (45715) | Time period for the observation (usually calendar year). |
| `line_code` | `VARCHAR` | 0.0000 | 13 | len 2-2 | 11 (86040); 35 (86040); 42 (86040); 45 (86040); 46 (86040) | Description of the economic activity in the row (from BEA metadata). |
| `unit_raw` | `VARCHAR` | 0.0000 | 1 | len 20-20 | Thousands of dollars (1097160) | Raw unit of measure for the value in long-format records (before any scaling or conversion). |
| `unit_mult` | `INTEGER` | 0.0000 | 1 | min 3, max 3 | 3 (1097160) | Multiplier for the raw value (i.e., 10^3 for thousands of dollars). |
| `value_raw` | `DOUBLE` | 0.0000 | 605835 | min -263181240, max 23279071000 | 0.0 (10176); 12696.0 (20); 1520.0 (20); 24984.0 (20); 4457.0 (20) | Raw value for the metric in long-format records (before any scaling or conversion). |
| `value` | `DOUBLE` | 0.0000 | 605835 | min -263181240000, max 23279071000000 | 0.0 (10176); 12696000.0 (20); 1520000.0 (20); 24984000.0 (20); 4457000.0 (20) | Numeric value for the metric in long-format records. |
| `note_ref` | `VARCHAR` | 59.0922 | 17 | len 1-8 | NULL (648336); 1 (83616); 6 (83616); 7 (83616); 8 (83616) | Reference number for the note in the BEA metadata. |
| `metric_key` | `VARCHAR` | 0.0000 | 13 | len 10-29 | pi_dividends_interest_rent (86040); pi_earnings_workplace (86040); pi_employer_pension_insurance (86040); pi_employer_social_insurance (86040); pi_net_earnings_residence (86040) | Key for the economic activity in the row (from BEA metadata). |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 13 | len 18-63 | Adjustment for residence (86040); Dividends, interest, and rent (86040); Earnings by place of work (86040); Employer contributions for employee pension and insurance funds (86040); Employer contributions for government social insurance (86040) | Description of the economic activity in the row (from BEA metadata). |
## Data Quality Notes
- Columns with non-zero null rates: note_ref=59.0922%
- Key uniqueness check for recommended PK (`geo_level + geo_id + period + metric_key`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/bea_cainc4_silver.R:158:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_cainc4_long"),`

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
