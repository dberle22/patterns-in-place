# Source Spec: ACS

## 1. Overview

- Source: U.S. Census Bureau American Community Survey
- Access pattern: API via `tidycensus`
- Primary credential dependency: Census API key
- Scope in Foundations: ACS supplies multiple topic families that land in staging as geography-replica tables and are then standardized into Silver base and KPI tables.
- Documentation goal: this file is the source-level spec for ACS as a provider. Topic-level variation is documented within each section below.

## 2. Coverage Matrix

This source spec covers all ACS topic families currently documented in the data dictionary.

| Topic | Staging family contract | Silver outputs |
| --- | --- | --- |
| Age | [../layers/staging/staging__acs_age.md](../layers/staging/staging__acs_age.md) | `silver.age_base`, `silver.age_kpi` |
| Education | [../layers/staging/staging__acs_education.md](../layers/staging/staging__acs_education.md) | `silver.education_base`, `silver.education_kpi` |
| Housing | [../layers/staging/staging__acs_housing.md](../layers/staging/staging__acs_housing.md) | `silver.housing_base`, `silver.housing_kpi` |
| Income | [../layers/staging/staging__acs_income.md](../layers/staging/staging__acs_income.md) | `silver.income_base`, `silver.income_kpi` |
| Labor | [../layers/staging/staging__acs_labor.md](../layers/staging/staging__acs_labor.md) | `silver.labor_base`, `silver.labor_kpi` |
| Migration | [../layers/staging/staging__acs_migration.md](../layers/staging/staging__acs_migration.md) | `silver.migration_base`, `silver.migration_kpi` |
| Race | [../layers/staging/staging__acs_race.md](../layers/staging/staging__acs_race.md) | `silver.race_base`, `silver.race_kpi` |
| Social Infrastructure | [../layers/staging/staging__acs_social_infrastructure.md](../layers/staging/staging__acs_social_infrastructure.md) | `silver.social_infra_base`, `silver.social_infra_kpi` |
| Transportation | [../layers/staging/staging__acs_transportation.md](../layers/staging/staging__acs_transportation.md) | `silver.transport_base`, `silver.transport_kpi` |
| Texas school metrics | no dedicated staging family contract in `layers/staging` | `silver.acs_tx_school_metrics` |

## 3. Source Contract

- Provider: U.S. Census Bureau American Community Survey
- Retrieval interface: `tidycensus`
- Common request pattern: topic-specific variable maps, repeated across a geography ladder and year range
- Common geography pattern: US, region, division, state, county, place, ZCTA, tract; most standard ACS topics also derive CBSA rows in Silver from county inputs
- Common time pattern: script-defined multi-year pulls, generally spanning 2012 forward in current Silver outputs

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/R/acs_ingest.R](../../etl/R/acs_ingest.R)
- [../../etl/R/standardize_acs_df.R](../../etl/R/standardize_acs_df.R)

| Topic | Source groups / subject area | Staging ingest entrypoint |
| --- | --- | --- |
| Age | `B01001` sex-by-age distribution and `B01002` median age | [../../etl/staging/get_acs_age.R](../../etl/staging/get_acs_age.R) |
| Education | educational attainment for population 25+ | [../../etl/staging/get_acs_edu.R](../../etl/staging/get_acs_edu.R) |
| Housing | housing units, occupancy, tenure, rent, home value, owner costs, structure type | [../../etl/staging/get_acs_housing.R](../../etl/staging/get_acs_housing.R) |
| Income | household income, per-capita income, poverty, income distribution, Gini index | [../../etl/staging/get_acs_income.R](../../etl/staging/get_acs_income.R) |
| Labor | labor-force status, occupation mix, industry mix | [../../etl/staging/get_acs_labor.R](../../etl/staging/get_acs_labor.R) |
| Migration | residence-one-year-ago migration and nativity / foreign-born status | [../../etl/staging/get_acs_migration.R](../../etl/staging/get_acs_migration.R) |
| Race | race / ethnicity composition, especially non-Hispanic subgroup counts plus Hispanic total | [../../etl/staging/get_acs_race.R](../../etl/staging/get_acs_race.R) |
| Social Infrastructure | household composition and health insurance coverage by age band | [../../etl/staging/get_acs_social_infra.R](../../etl/staging/get_acs_social_infra.R) |
| Transportation | commute mode, work-from-home, vehicle availability, aggregate travel time | [../../etl/staging/get_acs_transport.R](../../etl/staging/get_acs_transport.R) |
| Texas school metrics | combined ACS demographic, poverty, income, education, race, and household variables for Texas unified school districts | [../../etl/staging/tx_school_acs_ingest.R](../../etl/staging/tx_school_acs_ingest.R) |

## 4. Staging Shape

Common ACS staging pattern:
- one staging family contract per topic
- one materialized table per geography slice
- shared raw identifier pattern built around `GEOID`, `NAME`, and `year`
- wide landing tables with topic-specific estimate and margin-of-error columns

| Topic | Staging family | Column count | Coverage shape |
| --- | --- | ---: | --- |
| Age | `staging__acs_age` | 103 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Education | `staging__acs_education` | 53 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Housing | `staging__acs_housing` | 71 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Income | `staging__acs_income` | 47 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Labor | `staging__acs_labor` | 91 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Migration | `staging__acs_migration` | 23 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Race | `staging__acs_race` | 21 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Social Infrastructure | `staging__acs_social_infrastructure` | 43 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Transportation | `staging__acs_transportation` | 39 | standard geography ladder plus combined tract table and legacy tract compatibility tables |
| Texas school metrics | none in `layers/staging` | n/a | direct ACS pull at `school district (unified)` geography for Texas only |

Notes:
- For the standard ACS topic families, the preferred tract contract is the combined `*_tract` table.
- Legacy state-specific tract tables remain present for compatibility in the staging family contracts.
- Texas school metrics are a special ACS case because the pipeline writes the result directly to `silver.acs_tx_school_metrics` rather than maintaining a separate staging family contract.

## 5. Staging To Silver

Common ACS handoff pattern:
1. Read topic-specific staging tables by geography slice.
2. Standardize names and geography fields into a shared Silver contract.
3. Union all geography slices into one base table.
4. Derive CBSA rows from county rows where the Silver model uses crosswalk-based rebasing.
5. Create a base table for standardized source-aligned fields.
6. Create a KPI table for derived metrics.

| Topic | Silver handoff | Special path |
| --- | --- | --- |
| Age | `staging__acs_age` -> `silver.age_base` -> `silver.age_kpi` | CBSA rows rebased from county data via `silver.xwalk_cbsa_county` |
| Education | `staging__acs_education` -> `silver.education_base` -> `silver.education_kpi` | CBSA rows rebased from county data |
| Housing | `staging__acs_housing` -> `silver.housing_base` -> `silver.housing_kpi` | CBSA rows rebased from county data; weighted medians retained for value/rent metrics |
| Income | `staging__acs_income` -> `silver.income_base` -> `silver.income_kpi` | CBSA rows rebased from county data; weighted median household income and weighted Gini handling |
| Labor | `staging__acs_labor` -> `silver.labor_base` -> `silver.labor_kpi` | CBSA rows rebased from county data |
| Migration | `staging__acs_migration` -> `silver.migration_base` -> `silver.migration_kpi` | CBSA rows rebased from county data |
| Race | `staging__acs_race` -> `silver.race_base` -> `silver.race_kpi` | CBSA rows rebased from county data |
| Social Infrastructure | `staging__acs_social_infrastructure` -> `silver.social_infra_base` -> `silver.social_infra_kpi` | supports either combined tract table or fallback union of legacy tract tables |
| Transportation | `staging__acs_transportation` -> `silver.transport_base` -> `silver.transport_kpi` | CBSA rows rebased from county data |
| Texas school metrics | direct ACS ingest -> `silver.acs_tx_school_metrics` | bypasses normal staging-family -> Silver pattern |

## 6. Transformation Notes

| Topic | Base-table role | KPI / derivation logic |
| --- | --- | --- |
| Age | standardized ACS age and median-age fields across all geographies | age buckets, population shares, `aging_index`, `youth_dependency`, `old_age_dependency` |
| Education | detailed attainment counts for population 25+ | rollup into `lt_hs_25p`, `hs_ged_25p`, `somecol_assoc_25p`, `ba_25p`, `ma_plus_25p` and percent shares |
| Housing | direct occupancy, tenure, value, rent-burden, owner-cost, and structure fields | vacancy / occupancy / owner / renter rates, rent-burden thresholds, structure-category rollups and shares |
| Income | direct income, poverty, income-bin, and inequality fields | poverty rate, Gini, and household income distribution shares such as `<25k`, `25k-50k`, `50k-100k`, `100k+` |
| Labor | direct labor-force, occupation, and industry counts | LFPR, unemployment / employment ratios, occupation-mix shares, industry-mix shares |
| Migration | direct mobility and nativity counts | migration shares by move type, foreign-born / native shares, non-citizen share |
| Race | direct race / ethnicity counts | race / ethnicity shares and diversity index |
| Social Infrastructure | direct household composition and insurance counts | household-composition shares, insured / uninsured shares, age-band insurance coverage shares |
| Transportation | direct commute, work-from-home, vehicle, and travel-time fields | commute-mode shares, vehicle-availability shares, mean travel time |
| Texas school metrics | already modeled analytical output, not a base-plus-kpi pair | direct district-level metrics such as child poverty, education shares, household-with-children share, and race shares |

Additional ACS-wide transform notes:
- Most standard ACS Silver models use `standardize_acs_df()` to normalize geography fields.
- Most standard topic families rebase county rows to CBSA using `silver.xwalk_cbsa_county`.
- Social infrastructure explicitly supports either the combined tract table or fallback legacy tract tables in the Silver build.
- Texas school metrics are assembled from a mixed ACS variable map and written directly as an analysis-facing Silver table.

## 7. Data Quality Expectations

| Topic | Non-boilerplate checks worth preserving |
| --- | --- |
| Age | monitor denominator-driven nulls or `-nan` behavior in shares and dependency ratios; keep legacy tract compatibility tables aligned until retired |
| Education | watch zero-denominator behavior for `edu_total_25p`; confirm grouped attainment buckets still sum sensibly against the 25+ base |
| Housing | monitor null behavior in median rent / home value fields and rent-burden universes; confirm rent-denominator logic excludes `rent_not_computed` correctly |
| Income | monitor weighted CBSA median / inequality behavior; verify poverty universe and household-income denominators remain populated where shares are expected |
| Labor | review negative or >1 unemployment-rate anomalies already surfaced in current docs; monitor denominator behavior for occupation and industry shares |
| Migration | verify move-type shares remain bounded and that nativity components still reconcile to the nativity universe |
| Race | verify subgroup counts continue reconciling to the race total closely enough for share and diversity calculations |
| Social Infrastructure | preserve component reconciliation between household totals and household subgroups, and between insurance totals and age-band insurance components |
| Transportation | watch denominator-driven nulls in commute and vehicle shares; monitor aggregate-to-mean travel-time behavior where worker counts are zero or sparse |
| Texas school metrics | validate district-year uniqueness and watch the custom `racial_diversity_index` interpretation because the script currently computes concentration rather than `1 - sum(shares^2)` |

## 8. Operational Notes

- Shared helper code:
  [../../etl/R/acs_ingest.R](../../etl/R/acs_ingest.R),
  [../../etl/R/standardize_acs_df.R](../../etl/R/standardize_acs_df.R)
- Most standard ACS topic families follow the same ETL shape:
  `foundations/etl/staging/get_acs_<topic>.R` -> `foundations/etl/silver/acs_<topic>_silver.R`
- The main exception is Texas school metrics:
  [../../etl/staging/tx_school_acs_ingest.R](../../etl/staging/tx_school_acs_ingest.R)
  writes directly to `silver.acs_tx_school_metrics`
- Social infrastructure has a second operational wrinkle:
  the Silver builder can materialize from the combined tract table when present, or fall back to the legacy tract tables
- Current documentation pattern:
  staging remains family-contract based, Silver remains table-contract based, and this file sits above both as the provider-level spec

## 9. Known Gaps

- The ACS source spec now covers all current topics at a summary level, but it does not yet capture exact ACS table-code mappings for every topic the way the Age section originally did.
- Existing staging family contracts usually identify the ingest script but do not yet explain the full Silver handoff in place.
- Some table-level lineage references still use older path conventions and should be normalized over time.
- Texas school metrics still sit outside the standard staging-family documentation model and may eventually deserve either a staging-family contract or a clearer exception rule.
