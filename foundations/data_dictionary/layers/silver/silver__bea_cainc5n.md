# Data Dictionary: silver.bea_cainc5n

## Overview
- **Table**: `silver.bea_cainc5n`
- **Purpose**: Curated annual BEA CAINC5N industry table that keeps the source honest: broad industry rows carry published `earnings_total`, while the `all_industries` row carries the published compensation components and derived `compensation_total`.
- **Row count**: `1,416,915`
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + period + industry_key`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `period`, `industry_key`)
- **Time coverage**: `period` min=`2001`, max=`2023`
- **Geo coverage**: `county`, `cbsa`, `state`, `us`
- **Industry coverage**: `15` curated industry buckets per geography-year

## Contract Rule

This Silver contract intentionally does **not** pretend that CAINC5N publishes industry-detail compensation.

- Broad industry rows keep only `earnings_total`
- The `all_industries` row carries `wages_salaries`, `supplements`, `pension_insurance_supplements`, `govt_social_insurance_supplements`, and `proprietors_income`
- `compensation_total` is derived only on the `all_industries` row as `wages_salaries + supplements`
- CBSA rows are additive rollups from counties because all retained metrics are dollar totals rather than rates

Why this rule exists:
- The live CAINC5N payload publishes industry detail as earnings lines
- The same payload publishes wages and supplements as all-industries component lines rather than parallel industry rows
- Allocating wages or supplements across industries would create a modeled artifact instead of a source-faithful Silver contract

## Columns

| Column | DuckDB type | Definition |
|---|---|---|
| `geo_level` | `VARCHAR` | Geographic level for the row (`county`, `cbsa`, `state`, or `us`). |
| `geo_id` | `VARCHAR` | Geographic identifier for the row. County rows use 5-digit county FIPS, CBSA rows use CBSA codes, state rows use 2-digit state FIPS, and the U.S. row uses `1`. |
| `geo_name` | `VARCHAR` | Geographic display name for the row. |
| `period` | `INTEGER` | Calendar year for the annual CAINC5N observation. |
| `table` | `VARCHAR` | Source BEA table code. This contract currently materializes only `CAINC5N`. |
| `industry_key` | `VARCHAR` | Stable curated industry bucket identifier such as `all_industries`, `private_nonfarm`, `manufacturing`, or `public_admin`. |
| `industry_label` | `VARCHAR` | Human-readable label for the curated industry bucket. |
| `industry_rollup_family` | `VARCHAR` | Broad cross-source industry family used for downstream alignment in Gold. |
| `industry_rollup_level` | `VARCHAR` | Contract level for the row, currently `total`, `published_total`, or `broad_family`. |
| `naics_raw` | `VARCHAR` | Source-adjacent NAICS code or code range associated with the curated industry bucket when one exists. |
| `source_line_codes` | `VARCHAR` | Comma-delimited BEA CAINC5N line codes used to build the curated row. |
| `earnings_total` | `DOUBLE` | Earnings total for the curated bucket. Broad industry rows use published earnings lines; the `all_industries` row uses BEA line `35` earnings by place of work. |
| `compensation_total` | `DOUBLE` | Derived all-industries compensation total equal to `wages_salaries + supplements`. Populated only on the `all_industries` row because CAINC5N does not publish parallel industry-detail compensation rows. |
| `wages_salaries` | `DOUBLE` | All-industries wages and salaries from BEA line `50`. Null on the broad industry rows. |
| `supplements` | `DOUBLE` | All-industries supplements to wages and salaries from BEA line `60`. Null on the broad industry rows. |
| `pension_insurance_supplements` | `DOUBLE` | All-industries employer contributions for employee pension and insurance funds from BEA line `61`. |
| `govt_social_insurance_supplements` | `DOUBLE` | All-industries employer contributions for government social insurance from BEA line `62`. |
| `proprietors_income` | `DOUBLE` | All-industries proprietors' income from BEA line `70`. |
| `has_source_suppression` | `BOOLEAN` | Whether any contributing staged source line for the row was suppressed by BEA. |
| `earnings_total_note_ref` | `VARCHAR` | Source note reference attached to the retained earnings line(s), when present. |
| `wages_salaries_note_ref` | `VARCHAR` | Source note reference attached to the wages-and-salaries line, when present. |
| `supplements_note_ref` | `VARCHAR` | Source note reference attached to the supplements line, when present. |
| `pension_insurance_supplements_note_ref` | `VARCHAR` | Source note reference attached to the pension-and-insurance supplements line, when present. |
| `govt_social_insurance_supplements_note_ref` | `VARCHAR` | Source note reference attached to the government social insurance supplements line, when present. |
| `proprietors_income_note_ref` | `VARCHAR` | Source note reference attached to the proprietors' income line, when present. |

## Data Quality Notes
- Live materialization is unique at `geo_level + geo_id + period + industry_key`.
- Every geography-year has `15` curated industry buckets.
- `county` and `cbsa` rows are additive rollups from county-stage dollar totals.
- `public_admin` is the cross-source broad-family alignment bucket, but the retained source row is BEA `line 2000` government and government enterprises earnings rather than a strict NAICS `92` employment concept.
- Live profile after materialization:
  - `county` rows: `1,078,815`
  - `cbsa` rows: `317,400`
  - `state` rows: `20,355`
  - `us` rows: `345`
  - rows per `industry_key`: `94,461`

## Lineage
1. `foundations/etl/staging/get_bea_cainc5n.R` lands the dedicated CAINC5N staging fact table and line-code reference table.
2. `foundations/etl/silver/bea_cainc5n_silver.R` collapses published CAINC5N lines into the curated broad-industry Silver contract and derives CBSA rows from counties.

## Known Gaps / To-Dos
- Gold integration is still pending. The next step is to decide how the all-industries compensation columns and broad-family earnings rows should land in `gold.economics_industry_wide`.
- The staging family contract still needs to be written separately.
