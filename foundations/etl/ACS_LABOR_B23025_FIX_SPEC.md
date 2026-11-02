# ACS Labor B23025 Mapping Fix: Spec

**Status:** Done
**Updated:** 2026-10-23

> **Outcome, 2026-10-23.** Fixed and rebuilt; all acceptance checks pass.
> - **US 2024 (ACS 2020–24):** `unemp_rate` 0.0523 (8,902,365 / 170,199,520 civilian labor force); `emp_pop_ratio` 0.597, against 1 − `lfpr` = 0.365.
> - **Identities:** all three hold on every non-null row at every level. `lfpr` and the industry shares are unchanged.
> - **NY tract median `unemp_rate`, 2024:** 0.054 (was 0.40). The `gold.intelligence_zone_inputs` tract median is 0.045 (was 0.442).
> - **ACS vs LAUS 2020–24 average:** 51 of 52 states within 2 points (the exception is Puerto Rico, 10.7 vs 6.4). 79% of counties are within 2 points; the misses are mostly counties with under 25k in the civilian labor force, Puerto Rico and tribal-area counties. Only 7 of 347 counties of 100k+ miss.
> - **Gold:** county, CBSA and state rows of `gold.economics_labor_wide` are unchanged. Only `employed`, `unemployed`, `jobs_to_pop_ratio`, `pct_unemployment_rate` and `unemployment_rate_change_1yr` changed, on tract and ZCTA rows.
> - **Deviation:** the four legacy tract staging tables (`acs_labor_tract_fl/ga/nc/sc`) were not re-pulled, and still carry the old mapping. Nothing reads them.
> - **Before snapshot:** `foundations/etl/data/snapshots/acs_labor_fix_2026-10-22/before/`, which is gitignored.

A spec for one agent session. Fix the ACS B23025 variable mapping that corrupts employment and unemployment fields, rebuild the affected Foundations tables, and prove the numbers are right. A second spec picks up after this one: [PHASE7_LABOR_FIX_RERUN_SPEC.md](../../exploration/intelligence_framework/phase_7_zone_methodology/PHASE7_LABOR_FIX_RERUN_SPEC.md), which reruns the Phase 7 tract clusters. **Don't start Phase 7 work here.**

## Read first

1. `AGENTS.md` and `docs/CONVENTIONS.md`
2. `foundations/README.md` and `foundations/etl/README.md`: environments, `DB_PATH`, run order
3. `foundations/etl/staging/get_acs_labor.R`: the bug
4. `foundations/etl/silver/acs_labor_silver.R`: derives `unemployed`, `unemp_rate`, `emp_pop_ratio`, `unemp_rate_civ`
5. `foundations/etl/gold/gold_economy_labor.sql`: uses the ACS fields for tract and ZCTA rows only
6. `foundations/etl/gold/gold_intelligence_zone_inputs.sql`: carries `pct_unemployment_rate` to Phase 7
7. Data dictionary entries: `foundations/data_dictionary/layers/staging/staging__acs_labor.md`, `silver/silver__labor_kpi.*`, `silver/silver__labor_base.*`, `gold/gold__economics_labor_wide.md`

## The bug

[get_acs_labor.R:46-51](staging/get_acs_labor.R) maps ACS table B23025 ("Employment Status for the Population 16 Years and Over") one step off for three fields:

| Field | ACS meaning of the code used | Correct code |
|---|---|---|
| `pop_16plus = B23025_001` | Total | `_001` (correct) |
| `in_labor_force = B23025_002` | In labor force | `_002` (correct) |
| `in_lf_civilian = B23025_003` | Civilian labor force | `_003` (correct) |
| `in_lf_armed_forces = B23025_004` | **Civilian LF: Employed** | `_006` |
| `not_in_labor_force = B23025_005` | **Civilian LF: Unemployed** | `_007` |
| `employed = B23025_007` | **Not in labor force** | `_004` |

`acs_labor_silver.R` then derives `unemployed = in_labor_force - employed`. With `employed` holding not-in-labor-force, every downstream rate is wrong.

**Evidence (2026-10-22):** in `silver.labor_kpi`, `emp_pop_ratio` equals exactly `1 - lfpr` in every row (US 2024: 0.3653 = 1 − 0.6347). US `unemp_rate` is 0.4245, and NY tract medians run 0.40–0.45. Example: tract 36001000202, 2024 has `pop_16plus` 1,683, `in_labor_force` 1,405 and `employed` 278 (= 1,683 − 1,405). Found during Albany Lens 1 exploration ([build plan](../../metro-deep-dive-program/issues/ny_state/albany/ALBANY_LENS1_VISUALS_BUILD_PLAN.md), Findings).

## Blast radius (verify; this is the starting list)

- **`silver.labor_kpi`, every geography level:** `employed`, `unemployed`, `unemp_rate`, `emp_pop_ratio`, `unemp_rate_civ`, `in_lf_armed_forces`, `not_in_labor_force`. `lfpr` is **correct** (it uses `in_labor_force / pop_16plus`).
- **`silver.labor_base`:** whatever raw columns it carries from staging.
- **`gold.economics_labor_wide`, tract and ZCTA rows only:** `employed`, `unemployed`, `pct_unemployment_rate`, `jobs_to_pop_ratio`, its lags, and `unemployment_rate_lag1`. County, CBSA and state rows take these from BLS LAUS and are correct. Confirm by diffing before and after.
- **`gold.intelligence_zone_inputs.pct_unemployment_rate`** (tract), which is a Phase 7 clustering input. Rebuild the table here; the cluster rerun is the next spec's job.
- **`gold.economics_industry_wide`** reads `silver.labor_kpi` but only its industry shares (C24030). Confirm it is unaffected.
- **Search for other readers** of the affected columns across `foundations/`, `metro-deep-dive-program/`, `area-explorer/`, `public-cbsa-panel/` and `exploration/` (the semantic layer catalogs list `pct_unemployment_rate`, `emp_pop_ratio`, `jobs_to_pop_ratio`). List each one and whether it reads tract or ZCTA rows or ACS-sourced values.
- **ZCTA oddity to explain, not necessarily fix:** ZCTA rows for 2013+ have only ~323 NY rows and different medians from 2012. Note whether it relates.

## Required work

1. **Fix the mapping** in `get_acs_labor.R`: `employed = B23025_004`, `unemployed = B23025_005`, `in_lf_armed_forces = B23025_006`, `not_in_labor_force = B23025_007`. Pull `unemployed` directly instead of deriving it, unless there's a documented reason to derive it. If you keep the derivation, base it on the civilian labor force (`_003 − _004`), so armed forces aren't counted as unemployed.
2. **Update `acs_labor_silver.R`** to the corrected fields. `unemp_rate` = unemployed / civilian labor force (the BLS and ACS convention). Keep `lfpr` as is.
3. **Re-pull and rebuild,** in pipeline order. The staging pull needs the Census API key; follow `foundations/etl/README.md`. Order: staging ACS labor → `acs_labor` silver → `gold_economy_labor` → `gold_intelligence_zone_inputs` → any mart that copies these fields (from the consumer search).
   - **Stop before the first warehouse write.** Report the planned commands and the tables to be replaced, then wait for Dan.
   - The warehouse is shared, and a writer needs every other connection closed: check for open marimo kernels (`lsof` on the DuckDB file).
4. **Validate** (the acceptance checks below). Keep a before snapshot of the affected columns (e.g. a parquet export of US, NY-state, Albany-county and 10 sample-tract rows) so before and after can be diffed.
5. **Update docs:**
   - The data dictionary entries above: definitions, and a dated note on the fix.
   - Semantic layer catalog formulas if they name the wrong fields.
   - A one-line entry in `foundations/ROADMAP.md` or its changelog, per `docs/CONVENTIONS.md`.

## Acceptance checks

| Check | Expect |
|---|---|
| US 2024 (ACS 2020–24) `unemp_rate` | about 0.05 (published ACS 5-year US unemployment is in the 5% range; quote the exact published figure) |
| US 2024 `emp_pop_ratio` | about 0.60, and no longer equal to `1 - lfpr` |
| `employed + unemployed + armed forces = in_labor_force` | every row, within rounding |
| `employed + unemployed = in_lf_civilian` | every row |
| `in_labor_force + not_in_labor_force = pop_16plus` | every row |
| State and county ACS `unemp_rate` vs BLS LAUS (same year) | within about 2 points for nearly all; list the outliers |
| NY tract median `unemp_rate`, 2024 | about 0.04–0.06 (was 0.40) |
| `lfpr` | unchanged before vs after |
| `gold.economics_labor_wide`, county/CBSA/state rows | unchanged before vs after |
| `gold.intelligence_zone_inputs.pct_unemployment_rate` | tract median about 0.04–0.06 |

## Out of scope

- Rerunning Phase 7, rescoring zones or reloading zone marts (next spec)
- Changing BLS LAUS handling or the LAUS/ACS split by geography level
- Refactoring the labor pipeline beyond the fix

## Report back

- **What changed:** files, and the tables replaced with row counts.
- **The acceptance table** with actual values.
- **The consumer list:** each reader and whether it was affected.
- **Anything unexpected,** e.g. the ZCTA oddity.
- **A ready-to-run handoff line** for the Phase 7 rerun spec: the timestamp of the rebuilt `gold.intelligence_zone_inputs`, and confirmation that it carries the fixed rate.
