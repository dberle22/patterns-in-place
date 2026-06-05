# Data Dictionary: gold.migration_wide

## Overview
- **Table**: `gold.migration_wide`
- **Purpose**: ACS-backed migration and nativity mart with IRS migration summary enrichment for county, CBSA, and state rows.
- **Row count**: 1,891,571
- **KPI applicability**: Gold output table with ACS mobility rates plus IRS return-count and AGI migration fields where IRS summary coverage exists.

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
- **IRS return-count metrics**: `irs_inflow_total`, `irs_outflow_total`, `irs_net_migration`, `irs_net_migration_rate`, `irs_migration_churn`
- **IRS AGI metrics**: `irs_inflow_agi`, `irs_outflow_agi`, `irs_net_agi`

## Data Quality Notes
- Live query checks confirm the intended `geo_level + geo_id + year` grain with zero duplicate keys.
- `mobility_rate` is null in 6,288 rows, matching missing ACS migration base coverage.
- IRS fields populate in 42,575 rows (2.25% of the table), matching the county/CBSA/state coverage of `silver.irs_migration_summary`.
- IRS rate fields use `pop_nativity_total` as the denominator so they remain comparable on the same population base as the rest of the migration mart.
- IRS AGI fields retain nulls where the underlying Silver summary still carries suppressed or missing income values.

## Lineage
1. **Primary build script**: [scripts/etl/gold/gold_migration_wide.sql]
2. **Primary upstreams**:
   - `silver.migration_kpi`
   - `silver.irs_migration_summary`

## Known Gaps / To-Dos
- IRS enrichment still applies only to county, CBSA, and state rows; broader ACS geographies remain null for those fields by design.
- If the semantic layer needs IRS AGI metrics exposed as first-class queryable metrics, add them to the semantic catalogs in a follow-up pass.
