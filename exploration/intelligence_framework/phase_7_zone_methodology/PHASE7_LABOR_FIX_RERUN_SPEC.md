# Phase 7 Rerun After the ACS Labor Fix: Spec

**Status:** Done
**Updated:** 2026-10-23

> **Promoted, 2026-10-23.** Dan approved keeping the original names, carried forward to the matched clusters through a fixed `zone_name_map` in `R/phase7_config.R` that replaces the automatic labeler. Names stay draft and are reviewed CBSA by CBSA during issue work.
> - `outputs/` was rebuilt (model, ZCTA rollup, descriptive audit) and matches `fixed/` exactly. The July outputs are in `outputs_rerun_2026-10/pre_promotion_outputs/`.
> - Loaded: `mart_intelligence.intelligence_zones` (78,199 tracts, 0 null names) and `intelligence_zones_zcta` (29,282 ZCTAs, 0 null types, 1,119 Mixed Zone).
> - Updated the README model overview, and added a dated note to `docs/methodology/intelligence_framework/zone_methodology_notes.md`.
> - Downstream refreshes (Albany Q3 table, the corridor runs) are left to their areas; see the review's Downstream section.

> **Outcome, 2026-10-23.** Steps 1–6 done. Review: [PHASE7_LABOR_FIX_RERUN_REVIEW.md](PHASE7_LABOR_FIX_RERUN_REVIEW.md).
> - **Control reproduction:** pass (100% assignment agreement, identical scores and ZCTA rollup).
> - **Recommendation: hold.** k = 7 holds (k-means silhouette 0.0986), 83.4% of tracts unchanged, ARI 0.695. But the knowledge pair reorganised (Emerging Knowledge −67%, Knowledge Corridor +139%), and the automatic labeler returns NA for the matched Mixed-Income Middle cluster. Promotion needs a name map first.
> - **Pre-fix frame used:** `outputs/phase7_tract_frame.parquet`, which is equivalent to the foundations before-snapshot.
> - **Unplanned:** the ZCTA rollup no longer ran on today's warehouse (the crosswalk view lost its city and state columns on 2026-09-29), so it now reads them from HUD staging.

A spec for one agent session. Rerun the Phase 7 national tract clusters on the corrected unemployment input, measure what changed and why, and recommend whether to promote. **Start only after** [ACS_LABOR_B23025_FIX_SPEC.md](../../../foundations/etl/ACS_LABOR_B23025_FIX_SPEC.md) is done and its report confirms that `gold.intelligence_zone_inputs.pct_unemployment_rate` is fixed.

This session compares and recommends. **Promotion (overwriting `mart_intelligence.intelligence_zones` and the ZCTA mart) needs Dan's approval**, because issue work (Albany Lens 1) and Corridor Intelligence read those marts.

## Read first

1. `AGENTS.md`, `docs/CONVENTIONS.md`
2. This folder's `README.md` (model overview, locked decisions, run order) and `PHASE7_PLAN.md`
3. `K6_K7_CLUSTER_REVIEW.md`: how k = 7 and the names were chosen. Note its known error below.
4. `R/phase7_config.R` (KPI contract and polarity), `R/phase7_national_cluster.R` (seeds, calibration, k-means), `R/phase7_helpers.R` (automatic label scoring), `R/run_phase7_zone_model.R`
5. `docs/methodology/intelligence_framework/` (method docs; the Phase 7 section)
6. The foundations fix report
7. `metro-deep-dive-program/issues/VISUALS_BUILD_RULES.md`, rule R32 (read clusters on raw values)

## Why this rerun

`pct_unemployment_rate` is 1 of the 22 clustering KPIs (negative polarity). Until the fix, tract values were (labor force − not in labor force) / labor force, about 0.42 for the US: noise correlated with labor force participation, not unemployment. Cluster assignments, centroids, scores and percentiles may all move.

**A second, independent issue for the naming step:** the K6/K7 review read polarity-flipped centroids as raw values. In the flipped scale, a negative poverty centroid means *high* poverty. On raw medians, "Mixed-Income Middle Neighborhoods" is the lowest-poverty type nationally (6.1%, $104k), and "Established Residential" is rural (147 people per sq mi). Albany is testing plain-language working names against this ([Albany build plan](../../../metro-deep-dive-program/issues/ny_state/metro_deep_dives/albany/part_1/ALBANY_LENS1_VISUALS_BUILD_PLAN.md), Q3). This session reports raw profiles for every cluster but **doesn't rename anything**; renaming is a separate decision for Dan.

## Required work

1. **Don't overwrite the current outputs.** `phase7_config()` writes to a fixed `outputs/` folder. Add an output-directory override (an argument or env var, defaulting to today's behavior) and write to:
   - `outputs_rerun_2026-10/control/`: current code, *current pre-fix inputs* (from the saved `outputs/phase7_tract_frame.parquet`, or a snapshot of the inputs taken before the foundations rebuild)
   - `outputs_rerun_2026-10/fixed/`: current code, fixed inputs

   If a pre-fix input snapshot isn't available because the foundations rebuild already replaced the gold table, use `outputs/phase7_tract_frame.parquet` as the pre-fix frame. Say which one you used.
2. **Control run.** Seeds are fixed (`set.seed(20270701 + …)`), so the control should reproduce the published assignments exactly. Confirm 100% assignment agreement with `mart_intelligence.intelligence_zones`, or explain the difference. This separates the effect of the fix from run-to-run noise.
3. **Fixed run.** Same code and seeds, fixed inputs. Rerun calibration too: is k = 7 still the best k-means silhouette, and do the fit metrics in `phase7_cluster_calibration.csv` move?
4. **Compare control and fixed:**
   - **Assignment stability.** A crosstab of control cluster against fixed cluster: share of tracts unchanged nationally, per cluster, and for large CBSAs; adjusted Rand index. **Match clusters by centroid similarity**, because IDs and automatic labels can swap between runs. Report the matching.
   - **Cluster sizes**, before and after.
   - **Centroids** on the flipped, standardized scale, before and after, with the largest shifts called out.
   - **Raw profiles** (R32): median raw values per cluster for poverty, BA+, median income, owner share, density, age 65+ and the *fixed* unemployment rate, before and after.
   - **Automatic labels:** does `build_phase7_provisional_label_map` assign the same draft labels to the matched clusters? Flag any swap.
   - **Scores and percentiles:** how much character, livability, opportunity and composite tract scores move (median absolute change, and the share of tracts moving more than 10 percentile points).
   - **Albany (CBSA 10580) as the worked example:** a tract crosstab and any working-name implications (the build plan's Q3 table).
5. **ZCTA rollup:** rerun `R/phase7_zcta_rollup.R` into `fixed/` and report how many ZCTAs change dominant zone or flip to or from "Mixed Zone".
6. **Write `PHASE7_LABOR_FIX_RERUN_REVIEW.md`** in this folder, a dated REVIEW per `docs/CONVENTIONS.md`, containing the comparison and a recommendation:
   - **promote as is**,
   - **promote and revisit names**, or
   - **hold** (if k or the structure changed enough to need a fresh naming review).
7. **Stop. Don't run the loaders** (`foundations/loaders/load_zone_assignments.R`, `load_zone_scores_zcta.R`) until Dan approves. After approval: promote, update the README's model overview, and add a dated note on the method docs page.

## Downstream to list in the review (not to change)

- `mart_intelligence.intelligence_zones` and `intelligence_zones_zcta` readers: `metro-deep-dive-program/analyses/position/internal_structure/`, `engines/corridor_intelligence/inputs/corridor_inputs_v1.yml`, `issues/ny_state/metro_deep_dives/albany/` (zone map, composition, working names)
- Anything that caches zone scores or percentiles (search the repo)

## Out of scope

- Renaming zone types (separate decision)
- Changing the KPI contract, k, imputation or polarity
- The CBSA-level frames (Character, Livability, Opportunity, Cross-Frame). Their unemployment input is BLS LAUS and unaffected. Confirm this in one line.

## Report back

- Control reproduction: pass or fail.
- Headline stability numbers: share of tracts unchanged, adjusted Rand index, k-calibration result.
- The biggest movers, by cluster and by measure.
- Label swaps, if any.
- The Albany crosstab.
- The recommendation, and a link to the review doc.
