# Source Spec: HUD

## 1. Overview

- Source: U.S. Department of Housing and Urban Development
- Access pattern in current Foundations coverage: workbook downloads plus local raw files
- Primary dependency: public HUD files plus local raw-data and DuckDB paths
- Scope in Foundations: current HUD coverage includes CHAS affordability tabulations and FMR / SAFMR rent schedules. CHAS now feeds a documented Silver burden table, while FMR and rent50 feed analytical Silver wide tables.
- Documentation goal: this file is the provider-level spec for HUD as it is currently represented in Foundations.

## 2. Coverage Matrix

This source spec covers the HUD topic groups currently documented in the data dictionary.

| Topic group | Staging family contracts | Silver outputs |
| --- | --- | --- |
| CHAS | [../layers/staging/staging__hud_chas.md](../layers/staging/staging__hud_chas.md) | `silver.hud_chas_burden` |
| FMR / SAFMR | [../layers/staging/staging__hud_fmr.md](../layers/staging/staging__hud_fmr.md) | `silver.hud_fmr_wide`, `silver.hud_rent50_wide` |

## 3. Source Contract

- Provider: U.S. Department of Housing and Urban Development
- Retrieval interface in current coverage: workbook downloads for FMR / SAFMR and local source files for CHAS
- Common request pattern: provider-specific annual files are cached to the raw-data directory and then normalized into staging
- Common geography pattern:
  CHAS covers state, county, and place;
  FMR covers county and ZIP at ingest time, with CBSA and state added in Silver
- Common time pattern:
  CHAS uses source-specific yearly tabulations;
  FMR / rent50 are currently modeled for 2023 in the documented Silver outputs

Shared source references:
- [../../etl/staging/SOURCES.md](../../etl/staging/SOURCES.md)
- [../../etl/staging/get_hud_chas.R](../../etl/staging/get_hud_chas.R)
- [../../etl/staging/get_hud_fmr.R](../../etl/staging/get_hud_fmr.R)

| Topic group | Source files / subject area | Staging ingest entrypoint |
| --- | --- | --- |
| CHAS | Comprehensive Housing Affordability Strategy tabulations by geography and demographic segment | [../../etl/staging/get_hud_chas.R](../../etl/staging/get_hud_chas.R) |
| FMR / SAFMR | county FMR, ZIP SAFMR, and county 50th-percentile rent schedules | [../../etl/staging/get_hud_fmr.R](../../etl/staging/get_hud_fmr.R) |

## 4. Staging Shape

Common HUD staging pattern:
- one family contract per HUD topic group
- one materialized table per source slice
- source-aligned staging rather than a shared provider-wide schema

| Topic group | Staging family | Coverage shape |
| --- | --- | --- |
| CHAS | `staging__hud_chas` | state, county, and place tables with long-format affordability records keyed by geography, variable, and year |
| FMR / SAFMR | `staging__hud_fmr` | county FMR, ZIP SAFMR, and county rent50 staging tables with one row per geography-period source record |

Shared staging notes by topic:
- CHAS shared columns center on `geoid`, `variable`, `estimate`, demographic segment columns, `year`, and `geo_level`.
- FMR shared columns center on `hud_area_code`, `hud_area_name`, and `period`, with separate bedroom-rent fields by source slice.

## 5. Staging To Silver

Common HUD handoff pattern in current coverage:
1. Preserve topic-specific staging structures rather than forcing a single provider schema.
2. For FMR / rent50, join county rows to the county-to-CBSA crosswalk.
3. Compute population-weighted aggregates for derived CBSA and state rows.
4. Standardize geography names and materialize one Silver wide table per rent schedule.
5. For CHAS, standardize the staged county and place rows into a documented Silver burden table, then derive CBSA rows by rolling county CHAS counts through the county-to-CBSA crosswalk.

| Topic group | Silver handoff | Special path |
| --- | --- | --- |
| CHAS | `staging__hud_chas` -> `silver.hud_chas_burden` | county and place rows are standardized first, then county CHAS counts are rebased to CBSA; tenure and income bands are preserved, while household-type detail is aggregated away after segment totals are reconstructed |
| FMR / SAFMR | `staging__hud_fmr` -> `silver.hud_fmr_wide` and `silver.hud_rent50_wide` | county FMR and county rent50 are rebased to CBSA and state with population-weighted averages; ZIP SAFMR remains ZIP-only in the FMR wide output |

## 6. Transformation Notes

| Topic group | Silver-table role | Derivation logic |
| --- | --- | --- |
| CHAS | segmented affordability burden table | staging preserves long affordability records segmented by tenure, household type, income band, and cost burden; Silver rolls those into one row per geography + tenure + income band with burden counts and rates, including derived CBSA rows from county sums |
| FMR / SAFMR | geography-standardized annual rent benchmarks | county rows pass through directly; state and CBSA rows use population-weighted averages by bedroom count; ZIP rows are mapped from SAFMR source fields into the FMR wide schema |

Additional HUD-wide transform notes:
- `silver.hud_fmr_wide` combines county FMR, derived CBSA and state FMR, and ZIP SAFMR in one table.
- `silver.hud_rent50_wide` is county / CBSA / state only and does not include a ZIP slice.
- The current HUD FMR ingest script defines a wider year range variable, but the concrete downloads in the script are hard-coded to 2023 files.

## 7. Data Quality Expectations

| Topic group | Non-boilerplate checks worth preserving |
| --- | --- |
| CHAS | verify uniqueness at `geoid + variable + year + geo_level` plus relevant segment columns; confirm demographic-segment metadata still reconciles with the source workbook mapping |
| FMR / SAFMR | review the duplicate-key issue in both `silver.hud_fmr_wide` and `silver.hud_rent50_wide`; confirm weighted state and CBSA rents are derived from county values rather than averaging already-aggregated figures; watch HUD area-code to county mapping drift over time |

## 8. Operational Notes

- Staging entrypoints:
  [../../etl/staging/get_hud_chas.R](../../etl/staging/get_hud_chas.R),
  [../../etl/staging/get_hud_fmr.R](../../etl/staging/get_hud_fmr.R)
- Silver model entrypoint for modeled rent outputs:
  [../../etl/silver/hud_fmr_silver.R](../../etl/silver/hud_fmr_silver.R)
- Required local environment wiring:
  `DATA` for cached HUD files and `DB_PATH` for DuckDB materialization
- Important implementation wrinkle:
  CHAS now continues into Silver as a documented burden table, while FMR / rent50 continue into their rent benchmark tables
- Current documentation pattern:
  staging remains family-contract based, Silver remains table-contract based, and this file sits above both as the provider-level spec

## 9. Known Gaps

- CHAS Silver currently covers CBSA, county, and place rows; state and tract staging slices remain outside the documented Silver contract.
- The FMR family contract groups county FMR, ZIP SAFMR, and county rent50 together, but the downstream modeling paths are not identical.
- The current Silver HUD rent tables both show duplicate provisional keys and need contract hardening.

---

## 10. Architecture Decisions

**Decision date:** 2026-06-02

### CHAS Silver contract
Model CHAS into a documented Silver table: `silver.hud_chas_burden` at CBSA, county, and place grain, preserving all income bands (30/50/80/100% AMI plus `>100%`) and tenure splits (`all`, `owner`, `renter`) for analytical flexibility.

### CHAS Gold contract
Three columns added to `gold_affordability_wide` — the standard HUD/HCD reporting tiers, directly comparable to published benchmarks:

- `pct_cost_burdened` — all households spending >30% of income on housing
- `pct_severely_cost_burdened` — all households spending >50%
- `pct_renter_severely_cost_burdened` — renter households spending >50%

Income-band detail remains in Silver for deep-dive work. These three columns cover the severity gradient without overloading the Gold table.
