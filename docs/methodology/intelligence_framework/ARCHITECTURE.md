# Intelligence Framework — Scoring and Clustering Architecture

**Status:** Active (locked architecture)
**Updated:** 2026-09-29

The locked architecture every Intelligence frame is built on: universe, imputation, standardization, clustering, scoring, similarity, output format and benchmarks. This is carried over word for word from the "Scoring and Clustering Architecture" section of the retired `INTELLIGENCE_LAYER_ROADMAP.md` (archived at `docs/archive/2026-09_intelligence_layer_roadmap/`). Changes to it need a new decision record, not an edit here.

For how the frames were actually built and what they found, see [intelligence_framework_overview.md](intelligence_framework_overview.md).

---


*These decisions were locked in after Phase 1 (Variable Selection) was complete. Every Phase 2–4 frame notebook follows this architecture. Do not relitigate these choices inside individual notebooks — document deviations here instead.*

---

## Universe

**Decision:** All 401 CBSAs (population ≥ 100K) are included in every model. CBSAs are never dropped due to missing KPI coverage.

**How missingness is handled:** Per-KPI, not per-CBSA. Each Phase 2–4 notebook opens with a coverage audit for its KPI set. KPIs with any missing values are imputed before modeling. KPIs with coverage problems severe enough to warrant removal are dropped from the model (with a documented rationale), not the CBSAs they're missing for.

---

## Missing Data — Imputation Strategy

**Decision:** Median imputation as the default. KNN imputation considered only when a KPI has >15% missingness AND the missing pattern is clearly non-random (e.g. a source that systematically excludes small metros).

**Implementation:**
- Replace missing values with the national median for that KPI across the published CBSA universe
- Log which KPIs triggered imputation and how many CBSAs were affected
- Flag imputed values in the output so downstream analysis can identify imputation-sensitive results

**Rationale:** Median imputation is fast, transparent, and appropriate when missingness is random or coverage-driven (e.g. ZORI not covering smaller metros). KNN adds complexity that is not justified for this universe size unless missingness is structurally biased.

---

## KPI Standardization and Polarity

**Decision:** All KPIs are standardized to z-scores before any clustering or scoring. A polarity flag is assigned to each KPI before Phase 3 and carried forward:

- **Positive polarity** (`+`): higher values are better (e.g. `life_expectancy`, `lfpr`, `income_pc_growth_5yr`)
- **Negative polarity** (`-`): lower values are better (e.g. `premature_death_rate`, `pct_rent_burden_30plus`, `pct_unemployment_rate`)

**For scoring:** Negative-polarity KPIs are sign-flipped before computing sub-scores so that a higher score always means better on every axis.

**For clustering and similarity:** Polarity does not matter — distance metrics are direction-agnostic. No sign-flip needed.

---

## Clustering Architecture

Each frame runs three clustering passes in sequence, all on the same standardized KPI vectors:

**Step 1 — Hierarchical clustering (agglomerative)**
- Purpose: discover the natural number of clusters (k) from the data
- Output: dendrogram; cut point chosen based on within-cluster variance and interpretability
- k range: data-driven, no hard constraint — but must produce interpretable, nameable groups. Expect 5–9 for most frames.

**Step 2 — K-Means at natural k**
- Purpose: hard cluster assignments for publication-ready archetype labels
- Output: one cluster label per CBSA per frame (e.g. "Sun Belt Growth", "Immigrant Gateway")
- Labels are assigned after inspecting cluster centroids — not pre-specified

**Step 3 — Gaussian Mixture Model (GMM) at same k**
- Purpose: soft membership probabilities that capture metros that genuinely sit between archetypes
- Output: probability vector for each CBSA across all k clusters
- Use: "Austin is 68% Knowledge Hub, 28% Sun Belt Growth, 4% other" — honest about ambiguity and useful for narrative

**All three outputs are retained.** Hard labels are the default for display and publication. Soft memberships are the default for analysis and similarity scoring.

---

## Scoring Architecture

**Structure:** Hierarchical weighted averaging. Score flows upward through four levels:

```
KPI z-score (sign-flipped for negative polarity)
    → Topic score      (mean of KPI z-scores within topic)
        → Subject score    (weighted mean of topic scores within subject)
            → Frame composite  (weighted mean of subject scores)
                → Percentile rank  (0–100 within the published CBSA universe)
```

**Subject weights:** Equal weight across subjects within each frame for the initial model (e.g. Livability = 25% Affordability + 25% Health & Safety + 25% Access & Infrastructure + 25% Physical Environment). Revisit after first calibration pass if one subject is clearly dominating or underweighting.

**Topic weights within subject:**

```
raw_topic_weight = coverage_share × reliability_factor
```

Reliability factors:
- Recurring core topics: `1.00`
- Supplemental baseline topics: `0.75`
- Coverage-caution topics: `0.60`

Normalize within each subject, then apply the subject weight:

```
topic_weight = subject_weight × (raw_topic_weight / sum(raw_topic_weights in subject))
```

**KPI weights within topic:** Equal split across selected core KPIs within the topic.

**Final output:** Percentile rank (0–100) within the published CBSA universe. Percentile is the public-facing number — more interpretable than a raw z-score. Sub-scores at topic and subject level are also retained for drill-down analysis.

**Score anchoring:** Percentile ranks are relative to the current published CBSA universe. This is the correct default for the initial model. Anchoring scores to a base year for longitudinal comparability is a future calibration decision — flag it in the catalog entry when it becomes relevant.

---

## Similarity Scoring

**Method:** Cosine distance on the standardized KPI vectors (the same vectors used for clustering and scoring).

**Why cosine over Euclidean:** Cosine distance measures directional similarity — whether two metros are *shaped* the same way — rather than absolute magnitude. This is the right question for metro comparison: not "are these metros similar in size?" but "do they look like each other across the metric profile?"

**Three similarity matrices:**

1. **Frame-specific similarity** (three independent matrices — one per frame): "The metros most similar to Richmond VA on Livability" — computed on Livability KPI vectors only
2. **Cross-frame combined similarity** (one combined matrix): computed on the concatenated KPI vectors across all three frames — "the metros most like Richmond VA overall"
3. **Cross-frame overlap check**: compare cluster label assignments across frames to identify metros that are outliers on one frame but typical on another ("diverging from themselves" — key Deep Dive candidates)

**Frame independence:** Frames 2–4 are built and scored independently first. The cross-frame combined model is built after all three frame models are stable.

---

## Output Format

**During Phase 2–5 (calibration phase):** Each frame or combined model should live in its own phase folder and follow the same modular pattern:

- phase-local `R/` modules for build steps
- one phase runner script as the canonical execution surface
- one review `.qmd` that reads saved artifacts for visuals, QA, and interpretation
- one phase-local `outputs/` folder that holds the canonical artifacts for that phase

**Canonical workflow for Phases 2–5:**
1. run the phase runner script
2. write all artifacts to that phase's `outputs/` folder
3. render the review notebook against those built artifacts
4. promote only the final scored parquet to the later DuckDB loader step

**After calibration is stable:** Promoted to a Gold-layer scores datamart. This is the prerequisite for Area Explorer Phase 2 (Intelligence Frames views) and the Chatbot wire-up. Promotion happens in Phase 7 (Catalog Finalization).

**Minimum artifact set per phase:**
- one scored parquet with cluster labels, GMM probabilities, and topic/subject/frame scores
- one similarity CSV with top-10 peers per CBSA
- one cluster calibration CSV
- one cluster-centroid or representative-metros CSV
- any phase-specific audit outputs such as completeness, imputation, redundancy, or overlap flags

**Columns per CBSA in the scored output:**
- `cbsa_code`, `cbsa_name`, `census_division`
- One cluster label column per frame (`character_cluster`, `livability_cluster`, `opportunity_cluster`)
- GMM soft membership probabilities per frame (`character_prob_k1` … `character_prob_kN`)
- Topic scores (z-score scale) per frame
- Subject scores (z-score scale) per frame
- Frame composite (z-score scale) per frame
- Frame percentile rank (0–100) per frame
- Cross-frame similarity: top-10 most similar CBSAs by frame and combined

---

## Benchmark Strategy

Each CBSA score is benchmarked at three levels:

1. **National:** percentile rank within all 401 CBSAs
2. **Census Division:** percentile rank within the CBSA's Census Division (9 divisions)
3. **Cluster peers:** percentile rank within CBSAs sharing the same frame cluster label

Custom peer sets (e.g. user-defined geographic peers or size-matched peers) are supported as an optional fourth benchmark layer but are not part of the default model.

---

## Cross-Frame Overlap Acknowledgment

Several KPIs appear in more than one frame by design. The same metric can be evidence for different things:

- `pov_rate` — Livability (household burden) and Opportunity (trajectory context)
- `irs_net_migration_rate` — Character (residential stability) and Opportunity (market momentum)
- `permits_per_1000_housing_units` — Livability (housing supply) and Opportunity (market activity)
- `economic_connectedness` — Character (social fabric) and Opportunity (mobility proxy)
- `pop_weighted_density_sqmi` — Character (built form) and Livability (access proxy)

**Decision:** Cross-frame overlap is acknowledged and preserved. Metrics are not forced into a single frame. The cross-frame combined similarity model and the overlap check will surface where overlap is creating redundancy at the composite level.
