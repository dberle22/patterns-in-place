# Phase 4 Opportunity Calibration

This folder now contains the complete modular Opportunity build plus the review notebook layer.

## Model Overview

The Opportunity model scores the current `396`-CBSA universe on future-facing economic upside for residents, investors, and businesses. It combines the published Opportunity KPI set across three subjects:

- `Resident Opportunity`
- `Market And Investor Opportunity`
- `Business And Industry Opportunity`

The current published calibration uses a reduced clustering set, excludes Puerto Rico from the modeling universe, and locks `k = 6` for the Opportunity typology. The output includes:

- hard cluster assignments
- GMM soft membership probabilities
- topic, subject, and frame scores
- Opportunity percentile ranks
- top-10 Opportunity peers per CBSA
- hypothesis and cross-frame review outputs

## Cluster Choices

Three modeling choices were explicitly tested rather than assumed:

- **Use the reduced clustering set:** The Opportunity redundancy and PCA audit showed one clear overlap between `lq_information` and `pct_real_gdp_information`, plus a second overlap between `permits_per_1000_housing_units` and `pop_growth_5yr`. We kept both held-out metrics in scoring and descriptive outputs, but removed them from the published clustering set to make the typology cleaner without flattening the full model.
- **Use `k = 6`:** The reduced-set comparison showed that `k = 5` and `k = 6` were both defensible. We chose `k = 6` because the hierarchical structure supported the extra nuance and the sixth cluster surfaced a meaningful thin-base distressed subtype rather than arbitrary fragmentation.
- **Assign names from cluster attributes, not raw k-means IDs:** K-means numbering is arbitrary across reruns, so the published cluster names are mapped from the observed centroid and metric signature rather than the raw cluster number. That keeps the named Opportunity types stable even if cluster IDs reshuffle in a future run.

## Published Opportunity Types

- `Superstar Knowledge Capitals`
- `Broad-Based Opportunity Hubs`
- `Emerging Momentum Markets`
- `Industrial Rebound Markets`
- `Uneven Transition Markets`
- `Thin-Base Distressed Markets`

## Method Overview

The build follows the same modular sequence as the other calibrated intelligence frames:

1. Audit the expected KPI set against `metric_catalog.yml` and `intelligence_catalog.yml`
2. Build the live CBSA frame from DuckDB
3. Audit completeness and apply median imputation where needed
4. Apply polarity for scoring and standardize KPI inputs
5. Run redundancy diagnostics with correlation, PCA, and hierarchical-vs-kmeans comparison
6. Fit hierarchical clustering, k-means, and GMM for the published `k = 6` model
7. Compute topic, subject, and frame composite scores
8. Write similarity outputs, hypothesis datasets, and the Livability / Opportunity scatter

Build logic lives in `R/phase4_*.R`. The notebook is only for reviewing saved outputs, checking visuals, and interpreting the model.

## Scoring Method

The published `opportunity_score` is built as a hierarchical composite rather than a flat KPI average.

1. KPI values are imputed where needed, polarity-adjusted for scoring, and standardized across the modeling universe.
2. KPI scores are averaged within each topic to produce a single topic score.
3. Topic scores are combined into subject scores using normalized topic weights based on the semantic frame's coverage and reliability settings.
4. Subject scores are combined into the final frame score using the published subject weights for:
   `Resident Opportunity`, `Market And Investor Opportunity`, and `Business And Industry Opportunity`.
5. The raw frame score is converted into an `opportunity_percentile` across the CBSA modeling universe.

This structure is designed to avoid mechanically overweighting a topic just because it contains more KPIs, or a subject just because it contains more topics. Topics first collapse to a single score, and subjects retain their own explicit frame weights.

## Structure

- `R/phase4_config.R`
  Defines the KPI set, reduced clustering decisions, selected `k`, and output paths.
- `R/phase4_helpers.R`
  Shared helpers including z-score normalization and the lightweight diagonal-covariance GMM.
- `R/phase4_catalog_audit.R`
  Builds the semantic catalog and polarity audit bundle.
- `R/phase4_frame_build.R`
  Builds the `396`-CBSA Opportunity KPI frame from DuckDB.
- `R/phase4_imputation.R`
  Computes completeness, imputation, and imputation-sensitive metro outputs.
- `R/phase4_redundancy.R`
  Computes the correlation, PCA, and clustering-comparison audit.
- `R/phase4_modeling.R`
  Runs cluster assignments, soft memberships, scoring, naming, and similarity.
- `R/phase4_hypotheses.R`
  Builds the industry-leading-indicator, social-capital, signal-divergence, OZ overlay, and Livability/Opportunity scatter outputs.
- `R/run_phase4_opportunity.R`
  Orchestrates the full Phase 4 build and writes the canonical outputs.
- `opportunity_frame_model.qmd`
  Review notebook for hypothesis checks, representative metros, and visual QA on already-built outputs.

## Notebook Role

`opportunity_frame_model.qmd` is a review notebook:

- reads built artifacts from `outputs/`
- renders cluster summaries and representative metros
- renders similarity and hypothesis-test visuals
- supports manual interpretation and visual calibration

It should not be the primary execution surface for the model build.

## Canonical Run Order

1. Run `R/run_phase4_opportunity.R`
2. Review outputs in `outputs/`
3. Render `opportunity_frame_model.qmd` when you want visuals or narrative review
