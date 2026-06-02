# Data Dictionary: silver.bea_regional_metrics_ref

## Overview
- **Table**: `silver.bea_regional_metrics_ref`
- **Purpose**: Silver layer analytical table.
- **Row count**: 109
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `line_code`.
- **Primary key candidate (recommended)**: (`line_code`)
  - `line_code` => rows=109, distinct=50, duplicates=59
  - `table` => rows=109, distinct=6, duplicates=103
- **Time coverage**: `vintage` min=2025-12-09, max=2025-12-09
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `table` | `VARCHAR` | 0.0000 | 6 | len 5-6 | CAGDP2 (34); CAGDP9 (34); CAINC4 (20); SARPP (10); MARPP (8) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `line_code` | `VARCHAR` | 0.0000 | 50 | len 1-2 | 1 (5); 2 (5); 3 (5); 10 (4); 6 (4) | Line code from BEA source tables, used to link to BEA datasets and metadata. Examples include: 1, 2, 3, 10, 6, etc. |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 97 | len 10-107 | Employer contributions for government social insurance (2); Implicit regional price deflator (2); Per capita personal income (2); Personal income (2); Population (2) | Cleaned description of the economic activity in the row (from BEA metadata). |
| `metric_key` | `VARCHAR` | 0.0000 | 98 | len 7-46 | pi_per_capita (2); pi_total (2); population (2); rpp_all_items (2); rpp_goods (2) | Metric key for the economic activity in the row (from BEA metadata). |
| `metric_label` | `VARCHAR` | 0.0000 | 108 | len 19-116 | [CAINC4] Employer contributions for government social insurance (2); [CAGDP2] Gross Domestic Product (GDP): Accommodation and food services (72) (1); [CAGDP2] Gross Domestic Product (GDP): Administrative and support and waste management and remediation services (56) (1); [CAGDP2] Gross Domestic Product (GDP): Agriculture, forestry, fishing and hunting (11) (1); [CAGDP2] Gross Domestic Product (GDP): All industry total (1) | Metric label for the economic activity in the row, including BEA table code and line description (from BEA metadata). |
| `include_in_wide` | `BOOLEAN` | 0.0000 | 2 | len 4-5 | false (94); true (15) | Boolean flag indicating whether the metric should be included in wide-format tables (for example, silver.bea_regional_cagdp2_wide or silver.bea_regional_cagdp9_wide). |
| `naics_raw` | `VARCHAR` | 44.9541 | 30 | len 2-15 | NULL (49); 11 (2); 11,21 (2); 21 (2); 22 (2) | Raw NAICS code(s) associated with the metric, from BEA metadata. Needs confirmation. |
| `is_aggregate` | `BOOLEAN` | 0.0000 | 2 | len 4-5 | false (83); true (26) | Whether the metric is an aggregate (i.e., not a component of another metric). |
| `topic` | `VARCHAR` | 0.0000 | 4 | len 3-6 | gdp (68); income (23); other (10); prices (8) | Topic of the metric (e.g., gdp, income, prices). |
| `vintage` | `VARCHAR` | 0.0000 | 1 | len 10-10 | 2025-12-09 (109) | The vintage date of the BEA data (i.e., the date when the data was last updated). |
## Data Quality Notes
- Columns with non-zero null rates: naics_raw=44.9541%
- Key uniqueness check for recommended PK (`line_code`) found 59 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/bea_cainc4_silver.R:44:line_codes_ref <- dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref")`
   - `scripts/etl/silver/bea_cagdp9_silver.R:44:line_codes_ref <- dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref")`
   - `scripts/etl/silver/bea_metric_dictionary.R:214:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="bea_regional_metrics_ref"),`
   - `scripts/etl/silver/bea_cainc1_silver.R:43:line_codes_ref <- dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref")`
   - `scripts/etl/silver/bea_marpp_silver.R:42:line_codes_ref <- dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref")`
   - `scripts/etl/silver/bea_cagdp2_silver.R:44:line_codes_ref <- dbGetQuery(con, "SELECT * FROM silver.bea_regional_metrics_ref")`

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
