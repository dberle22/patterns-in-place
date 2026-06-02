# Data Dictionary: staging ACS Labor Family

## Overview
- Schema: `staging`
- Family: `ACS Labor`
- Contract scope: source/theme family contract covering 12 materialized table(s) produced by [`scripts/etl/staging/get_acs_labor.R`](../../../scripts/etl/staging/get_acs_labor.R).
- Documentation rule: geography-replica or variant tables listed in this family file are covered by this contract and should not receive standalone staging dictionaries unless their schema diverges materially.

## Geography Coverage Matrix
This family dictionary is the contract for every materialized geography slice listed below. Replica tables in the matrix are considered documented here and should not be tracked as missing standalone dictionaries.

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| US | `acs_labor_us` | ACS 5-year wide landing |
| Region | `acs_labor_region` | ACS 5-year wide landing |
| Division | `acs_labor_division` | ACS 5-year wide landing |
| State | `acs_labor_state` | ACS 5-year wide landing |
| County | `acs_labor_county` | ACS 5-year wide landing |
| Place | `acs_labor_place` | ACS 5-year wide landing |
| ZCTA | `acs_labor_zcta` | ACS 5-year wide landing |
| All supported tract states | `acs_labor_tract` | Preferred family-wide tract landing table |
| Legacy tract compatibility | `acs_labor_tract_fl`, `acs_labor_tract_ga`, `acs_labor_tract_nc`, `acs_labor_tract_sc` | Maintained for downstream compatibility |

## Contract Summary
- All tables in this family share one contract signature.
- Column count: 91
- Grain: one row per geography-time unit at this table's native geography level (inferred from table design).
- Common key columns used across the family: `GEOID`, `year`, `NAME`
- Preferred tract contract: use the combined `*_tract` table for new downstream work; keep the legacy state-specific tract tables only for compatibility until consumers are migrated.

## Shared Columns
- `GEOID`, `year`, `NAME`, `pop_16plusE`, `pop_16plusM`, `in_labor_forceE`, `in_labor_forceM`, `in_lf_civilianE`, `in_lf_civilianM`, `in_lf_armed_forcesE`, `in_lf_armed_forcesM`, `not_in_labor_forceE`, `not_in_labor_forceM`, `employedE`, `employedM`, `occ_totalE`, `occ_totalM`, `occ_male_mgmt_business_sci_artsE`, `occ_male_mgmt_business_sci_artsM`, `occ_male_serviceE`, `occ_male_serviceM`, `occ_male_sales_officeE`, `occ_male_sales_officeM`, `occ_male_nat_resources_const_maintE`, `occ_male_nat_resources_const_maintM`, `occ_male_prod_transp_materialE`, `occ_male_prod_transp_materialM`, `occ_female_mgmt_business_sci_artsE`, `occ_female_mgmt_business_sci_artsM`, `occ_female_serviceE`, `occ_female_serviceM`, `occ_female_sales_officeE`, `occ_female_sales_officeM`, `occ_female_nat_resources_const_maintE`, `occ_female_nat_resources_const_maintM`, `occ_female_prod_transp_materialE`, `occ_female_prod_transp_materialM`, `ind_totalE`, `ind_totalM`, `ind_male_ag_miningE`, `ind_male_ag_miningM`, `ind_male_constructionE`, `ind_male_constructionM`, `ind_male_manufacturingE`, `ind_male_manufacturingM`, `ind_male_wholesaleE`, `ind_male_wholesaleM`, `ind_male_retailE`, `ind_male_retailM`, `ind_male_transport_utilE`, `ind_male_transport_utilM`, `ind_male_informationE`, `ind_male_informationM`, `ind_male_finance_realE`, `ind_male_finance_realM`, `ind_male_professionalE`, `ind_male_professionalM`, `ind_male_educ_healthE`, `ind_male_educ_healthM`, `ind_male_arts_accomm_foodE`, `ind_male_arts_accomm_foodM`, `ind_male_otherE`, `ind_male_otherM`, `ind_male_public_adminE`, `ind_male_public_adminM`, `ind_female_ag_miningE`, `ind_female_ag_miningM`, `ind_female_constructionE`, `ind_female_constructionM`, `ind_female_manufacturingE`, `ind_female_manufacturingM`, `ind_female_wholesaleE`, `ind_female_wholesaleM`, `ind_female_retailE`, `ind_female_retailM`, `ind_female_transport_utilE`, `ind_female_transport_utilM`, `ind_female_informationE`, `ind_female_informationM`, `ind_female_finance_realE`, `ind_female_finance_realM`, `ind_female_professionalE`, `ind_female_professionalM`, `ind_female_educ_healthE`, `ind_female_educ_healthM`, `ind_female_arts_accomm_foodE`, `ind_female_arts_accomm_foodM`, `ind_female_otherE`, `ind_female_otherM`, `ind_female_public_adminE`, `ind_female_public_adminM`

## Lineage
- [`scripts/etl/staging/get_acs_labor.R`](../../../scripts/etl/staging/get_acs_labor.R) is the family ingest script and defines the write targets listed in the coverage matrix above.

## Data Quality Notes
- Verify row uniqueness for the family's natural grain keys before Silver transforms.
- Validate expected time coverage and geography coverage against the coverage matrix in this document.
- Track schema drift by comparing column count/signature against this document on each refresh.

## Known Gaps / To-Dos
- Add explicit pass/fail threshold checks in the staged DQ runner after data dictionary coverage is complete.
- Retire the legacy tract compatibility tables once downstream Silver consumers have fully moved to the shared `*_tract` landing tables.
