# Data Dictionary: staging IRS EO Business Master File

## Overview
- Schema: `staging`
- Family: `IRS EO Business Master File`
- Contract scope: source-family staging contract for the latest-snapshot national EO BMF table produced by [`foundations/etl/staging/get_irs_bmf.R`](../../../etl/staging/get_irs_bmf.R)
- Documentation rule: the first pass keeps one source-faithful national table because the regional IRS files share one schema and the downstream complexity lives in ZIP-to-county allocation rather than raw file shape

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Latest active U.S. EO BMF snapshot | `irs_bmf` | One row per active EIN in the combined regional IRS files after filtering to the supported U.S. state + DC scope |

## Contract Summary
- All staged EO BMF rows live in one table.
- Grain: one row per `ein`
- Geography scope: filing-address state / ZIP for the 50 states plus DC
- Current landed snapshot: `2026-05-12`
- Current landed shape: `1,969,837` rows, `34` columns
- Current distinct ZIP coverage: `36,760` ZIP5 values

## Shared Columns
- Identity and address:
  - `ein`
  - `name`
  - `ico`
  - `street`
  - `city`
  - `state`
  - `zip_raw`
  - `zip5`
- IRS organization coding:
  - `group_exemption_number`
  - `subsection_code`
  - `affiliation_code`
  - `classification_codes`
  - `deductibility_code`
  - `foundation_code`
  - `activity_codes`
  - `organization_code`
  - `status_code`
  - `filing_requirement_code`
  - `pf_filing_requirement_code`
  - `ntee_cd`
- Time and filing helpers:
  - `ruling_yyyymm`
  - `ruling_year`
  - `tax_period_yyyymm`
  - `accounting_period_mm`
- Financial fields:
  - `asset_code`
  - `income_code`
  - `asset_amt`
  - `income_amt`
  - `revenue_amt`
- Snapshot metadata:
  - `source_region`
  - `source_file`
  - `snapshot_date`
  - `snapshot_record_count`

## Lineage
- [`foundations/etl/staging/get_irs_bmf.R`](../../../etl/staging/get_irs_bmf.R) reads the IRS EO BMF landing page, extracts the four regional file URLs plus the published posting date, downloads the CSVs, filters to active U.S. state + DC rows, derives `zip5`, validates uniqueness at `ein`, and writes `staging.irs_bmf`.
- Provider-level modeling decisions and ZIP-allocation notes live in [`../../sources/source__irs_bmf.md`](../../sources/source__irs_bmf.md).

## Data Quality Notes
- The landed staging table is intentionally latest-snapshot only rather than a monthly panel.
- `zip_raw` is preserved exactly as published, while `zip5` is derived from the first five digits for downstream geographic allocation.
- The current landed snapshot has:
  - `579,931` rows with blank `ntee_cd`
  - `295,024` rows flagged by the church / religious filing-requirement codes `06` or `13`
- Staging already applies the active-status keep set (`01`, `02`, `12`, `25`) because Track 21.2 is scoped to active exempt organizations only.
- The regional raw surface still requires a U.S.-only state filter because `eo4.csv` can carry non-state rows in the broader IRS packaging.

## Known Gaps / To-Dos
- Filing-address geography is not the same as operating geography.
- The first pass excludes Puerto Rico and international organizations to stay aligned with the current Foundations backbone.
- The current staging contract does not preserve a historical archive of monthly snapshots.
