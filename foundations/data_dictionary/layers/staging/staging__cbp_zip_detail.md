# Data Dictionary: staging CBP ZIP Detail

## Overview
- Schema: `staging`
- Family: `County Business Patterns`
- Contract scope: latest-year ZIP industry-detail staging contract produced by [`foundations/etl/staging/get_cbp_zip.R`](../../../etl/staging/get_cbp_zip.R)
- Documentation rule: this table is intentionally separate from the county historical CBP contract because ZIP detail is a larger, latest-year-only expansion rather than part of the managed `2010-2023` county history

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Latest annual ZIP industry detail | `cbp_zip_detail` | One row per ZIP-year-NAICS observation from the most recent CBP ZIP industry-detail file |

## Contract Summary
- All staged ZIP-detail rows currently live in one table.
- Grain: one row per `zip_code + year + naics_code`
- Geography scope: five-digit ZIP rows from the published ZIP industry-detail file
- Current release scope: `2023` only
- Current source-file volume: `2,974,116` rows
- Current modeled purpose: preserve the ZIP-by-industry establishment surface in staging until we decide the exact `silver.cbp_zip` analytical contract

## Shared Columns
- Time:
  - `year`
- ZIP and place helpers:
  - `zip_code`
  - `zip_name`
  - `city`
  - `state_abbr`
  - `county_name`
- Industry key:
  - `naics_code`
- Establishment metrics:
  - `establishments`
  - `est_n_lt_5`
  - `est_n_5_9`
  - `est_n_10_19`
  - `est_n_20_49`
  - `est_n_50_99`
  - `est_n_100_249`
  - `est_n_250_499`
  - `est_n_500_999`
  - `est_n_1000_plus`
- Metadata:
  - `source_file`

## Lineage
- [`foundations/etl/staging/get_cbp_zip.R`](../../../etl/staging/get_cbp_zip.R) downloads the latest ZIP industry-detail ZIP artifact, reads the quoted comma-delimited `zbpYYdetail.txt` member, normalizes the field names, validates the ZIP-year-NAICS key, and writes `staging.cbp_zip_detail`.
- The provider-level ZIP boundary decision and county-vs-ZIP rationale live in [`../../sources/source__cbp.md`](../../sources/source__cbp.md).

## Data Quality Notes
- The ZIP-detail file is establishment-focused.
  - It does not carry employment or payroll the way the county file does.
- ZIP codes are zero-padded text in staging so downstream joins can treat them as identifiers rather than numbers.
- The current contract is latest-year-only by design.
- The source file volume for the current `2023` release is `2,974,116` rows; the staging script completed successfully against that artifact.

## Known Gaps / To-Dos
- `silver.cbp_zip` now provides the first analytical ZIP surface, but the ZIP geography is still ZIP-native rather than reconciled to a ZCTA-style contract.
- We still need to decide whether any future Gold output should consume ZIP detail directly or whether ZIP should remain a Silver-only business-presence surface.
