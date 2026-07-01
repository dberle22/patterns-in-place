# Phase 7 Zone Methodology

This folder now contains the completed modular Phase 7 tract model, the downstream ZCTA rollup, and the promotion path into the Intelligence DataMart.

## Model Overview

The Phase 7 model scores the current full tract universe on a combined zone methodology that blends Character, Livability, and Opportunity into one national tract typology. The current Sprint 2 build uses the locked `22`-KPI clustering contract from Sprint 1 and runs on the governed `gold.intelligence_zone_inputs` tract surface.

The current Phase 7 output includes:

- hard national tract cluster assignments
- optional GMM soft membership probabilities
- Character, Livability, Opportunity, and composite tract scores
- national, CBSA, and same-zone peer percentiles
- the final `k = 7` tract zone names
- the population-weighted ZCTA rollup with dominant-vs-mixed assignment
- promoted marts: `mart_intelligence.intelligence_zones` and `mart_intelligence.intelligence_zones_zcta`

## Phase 7 Decisions

The main Phase 7 implementation choices are now locked:

- **Use the governed Gold tract backbone:** Sprint 2 reads `gold.intelligence_zone_inputs` as the shared tract KPI source of truth, then joins tract metadata and Opportunity Zone flags. This avoids duplicating the wide tract join in the model code.
- **Keep the default `22`-KPI clustering contract:** The Stage 1 national model uses the Sprint 1 KPI decisions as-is, including the retained LODES trio and the log-transform treatment for `pop_weighted_density_sqmi`.
- **Use median imputation for the first national pass:** Even when a KPI would qualify for a deeper imputation review, Sprint 2 keeps the same median-first architecture used in Phases 2–5 so the first model pass stays easy to audit.
- **Keep `k = 7` as the published tract structure:** The national tract model now keeps the `k = 7` solution after the `k = 6` versus `k = 7` review confirmed it adds a real subtype without destabilizing the broader map.
- **Skip GMM by default at tract scale:** Sprint 2 now treats GMM as optional because the full-tract pass is expensive and lower-value analytically than the hard labels, centroids, and percentile outputs at this grain.
- **Use the final decision-point zone names in the tract output:** The canonical `zone_type` labels are now `Entry-Market Neighborhoods`, `Emerging Knowledge Districts`, `Knowledge Corridor`, `Established Residential`, `Mixed-Income Middle Neighborhoods`, `Working Neighborhoods`, and `Commercial Core / Jobs Center`.
- **Roll ZCTAs from tract composition, not a separate model:** The ZCTA layer is a population-weighted summary of tract assignments using `silver.xwalk_zcta_tract`, with a `Mixed Zone` label when no single tract type exceeds `50%` of the weighted population mix.
- **Keep DBSCAN corridor work optional:** Market-level corridor detection remains a Deep Dive workflow, not part of the canonical tract or ZCTA marts.

## Method Overview

The build follows the same modular sequence used in the earlier intelligence phases, then adds a lightweight downstream rollup:

1. Build the governed tract frame from DuckDB
2. Audit missingness and apply median imputation where needed
3. Apply polarity for scoring and standardize KPI inputs
4. Calibrate candidate cluster counts, then fit sampled hierarchical clustering plus full-matrix k-means
5. Assign the final zone labels from centroid signatures and the naming review
6. Compute theme, composite, and benchmark scores
7. Write the canonical tract outputs
8. Roll the tract assignments to ZCTAs using the HUD tract-to-ZCTA population weights
9. Promote both tract and ZCTA outputs into `mart_intelligence`

Build logic lives in `R/phase7_*.R`. The notebook is only for reviewing saved outputs, checking calibration, and interpreting the final zone labels.

## Structure

- `R/phase7_config.R`
  Defines the KPI contract, clustering decisions, draft label set, and output paths.
- `R/phase7_helpers.R`
  Shared helpers for z-scoring, GMM fitting, cluster flattening, label assignment, and zone-name slugging for the ZCTA share columns.
- `R/phase7_tract_frame_build.R`
  Builds the current tract frame from governed Gold plus tract metadata and Opportunity Zone flags.
- `R/phase7_imputation.R`
  Computes completeness, missing-tract audits, and the median-imputed model surface.
- `R/phase7_national_cluster.R`
  Runs standardization, sampled hierarchical calibration, hard clustering, optional soft memberships, centroids, representatives, and light market spot checks.
- `R/phase7_scoring.R`
  Computes theme scores, composite scores, and national / CBSA / same-zone peer percentiles.
- `R/run_phase7_zone_model.R`
  Orchestrates the full Sprint 2 build and writes the canonical outputs.
- `R/phase7_zcta_rollup.R`
  Population-weighted tract-to-ZCTA rollup with dominant-vs-mixed assignment logic and full cluster-share carrythrough.
- `zone_methodology.qmd`
  Review notebook for calibration, centroids, representative tracts, and final zone profiles on already-built outputs.

## Notebook Role

`zone_methodology.qmd` is a review notebook:

- reads built artifacts from `outputs/`
- renders the candidate-`k` calibration
- shows final cluster centroids and representative tracts
- surfaces the light Jacksonville and Richmond spot checks

It should not be the primary execution surface for the model build.

## Canonical Run Order

1. Run `R/run_phase7_zone_model.R`
2. Run `R/phase7_zcta_rollup.R`
3. Review outputs in `outputs/`
4. Render `zone_methodology.qmd` when you want visuals or narrative review
5. Run `foundations/loaders/load_zone_assignments.R` and `foundations/loaders/load_zone_scores_zcta.R` to promote the tract and ZCTA marts
