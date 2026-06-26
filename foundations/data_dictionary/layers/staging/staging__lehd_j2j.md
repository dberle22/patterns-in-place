# Data Dictionary: staging LEHD J2J

## Overview
- Schema: `staging`
- Family: `LEHD J2J`
- Contract scope: annualized state + metro J2J staging table produced by [`foundations/etl/staging/get_lehd_j2j.R`](../../../etl/staging/get_lehd_j2j.R)
- Documentation rule: this contract describes the managed annual staging table `staging.lehd_j2j`; published `J2JR` rates and `J2JOD` origin-destination flows are intentionally outside the current shared staging contract

## Contract Summary
- Materialized table: `lehd_j2j`
- Current first-pass scope: `J2J` counts only, state and metro files, worker-age family only, unadjusted source rows, all-sex / all-race / all-ethnicity / all-education slice, annualized before write
- Grain: one row per `source_scope_type + source_scope_id + geo_id + industry_code + agegrp + year`
- Common key columns used across the table: `source_scope_type`, `source_scope_id`, `geo_level`, `geo_id`, `ind_level`, `industry_code`, `ownercode`, `sex`, `agegrp`, `race`, `ethnicity`, `education`, `firmage`, `firmsize`, `year`
- Current managed history rule: rolling latest `5` completed years per source file
- Current observed landed coverage after the successful production run:
  - `457,889` total rows
  - `51` state scopes and `435` metro scopes
  - observed year range `2011-2024`
  - most current scopes retain `2020-2024`, but older source files keep earlier 5-year windows such as `2011-2015` or `2016-2020`

## Scope Decisions
- Geography:
  - retain state rows where `geo_level = 'S'`
  - retain metro / micropolitan rows where `geo_level = 'B'`
  - keep both in one staging table and preserve `source_scope_type` plus `source_scope_id` so downstream Silver can canonicalize them separately
- Demographic family:
  - state files come from the `sa` worker-age family
  - metro files come from the broader `sarhe` family, but staging keeps only the age-equivalent slice where `sex = '0'`, `race = 'A0'`, `ethnicity = 'A0'`, and `education = 'E0'`
  - `demo_family = 'age'` is the only retained first-pass slice
- Time handling:
  - source files are quarterly
  - staging annualizes them to one row per retained geography / year / industry / age slice
  - `periodicity = 'A'` in staging and `source_periodicity = 'Q'` preserves the provenance of the annualized rows
  - the completed-year window is determined per source file, not globally
- Product scope:
  - only `J2J` counts are retained
  - published `J2JR` rates are validation-only and are not materialized here
  - `J2JOD` is deferred to Deep Dive-specific follow-on work
- Seasonal adjustment:
  - only unadjusted `seasonadj = 'U'` source rows are retained in the current first pass

## Shared Columns
- Geography and identifiers: `source_scope_type`, `source_scope_id`, `state_scope`, `state_fips`, `geo_level`, `geo_id`, `geography`
- Time and source slices: `demo_family`, `periodicity`, `source_periodicity`, `seasonadj`, `year`, `quarters_observed`, `latest_source_year`, `keep_start_year`, `keep_end_year`
- Published worker and firm dimensions: `ind_level`, `industry_code`, `ownercode`, `sex`, `agegrp`, `race`, `ethnicity`, `education`, `firmage`, `firmsize`
- Annualized mobility counts:
  - `annual_mhire`, `annual_msep`, `annual_mjobstart`, `annual_mjobend`
  - `annual_eehire`, `annual_eesep`, `annual_aqhire`, `annual_aqsep`
  - `annual_j2jhire`, `annual_j2jsep`
  - `annual_nehire`, `annual_ensep`
  - `annual_eeseps`, `annual_eehires`, `annual_aqseps`, `annual_aqhires`
- Annualized average reference counts:
  - `annual_avg_nepersist`, `annual_avg_enpersist`
  - `annual_avg_nefullq`, `annual_avg_enfullq`
  - `annual_avg_mainb`, `annual_avg_maine`
  - `annual_avg_nepersists`, `annual_avg_enpersists`
  - `annual_avg_jobstays`, `annual_avg_mainbs`, `annual_avg_maines`
- Annualized average earnings fields:
  - `annual_avg_nehiresearn_dest`, `annual_avg_ensepsearn_orig`
  - `annual_avg_jobstaysearn_orig`, `annual_avg_jobstaysearn_dest`
  - `annual_avg_eesepsearn_orig`, `annual_avg_eehiresearn_dest`
  - `annual_avg_aqsepsearn_orig`, `annual_avg_aqhiresearn_dest`
- Source metadata: `source_file`, `release_id`, `schema_version`, `metadata_period_range`

## Annualization Rules
- Sum across observed quarters:
  - `MHire`, `MSep`, `MJobStart`, `MJobEnd`
  - `EEHire`, `EESep`, `AQHire`, `AQSep`
  - `J2JHire`, `J2JSep`
  - `NEHire`, `ENSep`
  - `EESepS`, `EEHireS`, `AQSepS`, `AQHireS`
- Average across observed quarters for reference / stock-like counts:
  - `NEPersist`, `ENPersist`
  - `NEFullQ`, `ENFullQ`
  - `MainB`, `MainE`
  - `NEPersistS`, `ENPersistS`
  - `JobStayS`, `MainBS`, `MainES`
- Average across observed quarters for earnings measures:
  - `NEHireSEarn_Dest`, `ENSepSEarn_Orig`
  - `JobStaySEarn_Orig`, `JobStaySEarn_Dest`
  - `EESepSEarn_Orig`, `EEHireSEarn_Dest`
  - `AQSepSEarn_Orig`, `AQHireSEarn_Dest`
- Quarter coverage:
  - `quarters_observed` records how many quarterly rows contributed to the annual row
  - valid values are `1` through `4`
  - current landed distribution:
    - `456,022` rows with `4` quarters observed
    - `905` rows with `3`
    - `626` rows with `2`
    - `336` rows with `1`

## Lineage
- [`foundations/etl/staging/get_lehd_j2j.R`](../../../etl/staging/get_lehd_j2j.R) downloads the scoped `J2J` state and metro source files plus the provider metadata files, filters the approved age-only slice in DuckDB, annualizes the quarterly rows, validates the resulting batch grain, and writes `staging.lehd_j2j`.
- Provider-level source structure, `J2JR` deferral, `J2JOD` deferral, and the current live release caveats live in [`../../sources/source__lehd_j2j.md`](../../sources/source__lehd_j2j.md).

## Data Quality Notes
- Verified uniqueness at `source_scope_type + source_scope_id + geo_level + geo_id + ind_level + industry_code + ownercode + sex + agegrp + race + ethnicity + education + firmage + firmsize + year`.
- Confirmed `periodicity = 'A'`, `source_periodicity = 'Q'`, `seasonadj = 'U'`, and `demo_family = 'age'` for the landed table.
- Confirmed `geo_level` is only `S` for state-scope rows and `B` for metro-scope rows.
- Confirmed state rows carry `2`-digit GEOIDs while metro rows carry `5`-digit source geography codes.
- Because the rolling `5`-year window is applied per source file, the combined table does not have one universal time span; some older scopes contribute earlier 5-year windows such as `2011-2015`.
- Keep `quarters_observed` so downstream Silver can detect incomplete annual observations before deriving canonical mobility rates.

## Known Gaps / To-Dos
- The current contract does not preserve quarter-level `s*` status / suppression fields; if downstream modeling needs explicit status propagation, staging should be widened in a future revision.
- `J2JR` should only be added if we decide published-rate parity is worth duplicating the row lattice.
- `J2JOD` remains outside this staging contract and should land as its own future source-family contract if and when Deep Dive labor-flow work begins.
