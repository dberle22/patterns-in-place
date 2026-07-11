# Phase 5 Cross-Frame Integration

This folder holds the cross-frame combined model work that sits on top of the completed Character, Livability, and Opportunity frame calibrations.

The Phase 5 goal is different from the single-frame phases:

- identify which metros look similar overall across all three frames
- identify where the three frames agree versus where they conflict
- build one national cross-frame typology without simply reproducing one frame's structure

The current calibrated Phase 5 working defaults are:

- `396`-CBSA universe
- `35` cross-frame clustering KPIs
- `k = 7` for the current published combined-model pass

The current published working cluster names are:

- `Entrepreneurial Strain Markets`
- `High-Amenity Knowledge Civics`
- `Stable Affordable Heartland Markets`
- `Inland Strain Corridors`
- `Global Knowledge Gateways`
- `Aging Amenity Expansion Markets`
- `Sun Belt Opportunity Engines`

## Input Bundle

Phase 5 does not rebuild the earlier phases. It loads the stable published score artifacts from:

- `phase_2_character_calibration/outputs/character_scores.parquet`
- `phase_3_livability_calibration/outputs/livability_scores.parquet`
- `phase_4_opportunity_calibration/outputs/opportunity_scores.parquet`

The cross-frame reference spine is now treated as the same `396` non-Puerto-Rico CBSAs used by the completed frame models. Puerto Rico is not treated as a temporary join gap here; it is out of scope for the current national cross-frame model by policy.

We start from the published clustering KPI sets from the completed frame decisions:

- Character: `17`
- Livability: `26`
- Opportunity: `20`

That gives a `63`-KPI combined candidate bundle before cross-frame redundancy review.

## Cross-Frame Overlap

Only three published clustering metrics were exact cross-frame duplicates:

- `pop_weighted_density_sqmi`
- `irs_net_migration_rate`
- `permits_share_units_5_plus`

Those were expected conceptual overlaps across frames, but they are perfect duplicates numerically in the combined matrix, so Phase 5 treats them as reduction candidates rather than counting them multiple times in the final clustering input.

## PCA And Reduction Review

The first cross-frame PCA was run on the full standardized `63`-KPI bundle.

Main structural findings:

- `PC1` explains `21.6%` of variance
- `PC2` explains `11.4%`
- `PC3` explains `9.6%`
- the model needs `18` PCs to reach `80.3%` cumulative variance

Interpretation:

- the combined frame is not a one-axis national ranking
- there is no single dominant "big coastal knowledge metro" component swallowing the rest of the model
- a reduced clustering input is still warranted, but the PCA argues for a multi-dimensional typology rather than a tiny handpicked factor set

Strongest flagged redundant pairs:

- `livability__pop_weighted_density_sqmi` vs `character__pop_weighted_density_sqmi`: `r = 1.00`
- `opportunity__irs_net_migration_rate` vs `character__irs_net_migration_rate`: `r = 1.00`
- `opportunity__permits_share_units_5_plus` vs `livability__permits_share_units_5_plus`: `r = 1.00`
- `livability__pct_commute_wfh` vs `character__pct_ba_plus`: `r = 0.816`
- `livability__jobs_access_45min_transit` vs `character__pop_weighted_density_sqmi`: `r = 0.795`

## Candidate Reduction Paths

Two reduced candidate sets were compared rather than jumping straight from `63` KPIs to one final answer.

### Lean Set

- `18` KPIs
- built from the stricter PCA signal thresholds
- strongest simplification path

Pros:

- maximum clarity
- very compact national feature bundle
- slightly better silhouette in some comparisons

Cons:

- over-concentrates the combined model in Opportunity-heavy signals
- repeatedly creates tiny `2`-metro fragments in both hierarchical and k-means calibration
- risks making the national typology look cleaner numerically than it is substantively

### Moderate Set

- `35` KPIs
- built from looser PCA signal thresholds plus removal of exact duplicate cross-frame metrics
- still meaningfully smaller than the original `63`

Pros:

- preserves much better balance across Character, Livability, and Opportunity
- cluster sizes stay healthy much longer in the `k` comparison
- still removes a large amount of low-signal and duplicate noise

Cons:

- slightly less minimalist than the `18`-KPI path
- silhouette gains are not quite as sharp at the extreme high-`k` end

## Cluster Count Comparison

Both the `18`-KPI and `35`-KPI sets were compared over `k = 3:10` using:

- hierarchical clustering with Ward linkage
- k-means silhouette
- cluster-size diagnostics

### Lean `18`-KPI Summary

Key results:

- best hierarchical silhouette: `k = 6` at `0.0866`
- best k-means silhouette: `k = 9` at `0.0962`
- tiny `2`-metro clusters appear across nearly the entire range

Interpretation:

- the lean set separates aggressively
- but it does so by carving off tiny national outlier groups too early
- that makes the typology feel less stable than the silhouette alone suggests

### Moderate `35`-KPI Summary

Key results:

- baseline comparison favored `k = 6`, but the revised AQI-median rerun reopened the cluster-count decision
- in the revised AQI-median pass, `k = 4` was the cleanest numeric solution while `k = 7` retained more interpretable nuance than `k = 4`
- the selected `k = 7` run introduces one `9`-metro elite cluster rather than a singleton
- cluster sizes remain otherwise healthy across the selected seven-cluster configuration

Interpretation:

- the moderate set still behaves like a credible national typology after the AQI swap
- `k = 4`, `k = 6`, and `k = 7` were all defensible in the revised run
- `k = 7` was selected because it recovers a meaningful elite knowledge / gateway cluster that `k = 4` compresses away while avoiding the singleton pathologies seen elsewhere in the framework

## Final Working Decision

The current Phase 5 default is:

- use the `35`-KPI moderate cross-frame clustering set
- use `k = 7` for the current published combined-model pass

Why this was chosen:

- it keeps the revised `35`-KPI bundle intact after the Livability AQI swap to `aqi_median`
- it preserves more nuance than the cleaner `k = 4` alternative
- it introduces one small but interpretable `Global Knowledge Gateways` cluster rather than a singleton
- it remains statistically defensible on k-means separation while yielding a more explainable national story than the flatter solutions

This is the historical decision baseline for the rest of the Phase 5 build. If we revise the KPI count or final `k` later, that change should be documented here rather than silently replacing this rationale.

## Candidate Ranking Note

The current candidate list should not be read as a generic ranking of the "best" or "most important" metros.

It is a **cross-frame divergence heuristic** meant for one narrow analytical purpose:

- surface metros where the three frame stories disagree sharply
- surface metros that look hybrid across combined clusters rather than cleanly assigned
- surface metros that sit far from the center of their assigned combined type

The current score is:

- `50%` frame divergence
  - measured as the summed pairwise gap across Character, Livability, and Opportunity percentiles
- `25%` hybrid membership
  - smaller GMM membership gap means the metro looks more cross-type and therefore more analytically ambiguous
- `25%` cluster outlier distance
  - metros farther from their cluster center get more weight as edge cases

This is useful when the question is:

- "Which metros are most useful for reviewing cross-frame contradiction or ambiguity?"

It is **not** the right score for questions like:

- "Which metros are strongest overall?"
- "Which metros should automatically become Deep Dive priorities?"
- "Which metros are the most representative of the national typology?"

So the candidate list is best treated as one review surface, not as the final market-prioritization answer by itself.

## Cluster Profiles

- `Entrepreneurial Strain Markets`
  Low-performing overall but with a relative Opportunity edge driven by business formation, alongside much weaker Livability and labor-market fundamentals.
- `High-Amenity Knowledge Civics`
  High-character, high-livability metros with strong walkability, smaller multifamily form, and broad knowledge-civics strength outside the top global gateway tier.
- `Stable Affordable Heartland Markets`
  Livability-leading interior markets with lower burden and steadier affordability, but less migration, diversity, and business dynamism.
- `Inland Strain Corridors`
  Low-livability, lower-character strain markets where safety, uninsured, and other resident-pressure signals stay elevated.
- `Global Knowledge Gateways`
  Elite national gateway metros with extreme knowledge-economy, migration, and information-sector signals plus very high cross-frame standing.
- `Aging Amenity Expansion Markets`
  Older, migration-sensitive amenity markets with vacancy, permit, and retirement-growth signatures but weaker near-term labor-market texture.
- `Sun Belt Opportunity Engines`
  Opportunity-led growth markets with strong labor-force and business-base signals, permit activity, and broad expansion-market energy outside the global gateway tier.

## Current Structure

- `R/phase5_config.R`
  Defines the Phase 5 paths, reduction thresholds, and current defaults including the selected `35`-KPI set and `k = 7`.
- `R/phase5_helpers.R`
  Shared helpers for z-scoring and candidate-set selection.
- `R/phase5_input_audit.R`
  Builds the combined Phase 5 input bundle from the stable Phase 2–4 score artifacts.
- `R/phase5_redundancy.R`
  Runs the cross-frame correlation and PCA reduction review.
- `R/phase5_modeling.R`
  Compares candidate reduced sets across cluster counts, fits the locked `35`-KPI / `k = 6` model, and writes cluster outputs plus similarity.
- `R/phase5_overlap.R`
  Builds the cross-frame overlap flags and cluster-level coherence / divergence summaries.
- `R/phase5_hypotheses.R`
  Builds the frame-alignment review outputs and the current cross-frame divergence heuristic candidate list.
- `R/run_phase5_cross_frame.R`
  Writes the current Phase 5 audit, PCA, cluster-count comparison, final combined model, overlap, and candidate outputs.

## Current Outputs

The current canonical Phase 5 outputs live in `outputs/` and include:

- input-audit tables
- combined input parquet
- context bundle parquet
- PCA variance and loadings
- KPI decision log
- candidate metric sets
- cluster-count comparison tables for the `18`-KPI and `35`-KPI paths
- cluster centroids, representatives, and metric extremes for the locked combined model
- overlap flags and overlap summaries
- the divergence heuristic candidate list
