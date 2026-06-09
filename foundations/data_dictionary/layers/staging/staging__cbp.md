# Data Dictionary: staging CBP County

## Overview
- Schema: `staging`
- Family: `County Business Patterns`
- Contract scope: source-family staging contract for the county historical table produced by [`foundations/etl/staging/get_cbp.R`](../../../etl/staging/get_cbp.R)
- Documentation rule: the current first-pass ingest lands one source-faithful county table for the approved `2010-2023` history; ZIP detail will remain a separate future staging surface rather than widening this county contract

## Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County annual history | `cbp_county` | One row per county-year-NAICS observation from the annual CBP county files, with the published employment, payroll, and establishment-size payload preserved |

## Contract Summary
- All staged CBP rows currently live in one table.
- Grain: one row per `county_fips + year + naics_code`
- Geography scope: county and county-equivalent rows published in the CBP county files
- Current landed shape: `22,577,676` rows, `26` columns
- Current time coverage: `2010` through `2023`
- Current first-pass history decision: keep the county historical series source-faithful in staging and derive `cbsa` and `state` downstream in Silver

## Shared Columns
- Time:
  - `year`
- Geography:
  - `state_fips`
  - `county_fips`
  - `county_fips_3`
- Industry key:
  - `naics_code`
- Source disclosure / noise flags:
  - `emp_noise_flag`
  - `qp1_noise_flag`
  - `ap_noise_flag`
- Core business metrics:
  - `employment_march12`
  - `first_quarter_payroll_k`
  - `annual_payroll_k`
  - `establishments`
- Establishment size buckets:
  - `est_n_lt_5`
  - `est_n_5_9`
  - `est_n_10_19`
  - `est_n_20_49`
  - `est_n_50_99`
  - `est_n_100_249`
  - `est_n_250_499`
  - `est_n_500_999`
  - `est_n_1000_plus`
  - `est_n_1000_1499`
  - `est_n_1500_2499`
  - `est_n_2500_4999`
  - `est_n_5000_plus`
- Metadata:
  - `source_file`

## Lineage
- [`foundations/etl/staging/get_cbp.R`](../../../etl/staging/get_cbp.R) downloads the annual county ZIP artifacts for `2010-2023`, reads the quoted comma-delimited `cbpYYco.txt` members, normalizes the historical header quirks, validates the county-year-NAICS key, and writes `staging.cbp_county`.
- The provider-level ZIP boundary, history decision, and CBP-vs-ZIP notes live in [`../../sources/source__cbp.md`](../../sources/source__cbp.md).

## Data Quality Notes
- Live staged key check passed at `county_fips + year + naics_code`.
- County and state FIPS are zero-padded text in staging so downstream joins do not depend on type coercion.
- Historical header quirks are normalized during ingest:
  - `2010` uses `n1_4` instead of `n<5`
  - `2015` has uppercase headers
  - legacy `empflag` is mapped into `emp_noise_flag` when present
- Staging intentionally keeps the full county NAICS universe (`2,249` distinct codes in the current landed history) rather than pruning to the smaller analytical subset used in Silver.
- The large step change beginning in `2017` reflects source-year shape changes in the published county files, not a staging bug.

## Current Landed History
- `2010`: `2,155,389` rows
- `2011`: `2,151,507` rows
- `2012`: `2,131,529` rows
- `2013`: `2,126,883` rows
- `2014`: `2,125,361` rows
- `2015`: `2,126,601` rows
- `2016`: `2,124,893` rows
- `2017`: `1,089,498` rows
- `2018`: `1,086,180` rows
- `2019`: `1,085,472` rows
- `2020`: `1,082,434` rows
- `2021`: `1,090,164` rows
- `2022`: `1,100,804` rows
- `2023`: `1,100,961` rows

## Known Gaps / To-Dos
- ZIP detail is intentionally not part of this table. When it is added, it should land as a separate latest-year staging surface rather than being mixed into the county history table.
- State, MSA, and CSA CBP files remain useful QA references but are not part of the current managed staging contract.
