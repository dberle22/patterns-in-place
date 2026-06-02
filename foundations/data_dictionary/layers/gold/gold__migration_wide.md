# Data Dictionary: gold.migration_wide

## Overview
- **Table**: `gold.migration_wide`
- **Purpose**: ACS-first migration and nativity mart for mobility, churn, and foreign-born context.
- **Row count**: 1,020,930
- **KPI applicability**: Gold output table with derived migration rates and placeholder IRS fields for the next phase.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
  - Live uniqueness check on April 10, 2026: rows=1,020,930; distinct PK=1,020,930; duplicates=0
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: 9 geo levels; 115,976 distinct `geo_id`

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `year`
- **ACS mobility counts and shares**: `mig_*`, `pct_same_house`, `pct_moved_same_cnty`, `pct_moved_same_st`, `pct_moved_diff_st`, `pct_moved_abroad`
- **Derived mobility metrics**: `mobility_rate`, `pct_moved_domestic`, `migration_churn`, `migration_churn_count`
- **Nativity counts and shares**: `pop_nativity_total`, `pop_native`, `pop_foreign_born`, `pop_foreign_born_citizen`, `pop_foreign_born_noncitizen`, `pct_native`, `pct_foreign_born`, `pct_non_citizen`, `pct_foreign_born_citizen`, `pct_foreign_born_noncitizen`
- **Future IRS placeholders**: `irs_inflow_total`, `irs_outflow_total`, `irs_net_migration`, `irs_net_migration_rate`, `irs_migration_churn`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- `mobility_rate` is null in 6,288 rows, matching missing ACS migration base coverage.
- All IRS fields are currently null in all 1,020,930 rows by design for the ACS-only first version.

## Lineage
1. **Primary build script**: [scripts/etl/gold/gold_migration_wide.sql]
2. **Primary upstream**:
   - `silver.migration_kpi`

## Known Gaps / To-Dos
- IRS migration is intentionally deferred and currently represented with null placeholder fields.
- If IRS flows are added later, document whether they apply only to county/CBSA/state or are backfilled to broader geographies.
