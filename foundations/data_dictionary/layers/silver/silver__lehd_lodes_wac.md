# Data Dictionary: silver.lehd_lodes_wac

## Overview
- **Table**: `silver.lehd_lodes_wac`
- **Purpose**: Silver labor-geography table that standardizes staged LODES WAC tract rows, preserves tract as the canonical base, and derives county, CBSA, state, and division rollups for downstream neighborhood and regional employment analysis.
- **Status**: materialized from the current tract-first staging implementation.
- **Row count**: `84,760`

## Grain & Keys
- **Declared grain**: one row per `geo_level + geo_id + year`
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `year`)
- **Current geography coverage**: `tract`, `county`, `cbsa`, `state`, and `division`
- **Current time coverage**: `year` min=`2023`, max=`2023`

## Contract Summary
- Input: `staging.lehd_lodes_wac`
- Base geography: tract
- Geography policy:
  - keep tract as the canonical Silver base geography
  - validate tract rows against `silver.xwalk_tract_county`
  - derive `county`, `cbsa`, `state`, and `division` from the validated tract base rather than from separate published geography files
  - exclude Alaska `02261` and any non-platform tract geographies consistent with broader geography policy
- Analytical surface:
  - preserve total jobs
  - preserve age bands
  - preserve earnings bands
  - preserve broad industry sectors
  - preserve education bands
  - preserve WAC-only firm age
  - preserve WAC-only firm size
- Defer from the first canonical Silver contract:
  - race / ethnicity
  - sex

## Recommended Canonical Columns
- Geography: `geo_level`, `geo_id`, `geo_name`
- Time: `year`
- Core jobs totals:
  - `jobs_total`
- Age composition:
  - `jobs_age_29_or_younger`
  - `jobs_age_30_54`
  - `jobs_age_55_plus`
- Earnings composition:
  - `jobs_earnings_low`
  - `jobs_earnings_mid`
  - `jobs_earnings_high`
- Education composition:
  - `jobs_edu_less_than_hs`
  - `jobs_edu_hs_or_some_college`
  - `jobs_edu_bachelors_or_advanced`
  - `jobs_edu_not_available`
- Employer structure:
  - `jobs_firm_age_0_1`
  - `jobs_firm_age_2_3`
  - `jobs_firm_age_4_5`
  - `jobs_firm_age_6_10`
  - `jobs_firm_age_11_plus`
  - `jobs_firm_size_0_19`
  - `jobs_firm_size_20_49`
  - `jobs_firm_size_50_249`
  - `jobs_firm_size_250_499`
  - `jobs_firm_size_500_plus`
- Broad industry sectors:
  - `jobs_ind_ag_mining_utilities`
  - `jobs_ind_construction`
  - `jobs_ind_manufacturing`
  - `jobs_ind_wholesale`
  - `jobs_ind_retail`
  - `jobs_ind_transport_warehouse`
  - `jobs_ind_information`
  - `jobs_ind_finance_real_estate`
  - `jobs_ind_professional`
  - `jobs_ind_admin_support`
  - `jobs_ind_education_health`
  - `jobs_ind_entertainment_hospitality`
  - `jobs_ind_other_services`
  - remaining direct `CNS*` columns if we preserve the full published sector matrix in the first pass

## Source Mappings
- `jobs_total` <- `C000`
- age bands <- `CA01`, `CA02`, `CA03`
- earnings bands <- `CE01`, `CE02`, `CE03`
- education bands <- `CD01`, `CD02`, `CD03`, `CD04`
- firm age <- `CFA01`, `CFA02`, `CFA03`, `CFA04`, `CFA05`
- firm size <- `CFS01`, `CFS02`, `CFS03`, `CFS04`, `CFS05`
- tract geography key <- `tract_geoid`

## Recommended Derived Measures
- `pct_jobs_age_29_or_younger` = `jobs_age_29_or_younger / jobs_total`
- `pct_jobs_age_30_54` = `jobs_age_30_54 / jobs_total`
- `pct_jobs_age_55_plus` = `jobs_age_55_plus / jobs_total`
- `pct_jobs_earnings_low` = `jobs_earnings_low / jobs_total`
- `pct_jobs_earnings_mid` = `jobs_earnings_mid / jobs_total`
- `pct_jobs_earnings_high` = `jobs_earnings_high / jobs_total`
- `pct_jobs_firm_age_0_1` = `jobs_firm_age_0_1 / jobs_total`
- `pct_jobs_firm_age_11_plus` = `jobs_firm_age_11_plus / jobs_total`
- `pct_jobs_firm_size_0_19` = `jobs_firm_size_0_19 / jobs_total`
- `pct_jobs_firm_size_500_plus` = `jobs_firm_size_500_plus / jobs_total`
- sector shares recomputed from tract totals rather than copied from staging

## Standardization Rules
- Set `geo_level = 'tract'` and `geo_id = tract_geoid`.
- Join tract metadata from the canonical geography backbone so `geo_name` and geography validation do not depend on staged helper columns alone.
- Rename the raw `C*` payload into analytical names that can be understood without consulting LODES documentation.
- Drop row-level helper geography and release metadata fields after rollups; managed crosswalks and source documentation remain the authoritative place for that context.
- Keep WAC-only employer structure fields as first-class analytical columns in this table; the WAC/RAC pair is intentionally asymmetric.

## Rollup Plan
- Keep tract as the source-of-truth base.
- Build county rows by summing validated tract rows by `county_geoid + year`.
- Build CBSA rows by summing validated tract rows after joining the tract-to-county backbone to `silver.xwalk_cbsa_county`.
- Build state rows by summing tract or county rows to `state_fips + year`.
- Build division rows by joining state rows to `silver.xwalk_state_region`.
- Recompute shares after each rollup from the rolled-up totals rather than averaging tract shares.
- Exclude staged tract rows that fail canonical geography validation from the rolled-up outputs until the crosswalk issue is resolved.
- Expect CBSA totals to be lower than county/state/division totals because non-metro counties do not belong to any CBSA and therefore stay out of the CBSA rollup.

Expected geography pattern in Silver:
- `tract`: canonical neighborhood base
- `county`: tract-derived
- `cbsa`: tract-derived through county membership
- `state`: tract-derived
- `division`: state-derived

## Gold Handoff
- Primary Gold home: `gold.economics_lodes_wide`
- Intended Gold use:
  - employment-side tract context for Deep Dive zone clustering
  - tract labor composition inputs that complement ACS residential demographics
  - joined jobs-versus-resident-workers comparison once WAC is paired with RAC

## Data Quality Notes
- Validate uniqueness at `geo_level + geo_id + year`.
- Confirm every tract row intended for retained Silver output maps to `silver.xwalk_tract_county`.
- Confirm `jobs_total` and all retained count columns are non-negative.
- Current live staging validation found `3` WAC tract rows missing from `silver.xwalk_tract_county`:
  - `25025990101` in Massachusetts
  - `24037990000` in Maryland
  - `45013990100` in South Carolina
- Silver should exclude or explicitly quarantine those unmatched tracts before county / CBSA / state / division rollups so they do not silently disappear in mixed ways across geographies.
- Keep the Silver contract focused on counts and shares that are directly interpretable at tract scale rather than prematurely widening to every available WAC payload family.
- WAC is intentionally wider than RAC because firm age and firm size are source-native WAC-only concepts and are useful for neighborhood economic character.
- Current landed Silver coverage:
  - `tract`: `80,782` rows / `80,782` geographies
  - `county`: `3,031` rows / `3,031` geographies
  - `cbsa`: `889` rows / `889` geographies
  - `state`: `49` rows / `49` geographies
  - `division`: `9` rows / `9` geographies

## Lineage
1. [`foundations/etl/staging/get_lehd_lodes.R`](../../../etl/staging/get_lehd_lodes.R) lands the tract-level WAC staging table.
2. [`foundations/etl/silver/lehd_lodes_silver.R`](../../../etl/silver/lehd_lodes_silver.R) normalizes the staged tract rows, renames the retained analytical fields, validates geography coverage, derives county / CBSA / state / division rollups from the tract base, and writes `silver.lehd_lodes_wac`.

## Known Gaps / To-Dos
- Decide the exact industry rollup strategy for `CNS01-20`: preserve the full published matrix in Silver or collapse immediately to broader platform families.
- The WAC contract now intentionally keeps firm age and firm size in the main Silver surface; keep that asymmetry explicit in the YAML companion and downstream docs.
- Add the YAML companion if we decide to keep YAML as a required artifact for this table family.
