# Data Dictionary: staging BLS OEWS Family

## Overview
- Schema: `staging`
- Family: `BLS OEWS`
- Contract scope: source-family staging contract for the `May 2025` OEWS state and metro/nonmetro workbooks produced by [`foundations/etl/staging/get_bls_oews.R`](../../../etl/staging/get_bls_oews.R)
- Documentation rule: the state and metro/nonmetro tables below share one staging contract because they publish the same column layout and differ only in geography coverage and workbook origin

## Geography Coverage Matrix

| Coverage slice | Materialized table(s) | Notes |
| --- | --- | --- |
| State and territory cross-industry occupational estimates | `bls_oews_state` | Includes the `51` state/DC rows plus `3` territorial areas (`Guam`, `Puerto Rico`, `Virgin Islands`) published in the state workbook |
| Metropolitan and nonmetropolitan cross-industry occupational estimates | `bls_oews_metro_nonmetro` | Combines the metro workbook (`393` metro areas) and the nonmetro workbook (`137` nonmetro areas) into one source-faithful staging table with a scope discriminator |

## Contract Summary
- This family currently lands as two source-faithful geography tables with the same shared schema.
- Grain:
  - `bls_oews_state`: one row per `release_year + area + occ_code`
  - `bls_oews_metro_nonmetro`: one row per `release_year + source_area_scope + area + occ_code`
- Current first-pass scope: `May 2025` only
- Current landed volume:
  - `staging.bls_oews_state`: `37,408` rows
  - `staging.bls_oews_metro_nonmetro`: `198,712` rows
- Current distinct-area counts:
  - state/territory table: `54`
  - metro/nonmetro table: `530`

## Shared Columns
- Geography and source IDs:
  - `area`: source geography code
  - `area_title`: provider-published geography label
  - `area_type`: provider geography type code
  - `prim_state`: primary state or territory abbreviation used by BLS
- Industry and ownership identifiers:
  - `naics`
  - `naics_title`
  - `i_group`
  - `own_code`
- Occupation identifiers:
  - `occ_code`
  - `occ_title`
  - `o_group`
- Employment and concentration fields:
  - `tot_emp`
  - `emp_prse`
  - `jobs_1000`
  - `loc_quotient`
  - `pct_total`
  - `pct_rpt`
- Wage and reliability fields:
  - `h_mean`
  - `a_mean`
  - `mean_prse`
  - `h_pct10`
  - `h_pct25`
  - `h_median`
  - `h_pct75`
  - `h_pct90`
  - `a_pct10`
  - `a_pct25`
  - `a_median`
  - `a_pct75`
  - `a_pct90`
  - `annual`
  - `hourly`
- Added provenance:
  - `release_year`
  - `source_geo_family`
  - `source_workbook`
  - `source_area_scope`

## What The Current Staging Script Cleans

The current OEWS staging script is intentionally light-touch. Between raw download and staged table write, it only does the minimum work needed to make the workbook rows reproducible and queryable:

1. Downloads the published BLS ZIP files for the current release and caches them locally.
2. Extracts the workbook members we actually need:
   - `state_M2025_dl.xlsx`
   - `MSA_M2025_dl.xlsx`
   - `BOS_M2025_dl.xlsx`
3. Reads the first worksheet from each workbook and preserves every published data column as text.
4. Standardizes the column names with `janitor::clean_names()`.
5. Adds four provenance columns:
   - `release_year = 2025`
   - `source_geo_family`
   - `source_workbook`
   - `source_area_scope`
6. Classifies the state workbook rows into `state` versus `territory` using the source `area_type`.
7. Binds the metro and nonmetro workbooks into one `staging.bls_oews_metro_nonmetro` table while preserving `source_area_scope`.
8. Validates uniqueness at the published source grain before writing the tables.

What it intentionally does **not** do yet:
- no conversion of wage or employment strings into numeric columns
- no coercion of `*`, `**`, `#`, or `~` note values
- no geography normalization from OEWS `area` codes into canonical `state_fips` or `cbsa_code`
- no filtering to cross-industry summary rows beyond what the workbook already publishes
- no dropping of territorial rows

That is the right staging behavior for this family. Silver should own type coercion, geography normalization, and any analytical pruning.

## Column Meanings

### Geography fields
- `area`: BLS source geography code. Examples:
  - state workbook uses codes like `01`, `06`, `72`
  - metro workbook uses 5-digit MSA-style codes like `10180`
  - nonmetro workbook uses 7-digit nonmetro area codes like `0100001`
- `area_title`: published geography name.
- `area_type`: BLS geography type code in the workbook.
  - `2` = state/DC
  - `3` = territory in the state workbook
  - `4` = metropolitan area
  - `6` = nonmetropolitan area
- `prim_state`: BLS primary state or territory abbreviation for the area.

### Industry and ownership fields
- `naics`: source industry code. In the current first-pass files, the cross-industry rows use `000000`.
- `naics_title`: source industry label, typically `Cross-industry` in the current workbooks.
- `i_group`: source indicator of industry grouping level. The cross-industry rows currently publish `cross-industry`.
- `own_code`: source ownership code. The workbook notes this as the ownership type associated with the estimate.

### Occupation fields
- `occ_code`: Standard Occupational Classification code.
- `occ_title`: published SOC title.
- `o_group`: source occupation-group indicator. This distinguishes major groups from detailed occupations and all-occupation totals.

### Employment and concentration fields
- `tot_emp`: estimated employment for the occupation in the geography.
- `emp_prse`: percent relative standard error for the employment estimate.
- `jobs_1000`: jobs in the occupation per 1,000 jobs in the geography.
- `loc_quotient`: occupational employment concentration relative to the U.S.
- `pct_total`: percent of industry employment in the occupation.
- `pct_rpt`: percent of establishments reporting the occupation.

### Wage fields
- `h_mean`: mean hourly wage.
- `a_mean`: mean annual wage.
- `mean_prse`: percent relative standard error for the mean wage estimate.
- `h_pct10`, `h_pct25`, `h_median`, `h_pct75`, `h_pct90`: hourly wage distribution percentiles.
- `a_pct10`, `a_pct25`, `a_median`, `a_pct75`, `a_pct90`: annual wage distribution percentiles.
- `annual`: conversion or availability note for annual wages.
- `hourly`: conversion or availability note for hourly wages.

### Provenance fields we add
- `release_year`: release year of the staged workbook.
- `source_geo_family`: broad workbook family, currently `state` or `metro_nonmetro`.
- `source_workbook`: exact workbook filename inside the ZIP.
- `source_area_scope`: normalized scope label we derive for staging QA:
  - `state`
  - `territory`
  - `metro`
  - `nonmetro`

## Provider Notes We Preserve In Staging

The workbook field-description sheet includes important note conventions:
- `*`: wage estimate not available
- `**`: employment estimate not available
- `#`: wage is top-coded at or above the published upper threshold
- `~`: the percent of establishments reporting the occupation is below the publishable threshold

Because the current script keeps the source columns as text, those note markers survive staging exactly as published.

## Recommended Keep Vs Drop Path For Silver

### Keep in staging exactly as-is

These should remain in the staging contract even if Silver narrows later:
- `area`, `area_title`, `area_type`, `prim_state`
- `naics`, `naics_title`, `i_group`, `own_code`
- `occ_code`, `occ_title`, `o_group`
- `tot_emp`, `emp_prse`, `jobs_1000`, `loc_quotient`, `pct_total`, `pct_rpt`
- all wage fields
- `annual`, `hourly`
- `release_year`, `source_geo_family`, `source_workbook`, `source_area_scope`

Why:
- the table is still small enough that source fidelity is cheap
- note-marked text values need to survive until we decide the Silver coercion rules
- `o_group`, `i_group`, and `own_code` are part of the provider’s row semantics, even if first-pass Silver filters most of them

### Keep for first-pass Silver

For the first modeled Silver table, the core keep set should likely be:
- geography:
  - `area`, `area_title`, `area_type`, `prim_state`, `source_area_scope`
- occupation keys:
  - `occ_code`, `occ_title`, `o_group`
- core analytical metrics:
  - `tot_emp`
  - `jobs_1000`
  - `loc_quotient`
  - `h_mean`, `a_mean`
  - `h_pct10`, `h_pct25`, `h_median`, `h_pct75`, `h_pct90`
  - `a_pct10`, `a_pct25`, `a_median`, `a_pct75`, `a_pct90`
- uncertainty / release notes:
  - `emp_prse`
  - `mean_prse`
  - `annual`
  - `hourly`
- provenance:
  - `release_year`
  - `source_workbook`

### Likely drop from first-pass Silver, but keep in staging

These are good candidates to retain only in staging unless a downstream use case appears:
- `naics`, `naics_title`, `i_group`
  - rationale: the current files are cross-industry; these are mostly constant in the first pass
- `own_code`
  - rationale: useful as a source-semantic check, but not likely central to the initial cross-industry Silver mart
- `pct_total`
  - rationale: only useful when the industry dimension matters
- `pct_rpt`
  - rationale: useful QA / quality context, but probably not a headline analytical field in the first Silver release
- `source_geo_family`
  - rationale: staging provenance only; `source_area_scope` is the more decision-relevant downstream field

## Lineage
- [`foundations/etl/staging/get_bls_oews.R`](../../../etl/staging/get_bls_oews.R) downloads the live `2025` state and metro/nonmetro OEWS ZIP files, extracts the workbook members, standardizes the headers, adds minimal provenance, validates the published row grain, and writes the two staging tables documented here.
- The source-spec rationale and first-pass modeling decisions live in [`../../sources/source__bls_oews.md`](../../sources/source__bls_oews.md).

## Data Quality Notes
- Verify uniqueness at:
  - `release_year + area + occ_code` for `staging.bls_oews_state`
  - `release_year + source_area_scope + area + occ_code` for `staging.bls_oews_metro_nonmetro`
- Preserve all note markers in the text-valued estimate fields until Silver defines coercion rules.
- State rows intentionally include `3` territorial areas in addition to the `50` states plus `DC`.
- Metro and nonmetro rows are staged together because the source publishes them in separate workbooks with the same schema and both are analytically relevant in the absence of county OEWS coverage.
- The current staged row counts imply that not every geography publishes every occupation, which is expected OEWS behavior.

## Known Gaps / To-Dos
- Write the companion Silver contract after we decide the exact coercion policy for `*`, `**`, `#`, and `~`.
- Add a managed lookup or explicit rule for translating OEWS metro `area` codes into canonical Foundations `cbsa_code`.
- Decide whether first-pass Silver should retain territorial state-workbook rows or intentionally narrow to the current domestic platform geography policy.
