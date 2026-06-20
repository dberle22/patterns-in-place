# Phase 2 Character Calibration

This folder now holds the modular Character build, the review notebook layer, and the canonical phase-local outputs.

## Model Overview

The Character model scores the current `396`-CBSA universe on who lives in a place, how rooted or mobile the population is, and what kind of civic and built-form context shapes metro identity. The current calibration keeps the full `17`-KPI Character set, excludes Puerto Rico from the modeling universe, and currently locks `k = 7` for the first full model pass.

The output includes:

- hard cluster assignments
- GMM soft membership probabilities
- topic, subject, and frame scores
- Character percentile ranks
- top-10 Character peers per CBSA
- Character-specific hypothesis review outputs

## Final Calibration Decisions

Three decisions were tested rather than assumed:

- **Keep the full `17`-KPI clustering set:** The Character redundancy audit did not produce any KPI pairs above the `|r| >= 0.75` reduction threshold. The strongest overlaps were real but still below that cutoff, so the default published clustering set stays identical to the approved roadmap core.
- **Proceed with median imputation as-is:** Completeness was effectively full. Only `Waterbury-Shelton, CT` was missing data, and only for four `social_fabric_wide` KPIs. This was a source-row coverage gap, not a broader modeling problem, so median imputation was accepted for the default build.
- **Use `k = 7` for the first full model pass:** The cluster-count calibration showed that `k = 6` and `k = 7` were both defensible. `k = 7` had the best useful k-means silhouette among the non-trivial options and surfaced an additional interpretable subtype without creating tiny k-means fragments.
- **Regularize the GMM soft-membership step:** The first diagonal-GMM pass collapsed too aggressively into a small number of dominant components, so the Character helper was updated to use smoothed mixture weights and variance shrinkage toward the global metric variance. That keeps soft memberships better aligned to the hard `k = 7` structure and makes hybrid-metro review more credible.

## Final Cluster Structure

The published Phase 2 Character model currently uses `k = 7` and the full `17`-KPI clustering set. The working cluster names are:

- `Global Knowledge Capitals`
- `Retirement And Lifestyle Havens`
- `College And Civic Anchors`
- `Established Community Anchors`
- `Immigrant Growth Corridors`
- `Rooted Heartland Centers`
- `Interior Family Opportunity Hubs`

These names reflect the main structural differences that showed up in the KPI profiles:

- `Global Knowledge Capitals` are the densest, most educated, and most globally connected metros in the frame.
- `Retirement And Lifestyle Havens` skew older and migration-driven, with lower density and a strong late-life destination profile.
- `College And Civic Anchors` separate because their education, civic, and association structure is stronger than their overall metro scale would suggest.
- `Established Community Anchors` are more settled, less immigrant-driven, and more rooted in legacy civic structure than the broader growth-oriented family-opportunity cluster.
- `Immigrant Growth Corridors` combine high diversity, high foreign-born share, and growth-corridor built form without collapsing into the global superstar metros.
- `Rooted Heartland Centers` are lower-churn, lower-density, and less globally connected than the faster-growing interior opportunity metros.
- `Interior Family Opportunity Hubs` are more educated, denser, and more mobility-linked than the rooted heartland group, but still sit outside the largest coastal knowledge centers.

## Main Findings

The main modeling takeaways from the completed Phase 2 pass are:

- Character appears to be genuinely multi-dimensional. The redundancy audit found no KPI pairs above the reduction threshold, and the PCA structure spread variance across several interpretable components rather than collapsing into one dominant axis.
- The final seven-cluster solution is meaningfully more informative than a coarse two- or three-cluster split, but it still avoids the tiny-cluster fragmentation that appeared at higher `k` values.
- The biggest naming challenge was not whether the clusters existed, but how to distinguish adjacent rooted-community types clearly. In the final interpretation, `Established Community Anchors`, `Rooted Heartland Centers`, and `Interior Family Opportunity Hubs` are separated by differences in mobility, diversity, density, education, and civic structure rather than by geography alone.
- Character is not simply a disguised metro-size measure. Density relates to Character score more than raw population does, and population size was not independently significant once density was included in the size-dominance check.
- `economic_connectedness` is useful as a hypothesis-test variable, but adding it to the core clustering input did not remap the Character typology enough to justify changing the published KPI set.
- Soft memberships are worth keeping. After the GMM tuning pass, boundary metros now look plausibly hybrid rather than mechanically collapsed into one dominant component.

## Checkpoint Notes

### Checkpoint 1 — KPI Audit

The approved Character KPI set is:

- `diversity_index`
- `pct_black_nh`
- `pct_asian_nh`
- `pct_hispanic`
- `pct_age_over_64`
- `pct_ba_plus`
- `pct_foreign_born`
- `pop_weighted_density_sqmi`
- `friending_bias`
- `civic_engagement_volunteering_rate`
- `civic_organizations_per_1000`
- `nonprofits_per_100k`
- `irs_net_migration_rate`
- `pct_moved_diff_st`
- `pct_moved_abroad`
- `social_associations_per_10k`
- `pct_struct_multifam`

All `17` exist in `metric_catalog.yml`, all `17` are present in `intelligence_catalog.yml`, all source columns matched, and all KPIs have explicit polarity. `friending_bias` is the only negative-polarity KPI in the published core set.

### Checkpoint 2 — Completeness Audit

Coverage was nearly complete:

- `13` KPIs had full `396 / 396` coverage
- `4` KPIs had `395 / 396` coverage:
  - `civic_engagement_volunteering_rate`
  - `civic_organizations_per_1000`
  - `friending_bias`
  - `nonprofits_per_100k`

The only affected metro was `Waterbury-Shelton, CT`, which is missing a `social_fabric_wide` CBSA row entirely. No additional cleanup was required before imputation.

### Checkpoint 3 — Redundancy And PCA Audit

The Character frame looked genuinely multi-dimensional rather than narrowly repetitive.

- No KPI pairs crossed the `|r| >= 0.75` redundancy threshold
- Strongest near-redundant pairs:
  - `pct_hispanic` vs `pct_foreign_born`: `r = 0.734`
  - `pop_weighted_density_sqmi` vs `pct_struct_multifam`: `r = 0.654`
  - `pct_foreign_born` vs `pop_weighted_density_sqmi`: `r = 0.652`
  - `civic_organizations_per_1000` vs `nonprofits_per_100k`: `r = 0.640`

PCA variance structure:

- `PC1`: `27.1%`
- `PC2`: `20.0%`
- `PC3`: `10.6%`
- `PC4`: `9.0%`
- first `6` PCs: `79.1%` cumulative variance

That was not strong enough evidence to shrink the clustering set, so the full `17`-KPI set was retained.

### Checkpoint 4 — Cluster Count Calibration

The `k` comparison showed:

- `k = 2` had the highest raw silhouette but was too coarse to be useful as a Character typology
- `k = 6` and `k = 7` were the real contenders
- `k = 8+` began to create small or fragile clusters without improving interpretability

Final calibration comparison:

- `k = 6`
  - k-means silhouette: `0.169`
  - k-means minimum cluster size: `14`
  - interpretable and stable
- `k = 7`
  - k-means silhouette: `0.171`
  - k-means minimum cluster size: `15`
  - added one extra meaningful subtype without introducing sub-10 k-means clusters

The working decision is `k = 7`.

## Structure

- `R/phase2_config.R`
  Defines the KPI set, clustering decisions, selected `k`, and output paths.
- `R/phase2_helpers.R`
  Shared helpers including z-score normalization and the lightweight diagonal-covariance GMM.
- `R/phase2_catalog_audit.R`
  Builds the semantic catalog and polarity audit bundle.
- `R/phase2_frame_build.R`
  Builds the `396`-CBSA Character KPI frame from DuckDB.
- `R/phase2_imputation.R`
  Computes completeness, imputation, and imputation-sensitive metro outputs.
- `R/phase2_redundancy.R`
  Computes the correlation and PCA redundancy audit.
- `R/phase2_modeling.R`
  Runs cluster calibration, final clustering, scoring, naming, and similarity.
- `R/phase2_hypotheses.R`
  Builds the size-dominance and connectedness cluster-shift review outputs.
- `R/run_phase2_character.R`
  Orchestrates the full Phase 2 build and writes the canonical outputs.
- `character_frame_model.qmd`
  Review notebook for saved outputs, visual QA, and interpretation.

## Notebook Role

`character_frame_model.qmd` is a review notebook:

- reads built artifacts from `outputs/`
- renders cluster summaries and representative metros
- renders similarity and hypothesis-test review outputs
- supports manual interpretation and naming calibration

It should not be the primary execution surface for the model build.
