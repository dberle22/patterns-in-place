# LODES Jobs Universe: Explicit Column Names: Spec

**Status:** Active
**Updated:** 2026-10-23

A spec for one agent session. Make every LODES WAC/RAC count and ratio in the warehouse say which jobs it counts, **private (JT02)** or **all (JT00)**. Then audit every reader so each analysis chooses one on purpose. Today `jobs_total` and `workers_total` are private-only, and their names read as totals. Several analyses used them as all jobs without saying so.

## Read first

1. `AGENTS.md`, `docs/CONVENTIONS.md`
2. `foundations/README.md`, `foundations/etl/README.md` (environments, `DB_PATH`, run order)
3. `foundations/etl/staging/get_lehd_lodes.R` §3: the design choice. The wide tables are a JT02 surface; JT00 adds only the headline total (`C000_all`).
4. `foundations/etl/silver/lehd_lodes_silver.R` (lines ~139–142, ~525–526, ~627–628): `total` ← `C000` → `jobs_total` / `workers_total`; `total_all` ← `C000_all` → `jobs_all_total` / `workers_all_total`
5. `foundations/etl/gold/gold_economics_lodes.sql`: `jobs_to_workers_ratio`, `jobs_minus_workers` etc. are computed from the **private** columns (lines ~185–188); the `jobs_all_*` ratios (lines ~219–224) are explicitly named
6. `foundations/etl/gold/gold_intelligence_zone_inputs.sql` (lines ~189–191): Phase 7's `jobs_per_resident` = gold `jobs_to_workers_ratio` (private); `pct_jobs_high_wage` and `pct_jobs_professional_services` are JT02 composition shares
7. Data dictionary: `silver__lehd_lodes_wac.*`, `silver__lehd_lodes_rac.*`, `gold__economics_lodes_wide.*`, `sources/source__lehd_lodes.md`; semantic layer `table_catalog.yml`, `metric_catalog.yml`
8. `metro-deep-dive-program/issues/VISUALS_BUILD_RULES.md`, rule R34 (how this was found)

## Why

Found 2026-10-22 during Albany Lens 1 ([build plan](../../metro-deep-dive-program/issues/ny_state/metro_deep_dives/albany/part_1/ALBANY_LENS1_VISUALS_BUILD_PLAN.md), Findings). In every county, WAC `jobs_total` equals LODES OD private jobs exactly. For Albany city that's 72.1k "jobs" against 131.8k in all, because 45% of the city's jobs are public. Q2's job centers and Q6's place jobs read `jobs_total`, and neither spec said so. Albany's largest job tract (downtown, 71% public) looked like a quarter of its real size.

## Required work

### 1. Name the universe in the warehouse (silver and gold)

- **Add explicit columns** in `silver.lehd_lodes_wac`, `silver.lehd_lodes_rac` and `gold.economics_lodes_wide`. Proposed: `jobs_private` and `jobs_all`; `workers_private` and `workers_all`; `jobs_private_to_workers_private_ratio` (or a shorter name you propose) next to the existing `jobs_all_to_workers_all_ratio`; and the same for the minus/diff and inverse ratios.
- **Keep the old names as deprecated aliases for one cycle:** `jobs_total`, `workers_total`, `jobs_all_total`, `workers_all_total`, `jobs_to_workers_ratio` and the other unprefixed ratios. Values unchanged. Mark them deprecated in the data dictionary with the removal condition: every reader migrated.
- **Composition fields** (`pct_jobs_*`, age, earnings, education, industry counts) are JT02-only by design. Propose one of two, and say why:
  - (a) document the universe at table and field level and leave the names, or
  - (b) prefix them as private.

  Default to (a) unless renaming is cheap and safe. Either way, the dictionary must say "private jobs (LODES JT02)" on every one.
- **Describe all of it** in the data dictionary and semantic layer: definitions, the universe, a dated note.

### 2. Audit every reader

Start from this inventory (2026-10-23; re-search to confirm, including `jobs_to_workers_ratio`, `jobs_minus_workers` and `economics_lodes_wide`):

| Reader | Uses | Question to answer |
|---|---|---|
| `analyses/explanation/q2_job_proximity/` (builder, 6 queries, 3 notebooks) | `jobs_total`, `workers_total` | Private job centers on purpose? Albany shows all jobs changes the centers (exploration notebook Q2a) |
| `analyses/explanation/q6_one_metro/sql/q6_place_profile.sql`, `q6_candidate_evidence.sql` | `jobs_total` | Place jobs presented as "workplace jobs" |
| `analyses/explanation/regional_role/` (notebook, spec, `regional_role_jobs_workers.sql`) | `gold.economics_lodes_wide` totals and ratios | Jobs vs workers balances: private or all? |
| `analyses/position/internal_structure/queries/internal_structure_d3_job_centers.sql` | `jobs_total` | |
| `analyses/explanation/catchment/` (notebook, `site_intelligence/SITE_INTELLIGENCE_CLIENT_BRIEF.py`, `site_bundle_adapter.py`) | `jobs_total`, `workers_total` | **Shipped client work (PR #7).** What did the brief present as "jobs"? Report what was shown and whether a correction note is needed. Don't edit the delivered brief; report to Dan. |
| `exploration/intelligence_framework/phase_7_zone_methodology/` (config, tract frame build, validator, app) | `jobs_per_resident` (private), high-wage and professional shares (private) | Note only (see Coordination) |
| `issues/ny_state/metro_deep_dives/albany/` | already on all jobs where it matters | No change |
| Semantic layer, data dictionary | | Updated in step 1 |

For each reader, record: the columns used, what the analysis claims (all jobs or private), whether the claim matches the data, and the **recommended choice**: private on purpose, switch to all, or show both. **Don't change analysis logic in this session**, except switching a reader from a deprecated alias to the explicit name *with the same values*. Changing which universe an analysis uses is that analysis's decision. List them for Dan.

### 3. Guard against regressions

- Add a contract check to the LODES silver build: `jobs_all >= jobs_private` for every row, and the county-level `jobs_private` sum equal to LODES OD `jobs_private` for the same county and year. The county OD check is the reconciliation that found this.
- Add a one-line note to `docs/GLOSSARY.md` (or the LODES source doc): "LODES jobs: say private (JT02) or all (JT00). The warehouse default composition fields are private."

## Coordination

- **A Phase 7 rerun is in progress** (`exploration/intelligence_framework/phase_7_zone_methodology/PHASE7_LABOR_FIX_RERUN_SPEC.md`). **Don't change the values or names that `gold.intelligence_zone_inputs` reads, and don't rebuild that table, until the rerun's review is written.** Aliases keep it working. Whether Phase 7 should cluster on all-jobs `jobs_per_resident` is a *separate* future rerun question. Record it in the audit table; don't act on it.
- **Warehouse writes need every other connection closed** (marimo kernels hold the DuckDB file; check with `lsof` on it). **Stop before the first write**: report the planned DDL and rebuild commands, and wait for Dan.

## Acceptance checks

| Check | Expect |
|---|---|
| New explicit columns exist in silver WAC/RAC and gold `economics_lodes_wide` | yes |
| Old names still resolve, with identical values | every row |
| `jobs_all >= jobs_private` (WAC), `workers_all >= workers_private` (RAC) | every row |
| County `jobs_private` sum = OD county `jobs_private`, 2023 | every county (Albany County: 173,555) |
| Albany city tracts (29, population weight ≥ 0.5) | `jobs_private` 72,080; `jobs_all` 131,841 |
| `gold.intelligence_zone_inputs` | unchanged (row count and checksum of the LODES-derived columns) |
| Dictionary entries | universe stated on every LODES count, ratio and composition field |

## Out of scope

- Changing which universe any analysis uses (the audit only recommends)
- Rerunning Phase 7, Q2 or any analysis mart
- Dropping the deprecated aliases (a later cleanup, once readers have migrated)
- LODES OD tables (their columns, `jobs_all` and `jobs_private`, are already explicit)

## Report back

- **Columns added, and aliases kept.**
- **The audit table,** with a recommendation per reader.
- **The Site Intelligence finding:** what the client brief showed.
- **The acceptance table,** with actual values.
- **The cleanup checklist** for removing the aliases later.
