# Data Dictionary: staging BEA CAINC5N Family

## Overview
- Schema: `staging`
- Family: `BEA CAINC5N`
- Contract scope: dedicated CAINC5N staging family produced by [`foundations/etl/staging/get_bea_cainc5n.R`](../../../etl/staging/get_bea_cainc5n.R).
- Documentation rule: this family covers both the main staged fact table and the companion line-code reference table because the dedicated ingest path writes them together and they are used as one logical staging surface.

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| Metrics fact table | `bea_cainc5n` | Annual CAINC5N rows at source geography-year-line-code grain; live coverage includes `county`, `state`, and `us` rows from the BEA Regional API |
| Line-code reference | `bea_cainc5n_line_codes` | One-row-per-line-code lookup table used to preserve raw labels, cleaned labels, raw NAICS snippets, and aggregate flags |

## Contract Summary
- The main fact table has `14` columns.
- The companion reference table has `6` columns.
- Fact-table grain: one row per `geo_level + geo_id + period + line_code`.
- Reference-table grain: one row per `line_code` in the curated CAINC5N lookup.
- Fact-table key columns: `table`, `geo_level`, `geo_id`, `period`, `line_code`.

## Main Fact Columns
- `code`
- `table`
- `geo_level`
- `geo_id`
- `geo_name`
- `period`
- `line_code`
- `unit_raw`
- `unit_mult`
- `data_value_text`
- `value_raw`
- `value`
- `note_ref`
- `is_value_suppressed`

## Reference Columns
- `table`
- `line_code`
- `line_desc`
- `line_desc_clean`
- `naics_raw`
- `is_aggregate`

## Live Profile
- `staging.bea_cainc5n` row count: `9,602,431`
- Distinct fact-table keys at `geo_level + geo_id + period + line_code`: `9,602,431`
- Time coverage: `2001-2023`
- Geography coverage in the fact table:
  - `county`: `9,421,651` rows
  - `state`: `177,767` rows
  - `us`: `3,013` rows
- `staging.bea_cainc5n_line_codes` row count: `131`
- Distinct line codes in the reference table: `131`

## Source-Specific Notes
- The dedicated ingest checkpoints one line-code pull at a time to manage BEA throttling during the live refresh.
- `data_value_text` preserves the source string, while `value` and `value_raw` carry parsed numeric forms where BEA published a numeric observation.
- `is_value_suppressed = TRUE` identifies suppressed source values such as `D`; downstream Silver logic should treat those rows as source-faithful null/suppression cases rather than coercing them into zeroes.
- The live CAINC5N payload is broader than a pure compensation table:
  - broad industry detail rows are published as earnings lines
  - wages and supplements are published as all-industries component lines
- The supplements fields are BEA accounting components, not an establishment microdata measure like QCEW payroll.
- County and state coverage use the same `131` published line codes in the current live pull, and the state pass also returns a U.S. row from the API.

## Lineage
- [`foundations/etl/staging/get_bea_cainc5n.R`](../../../etl/staging/get_bea_cainc5n.R) is the dedicated ingest script and defines both write targets in this family.

## Data Quality Notes
- Verify uniqueness at `geo_level + geo_id + period + line_code` before Silver transforms.
- Confirm that each geography slice keeps all `131` expected line codes after refresh.
- Watch for suppression behavior in `data_value_text` and `is_value_suppressed`; suppressed values are expected in some detailed rows and should remain source-faithful in staging.
- Treat `bea_cainc5n_line_codes` as a managed lookup artifact tied to the fact table refresh, not as an independent source family.

## Known Gaps / To-Dos
- If the dedicated CAINC5N path is later consolidated back into the shared BEA staging script, update this contract so the lineage path stays accurate.
