# IRS Migration Direction Fix: Spec

**Status:** Done
**Updated:** 2026-10-26
**Found in:** Albany Lens 1 exploration, Q4i (in-migration from the rest of New York)

> **Part C, 2026-10-26 (Dan: ship the IRS fix alone; hold the GDP refresh for a broader GDP and clustering refresh).**
> - [x] Promotion runs with the three BEA GDP Opportunity inputs (and the two GDP trajectory series) held at their June mart values, so the only input change is IRS. With GDP frozen, every control run reproduces its current mart exactly (Character, Opportunity, cross-frame, all four trajectory tables).
> - [x] Published cluster names carried forward by cluster ID (membership verified identical first). With GDP frozen, the Opportunity namer would have swapped Superstar Knowledge Capitals and Emerging Momentum Markets; cross-frame names already matched.
> - [x] C12 promoted: canonical `outputs/` replaced (previous copies in each phase's `outputs_irs_fix_2026-10/canonical_before/`); `load_character_scores.R`, `load_opportunity_scores.R`, `load_cross_frame_scores.R` run (396 rows each; clusters, names and peers unchanged; IRS fields exactly negated). Trajectory tables loaded from the reviewed run with `irs_fix_rerun_engine.py promote`, **not** `build_time_series_engine.py`, which would have published the GDP refresh; only IRS rows changed. `mart_benchmarking` rebuilt (only the 2 IRS metrics and the 3 Intelligence percentile ranks changed); `mart_area_explorer` rebuilt (IRS and Intelligence fields only); `mart_explanation_q1.supply_demand_base` rebuilt (IRS only). **Not rebuilt:** `mart_explanation_q1.tract_2020_harmonized_counts`, which has no IRS input; a rebuild would change about 20,000 tracts from unrelated drift.
> - [x] C13 Q1: the five `cbsa_county_context.csv` files re-exported (only `irs_net_migration_rate` changed, exactly negated); `national/cbsa_trend.csv` was written by an older query version, so only its IRS column was replaced. The Q1 composite doesn't use IRS (demand = five-year population growth). Regional role notebook runs headless; its audit has a dated note.
> - [x] C14 Albany: both workarounds removed; the guard now fails if the reversal returns. Q4i and the Q4a scorecard are row-for-row identical to the workaround versions (Albany +1,478 people a year net, 2018–22). Both notebooks run headless.
> - [x] C15 docs: data dictionary (staging, silver, gold, source), `intelligence_catalog.yml`, `table_catalog.yml`, phase READMEs, engine NOTES, `foundations/ROADMAP.md` (fix done; GDP and clustering refresh added), N8 unblocked.
> - **Written claims affected:** none found. No drafted or published piece quotes an IRS value, an Intelligence score or percentile, or a trajectory signal (the Albany Lens 1 draft mentions IRS only in review notes; Richmond's IRS sections are unbuilt).
> - **Follow-up:** the GDP and clustering refresh in `foundations/ROADMAP.md`. Until then, rerunning Phase 4/5 or `build_time_series_engine.py` as is publishes the GDP refresh and the rule-based names.

> **Part B, 2026-10-26.** Review: [IRS_FIX_RERUN_REVIEW.md](../../exploration/intelligence_framework/IRS_FIX_RERUN_REVIEW.md).
> - [x] B7–B9 control and fixed runs for Phases 2, 4, 5 and the trajectory engine (the engine, not the legacy `phase_6_trajectory/` R code, builds the trajectory marts), via harnesses that leave the phase code unchanged
> - [x] B8 control reproduction: Character passes; Opportunity, cross-frame and trajectory fail because of a BEA GDP refresh (county GDP now through 2024), not IRS
> - [x] B10 review: clusters and peers 100% unchanged; scores move as expected; trajectory unaffected (IRS metrics are `insufficient_history` at the 2023 end vintage)
> - [x] Dan: hold the GDP refresh (promote IRS only); published names carried forward

> **Progress, 2026-10-26.**
> - **Confirmed** against the raw files: the inflow file is keyed by Y2 (destination), and inflow and outflow files agree that Manhattan → Miami-Dade is 2,676 people in 2022.
> - **Root cause:** the script's single-year test block read `DATA/demographics/raw/irs/inflow2122.csv`, which is byte-identical to `outflow2122.csv` (an outflow file, keyed by Y1). The mapping was written against that file and carried into the loops, which read the real inflow files. The test block now reads `countyinflow{code}.csv`, the same file as the loop. The mislabeled raw file is still on disk.
> - **Correction:** the stored New York 2022 net is +222,702, not +412,599 (fixed in the evidence and acceptance tables below).
> - [x] A1 before snapshot: `foundations/etl/data/snapshots/irs_direction_fix_2026-10/before/` (18 parquet files)
> - [x] A2 staging mapping fixed (county test block, county loop, state loop, summary block); test block column names fixed (it referenced `y2_` name columns the inflow file doesn't have)
> - [x] A3 silver name fallback keyed to origin
> - [x] A5 check added: `gold/check_irs_migration_direction.sql`, in `create_DB.R` and `pipeline_manifest.yml` (plus the missing `irs_migration_staging` step)
> - [x] Dry run (read-only, outputs to scratch): silver summary in/out exactly swapped and net exactly negated on all 42,575 rows; all 654,225 flows match their reversed old rows; names unchanged
> - [x] A4 rebuilt (Dan approved): `staging.irs_inflow_migration_county` 627,182 rows, `staging.irs_inflow_migration_state` 28,050, `silver.irs_migration_flows` 654,225, `silver.irs_migration_summary` 42,575, `gold.migration_wide` 1,891,571. Dropped `staging.irs_migration_state` (an exact duplicate of the state inflow table, with no readers).
> - [x] Direction check passes: NY State net −248,305 / −261,785 / −222,702 (2020–22); Manhattan → Miami-Dade 2,676 vs 1,100; gold NY 2022 `irs_net_migration` −108,586 households
> - [x] A6 gold diff, all 1,891,571 rows matched: in/out and AGI in/out exactly swapped, `irs_net_migration`, `irs_net_migration_rate` and `irs_net_agi` exactly negated, churn identical, row count identical. Albany (10580) 2022: 8,623 in, 7,600 out, net +1,023 households.
> - [x] Inflow vs outflow file, 2022: 54,522 of 54,522 county pairs equal
> - [ ] Delete the mislabeled `DATA/demographics/raw/irs/inflow2122.csv` (Dan approved; agent permission blocked it, left for Dan)
> - **Interim state:** the marts and the Albany notebook still carry the reversed values; the Albany `irs_flows_reversed` guard now fails. Both are fixed in Parts B and C.

A spec for one agent session, in three parts: **A** fixes the IRS staging mapping and rebuilds Foundations; **B** reruns the Intelligence Framework phases that use IRS inputs and compares before and after; **C** refreshes the downstream marts and saved outputs, and removes the Albany workaround. There are two stops for Dan: before the first warehouse write (end of A3), and before the Intelligence marts are overwritten (end of B).

## Read first

1. `AGENTS.md` and `docs/CONVENTIONS.md`
2. `foundations/README.md` and `foundations/etl/README.md`: environments, `DB_PATH`, run order
3. `foundations/etl/staging/get_irs_migration.R`: the bug
4. `foundations/etl/silver/irs_migration_silver.R`: builds the flows and the county, CBSA and state summaries
5. `foundations/etl/gold/gold_migration_wide.sql`: the `irs_*` fields
6. The two earlier fix specs, for the pattern this one follows: [ACS_LABOR_B23025_FIX_SPEC.md](ACS_LABOR_B23025_FIX_SPEC.md) and [PHASE7_LABOR_FIX_RERUN_SPEC.md](../../exploration/intelligence_framework/phase_7_zone_methodology/PHASE7_LABOR_FIX_RERUN_SPEC.md)
7. `exploration/intelligence_framework/README.md` and the Phase 2, 4, 5 and 6 READMEs (run order, output folders, loaders)

## The bug

The script reads the IRS SOI **inflow** files (`countyinflowYYYY.csv`, `stateinflowYYYY.csv`). In those files each row is keyed by the county or state people moved **to** (`y2_`, where filers lived in the later year), and names the place they moved **from** (`y1_`, the earlier year; `y1_countyname` and `y1_state_name` are the origin's names). The script maps them the other way round, in three places:

| Place | Lines | Mapping now | Correct |
|---|---|---|---|
| County test block | 137–144 | origin ← `y2_`, dest ← `y1_`, `dest_county_name` ← `y1_countyname` | origin ← `y1_`, dest ← `y2_`, `origin_county_name` ← `y1_countyname` |
| County loop (writes `staging.irs_inflow_migration_county`) | 310–317 | same as above | same fix |
| State loop (writes `staging.irs_inflow_migration_state`) | 452–455 | origin ← `y2_statefips`, dest ← `y1_statefips`, `dest_state_name` ← `y1_state_name` | origin ← `y1_`, dest ← `y2_`, `origin_state_name` ← `y1_state_name` |

The unused summary block (lines 184–188) has the same mapping and a wrong comment ("inflow file: Y1 is destination"). That block isn't written to the warehouse, but correct or delete it so it doesn't mislead.

**What it does to the numbers.** Every flow is stored backwards, so for every county, metro and state, inflow and outflow are swapped and every net value has the wrong sign. The error is an **exact sign flip** for net values: `irs_net_migration`, `irs_net_migration_rate` and `irs_net_agi` are each the negative of the true value, and `irs_migration_churn` (in + out) is correct.

**Evidence (2026-10-26, 2022, people = exemptions):**

| Test | As stored | Reality |
|---|---|---|
| New York State, people from other states minus people to other states | **+222,702** | New York lost about 223k people to other states (raw `stateinflow2122.csv`, read Y1 → Y2) |
| New York County → Miami-Dade, vs the reverse | 1,100 vs **2,676** | Manhattan → Miami is the larger flow |
| Suffolk → Palm Beach, vs the reverse | 388 vs **1,513** | Long Island → Palm Beach is the larger flow |
| Albany metro (10580), households in / out / net | 7,600 / 8,623 / −1,023 | Albany gains: about +1,000 households a year, read the right way round |

**Secondary effect, names.** `dest_county_name` holds the origin's name. Silver uses it only as a fallback in `county_name_ref` (keyed to `dest_geoid`), for county codes missing from the current crosswalk. Some old or changed county codes may carry a wrong name today; the fix should key the fallback to the origin side.

## Downstream impact

Starting list from a repo and warehouse search on 2026-10-26. Verify it, and add anything missed.

### Warehouse tables

| Table | Fields affected | How it's rebuilt |
|---|---|---|
| `staging.irs_inflow_migration_county`, `staging.irs_inflow_migration_state` | origin and destination swapped; name column holds the origin's name | `get_irs_migration.R` |
| `staging.irs_migration_state` | an older state table (28,050 rows, 11 years); nothing found reads it | confirm no readers, then drop it or rebuild it with the fix; report which |
| `silver.irs_migration_flows` | origin and destination swapped (and their names, state codes and CBSA joins) | `irs_migration_silver.R` |
| `silver.irs_migration_summary` | inflow ↔ outflow swapped; net negated (county, CBSA, state) | `irs_migration_silver.R` |
| `gold.migration_wide` | `irs_inflow_total` ↔ `irs_outflow_total`, `irs_inflow_agi` ↔ `irs_outflow_agi` swapped; `irs_net_migration`, `irs_net_migration_rate`, `irs_net_agi` negated | `gold_migration_wide.sql` |
| `mart_intelligence.intelligence_character` | `irs_net_migration_rate`, and the character score, percentile and topic scores | Part B (Phase 2 rerun + `load_character_scores.R`) |
| `mart_intelligence.intelligence_opportunity` | `irs_net_migration_rate`, `irs_net_agi`, and the opportunity score, percentile and topic scores | Part B (Phase 4 + `load_opportunity_scores.R`) |
| `mart_intelligence.intelligence_cross_frame` | the cross-frame score and percentile (`rowMeans` of the inputs); clusters and peers expected unchanged (see below) | Part B (Phase 5 + `load_cross_frame_scores.R`) |
| `mart_intelligence.intelligence_trajectory_metric`, `_series`, `_frame`, `_turn_signals` | IRS metric rows (1,980 and 7,128 rows), and any trajectory pattern or turn signal that uses them | Part B (Phase 6) and `engines/time_series/build_time_series_engine.py` |
| `mart_benchmarking.benchmark_cbsa_metrics`, `benchmark_metric_catalog` | IRS metric rows (792 and 2) | `engines/benchmarking/build_benchmark_schema.py` |
| `mart_area_explorer.cbsa_profile_year`, `cbsa_metric_long` | `irs_net_migration_rate` | `foundations/etl/mart_area_explorer/mart_cbsa_explorer.sql` (area paused; rebuild anyway so the mart isn't wrong) |
| `mart_explanation_q1.supply_demand_base` | `irs_net_migration_rate` (context only; not in the Q1 composite, per the method note) | `q1_supply_demand_mart.sql` |

**Not affected (confirm in one line each):** Phase 3 Livability (no IRS input); Phase 7 tract zones (their migration inputs, `pct_same_house` and `pct_foreign_born`, are ACS); What NY Is (`benchmark_stack_up.sql` and `benchmark_state_values.sql` read only ACS fields from `gold.migration_wide`); readers that query gold directly at run time (the `metro-deep-dive/research-tool`, `analyses/position/*` queries), which correct themselves once gold and the marts are rebuilt.

### What should and shouldn't move in the Intelligence Framework

`irs_net_migration_rate` is a clustering input in Character (Phase 2) and Opportunity (Phase 4); `irs_net_agi` is one in Opportunity. Both have **positive** polarity in `intelligence_catalog.yml`. Because the stored values are an exact sign flip of the true values for every metro:

- **Clusters and peers should not change.** The standardized column is negated for every metro, so Euclidean distances (Ward and k-means, with the same seeds picking the same starting rows) and cosine similarity (Phase 5 peers) are identical. Median imputation commutes with negation.
- **Scores, percentiles and topic scores will change.** Positive polarity means metros that *gain* migrants and income have been scored down. This hits `opportunity_score` (two IRS inputs), `character_score` (one), the migration-and-wealth and residential-stability topic scores, and `cross_frame_score` (a row mean of the inputs).
- **Cluster descriptions may change.** Phase 5's extreme-metric profile (top and bottom five metrics per cluster, on `clustering_z`) will list the IRS metrics with the opposite sign. Check whether any cluster name or description rests on migration.
- **Phase 6 trajectory will change.** Changes in the IRS metrics flip sign, and patterns and turn signals use thresholds and polarity, which aren't sign-symmetric.

Part B tests this rather than assuming it. If clusters or peers do move, stop and report, as in the Phase 7 labor-fix review.

### Analyses, issues and saved outputs

| Reader | What it uses | Action |
|---|---|---|
| `metro-deep-dive-program/issues/ny_state/albany/` | `sql/q4_metro_migration.sql` (swaps flows back), `sql/q4_metro_scorecard.sql` (negates `irs_net_migration_rate`), `irs_flows_reversed()` guard in the exploration helpers | Part C: remove both workarounds once the guard fails; rerun the notebook and confirm Q4i reads the same |
| `analyses/explanation/regional_role/` | `queries/regional_role_irs_partner_exchange.sql` (flows), `irs_net_migration_rate` in the notebook; no saved outputs | Rerun the notebook. Note in its audit doc that runs before the fix had the direction reversed |
| `analyses/explanation/q1_supply_or_demand/` | `irs_net_migration_rate` as context in `q1_cbsa_trend.sql`, `q1_market_cbsa_county_context.sql`, `q1_supply_demand_mart.sql`; saved CSVs in `outputs/market_10580`, `market_32580`, `market_40060`, `market_43340`, `market_45300`, `national` | Rebuild the mart; re-export those CSVs; confirm the composite didn't use IRS |
| `analyses/position/` (profile, peers, trajectory) and `engines/intelligence_framework/queries/` | mart_intelligence raw values and scores | Correct after the mart reload; note any saved reads that quote IRS values or scores |
| `metro-deep-dive/research-tool/` | `irs_net_migration_rate`, `irs_net_agi` from `gold.migration_wide` | Corrects itself; nothing to do |
| `metro-deep-dive/markets/richmond_va/` and any other drafted or published piece | Richmond's spec names IRS net migration; written pieces may quote Q1, regional role, scores, percentiles or trajectory signals | **Report, don't edit:** list each claim that cites IRS migration, an Opportunity, Character or cross-frame score or percentile, or a trajectory signal, with the before and after value |
| `foundations/semantic_layer/` (`metric_catalog.yml`, `intelligence_catalog.yml`, `table_catalog.yml`), data dictionary entries for the staging, silver and gold IRS tables, `source__irs.md` | definitions | Update definitions where they describe direction, and add a dated note on the fix |

## Required work

### Part A: fix and rebuild Foundations

1. **Before snapshot.** Export to `foundations/etl/data/snapshots/irs_direction_fix_2026-10/before/` (gitignored): `silver.irs_migration_summary`, the `irs_*` columns of `gold.migration_wide`, and the IRS rows or columns of every mart table listed above. Part B and C diffs read from here.
2. **Fix the mapping** in `get_irs_migration.R` (all three places): origin from `y1_`, destination from `y2_`. Rename the name column to `origin_county_name` (county) and `origin_state_name` (state). Keep the `flow_id` format (`year_origin_dest`); the values will change because the codes swap.
3. **Update `irs_migration_silver.R`**: build the `county_name_ref` fallback from `origin_geoid` and `origin_county_name`; in the flow table, fall back to the name reference (not the staging name) for `dest_geo_name`. Nothing else in silver should need changing: it already treats destination rows as inflows and origin rows as outflows.
   - **Stop before the first warehouse write.** Report the planned commands and the tables to be replaced, and wait for Dan. The warehouse needs every other connection closed: check for open marimo kernels with `lsof` on the DuckDB file.
4. **Rebuild** in pipeline order: staging (the raw CSVs are already in `DATA/demographics/raw/irs`; no re-download needed) → `irs_migration_silver.R` → `gold_migration_wide.sql`.
5. **Add checks** that fail on a reversal, where Foundations keeps its validations (see `foundations/etl/README.md`; if there's no home, add a short SQL check file next to the gold script and register it in `pipeline_manifest.yml`). The acceptance checks below are the content.
6. **Diff against the before snapshot.** Expect net fields exactly negated, inflow and outflow exactly swapped, churn identical. Anything else is a finding to report.

### Part B: rerun the Intelligence Framework phases that use IRS inputs

7. **Don't overwrite current outputs.** Write to a dated folder per phase (`outputs_irs_fix_2026-10/control/` and `/fixed/`), adding an output-directory override where a phase lacks one, as in the Phase 7 labor-fix rerun. Phase 5 already takes `output_dir_name`.
8. **Control runs** (current code, the before snapshot's IRS values) for Phases 2, 4, 5 and 6 should reproduce the current marts exactly. Confirm, or explain the difference.
9. **Fixed runs** for Phases 2, 4, 5 and 6, in that order (5 reads 2–4; Phase 3 outputs are reused unchanged).
10. **Compare control and fixed** and write `exploration/intelligence_framework/IRS_FIX_RERUN_REVIEW.md` (a dated REVIEW per `docs/CONVENTIONS.md`):
    - **Clusters**, per frame and cross-frame: assignment agreement (expect 100%) and calibration (k unchanged).
    - **Peers**: share of metros whose top-10 peer list is unchanged (expect 100%). Albany (10580) as the worked example.
    - **Cluster descriptions**: Phase 5 extreme-metric lists before and after; flag any cluster whose name or description relied on the IRS metrics.
    - **Scores**: for character, opportunity and cross-frame scores and the affected topic scores, the median absolute change in percentile, the share of metros moving more than 10 points, and the 20 biggest movers each way.
    - **Trajectory**: pattern and turn-signal changes, counts and the biggest movers.
    - A recommendation: **promote**, or **hold** (if clusters or peers moved).
11. **Stop. Don't run the loaders** (`load_character_scores.R`, `load_opportunity_scores.R`, `load_cross_frame_scores.R`, the trajectory mart build) until Dan approves.

### Part C: after Dan approves

12. **Promote**: run the loaders and `build_time_series_engine.py`; rebuild `mart_benchmarking` (`build_benchmark_schema.py`), `mart_area_explorer` (`mart_cbsa_explorer.sql`) and `mart_explanation_q1` (`q1_supply_demand_mart.sql`).
13. **Saved outputs**: re-export the Q1 CSVs listed above; rerun the regional role notebook headless.
14. **Albany**: remove the workarounds in `sql/q4_metro_migration.sql` and `sql/q4_metro_scorecard.sql`, and invert the `irs_flows_reversed` guard into a check that fails if the reversal comes back (or delete it, and rely on the Foundations check). Rerun the exploration notebook and confirm Q4i reads the same as the workaround version: Albany metro +1,478 people a year net, 2018–22.
15. **Docs**: data dictionary entries, semantic layer catalogs, phase READMEs (a dated note), `foundations/ROADMAP.md`. In `metro-deep-dive-program/issues/NATIONAL_FOLLOWUPS.md`, mark N8 unblocked.

## Acceptance checks

| Check | Expect |
|---|---|
| New York State net interstate migration (people), 2020, 2021, 2022 | negative each year (2022 −222,702, the stored value negated) |
| New York County → Miami-Dade vs the reverse, 2022 | Manhattan → Miami is larger (2,676 vs 1,100) |
| Inflow file against outflow file, 2022 (the outflow CSV is already downloaded by the test block) | for a sample of county pairs, the corrected inflow row (origin B → destination A) equals the outflow file's row for the same pair |
| Albany metro (10580), 2022 households | in 8,623, out 7,600, net +1,023 |
| `gold.migration_wide` before vs after | net fields exactly negated, in/out exactly swapped, churn identical, row counts identical |
| Intelligence cluster assignments and top-10 peers | unchanged (100%); if not, hold |
| Albany Q4i after removing the workaround | the same numbers as the workaround version |

## Out of scope

- Renaming clusters, or changing KPI selection, polarity or weights (if the review shows a name rests on migration, raise it with Dan)
- Editing published or drafted article text (report claims only)
- Adding newer IRS years (2023 and later) or the IRS foreign-migration rows
- Refactoring the IRS pipeline beyond the fix

## Report back

- **Part A:** files changed, tables replaced with row counts, the acceptance table with actual values, the consumer list with each reader's status.
- **Part B:** control reproduction (pass or fail), cluster and peer stability, the biggest score movers, any cluster description that relied on migration, the recommendation, and a link to the review.
- **Part C:** marts rebuilt, outputs re-exported, the Albany confirmation, and the list of written claims affected.

## Workaround in place until the fix lands

The Albany exploration notebook reads `silver.irs_migration_flows` with origin and destination swapped back (`sql/q4_metro_migration.sql`) and negates `irs_net_migration_rate` in `sql/q4_metro_scorecard.sql`. A guard (`irs_flows_reversed`) asserts that the stored table still shows New York gaining interstate migrants; once the fix lands the guard fails and stops the notebook, so both workarounds come out (step 14).
