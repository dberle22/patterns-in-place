# Data Dictionary: staging LEHD QWI

## Overview
- Schema: `staging`
- Family: `LEHD QWI`
- Contract scope: annualized county-first QWI staging table produced by [`foundations/etl/staging/get_lehd_qwi.R`](../../../etl/staging/get_lehd_qwi.R)
- Documentation rule: this contract describes the managed annual staging table `staging.lehd_qwi`; the retained quarter-native fallback loader is documented in the source spec but is not the current canonical staging output

## Contract Summary
- Materialized table: `lehd_qwi`
- Current first-pass scope: county rows only, all-private ownership, NAICS sector industry detail, unadjusted source files, all-sex age rows, and all-sex education rows
- Grain: one row per `state_scope + demo_family + geo_id + industry_code + agegrp + education + year`
- Common key columns used across the table: `state_scope`, `demo_family`, `geo_id`, `industry_code`, `ownercode`, `sex`, `agegrp`, `race`, `ethnicity`, `education`, `firmage`, `firmsize`, `year`
- Current managed history window: rolling latest `10` years from each state file; current expected range is `2016` through `2025`

## Scope Decisions
- Geography: keep only published county rows where `geo_level = 'C'`
- Demographic families:
  - `demo_family = 'age'` comes from the `sa` source file family and keeps only `sex = '0'` and `education = 'E0'`
  - `demo_family = 'education'` comes from the `se` source file family and keeps only `sex = '0'`, `agegrp = 'A00'`, and `education <> 'E0'`
- Time handling:
  - source files are quarterly
  - the managed staging contract annualizes them to one row per retained county / year / industry / demographic slice
  - `periodicity = 'A'` in staging and `source_periodicity = 'Q'` preserves the provenance of the annualized rows
- Ownership and industry scope:
  - only `ownercode = 'A05'` all-private rows are retained
  - only `ind_level = 'CNS'` style sector rows from the `ns` file family are retained
- Seasonal adjustment: only unadjusted `seasonadj = 'U'` source rows are retained in the current first pass

## Shared Columns
- Geography and identifiers: `state_scope`, `state_fips`, `geo_level`, `geo_id`, `geography`
- Time and source slices: `demo_family`, `periodicity`, `source_periodicity`, `seasonadj`, `year`, `quarters_observed`, `keep_start_year`, `keep_end_year`
- Published worker and firm dimensions: `ind_level`, `industry_code`, `ownercode`, `sex`, `agegrp`, `race`, `ethnicity`, `education`, `firmage`, `firmsize`
- Annualized employment and payroll measures: `annual_avg_emp`, `annual_avg_empend`, `annual_avg_emps`, `annual_avg_emptotal`, `annual_avg_empspv`, `annual_hira`, `annual_hirn`, `annual_hirr`, `annual_sep`, `annual_hiraend`, `annual_sepbeg`, `annual_hiraendrepl`, `annual_avg_earns`, `annual_avg_earnbeg`, `annual_avg_earnhiras`, `annual_avg_earnhirns`, `annual_avg_earnseps`, `annual_payroll`
- Source metadata: `source_file`, `release_id`, `schema_version`, `metadata_period_range`

## Annualization Rules
- Average across observed quarters:
  - `Emp`, `EmpEnd`, `EmpS`, `EmpTotal`, `EmpSpv`
  - `EarnS`, `EarnBeg`, `EarnHirAS`, `EarnHirNS`, `EarnSepS`
- Sum across observed quarters:
  - `HirA`, `HirN`, `HirR`, `Sep`, `HirAEnd`, `SepBeg`, `HirAEndRepl`, `Payroll`
- Quarter coverage:
  - `quarters_observed` records how many quarterly rows contributed to the annual row
  - valid values are `1` through `4`

## Suppression And Status Handling
- The current annual staging table keeps the published measure payload but does not yet carry forward the quarter-level `s*` suppression/status columns.
- This is an intentional size-management tradeoff in the current annual contract.
- Suppression-aware downstream modeling should therefore treat null or structurally missing measure values conservatively and rely on the source spec for the underlying LEHD flag definitions until a future staging expansion restores explicit status fields.

## Lineage
- [`foundations/etl/staging/get_lehd_qwi.R`](../../../etl/staging/get_lehd_qwi.R) downloads `version_qwi.txt` plus the scoped `sa` and `se` county-sector source files for each requested state scope, filters the approved demographic slices in DuckDB, annualizes the quarterly rows, validates the resulting batch grain, and writes `staging.lehd_qwi`.
- [`foundations/etl/staging/get_lehd_qwi_quarterly.R`](../../../etl/staging/get_lehd_qwi_quarterly.R) preserves the quarter-native fallback path for future use if quarterly analysis becomes necessary again.

## Data Quality Notes
- Verify uniqueness at `state_scope + demo_family + geo_id + industry_code + ownercode + sex + agegrp + race + ethnicity + education + firmage + firmsize + year`.
- Confirm `geo_id` is always a valid `5`-digit county GEOID in the current managed table.
- Confirm `geo_level = 'C'`, `seasonadj = 'U'`, `ownercode = 'A05'`, `periodicity = 'A'`, and `source_periodicity = 'Q'` for all rows.
- Keep `quarters_observed` so downstream Silver can identify edge years or structurally incomplete annual observations if needed.
- The observed live first-pass history is broader than the older planning assumption that some demographic families only begin in `2009`; the current staging window is instead bounded by the rolling `10`-year retention rule.

## Known Gaps / To-Dos
- If quarterly QWI becomes a real analytical requirement, restore a second managed staging contract that carries quarter rows and the published `s*` suppression fields directly.
- Document the final live row count and state coverage after the full national staged run is complete.
