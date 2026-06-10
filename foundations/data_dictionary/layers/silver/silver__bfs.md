# Data Dictionary: silver.bfs

## Overview
- **Table**: `silver.bfs`
- **Purpose**: Annual BFS business-applications table at county grain with derived CBSA and state rollups, plus a CBP-based business-application intensity rate where the denominator exists.
- **Row count**: `82,640`
- **Time coverage**: `2005` to `2024`

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + period + series_code`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `series_code`)
- **Observed geo coverage**:
  - `county`: `63,120` rows across `3,156` county or county-equivalent GEOIDs
  - `cbsa`: `18,500` rows across `925` CBSA GEOIDs
  - `state`: `1,020` rows across `51` state GEOIDs
- **Series coverage**: `BA` only in the current first-pass BFS contract
- **Key QA**: live duplicate check on `geo_level + geo_id + period + series_code` returned zero duplicates.

## Current Contract Rule

This table is intentionally annual-only in the first pass.

- Keep the annual county `BA` rows from `staging.bfs_county`
- Derive `cbsa` rows by summing county rows through `silver.xwalk_cbsa_county`
- Derive `state` rows by summing county rows through `silver.xwalk_county_state`
- Join `silver.cbp` all-sector establishments as the denominator where the annual year overlap exists
- Do not include monthly BFS in this table yet

Why this rule exists:
- the verified county workbook only carries annual Business Applications
- the immediate product need is annual entrepreneurial activity rather than monthly BFS trend analysis
- keeping the first BFS Silver contract annual-only makes the CBP denominator join straightforward and avoids implying county monthly coverage that the current source does not support

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `period_type`, `period`, `year`, `series_code`, `series_label`
- **Geography helpers**: `state_fips`, `state_abbr`
- **Primary BFS values**: `value`, `business_applications`
- **Derived annual trend**: `business_applications_yoy_pct`
- **CBP denominator fields**: `cbp_total_estabs`, `business_application_rate_per_1000_establishments`
- **Metadata**: `source`

## Data Quality Notes
- County rows come directly from the staged annual county workbook.
- CBSA and state rows are derived from county rows after the annual county surface is standardized.
- `value` and `business_applications` are identical in the current annual-only `BA` contract.
- `business_applications_yoy_pct` is computed within each `geo_level + geo_id + series_code` history.
- `business_application_rate_per_1000_establishments` is only populated where the CBP denominator exists.
  - live rate coverage: `57,538` rows
  - current denominator-supported years: `2010-2023`
  - `2005-2009` and `2024` correctly remain null for the rate because annual CBP is not available for those years in the current managed join window
- Live profile after materialization:
  - null `geo_name`: `0`
  - `series_code` values: `BA` only

## Lineage
1. `foundations/etl/staging/get_bfs.R` lands the annual county BFS workbook as `staging.bfs_county`.
2. `foundations/etl/silver/bfs_silver.R` standardizes county rows, derives CBSA and state rollups, joins the CBP all-sector establishment denominator where available, and writes `silver.bfs`.

## Known Gaps / To-Dos
- This table does not yet include any monthly BFS series.
- If we later add monthly BFS, we should extend this contract carefully rather than implying county monthly coverage from the annual county workbook.
- The CBP-based denominator join should be revisited when the next CBP annual release is added so the BFS `2024` rate can fill in.
