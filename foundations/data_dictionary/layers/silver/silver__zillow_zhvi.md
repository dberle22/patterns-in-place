# Data Dictionary: silver.zillow_zhvi

## Overview
- **Table**: `silver.zillow_zhvi`
- **Purpose**: Standardized monthly Zillow Home Value Index table for county, ZCTA, and derived CBSA geographies.
- **Row count**: 3,404,602
- **Time coverage**: 2016-01-31 to 2025-10-31

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + period`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`)
- **Observed geo coverage**: `county`, `zcta`, and `cbsa`
- **Key QA**: live duplicate check on `geo_level + geo_id + period` returned zero duplicates.

## Columns

| Column | Type | Null % | Definition |
|---|---|---:|---|
| `geo_level` | `VARCHAR` | 0.0000 | Geographic level for the Zillow observation row (`county`, `zcta`, or `cbsa`). |
| `geo_id` | `VARCHAR` | 0.0000 | Geographic identifier for the observation row. County rows use 5-digit county FIPS, ZCTA rows use 5-digit ZIP Code tabulation area identifiers, and CBSA rows use 5-digit CBSA codes. |
| `geo_name` | `VARCHAR` | 0.0000 | Geographic display name for the observation row. |
| `period` | `DATE` | 0.0000 | Month-end observation date for the Zillow series. |
| `year` | `INTEGER` | 0.0000 | Calendar year extracted from `period`. |
| `month` | `INTEGER` | 0.0000 | Calendar month number extracted from `period`. |
| `zhvi` | `DOUBLE` | 0.0000 | Zillow Home Value Index monthly level for the geography and month. |

## Data Quality Notes
- `cbsa` rows are derived from county Zillow observations rather than source-native CBSA files, using housing-unit-weighted averages from `silver.housing_base`.
- For Zillow months after the ACS coverage window, the CBSA rebasing uses the latest available county housing weights from 2024.
- Silver now keeps only the last 10 calendar years and drops null-value rows, so this table is a sparse analytical series rather than a dense geography-month panel.
- City and state Zillow staging tables are intentionally excluded from this Silver contract for now because the approved Track 1.4 scope is the cleaner county/ZCTA/CBSA surface.

## Lineage
1. `foundations/etl/staging/get_zillow.R` downloads Zillow county and ZIP ZHVI files and pivots them into monthly staging tables.
2. `foundations/etl/silver/zillow_silver.R` standardizes county and ZCTA rows, rebases county rows to CBSA using `silver.xwalk_cbsa_county` and county `hu_totalE` weights from `silver.housing_base`, filters to 2016+ non-null observations, and writes `silver.zillow_zhvi`.

## Known Gaps / To-Dos
- This table intentionally excludes city and state rows pending a separate post-Gold review of whether those staging slices can support a clean Silver extension.
- The Zillow source remains monthly but Silver no longer preserves missing months, so downstream annual Gold logic should not assume a full 12-month panel for every geography-year.

## How To Extend (Next Table)
1. Confirm live row count, time coverage, and key uniqueness in DuckDB.
2. Re-check the CBSA weighting assumptions if ACS housing coverage changes beyond 2024.
3. Update the `.yml` contract first, then sync the `.md` companion.
