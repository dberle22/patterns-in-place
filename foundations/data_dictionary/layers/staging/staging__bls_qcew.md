# Data Dictionary: staging BLS QCEW Family

## Overview
- Schema: `staging`
- Family: `BLS QCEW`
- Contract scope: source/theme family contract covering the geography-replica QCEW tables produced by [`foundations/etl/staging/get_bls_qcew.R`](../../../etl/staging/get_bls_qcew.R)
- Documentation rule: the state and county tables below share one staging contract and should be documented here together unless their schemas diverge materially later

## Geography Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| County | `bls_qcew_county` | Annual QCEW county rows from the annual singlefile, with titles backfilled from metadata so we can keep the broader staging contract without thousands of per-industry reads |
| State | `bls_qcew_state` | Annual QCEW state rows from the same singlefile source, preserved separately so Silver can continue to derive CBSA from counties without losing direct state source coverage |

## Contract Summary
- All tables in this family share one contract signature.
- Grain: one row per `geo_id + period + own_code + industry_code + agglvl_code + size_code + qtr`
- Common key columns used across the family: `geo_level`, `geo_id`, `period`, `own_code`, `industry_code`, `agglvl_code`, `size_code`, `qtr`
- Current annual scope: `2010` through `2024`

## Shared Columns
- Geography: `geo_level`, `geo_id`, `state_fips_code`, `county_fips_code`, `county_name`, `area_title`
- Time and source slices: `period`, `own_code`, `own_title`, `industry_code`, `industry_title`, `agglvl_code`, `agglvl_title`, `size_code`, `size_title`, `qtr`, `disclosure_code`
- Core annual metrics: `annual_avg_estabs`, `annual_avg_emplvl`, `total_annual_wages`, `taxable_annual_wages`, `annual_contributions`, `annual_avg_wkly_wage`, `avg_annual_pay`
- Location quotients: `lq_disclosure_code`, `lq_annual_avg_estabs`, `lq_annual_avg_emplvl`, `lq_total_annual_wages`, `lq_taxable_annual_wages`, `lq_annual_contributions`, `lq_annual_avg_wkly_wage`, `lq_avg_annual_pay`
- Over-the-year fields: `oty_disclosure_code`, `oty_annual_avg_estabs_chg`, `oty_annual_avg_estabs_pct_chg`, `oty_annual_avg_emplvl_chg`, `oty_annual_avg_emplvl_pct_chg`, `oty_total_annual_wages_chg`, `oty_total_annual_wages_pct_chg`, `oty_taxable_annual_wages_chg`, `oty_taxable_annual_wages_pct_chg`, `oty_annual_contributions_chg`, `oty_annual_contributions_pct_chg`, `oty_annual_avg_wkly_wage_chg`, `oty_annual_avg_wkly_wage_pct_chg`, `oty_avg_annual_pay_chg`, `oty_avg_annual_pay_pct_chg`
- Metadata: `src`, `version`

## Lineage
- [`foundations/etl/staging/get_bls_qcew.R`](../../../etl/staging/get_bls_qcew.R) downloads each annual BLS `annual_singlefile` ZIP, keeps annual state and county rows, backfills the omitted title columns from metadata, and writes the replica tables listed above.
- [`foundations/etl/reference/bls_qcew_industry_map.csv`](../../../etl/reference/bls_qcew_industry_map.csv) is the current metadata seed for distinguishing plain NAICS-style codes from BLS aggregate supersectors in downstream modeling.

## Data Quality Notes
- Verify uniqueness at `geo_level + geo_id + period + own_code + industry_code + agglvl_code + size_code + qtr`.
- Confirm the staged `industry_code` universe matches the ZIP member inventory for each ingested year.
- Preserve both state and county geographies; county rows remain the canonical fine-grain path for future CBSA derivation.
- Keep `lq_*` and `oty_*` fields intact so we do not have to re-ingest when those become analytically useful later.
- Unknown county rows such as `xx999` are intentionally retained in staging for source fidelity, even though they may be excluded or quarantined in downstream geography products.

## Known Gaps / To-Dos
- This family now favors source fidelity over compactness. The current full-history materialization is large by design:
  - `staging.bls_qcew_county`: `43,342,060` rows across `2010–2024`
  - `staging.bls_qcew_state`: `2,073,926` rows across `2010–2024`
- `silver.bls_qcew` should be revisited so its canonical analytical subset is driven by the mapping seed rather than by assumptions from the earlier county-only subset ingest.
