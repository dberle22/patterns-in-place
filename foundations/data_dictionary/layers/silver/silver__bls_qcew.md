# Data Dictionary: silver.bls_qcew

## Overview
- **Table**: `silver.bls_qcew`
- **Purpose**: Curated annual QCEW analytical table for total-covered headline employment plus private-sector industry employment, establishments, and wages, with Public Administration added back as an explicit government-sector exception.
- **Row count**: `1,412,242`
- **KPI applicability**: Not explicitly a KPI table.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + period + own_code + industry_code`.
- **Primary key candidate**: (`geo_level`, `geo_id`, `period`, `own_code`, `industry_code`)
- **Time coverage**: `period` min=`2010`, max=`2024`
- **Geo coverage**: `county`, `cbsa`, and `state`
- **Ownership coverage**: `own_code = 0` for the total-covered headline row, `own_code = 5` for most private-sector industry rows, and `own_code in (1, 2, 3)` for the Public Administration exception
- **Industry coverage**: `21` curated industry codes across the full annual range

## Curated Subset Rule

This table is intentionally narrower than staging.

- Keep `industry_code = 10` only from the county `Total Covered` slice: `own_code = 0`, `agglvl_code = 70`
- Keep canonical industry rows from the county private-sector slice only: `own_code = 5`, `agglvl_code = 74`
- Add `industry_code = 92` from the county government sector slices: `own_code in (1, 2, 3)`, `agglvl_code = 74`
- Roll those county rows to `cbsa` and `state` after filtering

Why this rule exists:
- QCEW does not provide one clean all-ownership slice for every canonical sector.
- Using the private sector for most industry detail avoids mixing incompatible ownership concepts inside one analytical Silver table.
- `92 Public administration` is intentionally added back from the government ownership slices because it is analytically important and otherwise absent from the curated contract.

## Columns

| Column | DuckDB type | Definition |
|---|---|---|
| `geo_level` | `VARCHAR` | Geographic level for the row (`county`, `cbsa`, or `state`). |
| `geo_id` | `VARCHAR` | Geographic identifier for the row. County rows use 5-digit county FIPS, CBSA rows use CBSA codes, and state rows use 2-digit state FIPS. |
| `geo_name` | `VARCHAR` | Geographic name for the row. County rows use county names, CBSA rows use CBSA names, and state rows use USPS abbreviations. |
| `period` | `INTEGER` | Calendar year for the QCEW annual-average observation. |
| `own_code` | `VARCHAR` | Ownership code retained in the curated subset. `0` identifies the total-covered headline row, `5` identifies most private-sector industry rows, and `1`/`2`/`3` identify the Public Administration exception rows. |
| `own_title` | `VARCHAR` | Human-readable ownership title for the row. |
| `industry_code` | `VARCHAR` | Curated QCEW industry code for the row. |
| `industry_title` | `VARCHAR` | Human-readable QCEW industry title for the row's industry code. |
| `code_type` | `VARCHAR` | Industry-code classification from `silver.bls_qcew_industry_map` such as `total`, `naics_sector`, or `naics_compound_sector`. |
| `is_aggregate` | `BOOLEAN` | Whether the industry code is an aggregate rather than a leaf NAICS-style code. |
| `aggregate_components` | `VARCHAR` | Delimited component-code list for aggregate rows when known. |
| `silver_rollup_family` | `VARCHAR` | Optional grouped family label carried from the QCEW industry map. |
| `annual_avg_estabs` | `DOUBLE` | Annual average number of establishments for the geography-year-ownership-industry row. |
| `annual_avg_emplvl` | `DOUBLE` | Annual average employment level for the geography-year-ownership-industry row. |
| `total_annual_wages` | `DOUBLE` | Total annual wages for the geography-year-ownership-industry row. |
| `taxable_annual_wages` | `DOUBLE` | Total taxable annual wages for the geography-year-ownership-industry row. |
| `annual_contributions` | `DOUBLE` | Annual unemployment-insurance contributions for the geography-year-ownership-industry row. |
| `annual_avg_wkly_wage` | `DOUBLE` | Average weekly wage for the row. CBSA and state rows are recomputed from summed wages and summed employment rather than averaged from county wage rates. |
| `avg_annual_pay` | `DOUBLE` | Average annual pay for the row. CBSA and state rows are recomputed from summed wages and summed employment. |
| `disclosure_code` | `VARCHAR` | QCEW disclosure flag for the row. Derived CBSA and state rows carry `N` when any contributing county record is suppressed. |
| `source` | `VARCHAR` | Source system or provider for the row (`BLS QCEW`). |

## Data Quality Notes
- County rows should remain unique at `geo_id + period + own_code + industry_code`.
- CBSA and state rows are derived from county rows after the curated subset filter is applied.
- Derived wage rates are intentionally recomputed from summed wage and employment levels so rolled-up rows behave like true aggregate observations.
- `silver.bls_qcew` is intentionally not a full ownership cube; use staging for the broader ownership universe.
- Public Administration is the only government-sector exception in this curated table.
- Live profile after materialization:
  - `county` rows: `1,075,770`
  - `cbsa` rows: `318,224`
  - `state` rows: `18,248`
  - null `geo_name`: `0`

## Lineage
1. `foundations/etl/staging/get_bls_qcew.R` lands the source-faithful county and state staging tables.
2. `foundations/etl/silver/bls_qcew_silver.R` materializes `silver.bls_qcew_industry_map`.
3. The same Silver script filters county staging to the curated subset and rolls it to CBSA and state.

## Companion Table
- `silver.bls_qcew_industry_map` is the managed metadata table for QCEW industry-code interpretation and curated-subset flags.

## Known Gaps / To-Dos
- If we later need a broader ownership-aware analytical view, create a separate Silver table rather than widening this curated contract.
