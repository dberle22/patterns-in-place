# Intelligence Calibration Notes

Phase 8 summary of the final published calibration decisions across the Intelligence Framework. This note is the compact handoff document for the semantic layer, Area Explorer, and downstream query surfaces.

## Published universe

- The current published universe is `396` CBSAs.
- Puerto Rico is excluded from the modeled universe in the current published builds.
- Each promoted mart is a static CBSA-grain snapshot rather than a time series.

## Shared modeling architecture

- All three base frames follow the same sequence: hierarchical clustering to inspect natural `k`, K-Means for published hard assignments, and Gaussian Mixture Models for soft memberships.
- Scoring follows the same hierarchy everywhere: KPI z-scores to topic scores, topic scores to subject scores, subject scores to frame composite scores, then percentile ranks within the published universe.
- Negative-polarity KPIs are sign-flipped for scoring so higher score values consistently mean better conditions for Livability and Opportunity.
- Character remains descriptive rather than normative even though it uses the same scoring machinery.
- Similarity uses cosine distance on the standardized KPI vectors. The promoted `mart_intelligence` tables now carry the published top-10 peers for each CBSA.

## Character

- Final phase: Phase 2.
- Final `k`: `7`.
- Final KPI set: full `17`-KPI Character bundle retained after redundancy review.
- Imputation note: Waterbury-Shelton, CT required bounded median imputation for four `social_fabric_wide` KPIs because of a missing source row.
- Interpretation note: cluster naming was literature-anchored against Brookings, Pew, and Moretti-style metro typology references.
- Promoted mart: `mart_intelligence.intelligence_character`.

## Livability

- Final phase: Phase 3.
- Final `k`: `6`.
- Final KPI set: full `26`-KPI Livability bundle retained for the published clustering pass after PCA and correlation review.
- Imputation note: median imputation was applied to six KPIs in the final published run.
- Coverage note: the Connecticut crosswalk rebuild and the `gold.environment_wide` geography fix are reflected in the current outputs.
- Promoted mart: `mart_intelligence.intelligence_livability`.

## Opportunity

- Final phase: Phase 4.
- Final `k`: `6`.
- Final KPI set: reduced published set after redundancy review, with the calibrated output reflecting the final Opportunity notebook decisions.
- Interpretation note: Opportunity is intentionally split across Resident Opportunity, Market and Investor Opportunity, and Business and Industry Opportunity rather than collapsed into a single growth-only story.
- Coverage note: `zori_annual_avg_yoy_pct` remains in the published surface with coverage caution rather than being removed.
- Promoted mart: `mart_intelligence.intelligence_opportunity`.

## Cross-Frame

- Final phase: Phase 5.
- Final `k`: `6`.
- Final KPI set: published reduced `35`-KPI combined bundle.
- Purpose: the Cross-Frame model is a combined similarity and alignment surface, not a replacement for the three base frame interpretations.
- Promoted mart: `mart_intelligence.intelligence_cross_frame`.
- Additional promoted context:
  - top-10 overall peers
  - frame percentile carrythrough
  - overlap and divergence fields such as `frame_percentile_gap`, `top_frame`, `bottom_frame`, and `overlap_profile`

## Zone Methodology

- Final phase: Phase 7.
- Final tract `k`: `7`.
- Final zone names:
  - `Entry-Market Neighborhoods`
  - `Emerging Knowledge Districts`
  - `Knowledge Corridor`
  - `Established Residential`
  - `Mixed-Income Middle Neighborhoods`
  - `Working Neighborhoods`
  - `Commercial Core / Jobs Center`
- Tract surface: `78,199` tracts across `925` CBSAs in the current published run.
- Rollup rule: ZCTAs inherit the dominant tract zone only when one zone exceeds `50%` of the HUD population-weighted tract mix; otherwise the published label is `Mixed Zone`.
- Promoted marts:
  - `mart_intelligence.intelligence_zones`
  - `mart_intelligence.intelligence_zones_zcta`
- Interpretation note: per-market DBSCAN corridor detection remains optional Deep Dive workflow rather than a dependency for the canonical tract or ZCTA marts.

## DataMart contract

- The Intelligence outputs are intentionally promoted into the dedicated `mart_intelligence` schema rather than back into Gold.
- Gold remains the source KPI layer.
- The promoted marts are product-facing downstream tables built from the canonical phase outputs and their companion similarity / overlap artifacts.

## Remaining DataMart follow-up

- MotherDuck validation still needs to confirm the `mart_intelligence` tables, including the new Phase 7 tract and ZCTA marts, are queryable by Area Explorer and the Chatbot.
- If additional downstream marts are added later, they should follow the same `mart_*` naming pattern rather than being folded back into Gold.
