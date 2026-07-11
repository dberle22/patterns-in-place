# AQI KPI Swap Plan

## Goal

Evaluate and, if warranted, replace `aqi_unhealthy_days` with `aqi_median` in the Livability model pipeline without losing the ability to compare the old and new model behavior side by side.

## Working Assumptions

- `aqi_median` is the preferred Livability AQI KPI for default clustering and scoring.
- We want a comparison-first workflow before overwriting the current published Phase 3 and Phase 5 outputs.
- If the revised runs support the same `k` choices and existing cluster names, we should preserve them rather than renaming for cosmetic reasons.
- Phase 6 is lower risk and can be updated after the Phase 3 and Phase 5 comparison is understood.

## Success Criteria

- We can compare old vs revised Phase 3 PCA, selected KPI behavior, cluster calibration, and cluster assignments side by side.
- We can compare old vs revised Phase 5 reduction outputs, selected KPI sets, `k` diagnostics, and final cluster outputs side by side.
- We make an explicit keep-or-change decision on:
  - Phase 3 `k`
  - Phase 3 cluster names
  - Phase 5 `k`
  - Phase 5 cluster names
  - Phase 6 AQI trajectory KPI
- We only replace the current default outputs after the comparison artifacts are reviewed.

## Task Plan

- [x] Create a comparison-safe copy of the Phase 3 review notebook and outputs convention.
  Verify: we have a clearly named revised notebook and a revised output target that does not overwrite the current baseline artifacts.

- [x] Update Phase 3 Livability config and frame build to swap `aqi_unhealthy_days` for `aqi_median`.
  Verify: the revised Phase 3 frame and clustering decision inputs reference `aqi_median`, and no expected clustering input still points at `imputed_aqi_unhealthy_days`.

- [x] Update Phase 3 hypothesis and review surfaces to use the revised AQI KPI.
  Verify: revised notebook tables, plots, and hypothesis text no longer assume `aqi_unhealthy_days` as the default AQI axis.

- [x] Run the revised Phase 3 build into side-by-side artifacts.
  Verify: revised outputs exist for score parquet, clustering decisions, PCA diagnostics, cluster calibration, and notebook-ready review files.

- [x] Compare baseline vs revised Phase 3 KPI diagnostics and clustering behavior.
  Verify: we have a written summary of changes in PCA signal, cluster calibration, cluster sizes, cluster assignments, percentile movement, and representative metros.

- [x] Decide whether Phase 3 can keep the existing `k = 6`.
  Verify: the comparison summary explicitly states whether the current `k` remains defensible or should be changed.

- [x] Decide whether Phase 3 cluster names can be reused.
  Verify: each revised cluster is mapped to its closest baseline analog, and any rename need is documented only if the profile meaning actually changed.

- [x] Create a comparison-safe copy of the Phase 5 review notebook and outputs convention.
  Verify: we have a revised notebook and revised output target for cross-frame comparison without overwriting current baseline artifacts.

- [x] Point the revised Phase 5 run at the revised Phase 3 outputs.
  Verify: the revised Phase 5 config reads the revised Livability score parquet and revised Livability decision CSV while leaving Character and Opportunity inputs unchanged.

- [x] Run the revised Phase 5 build into side-by-side artifacts.
  Verify: revised outputs exist for feature spec, KPI decisions, candidate metric sets, PCA variance/loadings, cluster calibration, and final cross-frame scores.

- [x] Compare baseline vs revised Phase 5 KPI reduction and clustering behavior.
  Verify: we have a written summary of whether `aqi_unhealthy_days` dropped out, whether `aqi_median` entered the kept set, whether the final KPI count stayed at `35`, how calibration changed across `k`, and how cluster assignments shifted.

- [x] Decide whether Phase 5 can keep the existing `k = 6`.
  Verify: comparison work showed that revised Phase 5 `k = 6` remained defensible, but the final published choice moved to `k = 7` to preserve a meaningful extra national type.

- [x] Decide whether Phase 5 cluster names can be reused.
  Verify: revised cross-frame clusters were remapped semantically, and the final published label set adds `Global Knowledge Gateways` for the new seventh cluster.

- [x] If the revised Phase 3 and Phase 5 runs are accepted, promote the revised outputs to the default paths and update semantic documentation.
  Verify: production paths, `intelligence_catalog.yml`, and any Livability / cross-frame notes describe `aqi_median` as the default AQI KPI.

- [x] Update Phase 6 AQI trajectory handling after the clustering decision is settled.
  Verify: Phase 6 now uses `aqi_median` as the Livability AQI trajectory KPI and environmental outlier companion metric alongside `fema_risk_score`, with the canonical outputs rerun.

- [x] Update Phase 8 documentation to record the AQI KPI swap and its downstream effects.
  Verify: Phase 8 documentation explains why `aqi_unhealthy_days` was replaced by `aqi_median`, records that Phase 3 stayed at `k = 6` while Phase 5 moved to `k = 7`, notes the `Global Knowledge Gateways` addition, and leaves Phase 6 as the remaining explicit follow-up.

## Comparison Checklist

### Phase 3

- [ ] Compare completeness and imputation behavior for `aqi_unhealthy_days` vs `aqi_median`
- [ ] Compare PCA retained variance and loadings
- [ ] Compare candidate `k` diagnostics and cluster-size behavior
- [ ] Compare hard cluster assignments and GMM soft membership
- [ ] Compare cluster profiles, representative metros, and percentile shifts
- [ ] Confirm whether existing cluster names still describe the revised profiles

### Phase 5

- [ ] Compare the full feature spec inherited from upstream phases
- [ ] Compare redundant-pair flags and PCA reduction behavior
- [ ] Compare the `lean_18_kpi_set` and `moderate_35_kpi_set`
- [ ] Confirm whether the revised run still lands on `35` KPIs for the selected moderate set
- [ ] Compare `k = 3:10` calibration tables and fragmentation behavior
- [ ] Compare final cluster centroids, representative metros, and divergence candidates
- [ ] Confirm whether existing cluster names still describe the revised profiles

## Notes

- We should prefer copying notebooks and redirecting outputs rather than editing the current notebooks in place for the first comparison pass.
- The safest first production choice is likely:
  - Phase 3: swap to `aqi_median`, rerun, compare
  - Phase 5: rerun from revised Phase 3 outputs, compare
  - Phase 6: update after we decide whether the new AQI KPI changes the frame story enough to warrant consistency there too

## Completed Work

- [x] Scoped the dependency surface for the AQI KPI swap across Phase 3, Phase 5, and Phase 6.
- [x] Confirmed that the current selected Phase 5 `moderate_35_kpi_set` still includes `livability__aqi_unhealthy_days`.
- [x] Created this task plan to guide the comparison-first revision workflow.
- [x] Added a parameterized Phase 3 review run that swaps the Livability AQI KPI to `aqi_median` and writes to `outputs_aqi_median_review/`.
- [x] Added and rendered a side-by-side Phase 3 comparison notebook at `phase_3_livability_calibration/livability_frame_model_aqi_median_review.qmd`.
- [x] Added a parameterized Phase 5 review run that reads the revised Phase 3 Livability outputs and writes to `phase_5_cross_frame_integration/outputs_aqi_median_review/`.
- [x] Added and rendered a side-by-side Phase 5 comparison notebook at `phase_5_cross_frame_integration/cross_frame_model_aqi_median_review.qmd`.
- [x] Promoted the revised Phase 3 and Phase 5 outputs to the canonical `outputs/` paths and refreshed `mart_intelligence.intelligence_livability` plus `mart_intelligence.intelligence_cross_frame` in DuckDB.
- [x] Swapped Phase 6 trajectory handling from `aqi_unhealthy_days` to `aqi_median`, updated the environmental outlier review notebook, and reran the canonical Phase 6 outputs.
