# Data Dictionary: silver.cbp_zip

## Overview
- **Table**: `silver.cbp_zip`
- **Purpose**: Curated latest-year CBP ZIP industry-detail table for ZIP-native business-presence analysis.
- **Row count**: `294,824`
- **Time coverage**: `2023` only

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + period + industry_code`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `period`, `industry_code`)
- **Observed geo coverage**:
  - `zip`: `294,824` rows across `34,954` ZIP codes
- **Industry coverage**: `20` curated CBP industry codes spanning the all-sectors row plus broad sector rows
- **Key QA**: live duplicate check on `geo_level + geo_id + period + industry_code` returned zero duplicates.

## Curated Subset Rule

This table is intentionally narrower than the staged ZIP detail file.

- Keep the all-sectors row: `industry_code = '------'`
- Keep the published broad sector rows only:
  - `11----`, `21----`, `22----`, `23----`, `31----`, `42----`, `44----`, `48----`
  - `51----`, `52----`, `53----`, `54----`, `55----`, `56----`
  - `61----`, `62----`, `71----`, `72----`, `81----`
- Drop the deeper NAICS rows from the staged ZIP detail file
- Keep ZIP geography native in Silver rather than forcing a ZIP-to-ZCTA reconciliation in this first pass

Why this rule exists:
- the staged ZIP detail file is large and too wide for the first analytical contract
- the broad-sector subset keeps ZIP detail aligned with the county CBP table and the rest of the economics layer
- the ZIP source only carries establishments and size buckets, so this table stays focused on business presence rather than payroll or employment

## Column Groups
- **Keys**: `geo_level`, `geo_id`, `geo_name`, `period`, `industry_code`, `industry_title`
- **ZIP helpers**: `zip_code`, `zip_name`, `city`, `state_abbr`, `county_name`
- **Industry grouping helpers**: `silver_rollup_family`, `is_total_row`
- **Business-presence metrics**: `establishments`
- **Establishment size buckets**: `est_n_lt_5`, `est_n_5_9`, `est_n_10_19`, `est_n_20_49`, `est_n_50_99`, `est_n_100_249`, `est_n_250_499`, `est_n_500_999`, `est_n_1000_plus`
- **Metadata**: `source`

## Data Quality Notes
- ZIP rows come directly from the staged ZIP detail file after the curated industry filter is applied.
- The ZIP source does not provide employment or payroll, so this Silver contract is establishment-only by design.
- ZIP geography remains ZIP-native in this first pass.
  - No ZIP-to-ZCTA reconciliation is attempted yet.
- Live profile after materialization:
  - `20` curated industry codes
  - `34,954` ZIP codes
  - `34,954` all-sector rows
  - null `geo_name`: `0`

## Lineage
1. `foundations/etl/staging/get_cbp_zip.R` lands the latest-year ZIP industry-detail file in `staging.cbp_zip_detail`.
2. `foundations/etl/silver/cbp_zip_silver.R` filters that staged ZIP detail to the approved broad-sector analytical subset, keeps ZIP geography native, and writes `silver.cbp_zip`.

## Known Gaps / To-Dos
- This table is latest-year-only in the current contract.
- If we later need ZIP-to-ZCTA reconciliation, that should be a separate geography decision rather than silently changing this first ZIP analytical surface.
- There is no Gold consumer yet for ZIP detail; the current role is to make the ZIP establishment structure available as a managed Silver table.
