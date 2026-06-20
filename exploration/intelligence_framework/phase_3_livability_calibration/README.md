# Phase 3 Livability Calibration

This folder now separates the Livability build pipeline from the review notebook layer.

## Model Overview

The Livability model scores the current `396`-CBSA universe on whether day-to-day living conditions support quality of life. It combines `26` KPIs across four subjects:

- `Affordability`
- `Health And Safety`
- `Access And Infrastructure`
- `Physical Environment`

The current published calibration keeps all `26` KPIs, excludes Puerto Rico from the modeling universe, and uses `k = 6` for the Livability typology. The output includes:

- hard cluster assignments
- GMM soft membership probabilities
- topic, subject, and frame scores
- Livability percentile ranks
- top-10 Livability peers per CBSA

## Calibration Decisions

Two modeling choices were explicitly tested rather than assumed:

- **Keep all `26` KPIs:** A correlation and PCA audit showed some redundancy, but not enough to justify shrinking the published Livability input set. The strongest overlaps were real, but the overall structure still carried multiple independent dimensions, so we kept the full KPI set for the default model and treated the redundancy pass as a diagnostic rather than a reduction rule.
- **Use `k = 6`:** We compared multiple cluster counts, including values above the original `5-9` heuristic range. Higher `k` values fragmented quickly and did not reveal a hidden `10+` cluster optimum. On the full 26-KPI set, `k = 5` and `k = 6` were both defensible, but `k = 6` produced a meaningful extra split without over-fragmenting the system. The final model keeps that added nuance and preserves a distinct 3-metro outlier cluster, `Megametro Extremes`.
- **Stabilize names from cluster pattern, not raw k-means IDs:** K-means numbering is arbitrary across reruns, so published cluster names are assigned from the observed cluster profile rather than the raw numeric label. This keeps the smallest outlier cluster tagged as `Megametro Extremes` even if the underlying cluster ID changes between runs.

## Method Overview

The build follows the same sequence from raw KPI frame to scored model:

1. Audit the expected KPI set against `metric_catalog.yml` and `intelligence_catalog.yml`
2. Build the live CBSA frame from DuckDB
3. Audit completeness and apply median imputation where needed
4. Apply polarity for scoring and standardize KPI inputs
5. Run redundancy diagnostics with correlation and PCA
6. Calibrate cluster count, then fit hierarchical clustering, k-means, and GMM
7. Compute topic, subject, and frame composite scores
8. Write similarity outputs and hypothesis-test datasets

Build logic lives in `R/phase3_*.R`. The notebook is only for reviewing saved outputs, checking visuals, and interpreting the model.

## How `livability_score` Is Computed

The `livability_score` is a hierarchical weighted average built from the KPI level up:

1. Missing KPI values are median-imputed where needed.
2. Negative-polarity KPIs are sign-flipped so higher is always better for scoring.
3. Each KPI is standardized to a z-score across the `396`-CBSA universe.
4. Topic scores are the mean of the scoring z-scores for the KPIs in that topic.
5. Topic scores are weighted within each subject using:
   - `raw_topic_weight = coverage * reliability_factor`
   - `core = 1.00`
   - `supplemental_baseline = 0.75`
   - `coverage_caution = 0.60`
6. Subject scores are the weighted mean of topic scores within each subject.
7. The final `livability_score` is the weighted mean of the four subject scores.

Current subject weights are equal:

- `Affordability = 0.25`
- `Health And Safety = 0.25`
- `Access And Infrastructure = 0.25`
- `Physical Environment = 0.25`

The public-facing output is `livability_percentile`, which is the percentile rank of `livability_score` within the modeled CBSA universe.

## Structure

- `R/phase3_config.R`
  Defines the KPI set, cluster names, selected `k`, and output paths.
- `R/phase3_helpers.R`
  Shared helpers including z-score normalization and the lightweight diagonal-covariance GMM.
- `R/phase3_catalog_audit.R`
  Builds the semantic catalog and polarity audit bundle.
- `R/phase3_frame_build.R`
  Builds the `396`-CBSA Livability KPI frame from DuckDB.
- `R/phase3_imputation.R`
  Computes completeness and median-imputation outputs.
- `R/phase3_redundancy.R`
  Computes the correlation and PCA redundancy review.
- `R/phase3_modeling.R`
  Runs standardization, cluster calibration, hard clusters, soft memberships, scoring, and similarity.
- `R/phase3_hypotheses.R`
  Builds the affordability-vs-health and AQI-vs-FEMA test outputs.
- `R/run_phase3_livability.R`
  Orchestrates the full Phase 3 build and writes the canonical outputs.
- `livability_frame_model.qmd`
  Review notebook for hypothesis checks, representative metros, and visual QA on already-built outputs.

## Dependency Map

`phase3_config`
-> `phase3_catalog_audit`
-> `phase3_frame_build`
-> `phase3_imputation`
-> `phase3_redundancy`
-> `phase3_modeling`
-> `phase3_hypotheses`
-> `outputs/`

## Notebook Role

`livability_frame_model.qmd` is now a review notebook:

- reads built artifacts from `outputs/`
- renders cluster summaries and representative metros
- renders hypothesis-test visuals
- supports manual interpretation and visual calibration

It should not be the primary execution surface for the model build.

## Canonical Run Order

1. Run `R/run_phase3_livability.R`
2. Review outputs in `outputs/`
3. Render `livability_frame_model.qmd` when you want visuals or narrative review
