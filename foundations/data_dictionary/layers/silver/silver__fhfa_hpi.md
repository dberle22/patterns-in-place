# Data Dictionary: silver.fhfa_hpi

## Overview
- **Table**: `silver.fhfa_hpi`
- **Purpose**: Standardized annual FHFA House Price Index table for the first-pass analytical geography set: `us`, `state`, `cbsa`, `county`, and ZIP5-as-`zcta`.
- **Row count**: 819,404
- **Time coverage**: 1975 to 2025

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Observed geo coverage**: `us`, `state`, `cbsa`, `county`, and `zcta`
- **Key QA**: live duplicate check on `geo_level + geo_id + year` returned zero duplicates.

## Columns

| Column | Type | Null % | Definition |
|---|---|---:|---|
| `geo_level` | `VARCHAR` | 0.0000 | Geographic level for the FHFA observation row (`us`, `state`, `cbsa`, `county`, or ZIP5-as-`zcta`). |
| `geo_id` | `VARCHAR` | 0.0000 | Geographic identifier for the FHFA observation row. State rows use 2-digit state FIPS, county rows use 5-digit county FIPS, CBSA rows use 5-digit CBSA codes, ZCTA rows use 5-digit ZIP proxies, and the national row uses `US`. |
| `geo_name` | `VARCHAR` | 0.0000 | Geographic display name for the FHFA observation row. CBSA and county names are normalized from crosswalk-backed metadata where available. |
| `year` | `INTEGER` | 0.0000 | Calendar year of the annual FHFA house-price observation. |
| `hpi_level` | `DOUBLE` | 0.0000 | FHFA annual HPI level using the source table's canonical `hpi` series rather than the helper rebases. |
| `hpi_yoy_pct` | `DOUBLE` | 3.7905 | Exact year-over-year growth rate in `hpi_level`, computed only when a prior `year - 1` observation exists for the same geography. |
| `hpi_5yr_pct` | `DOUBLE` | 14.3050 | Five-year growth rate in `hpi_level`, computed only when a prior `year - 5` observation exists for the same geography. |
| `hpi_10yr_pct` | `DOUBLE` | 27.7644 | Ten-year growth rate in `hpi_level`, computed only when a prior `year - 10` observation exists for the same geography. |

## Data Quality Notes
- Silver uses FHFA's canonical annual `hpi` column as `hpi_level`. The `hpi_1990_base` and `hpi_2000_base` helper series remain available in staging only.
- CBSA rows are sourced from the FHFA annual CBSA workbook but filtered to true 5-digit CBSA codes. FHFA's non-CBSA residual rows are intentionally excluded from this first-pass analytical contract.
- ZIP5 rows are intentionally treated as a `zcta` proxy in Foundations. That decision is explicit in the FHFA provider spec and can be revisited later if a stricter ZIP-to-ZCTA reconciliation becomes necessary.
- Growth metrics use exact `year - 1`, `year - 5`, and `year - 10` joins rather than row-based lag logic, so sparse series do not overstate appreciation when intermediate years are missing.
- Tract HPI is already staged upstream but is intentionally excluded from Silver for now to keep the first-pass market contract lighter. It can be added later without re-ingesting FHFA.

## Lineage
1. `foundations/etl/staging/get_fhfa.R` downloads the annual FHFA national, state, CBSA, county, ZIP5, and tract files and writes source-faithful staging tables.
2. `foundations/etl/silver/fhfa_hpi_silver.R` keeps the first-pass analytical geography set, normalizes names with CBSA and county crosswalks, computes exact 1-year, 5-year, and 10-year appreciation metrics, and writes `silver.fhfa_hpi`.

## Known Gaps / To-Dos
- Tract rows remain staged-only for now even though the FHFA tract file is already available and landed.
- This contract does not try to manufacture a separate nonmetro geography family from FHFA's residual CBSA workbook rows.
- Gold currently uses the Zillow market surface for row coverage, so `silver.fhfa_hpi` contains broader historical and geography coverage than the downstream Gold market mart.

## How To Extend (Next Table)
1. Decide whether tract should graduate from staged-only status into the analytical Silver contract.
2. Re-check ZIP5-as-`zcta` assumptions if a stricter national ZCTA reconciliation layer becomes necessary.
3. If FHFA publishes a geography or methodology revision, rerun the landed profile and sync both this `.md` file and `silver__fhfa_hpi.yml`.
