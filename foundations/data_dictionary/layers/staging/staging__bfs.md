# Data Dictionary: staging BFS County

## Overview
- Schema: `staging`
- Family: `Business Formation Statistics`
- Contract scope: source-family staging contract for the annual county workbook produced by [`foundations/etl/staging/get_bfs.R`](../../../etl/staging/get_bfs.R)
- Documentation rule: the current first-pass ingest lands only the annual county business-applications workbook; richer monthly BFS series remain a future sibling staging surface rather than part of this contract

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Annual county business applications | `bfs_county` | One row per county-year Business Applications (`BA`) observation from the Census annual county workbook |

## Contract Summary
- All staged BFS rows currently live in one table.
- Grain: one row per `county_fips + year + series_code`
- Geography scope: county and county-equivalent rows published in the annual county BFS workbook
- Current landed shape: `63,120` rows, `9` columns
- Current time coverage: `2005` through `2024`
- Current first-pass scope decision: annual county `BA` only; monthly BFS is documented for later but intentionally not staged in this pass

## Shared Columns
- Time:
  - `year`
- Geography:
  - `state_abbr`
  - `county_name`
  - `county_fips`
  - `state_fips`
  - `county_fips_3`
- Series and metric:
  - `business_applications`
  - `series_code`
- Metadata:
  - `source_file`

## Lineage
- [`foundations/etl/staging/get_bfs.R`](../../../etl/staging/get_bfs.R) downloads the annual county BFS workbook, reads the `County Data` sheet, skips the title rows, pivots `BA2005` through `BA2024` into a long county-year table, validates the county-year-series key, and writes `staging.bfs_county`.
- The provider-level annual-vs-monthly BFS decision lives in [`../../sources/source__bfs.md`](../../sources/source__bfs.md).

## Data Quality Notes
- Live staged key check passed at `county_fips + year + series_code`.
- County and state FIPS are zero-padded text in staging so downstream joins do not depend on numeric coercion.
- The workbook is wide by year, so staging intentionally pivots to long immediately rather than preserving one column per year.
- The current landed table has `3,156` counties or county-equivalents for every year `2005-2024`.
- `series_code` is fixed to `BA` because the verified county annual workbook contains only Business Applications.

## Current Landed History
- `2005`: `3,156` rows
- `2006`: `3,156` rows
- `2007`: `3,156` rows
- `2008`: `3,156` rows
- `2009`: `3,156` rows
- `2010`: `3,156` rows
- `2011`: `3,156` rows
- `2012`: `3,156` rows
- `2013`: `3,156` rows
- `2014`: `3,156` rows
- `2015`: `3,156` rows
- `2016`: `3,156` rows
- `2017`: `3,156` rows
- `2018`: `3,156` rows
- `2019`: `3,156` rows
- `2020`: `3,156` rows
- `2021`: `3,156` rows
- `2022`: `3,156` rows
- `2023`: `3,156` rows
- `2024`: `3,156` rows

## Known Gaps / To-Dos
- This contract does not yet include a `staging.bfs_monthly` sibling table.
- The annual county workbook carries only `BA`, so any future `HBA`, `WBA`, `CBA`, or `BF*` BFS coverage must come from separate monthly BFS files.
