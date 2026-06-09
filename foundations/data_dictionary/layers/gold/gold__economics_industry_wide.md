# Data Dictionary: gold.economics_industry_wide

## Overview
- **Table**: `gold.economics_industry_wide`
- **Purpose**: Gold-layer industry structure mart that combines ACS industry employment mix, curated CBP establishment structure, curated QCEW industry employment and wage levels, and BEA industry GDP structure in one geography-year table.
- **Row count**: `54,631`
- **KPI applicability**: Gold analytical output table.

## Grain & Keys
- **Declared grain**: One row per `geo_level + geo_id + year`
- **Primary key candidate**: (`geo_level`, `geo_id`, `year`)
- **Current key check**: `54,631` rows and `54,631` distinct `geo_level + geo_id + year` combinations
- **Time coverage**: `year` min=`2012`, max=`2024`
- **Geo coverage**: `county`, `cbsa`, and `state`

## QCEW Coverage Notes

QCEW does not fully populate every row in this Gold mart, but the table is now intentionally limited to the geography levels where the cross-source industry story is strongest.

- The Gold table keeps only `county`, `cbsa`, and `state`.
- QCEW columns are populated only where `silver.bls_qcew` exists.
- Live profile after materialization:
  - total rows with non-null `qcew_total_covered_emp`: `54,586`
  - `county` rows with QCEW coverage: `41,839`
  - `cbsa` rows with QCEW coverage: `12,071`
  - `state` rows with QCEW coverage: `676`

## CBP Coverage Notes

CBP now supplies the establishment-structure layer for this Gold mart.

- The Gold table keeps CBP on the same `county`, `cbsa`, and `state` geography surface as the rest of the mart.
- CBP columns are populated where `silver.cbp` exists.
- Live profile after materialization:
  - total rows with non-null `cbp_total_estabs`: `49,327`
  - `county` rows with CBP coverage: `37,685`
  - `cbsa` rows with CBP coverage: `11,030`
  - `state` rows with CBP coverage: `612`
- The current CBP range stops at `2023`, so `2024` rows in this Gold table are expected to have null CBP fields until the next CBP annual release is added.

## Industry Family Alignment

The Gold table keeps the existing broad industry families used by ACS and BEA, then aligns QCEW into the same family structure.

- `ag_mining`: QCEW `11` + `21`
- `construction`: QCEW `23`
- `manufacturing`: QCEW `31-33`
- `wholesale`: QCEW `42`
- `retail`: QCEW `44-45`
- `transport_util`: QCEW `22` + `48-49`
- `information`: QCEW `51`
- `finance_real`: QCEW `52` + `53`
- `professional`: QCEW `54` + `55` + `56`
- `educ_health`: QCEW `61` + `62`
- `arts_accomm_food`: QCEW `71` + `72`
- `other_services`: QCEW `81`
- `public_admin`: QCEW `92`

## Column Families

| Family | Columns | Definition |
| --- | --- | --- |
| Geography and base population | `geo_level`, `geo_id`, `geo_name`, `year`, `pop_total` | Shared geography-year keys plus total population from `silver.age_kpi`. |
| ACS industry employment levels | `acs_ind_*` | Employment counts by broad industry family from `silver.labor_kpi`. |
| ACS industry shares | `pct_acs_ind_*` | Industry employment shares from `silver.labor_kpi`. |
| CBP total structure | `cbp_total_*`, `cbp_estabs_per_1000_residents` | All-sector CBP establishments, March employment, payroll, and overall establishment density from `silver.cbp`. |
| CBP establishment mix | `cbp_estabs_*`, `pct_cbp_estabs_*` | Establishment counts and shares by aligned broad industry family from `silver.cbp`. |
| QCEW total-covered headline metrics | `qcew_total_covered_*` | Headline all-ownership covered employment, establishments, wages, and average weekly wage from the curated `industry_code = 10` row. |
| QCEW private-sector totals | `qcew_private_*_total`, `qcew_private_avg_wkly_wage` | Private-sector total employment, establishments, wages, and overall weekly wage across the curated private industry subset. |
| QCEW private-sector industry levels | `qcew_private_emp_*`, `qcew_private_avg_wkly_wage_*` | Private-sector employment levels and weekly wages by aligned industry family. |
| QCEW public administration | `qcew_public_admin_emp`, `qcew_public_admin_avg_wkly_wage` | Government-slice Public Administration metrics carried through from the explicit Silver exception for `industry_code = 92`. |
| QCEW private-sector shares | `pct_qcew_private_emp_*`, `pct_qcew_private_emp_of_total_covered`, `pct_qcew_public_admin_emp_of_total_covered` | Industry employment shares relative to private-sector total employment, plus the share of total covered employment represented by private employment and Public Administration. |
| BEA industry GDP levels | `real_gdp_*` | Real GDP levels by broad industry family from `silver.bea_regional_cagdp9_wide`. |
| BEA industry GDP shares | `pct_real_gdp_*` | GDP shares by industry family from `silver.bea_regional_cagdp9_wide`. |
| Derived diagnostics | `sector_sum`, `calc_real_gdp_other`, `pct_calc_real_gdp_other`, `industry_concentration_hhi`, `acs_industry_concentration_hhi`, `sector_sum_ratio`, `sector_sum_ratio_quality_flag` | Derived GDP balance and industry concentration diagnostics layered onto the ACS/BEA/QCEW joins. |

## Data Quality Notes
- `geo_name` is fully populated in the current live table.
- The Gold mart is intentionally narrowed to `county`, `cbsa`, and `state` so it behaves like a cross-source economic mart rather than an ACS-only geography spine with sparse enrichments.
- CBP industry totals in Gold are derived from the curated Silver contract:
  - `cbp_total_*` comes from the Silver all-sectors row `industry_code = '------'`
  - `cbp_estabs_*` sums the aligned broad-family rows in `silver.cbp`
  - `pct_cbp_estabs_*` uses `cbp_total_estabs` as the denominator
- The Gold mart still inherits its year range from `silver.age_kpi`, so it does not currently expose the full `2010–2024` QCEW range even though Silver QCEW does.
- QCEW industry totals in Gold are derived from the curated Silver contract:
  - `10` total covered from `own_code = 0`
  - most industry detail from private `own_code = 5`
  - `92 Public administration` from the government slices

## Lineage
1. `foundations/etl/silver/acs_age_silver.R` materializes the geography-year spine used as the Gold base.
2. `foundations/etl/silver/acs_labor_silver.R` materializes ACS industry employment levels and shares.
3. `foundations/etl/silver/cbp_silver.R` materializes the curated CBP long table joined here.
4. `foundations/etl/silver/bls_qcew_silver.R` materializes the curated QCEW long table joined here.
5. `foundations/etl/silver/bea_cagdp9_silver.R` materializes BEA regional GDP metrics joined here.
6. `foundations/etl/gold/gold_economy_industry.sql` builds `gold.economics_industry_wide`.

## Known Gaps / To-Dos
- If we later need lower ACS-only geographies such as `tract`, `zcta`, or `place`, add a separate industry-mix surface rather than widening this cross-source Gold mart again.
- The QCEW family mapping is intentionally broad; use `silver.bls_qcew` or `silver.bls_qcew_industry_map` for more granular industry analysis.
