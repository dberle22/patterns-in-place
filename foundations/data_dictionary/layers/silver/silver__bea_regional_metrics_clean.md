# Data Dictionary: silver.bea_regional_metrics_clean

## Overview
- **Table**: `silver.bea_regional_metrics_clean`
- **Purpose**: Silver layer analytical table.
- **Row count**: 99
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `line_code`.
- **Primary key candidate (recommended)**: (`line_code`)
  - `line_code` => rows=99, distinct=49, duplicates=50
  - `table` => rows=99, distinct=5, duplicates=94
- **Time coverage**: `vintage` min=2025-11-16, max=2025-11-16
- **Geo coverage**: No standard geography columns detected.

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `table` | `VARCHAR` | 0.0000 | 5 | len 5-6 | CAGDP2 (34); CAGDP9 (34); CAINC4 (20); MARPP (8); CAINC1 (3) | BEA source table identifier (for example, CAGDP2, CAGDP9, CAINC1, CAINC4, MARPP). |
| `line_code` | `VARCHAR` | 0.0000 | 49 | len 1-2 | 1 (4); 2 (4); 3 (4); 10 (3); 11 (3) | Descriptor for the metric in the row, based on BEA line codes. Needs confirmation. |
| `line_desc_clean` | `VARCHAR` | 0.0000 | 95 | len 10-107 | Employer contributions for government social insurance (2); Per capita personal income (2); Personal income (2); Population (2); Adjustment for residence (1) | Cleaned description of the economic activity in the row (from BEA metadata). |
| `metric_key` | `VARCHAR` | 0.0000 | 96 | len 7-46 | pi_per_capita (2); pi_total (2); population (2); gdp_accomodation_food (1); gdp_agriculture (1) | Metric key for the economic activity in the row (from BEA metadata). |
| `metric_label` | `VARCHAR` | 0.0000 | 98 | len 19-116 | [CAINC4] Employer contributions for government social insurance (2); [CAGDP2] Gross Domestic Product (GDP): Accommodation and food services (72) (1); [CAGDP2] Gross Domestic Product (GDP): Administrative and support and waste management and remediation services (56) (1); [CAGDP2] Gross Domestic Product (GDP): Agriculture, forestry, fishing and hunting (11) (1); [CAGDP2] Gross Domestic Product (GDP): All industry total (1) | Metric label for the economic activity in the row, including BEA table code and line description (from BEA metadata). |
| `include_in_wide` | `BOOLEAN` | 0.0000 | 2 | len 4-5 | false (87); true (12) | Whether the metric should be included in wide-format output. |
| `naics_raw` | `VARCHAR` | 39.3939 | 30 | len 2-15 | NULL (39); 11 (2); 11,21 (2); 21 (2); 22 (2) | Raw NAICS code(s) associated with the metric, from BEA metadata. Needs confirmation. |
| `is_aggregate` | `BOOLEAN` | 0.0000 | 2 | len 4-5 | false (73); true (26) | Whether the metric is an aggregate (i.e., not a component of another metric). |
| `topic` | `VARCHAR` | 0.0000 | 3 | len 3-6 | gdp (68); income (23); prices (8) | Topic of the metric (e.g., gdp, income, prices). |
| `vintage` | `VARCHAR` | 0.0000 | 1 | len 10-10 | 2025-11-16 (99) | The vintage date of the BEA data (i.e., the date when the data was last updated). |
## Data Quality Notes
- Columns with non-zero null rates: naics_raw=39.3939%
- Key uniqueness check for recommended PK (`line_code`) found 50 duplicate rows in current snapshot; treat key as provisional.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/gold/gold_economy_industry.sql:126:from metro_deep_dive.silver.bea_regional_metrics_clean`

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
