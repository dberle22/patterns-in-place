# Data Dictionary: silver.lehd_qwi

## Overview
- **Table**: `silver.lehd_qwi`
- **Purpose**: Silver-layer labor-dynamics table that standardizes staged LEHD QWI county rows, rolls them to canonical higher geographies, and preserves the detailed worker-composition surface needed for downstream labor analysis.
- **Status**: materialized from the current annual county-first staging implementation.
- **Row count**: `11,387,040`

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year + demo_family + demo_code + industry_code`
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`, `demo_family`, `demo_code`, `industry_code`)
- **Current geography coverage**: `county`, `cbsa`, `state`, `division`, and `us`
- **Current time coverage**: `year` min=`2007`, max=`2025`

## Contract Summary
- Input: `staging.lehd_qwi`
- Base geography: county
- Rollup pattern:
  - county retained directly
  - counties rolled to `cbsa` using `silver.xwalk_cbsa_county`
  - counties rolled to `state` using `silver.xwalk_county_state`
  - states rolled to `division` using `silver.xwalk_state_region`
  - counties rolled to `us` by national aggregation
- Demographic surface:
  - one `age` family keyed by LEHD `agegrp`
  - one `education` family keyed by LEHD `education`
- Industry surface: retained at the scoped QWI sector level and mapped to the repo's canonical broad industry families for downstream joins

## Recommended Dimensions
- Geography: `geo_level`, `geo_id`, `geo_name`
- Time: `year`
- Demographic identifiers: `demo_family`, `demo_code`, `demo_label`
- Industry identifiers: `industry_code`, `industry_label`, `industry_rollup_family`
- Provenance and QA: `ownercode`, `periodicity`, `source_periodicity`, `quarters_observed`, `release_id`, `schema_version`

## Recommended Canonical Measures
- `employment`
- `avg_earnings`
- `new_hire_avg_earnings`
- `separation_avg_earnings`
- `hires`
- `separations`
- `replacements`
- `payroll`

## Source Mappings
- `employment` <- `annual_avg_emp`
- `avg_earnings` <- `annual_avg_earns`
- `new_hire_avg_earnings` <- `annual_avg_earnhiras`
- `separation_avg_earnings` <- `annual_avg_earnseps`
- `hires` <- `annual_hira`
- `separations` <- `annual_sep`
- `replacements` <- `annual_hiraendrepl`
- `payroll` <- `annual_payroll`

## Recommended Derived Measures
- `hire_rate` = `hires / employment`
- `separation_rate` = `separations / employment`
- `replacement_rate` = `replacements / employment`
- `payroll_per_employee` = `payroll / employment`

## Standardization Rules
- Demographic mapping:
  - for `demo_family = 'age'`, set `demo_code = agegrp`
  - for `demo_family = 'education'`, set `demo_code = education`
  - enrich `demo_label` from LEHD label references so Gold and semantic outputs do not need to interpret raw LEHD codes
- Industry mapping:
  - preserve the published `industry_code`
  - add `industry_label`
  - map sector codes into the repo's broad rollup families so QWI can align with ACS, QCEW, CBP, and BEA industry stories
- Geography mapping:
  - convert staged county GEOIDs into canonical `geo_level + geo_id + geo_name`
  - ensure rolled rows do not duplicate overlapping published metro-state part geographies because Silver is county-derived rather than mixed-source geography-derived

## Rollup Rules
- Sum counts directly when rolling counties upward:
  - `employment`
  - `hires`
  - `separations`
  - `replacements`
  - `payroll`
- Recompute derived rates after rollup rather than averaging county rates:
  - `hire_rate`
  - `separation_rate`
  - `replacement_rate`
- Recompute earnings after rollup using weighted logic:
  - `avg_earnings` weighted by `employment`
  - `new_hire_avg_earnings` weighted by `hires`
  - `separation_avg_earnings` weighted by `separations`

## Gold Handoff
- Primary Gold home: `gold.economics_labor_wide`
- Intended Gold use:
  - headline private labor-dynamics metrics by geography-year
  - workforce age and education composition shares at the all-sector private total level
- Intentionally not the primary feed for `gold.economics_industry_wide`, which should stay focused on structure, establishments, GDP, and broad industry employment mix rather than labor-market churn

## Data Quality Notes
- Validate uniqueness at `geo_level + geo_id + year + demo_family + demo_code + industry_code`.
- Confirm every non-county row can be traced back to county inputs through one rollup path only.
- Check that `employment`, `hires`, `separations`, `replacements`, and `payroll` are non-negative after rollup.
- Keep `quarters_observed` in Silver so downstream users can flag annual rows built from fewer than four quarters.

## Lineage
1. [`foundations/etl/staging/get_lehd_qwi.R`](../../../etl/staging/get_lehd_qwi.R) materializes the annual county-first staging table.
2. [`foundations/etl/silver/lehd_qwi_silver.R`](../../../etl/silver/lehd_qwi_silver.R) normalizes the county rows, enriches labels and geography metadata, computes canonical measures, and rolls the county base to higher geographies.

## Known Gaps / To-Dos
- `E5` is now labeled with the official LEHD wording: `Educational attainment not available (workers aged 24 or younger)`. When the YAML companion is added, keep that wording aligned there as well.
- Decide whether any secondary employment variants such as `annual_avg_emps` or `annual_avg_emptotal` should survive as non-canonical diagnostic columns in Silver.
- Add the YAML companion once the table is materialized and profiled live.
