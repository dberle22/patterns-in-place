# Data Dictionary: silver.bls_qcew_industry_map

## Overview
- **Table**: `silver.bls_qcew_industry_map`
- **Purpose**: Managed Silver reference table for QCEW industry-code interpretation, year presence, and curated-subset flags.
- **Row count**: `2,660`
- **KPI applicability**: Not a KPI table.

## Grain & Keys
- **Declared grain**: One row per `industry_code`
- **Primary key candidate**: (`industry_code`)
- **Time coverage**: Non-time-series reference table; includes `first_seen_year`, `last_seen_year`, and `years_present`

## Columns

| Column | DuckDB type | Definition |
|---|---|---|
| `industry_code` | `VARCHAR` | Raw QCEW industry code published by BLS. |
| `industry_title` | `VARCHAR` | Human-readable title for the QCEW industry code. |
| `first_seen_year` | `INTEGER` | First annual archive year in which the code appeared in the mapping build. |
| `last_seen_year` | `INTEGER` | Most recent annual archive year in which the code appeared in the mapping build. |
| `years_present` | `VARCHAR` | Pipe-delimited list of annual archive years in which the code appeared. |
| `member_count` | `INTEGER` | Number of annual archive members contributing to the code's presence record. |
| `code_length` | `INTEGER` | Character length of the published code after preserving hyphens. |
| `code_type` | `VARCHAR` | Code classification such as `total`, `naics_sector`, `naics_compound_sector`, or `supersector_aggregate`. |
| `is_aggregate` | `BOOLEAN` | Whether the published code is an aggregate rather than a leaf NAICS-style code. |
| `aggregate_components` | `VARCHAR` | Delimited component-code list for aggregate rows when known. |
| `keep_in_staging` | `BOOLEAN` | Whether the code should be retained in source-faithful staging coverage. |
| `keep_in_silver_canonical` | `BOOLEAN` | Whether the code belongs to the canonical curated industry family used by `silver.bls_qcew`. |
| `silver_rollup_family` | `VARCHAR` | Optional grouped family label for downstream Silver analytical rollups. |
| `notes` | `VARCHAR` | Free-text note or caveat about the code. |

## Data Quality Notes
- This table is the governed DuckDB version of the authored CSV seed at `foundations/etl/reference/bls_qcew_industry_map.csv`.
- `keep_in_silver_canonical` identifies the curated industry family, but the final `silver.bls_qcew` table applies one more ownership rule on top of it:
  - `10` keeps the total-covered slice
  - non-total industries keep the private-sector slice
- Because of that ownership rule, some canonical codes such as `92 Public administration` can exist in this map while not appearing in `silver.bls_qcew`.
- Live profile after materialization:
  - distinct `industry_code`: `2,660`
  - `first_seen_year` min: `2010`
  - `last_seen_year` max: `2024`

## Lineage
1. `foundations/etl/reference/build_bls_qcew_industry_map.R` builds the CSV seed across the annual archives.
2. `foundations/etl/silver/bls_qcew_silver.R` materializes the managed Silver table from that seed.

## Known Gaps / To-Dos
- If the map stabilizes further, consider moving the seed maintenance into a more explicit reference-build step in the ETL pipeline.
