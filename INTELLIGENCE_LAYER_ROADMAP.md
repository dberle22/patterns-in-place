# Intelligence Layer Roadmap

*The Intelligence Layer is the analytical core of Patterns in Place: the scoring models, archetypes, and zone classifications that make the three frames (Character, Livability, Opportunity) say something meaningful. This roadmap covers the work from raw metrics to publishable Deep Dive findings. It is ordered by dependency, not by calendar.*

---

## What we're building

The Intelligence Layer is not a single artifact — it's a stack of decisions that compound:

```
Gold tables (facts)
    → Metric selection [Phase 0 — complete]
        → Variance + correlation passes (which inputs differentiate, which are redundant?)
            → Frame calibration (scoring models and archetypes)
                → intelligence_catalog.yml (formalized, not final)
                    → Zone methodology (tract-level clustering)
                        → First Deep Dives (Jacksonville + Richmond VA)
```

Every entry in `foundations/semantic_layer/intelligence_catalog.yml` is currently `status: placeholder`. The goal of this roadmap is to move them to `status: calibrated` through actual analysis — not through upfront spec work.

**Phase 0 is complete.** The confirmed, gap-annotated metric map lives at `exploration/intelligence_framework/docs/metric_map.md`.

---

## Scoring and Clustering Architecture

*These decisions were locked in after Phase 1 (Variable Selection) was complete. Every Phase 2–4 frame notebook follows this architecture. Do not relitigate these choices inside individual notebooks — document deviations here instead.*

---

### Universe

**Decision:** All 401 CBSAs (population ≥ 100K) are included in every model. CBSAs are never dropped due to missing KPI coverage.

**How missingness is handled:** Per-KPI, not per-CBSA. Each Phase 2–4 notebook opens with a coverage audit for its KPI set. KPIs with any missing values are imputed before modeling. KPIs with coverage problems severe enough to warrant removal are dropped from the model (with a documented rationale), not the CBSAs they're missing for.

---

### Missing Data — Imputation Strategy

**Decision:** Median imputation as the default. KNN imputation considered only when a KPI has >15% missingness AND the missing pattern is clearly non-random (e.g. a source that systematically excludes small metros).

**Implementation:**
- Replace missing values with the national median for that KPI across the 401-CBSA universe
- Log which KPIs triggered imputation and how many CBSAs were affected
- Flag imputed values in the output so downstream analysis can identify imputation-sensitive results

**Rationale:** Median imputation is fast, transparent, and appropriate when missingness is random or coverage-driven (e.g. ZORI not covering smaller metros). KNN adds complexity that is not justified for this universe size unless missingness is structurally biased.

---

### KPI Standardization and Polarity

**Decision:** All KPIs are standardized to z-scores before any clustering or scoring. A polarity flag is assigned to each KPI before Phase 3 and carried forward:

- **Positive polarity** (`+`): higher values are better (e.g. `life_expectancy`, `lfpr`, `income_pc_growth_5yr`)
- **Negative polarity** (`-`): lower values are better (e.g. `premature_death_rate`, `pct_rent_burden_30plus`, `pct_unemployment_rate`)

**For scoring:** Negative-polarity KPIs are sign-flipped before computing sub-scores so that a higher score always means better on every axis.

**For clustering and similarity:** Polarity does not matter — distance metrics are direction-agnostic. No sign-flip needed.

---

### Clustering Architecture

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

### Scoring Architecture

**Structure:** Hierarchical weighted averaging. Score flows upward through four levels:

```
KPI z-score (sign-flipped for negative polarity)
    → Topic score      (mean of KPI z-scores within topic)
        → Subject score    (weighted mean of topic scores within subject)
            → Frame composite  (weighted mean of subject scores)
                → Percentile rank  (0–100 within 401-CBSA universe)
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

**Final output:** Percentile rank (0–100) within the 401-CBSA universe. Percentile is the public-facing number — more interpretable than a raw z-score. Sub-scores at topic and subject level are also retained for drill-down analysis.

**Score anchoring:** Percentile ranks are relative to the current 401-CBSA universe. This is the correct default for the initial model. Anchoring scores to a base year for longitudinal comparability is a future calibration decision — flag it in the catalog entry when it becomes relevant.

---

### Similarity Scoring

**Method:** Cosine distance on the standardized KPI vectors (the same vectors used for clustering and scoring).

**Why cosine over Euclidean:** Cosine distance measures directional similarity — whether two metros are *shaped* the same way — rather than absolute magnitude. This is the right question for metro comparison: not "are these metros similar in size?" but "do they look like each other across the metric profile?"

**Three similarity matrices:**

1. **Frame-specific similarity** (three independent matrices — one per frame): "The metros most similar to Richmond VA on Livability" — computed on Livability KPI vectors only
2. **Cross-frame combined similarity** (one combined matrix): computed on the concatenated KPI vectors across all three frames — "the metros most like Richmond VA overall"
3. **Cross-frame overlap check**: compare cluster label assignments across frames to identify metros that are outliers on one frame but typical on another ("diverging from themselves" — key Deep Dive candidates)

**Frame independence:** Frames 2–4 are built and scored independently first. The cross-frame combined model is built after all three frame models are stable.

---

### Output Format

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

### Benchmark Strategy

Each CBSA score is benchmarked at three levels:

1. **National:** percentile rank within all 401 CBSAs
2. **Census Division:** percentile rank within the CBSA's Census Division (9 divisions)
3. **Cluster peers:** percentile rank within CBSAs sharing the same frame cluster label

Custom peer sets (e.g. user-defined geographic peers or size-matched peers) are supported as an optional fourth benchmark layer but are not part of the default model.

---

### Cross-Frame Overlap Acknowledgment

Several KPIs appear in more than one frame by design. The same metric can be evidence for different things:

- `pov_rate` — Livability (household burden) and Opportunity (trajectory context)
- `irs_net_migration_rate` — Character (residential stability) and Opportunity (market momentum)
- `permits_per_1000_housing_units` — Livability (housing supply) and Opportunity (market activity)
- `economic_connectedness` — Character (social fabric) and Opportunity (mobility proxy)
- `pop_weighted_density_sqmi` — Character (built form) and Livability (access proxy)

**Decision:** Cross-frame overlap is acknowledged and preserved. Metrics are not forced into a single frame. The cross-frame combined similarity model and the overlap check will surface where overlap is creating redundancy at the composite level.

---

## Deliverable formats

| Artifact type | Format | Location |
|---|---|---|
| Analysis notebooks | Quarto `.qmd` | `exploration/intelligence_framework/` |
| Methodology docs | Markdown `.md` | `exploration/intelligence_framework/docs/` |
| Catalog updates | YAML | `foundations/semantic_layer/intelligence_catalog.yml` |
| Publishable charts | Quarto-rendered HTML → ported to Substack | See Publishing section |

All Quarto notebooks should render to self-contained HTML. For Phases 2–5, the runner script plus phase-local outputs are the source of record for the build, and the review notebook is the source of record for visuals and written interpretation. The Substack post is a prose adaptation of those findings, not a separate document.

---

## Phase 0 — Metric Mapping ✓ Complete

**Output:** `exploration/intelligence_framework/docs/metric_map.md`

All three frames mapped to Gold table columns. Key gaps documented:
- Voting rates — MIT Election Lab not yet ingested (Track 21.1)
- Intergenerational mobility — Opportunity Atlas deferred (Track 14)
- Recreation / cultural amenities — Points layer (Tracks 16/17)
- K-12 learning quality (Stanford SEDA) — Track 22

Previously flagged gaps now resolved:
- `pct_family_single_parent` — in `gold.social_infra_wide` (Track 19.3.2b complete)
- `pov_rate_change_1yr` / `pov_rate_change_5yr` — in `gold.economics_income_wide` (Track 19.5.1 complete)
- Location quotients (`lq_*` by sector) — in `gold.economics_industry_wide` (Track 19.5.3 complete)
- `pct_ba_plus_change_5yr` — in `gold.population_demographics` (Track 19.5.2 complete)

---

## Phase 1 — Variable Selection (Variance + Correlation + PCA diagnostic)

**Status:** Complete
**Depends on:** Phase 0 (complete)
**Goal:** Identify the non-redundant, high-variance inputs for each frame. Three passes in a single notebook per frame: variance ranking → correlation matrix → PCA diagnostic.

**Scope:** CBSA grain only. ~380 CBSAs with population ≥ 100K. No county grain in this phase.

### Work per frame

**Character**
- Demographic composition: `median_age`, `pct_foreign_born`, `pct_ba_plus`, `diversity_index`, race/ethnicity shares (`pct_white_nh`, `pct_black_nh`, `pct_hispanic`, `pct_asian_nh`)
- Social fabric: `pct_same_house`, `mobility_rate`, `pct_moved_diff_st`, `irs_net_migration_rate`, `economic_connectedness`, `civic_engagement_volunteering_rate`
- Built form: `owner_occ_rate`, `pct_struct_multifam`, `pop_weighted_density_sqmi`

Look for: bimodality, geographic clustering, metrics that just reflect population size (drop those).

**Livability**
- Affordability: `pct_rent_burden_30plus`, `rent_to_income`, `value_to_income`, `rpp_real_pc_income`
- Mobility: `pct_commute_transit`, `mean_travel_time`, `pct_hh_0_vehicles`
- Health (CHR): `life_expectancy`, `premature_death_rate`, `physical_inactivity`, `adult_obesity`, `poor_mental_health_days`, `drug_overdose_death_rate`
- Safety: `homicide_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`
- Environment: `aqi_median`, `aqi_unhealthy_days`, `fema_risk_score`, `ej_pm25`
- Housing supply: `permits_per_1000_housing_units`, `permits_share_multifam_units`, `permits_avg_units_per_bldg`, `vacancy_rate`

Look for: regional patterning in health outcomes (Southern markets hypothesis), affordability bimodal split (coastal vs. interior), environmental risk clustering (Gulf Coast, Tornado Alley).

**Opportunity**
- Resident: `income_pc_growth_5yr`, `income_pc_growth_1yr`, `lfpr`, `pct_unemployment_rate`, `gini_index`
- Market: `hpi_5yr_pct`, `hpi_yoy_pct`, `zori_annual_avg_yoy_pct`, `pop_growth_5yr`, `irs_net_migration_rate`, `permits_per_1000_housing_units`
- Business / Industry: `real_gdp_growth_5yr`, `productivity_growth_5yr`, `industry_concentration_hhi`, `bfs_business_application_rate_per_1000_establishments`, sector shares / specialization signals (QCEW + LQ)
- Social: `economic_connectedness` (also a Character signal — flag the cross-frame overlap)

Look for: the leading indicator hypothesis (industry mix predicts income growth), bounce-back markets post-2020, markets where `irs_net_agi` and `pop_growth_5yr` diverge (income-selective migration).

**PCA is used as a diagnostic inside each notebook, not as the scoring approach.** It reveals how many independent dimensions the surviving metric set has and flags metrics with low communality. Final decisions are manual and theory-grounded so scores stay interpretable for publication.

**Specific pairs to test in each correlation pass:**
- Character: `diversity_index` vs. `pct_foreign_born` vs. race shares; `economic_connectedness` vs. `pct_ba_plus`
- Livability: `rent_to_income` vs. `pct_rent_burden_30plus` vs. `rpp_real_pc_income`; `homicide_rate` vs. `firearm_fatality_rate`; `fema_risk_score` vs. `aqi_unhealthy_days`
- Opportunity: `real_gdp_growth_5yr` vs. `income_pc_growth_5yr` vs. `pop_growth_5yr`; 1yr vs. 5yr signal divergence

### Tasks

- [ ] Run `phase_variable_selection/character_variable_selection.qmd` — variance + correlation + PCA + decisions
- [ ] Run `phase_variable_selection/livability_variable_selection.qmd` — includes Southern markets health hypothesis test
- [ ] Run `phase_variable_selection/opportunity_variable_selection.qmd` — includes 1yr vs. 5yr test and L/O scatter stub
- [ ] Write `phase_variable_selection/docs/metric_selections.md` with the final reduced set per frame
- [ ] Update `intelligence_catalog.yml` input lists to reflect the reduction

**Deliverable:** Three notebooks with variance rankings, correlation matrices, PCA scree plots, and written decisions. `metric_selections.md` updated. Stub for Article 1 Livability/Opportunity scatter (completed with calibrated scores in Phase 4).

---

## Phase 2 — Character Frame Model

**Status:** Complete
**Depends on:** Phase 1 metric selections; Architecture decisions (above — locked)
**Execution order:** Third, after Phases 3 and 4. Livability and Opportunity scoring are higher-priority unblocks for Area Explorer and the Chatbot. Character clustering requires a literature review step before labels can be defended, making it the slower pass.

**Goal:** Produce the full Character artifact set using the same modular pattern now established in Phases 3 and 4:
- a canonical runner script in `phase_2_character_calibration/R/`
- a review notebook that reads built artifacts from `phase_2_character_calibration/outputs/`
- scored, similarity, calibration, and interpretation-ready outputs in the phase-local `outputs/` folder

**Input set (from Phase 1 metric_selections.md — Character core):**
`diversity_index`, `pct_black_nh`, `pct_asian_nh`, `pct_hispanic`, `pct_age_over_64`, `pct_ba_plus`, `pct_foreign_born`, `pop_weighted_density_sqmi`, `friending_bias`, `civic_engagement_volunteering_rate`, `civic_organizations_per_1000`, `nonprofits_per_100k`, `irs_net_migration_rate`, `pct_moved_diff_st`, `pct_moved_abroad`, `social_associations_per_10k`, `pct_struct_multifam`

**Canonical workflow:**
1. `R/run_phase2_character.R` performs the catalog audit, frame build, completeness/imputation pass, clustering, scoring, similarity, and any Character-specific tests
2. `character_frame_model.qmd` reads the saved outputs for visual QA, cluster interpretation, and literature anchor review
3. canonical artifacts live in `exploration/intelligence_framework/phase_2_character_calibration/outputs/`

**Build sequence:**
1. Coverage audit — check missingness per KPI across the current `396`-CBSA modeling universe; apply median imputation; log affected KPIs and counts
2. Assign polarity flags per KPI
3. Standardize all inputs (z-score)
4. Hierarchical clustering — dendrogram, choose natural k; evaluate silhouette scores
5. K-Means at natural k — hard cluster assignments
6. GMM at same k — soft membership probabilities
7. Label clusters from centroids; evaluate against draft label set and literature anchors
8. Scoring — topic scores → subject scores → frame composite → percentile rank
9. Cosine similarity matrix — Character-specific peers
10. Written interpretation per cluster with named metro examples

**Draft label set to evaluate against:**
- Immigrant Gateway — high diversity + high foreign-born + younger age
- Creative Class / Knowledge Hub — high BA+, younger age, high in-migration of young adults
- Established / Rooted — low diversity, older age, low mobility, high homeownership
- College Town — high college enrollment relative to population
- Sunbelt Growth — fast population growth, younger, newer housing stock
- Rust Belt / Industrial — older vintage housing, declining population, mixed education

**Key tests:**
- Do groups reflect structural differences, or just population size and region? If size is dominating, normalize for it.
- Does `economic_connectedness` change cluster shapes vs. demographic-only inputs?
- Do soft GMM memberships reveal meaningful hybrid metros?

**Literature anchor (required before labeling):** Identify 2–3 published metro classification frameworks (Brookings, Pew Research metro typologies, Moretti's "Great Divergence") and document where clusters align or diverge. Write up in `docs/character_clustering_notes.md`.

### Tasks

- [x] Coverage audit and imputation pass for Character KPI set
- [x] Write `exploration/intelligence_framework/phase_2_character_calibration/R/run_phase2_character.R` — canonical Character build
- [x] Write `exploration/intelligence_framework/phase_2_character_calibration/character_frame_model.qmd` — review notebook over built artifacts
- [x] Document literature anchor comparisons in `docs/character_clustering_notes.md`
- [x] Produce cosine similarity output: top-10 Character peers per CBSA
- [x] Update `intelligence_catalog.yml` character entry from placeholder to specified methodology
- [x] Write outputs to `exploration/intelligence_framework/phase_2_character_calibration/outputs/character_scores.parquet`

**Expected outputs:**
- `outputs/character_scores.parquet`
- `outputs/character_phase2_cluster_count_calibration.csv`
- `outputs/character_phase2_cluster_centroids.csv`
- `outputs/character_phase2_similarity_top10.csv`
- `outputs/character_phase2_gmm_summary.csv`
- `outputs/character_phase2_cluster_representatives.csv`

**Completed summary:** Phase 2 is now calibrated in `exploration/intelligence_framework/phase_2_character_calibration/`. The final build keeps the full `17`-KPI Character set, accepts bounded median imputation for the single missing `social_fabric_wide` row, uses `k = 7`, includes tuned GMM soft memberships, and ships a review notebook, literature-anchor notes, phase-local outputs, and an updated Character catalog entry.

**Deliverable:** `R/run_phase2_character.R` builds the canonical Character artifacts, and `character_frame_model.qmd` reviews them with cluster visuals, soft memberships, similarity, and literature-anchored interpretation. Feeds Article 2 ("A new map of American metros").

---

## Phase 3 — Livability Frame Model

**Status:** Complete (L/O scatter stub unblocked — Phase 4 now complete)
**Depends on:** Phase 1 metric selections; Architecture decisions (above — locked)
**Execution order:** First. Livability + Opportunity together produce Article 1 (the Livability/Opportunity scatter), which is the highest-value near-term publishable output and the clearest connection to the ROADMAP.md flywheel.

**Goal:** Produce all three outputs for the Livability frame: cluster labels (Livability types), scored sub-scores + composite percentile, and similarity vectors.

**Kickoff note (2026-06-17):** `exploration/intelligence_framework/phase_3_livability_calibration/R/run_phase3_livability.R` is now the primary execution surface for Phase 3. It handles the semantic-catalog KPI audit, the `396`-CBSA Livability input frame build, the completeness review, the polarity audit, the median-imputation pass, the PCA/correlation redundancy review, the full clustering / scoring / similarity output, the `k = 5` vs `k = 6` calibration comparison, GMM soft memberships, human-readable cluster naming, and the two Phase 3 hypothesis-test datasets. `exploration/intelligence_framework/phase_3_livability_calibration/livability_frame_model.qmd` is now a review notebook that reads those built artifacts for visual QA and interpretation. Puerto Rico is excluded from the current modeling universe. The Connecticut crosswalk rebuild and the `gold.environment_wide` geography fix are reflected in the current coverage outputs. Phase artifacts now live under `exploration/intelligence_framework/phase_3_livability_calibration/outputs/`. The chosen default Livability calibration keeps all 26 KPIs for clustering and uses `k = 6` for the published typology.

**Reference workflow for later phases:** Phase 3 is now the template for Phases 2, 4, and 5:
- build logic is split across `R/phase3_*.R`
- `R/run_phase3_livability.R` is the canonical runner
- `livability_frame_model.qmd` is a review notebook only
- all canonical artifacts live under `phase_3_livability_calibration/outputs/`

**Input set (from Phase 1 metric_selections.md — Livability core):**

*Recurring core:*
`value_to_income`, `pct_rent_burden_30plus`, `pov_rate`, `permits_per_1000_housing_units`, `permits_share_units_5_plus`, `pct_struct_mobile`, `pct_struct_small_mf`, `pct_struct_mid_mf`, `premature_death_rate`, `mental_health_provider_ratio`, `drug_overdose_death_rate`, `pct_uninsured_adults`, `preventable_hospital_stay_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`, `pct_commute_walk`, `pct_commute_wfh`, `vacancy_rate`, `pct_hh_0_vehicles`, `pct_no_internet_access`

*Supplemental baseline / coverage-caution (weighted at 0.60–0.75):*
`walkability_index`, `jobs_access_45min_transit`, `pct_population_low_income_low_access_1_10`, `pop_weighted_density_sqmi`, `aqi_unhealthy_days`, `fema_risk_score`

**Subject structure and initial weights:**
- `Affordability`: 0.25 — topics: Price Pressure, Housing Burden, Poverty Context, Housing Supply, Housing Structure Mix
- `Health & Safety`: 0.25 — topics: Health Outcomes, Health Behavior & Access, Violence & Injury
- `Access & Infrastructure`: 0.25 — topics: Commute & Mode, Vehicle Access, Housing Slack, Digital Access, Walkability baseline, Food Access baseline, Built-Form Proxy
- `Physical Environment`: 0.25 — topics: Air Pollution, Climate Hazard Risk (both coverage-caution weighted)

**Build sequence:**
1. Coverage audit — check missingness per KPI across the current `396`-CBSA modeling universe; apply median imputation; log affected KPIs and counts
2. Assign polarity flags per KPI (note: most Livability KPIs are negative-polarity — lower is better)
3. Standardize all inputs (z-score); sign-flip negative-polarity KPIs for scoring
4. Hierarchical clustering — dendrogram, choose natural k; evaluate silhouette scores
5. K-Means at natural k — hard cluster assignments (Livability type labels)
6. GMM at same k — soft membership probabilities
7. Label clusters from centroids; name Livability types
8. Scoring — topic → subject → frame composite → percentile rank (per architecture above)
9. Cosine similarity matrix — Livability-specific peers
10. Key hypothesis tests (see below)
11. Written interpretation per cluster with named metro examples

**Key hypothesis tests:**
- Southern markets health hypothesis: do metros that score well on Affordability score poorly on Health? (Article 3)
- Environmental risk axis: does `fema_risk_score` add non-redundant signal beyond `aqi_unhealthy_days`?
- Livability / Opportunity scatter: combine Livability percentile with Opportunity percentile to produce the four-quadrant view (Article 1)

**Smell test:** Does the Affordability topic rank NYC / coastal metros at the bottom and Midwest interior metros near the top? If not, revisit polarity or weighting before proceeding.

### Tasks

- [x] Coverage audit and imputation pass for Livability KPI set
- [x] Assign polarity flags to all Livability KPIs
- [x] Write `exploration/intelligence_framework/phase_3_livability_calibration/R/run_phase3_livability.R` — full clustering + scoring + similarity pass
- [x] Refactor `exploration/intelligence_framework/phase_3_livability_calibration/livability_frame_model.qmd` into a review notebook over built artifacts
- [x] Test Southern markets health hypothesis: affordability sub-score vs. health sub-score scatter
- [x] Test environmental risk axis: `fema_risk_score` vs. `aqi_unhealthy_days` non-redundancy check
- [x] Produce Livability/Opportunity scatter with Opportunity scores after Phase 4
- [x] Produce cosine similarity output: top-10 Livability peers per CBSA
- [x] Update `intelligence_catalog.yml` Livability entries from placeholder to specified methodology
- [x] Write outputs to `exploration/intelligence_framework/phase_3_livability_calibration/outputs/livability_scores.parquet`

**Deliverable:** `R/run_phase3_livability.R` builds the canonical Livability artifacts, and `livability_frame_model.qmd` reviews them with cluster visuals, soft-membership summaries, similarity highlights, and written interpretation. Two publishable findings: Livability/Opportunity scatter (Article 1, completed with Phase 4), Health vs. Affordability scatter (Article 3).

---

## Phase 4 — Opportunity Frame Model

**Status:** Complete
**Depends on:** Phase 1 metric selections; Architecture decisions (above — locked)
**Execution order:** Second, immediately after Phase 3. Opportunity scores complete the Livability/Opportunity scatter (Article 1).

**Goal:** Produce the full Opportunity artifact set using the same modular pattern as Phase 3:
- a canonical runner script in `phase_4_opportunity_calibration/R/`
- a review notebook that reads built artifacts from `phase_4_opportunity_calibration/outputs/`
- scored, similarity, calibration, and hypothesis-test outputs in the phase-local `outputs/` folder

**Input set (from Phase 1 metric_selections.md — Opportunity core):**
`income_pc_growth_5yr`, `pct_unemployment_rate`, `lfpr`, `pov_rate_change_5yr`, `qcew_private_avg_wkly_wage`, `hpi_5yr_pct`, `hpi_yoy_pct`, `zori_annual_avg_yoy_pct`, `pop_growth_5yr`, `irs_net_migration_rate`, `irs_net_agi`, `permits_per_1000_housing_units`, `permits_share_units_5_plus`, `productivity_growth_5yr`, `industry_concentration_hhi`, `bfs_business_application_rate_per_1000_establishments`, `cbp_estabs_per_1000_residents`, `pct_ba_plus_change_5yr`, `lq_professional`, `lq_information`, `lq_manufacturing`, `pct_real_gdp_information`

**Subject structure and initial weights:**
- `Resident Opportunity`: 0.33 — topics: Income Growth, Wage Levels, Labor Market Tightness, Poverty & Inclusion, Intergenerational Mobility Proxy
- `Market / Investor Opportunity`: 0.33 — topics: Home Price Appreciation, Rent Growth, Population Growth, Migration & Wealth Flows, Permit Activity
- `Business & Industry Opportunity`: 0.33 — topics: GDP Growth, Industry Concentration, Human Capital Momentum, Business Formation, Establishment Density, Location Quotient Specialization, Sector GDP Mix

**Note on ZORI coverage:** `zori_annual_avg_yoy_pct` has ~48% topic-level coverage once level fields are included. Carry the YoY growth field only; impute missing CBSAs at the national median. Flag this as a coverage-caution KPI in the output.

**Note on cross-frame overlap:** `permits_per_1000_housing_units`, `irs_net_migration_rate`, and `pov_rate` appear in both Livability and Opportunity. This is intentional — they serve different conceptual roles in each frame. Acknowledge in the notebook; do not remove.

**Canonical workflow:**
1. `R/run_phase4_opportunity.R` performs the catalog audit, frame build, completeness/imputation pass, clustering, scoring, similarity, and Opportunity-specific tests
2. `opportunity_frame_model.qmd` reads the saved outputs for visual QA, cluster interpretation, and the Livability/Opportunity scatter review
3. canonical artifacts live in `exploration/intelligence_framework/phase_4_opportunity_calibration/outputs/`

**Build sequence:**
1. Coverage audit — check missingness per KPI across 401 CBSAs; apply median imputation; log affected KPIs and counts; flag ZORI specifically
2. Assign polarity flags per KPI (note: mixed polarity — `pct_unemployment_rate` and `industry_concentration_hhi` are negative; most others are positive)
3. Standardize all inputs (z-score); sign-flip negative-polarity KPIs for scoring
4. Hierarchical clustering — dendrogram, choose natural k; evaluate silhouette scores
5. K-Means at natural k — hard cluster assignments (Opportunity type labels)
6. GMM at same k — soft membership probabilities
7. Label clusters from centroids; name Opportunity types
8. Scoring — topic → subject → frame composite → percentile rank (per architecture above)
9. Cosine similarity matrix — Opportunity-specific peers
10. Key hypothesis tests (see below)
11. Complete the Livability/Opportunity scatter with Phase 3 Livability percentiles (Article 1)
12. Written interpretation per cluster with named metro examples

**Key hypothesis tests:**
- Industry mix as leading indicator: does industry mix in 2015 (QCEW) predict income growth by 2022? Test longitudinally. (Article 4)
- Social capital as Opportunity signal: `economic_connectedness` vs. `income_pc_growth_5yr` scatter — does who you know predict income growth beyond industry mix? (Article 5)
- 1yr vs. 5yr signal divergence: do short-run and long-run signals tell different stories for the same metros?
- OZ exposure: flag `pct_oz_tracts` from `gold.dim_policy_designations` as a contextual overlay — which high-momentum metros have significant OZ exposure?
- Livability / Opportunity four quadrants: unicorns (high/high), pleasant-but-stagnant (high L / low O), high-growth-expensive (low L / high O), distress cases (low/low)

### Tasks

- [x] Coverage audit and imputation pass for Opportunity KPI set; flag ZORI coverage issue explicitly
- [x] Assign polarity flags to all Opportunity KPIs
- [x] Write `exploration/intelligence_framework/phase_4_opportunity_calibration/R/run_phase4_opportunity.R` — canonical Opportunity build
- [x] Write `exploration/intelligence_framework/phase_4_opportunity_calibration/opportunity_frame_model.qmd` — review notebook over built artifacts
- [x] Test industry-as-leading-indicator hypothesis longitudinally (QCEW 2010–2024 backfill)
- [x] Test social capital → income growth hypothesis: `economic_connectedness` vs. `income_pc_growth_5yr`
- [x] Test 1yr vs. 5yr signal divergence across resident and market subjects
- [x] Flag CBSA OZ exposure as contextual field
- [x] Complete Livability/Opportunity scatter (four-quadrant plot) using Phase 3 percentiles
- [x] Produce cosine similarity output: top-10 Opportunity peers per CBSA
- [x] Update `intelligence_catalog.yml` Opportunity entries from placeholder to specified methodology
- [x] Write outputs to `exploration/intelligence_framework/phase_4_opportunity_calibration/outputs/opportunity_scores.parquet`

**Expected outputs:**
- `outputs/opportunity_scores.parquet`
- `outputs/opportunity_phase4_cluster_count_calibration.csv`
- `outputs/opportunity_phase4_cluster_centroids.csv`
- `outputs/opportunity_phase4_similarity_top10.csv`
- `outputs/opportunity_phase4_gmm_summary.csv`
- `outputs/opportunity_phase4_livability_opportunity_scatter.csv`

**Checkpoint log:**
- 2026-06-17: Modular Phase 4 scaffold created under `phase_4_opportunity_calibration/` with a checkpoint-first runner, review notebook shell, and checkpoint 1 catalog outputs.
- 2026-06-17: Checkpoint 1 complete. The expected Opportunity KPI set was audited against `metric_catalog.yml` and `intelligence_catalog.yml`; all expected KPIs were found, all source-column mappings matched, and all polarity flags were present. `economic_connectedness` is carried as a proxy audit-only KPI and not yet included in the default clustering set.
- 2026-06-18: Checkpoint 2 complete. Built the Opportunity KPI frame, wrote completeness and median-imputation outputs, and preserved per-metric polarity flags. We are accepting the current Connecticut `2022`-forward history limitation for ACS-derived 5-year change metrics in this calibration pass. Waterbury plus the BEA-affected Danville / Harrisonburg / Staunton / Kahului set are carried forward as imputation-sensitive metros rather than blocking Phase 4 on upstream ETL repairs.
- 2026-06-18: Checkpoint 3 evidence built. Wrote the Opportunity redundancy / PCA audit plus side-by-side cluster-count calibration outputs for the full KPI set and a provisional PCA-recommended reduced set. The evidence pass is ready for a user decision on the clustering input set and final `k`.
- 2026-06-18: Checkpoint 4 evidence built. Activated the reduced clustering set for Opportunity (`pct_real_gdp_information` and `permits_per_1000_housing_units` held out from clustering), wrote side-by-side `k = 5` and `k = 6` reduced-set clustering outputs, and saved the cluster sizes, assignments, centroids, representative metros, and `k5` to `k6` split diagnostics for user review before locking the final Opportunity type count.
- 2026-06-18: Checkpoint 4 decision confirmed. We are carrying the reduced clustering set forward and locking `k = 6` as the final Opportunity hard-cluster count, accepting a slightly lower `k`-means silhouette in exchange for a more realistic and narratively useful subtype split supported by the hierarchical structure.
- 2026-06-18: Checkpoint 5 first pass built. Wrote the full `k = 6` Opportunity artifacts including named clusters, GMM soft-membership summaries, top-10 similarity peers, a first social-capital test, a first 1-year vs. 5-year divergence test, and the Livability/Opportunity four-quadrant scatter. The remaining review step is naming and interpretation tuning, plus follow-up work on the OZ contextual overlay because the current policy-designation tables do not yet expose a populated CBSA rollup.
- 2026-06-18: Phase 4 review layer completed. The Opportunity notebook now reads the built artifacts from `outputs/`, and the Opportunity entry in `intelligence_catalog.yml` now reflects the calibrated reduced-set `k = 6` methodology instead of placeholder `TBD` notes. The remaining Opportunity gap is the upstream CBSA OZ overlay rollup, which is being handled separately.
- 2026-06-18: Phase 4 completed. The CBSA Opportunity Zones overlay is now available through `gold.dim_policy_designations`, the Opportunity notebook now surfaces OZ context using both `pct_oz_tracts` and `pct_population_in_oz`, and the Phase 4 folder now includes a README that documents the final cluster choices and the reduced-set `k = 6` calibration rationale.

**Deliverable:** `R/run_phase4_opportunity.R` builds the canonical Opportunity artifacts, and `opportunity_frame_model.qmd` reviews them with cluster visuals, soft memberships, similarity, and hypothesis interpretation. Three publishable findings: Livability/Opportunity four-quadrant scatter (Article 1), industry mix as leading indicator (Article 4), social capital as hidden differentiator (Article 5).

---

## Phase 5 — Cross-Frame Combined Model

**Status:** Complete
**Depends on:** Phases 2, 3, and 4 — all three frame models must be stable before this runs
**Goal:** Produce the combined cross-frame clustering, similarity scoring, and overlap analysis. Answer: which metros are alike *overall*, and which metros are diverging across frames?

**This is a distinct phase from Phase 6 (Trajectory Analysis).** Phase 5 is about *simultaneous position* across all three frames (clustering + similarity on the full vector). Phase 6 is about *movement over time* within each frame. Both produce Deep Dive candidate lists, but through different lenses.

**PCA note:** The combined KPI vector across all three frames will be large and heavily redundant. Run a heavy PCA pass before any clustering — identify the KPIs that are doing real discriminatory work and drop the rest from the model. Dropped KPIs are not lost: carry them as descriptive context columns in the output so they can be used for cluster interpretation and narration. The goal is the most meaningful model, not the most complete one.

**Canonical workflow:**
1. `R/run_phase5_cross_frame.R` loads the stable Phase 2–4 outputs, builds the combined vector, runs the PCA reduction, then clustering and overlap logic, and writes all canonical artifacts
2. `cross_frame_model.qmd` reads those built outputs for visual QA, overlap review, and candidate-market interpretation; PCA diagnostics are the first section
3. canonical artifacts live in `exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/`

**Build sequence:**
1. Load the three frame score parquets (`livability_scores.parquet`, `opportunity_scores.parquet`, `character_scores.parquet`)
2. Join to the `396`-CBSA non-Puerto-Rico spine on `cbsa_code`
3. Concatenate the standardized KPI vectors from all three frames into a single combined vector per CBSA
4. **PCA reduction pass** — scree plot, cumulative variance explained, loading review; drop KPIs with low communality or that are clearly proxies for retained KPIs; document every drop; carry dropped KPIs as descriptive columns only
5. Run hierarchical clustering on the **PCA-reduced** KPI set — find natural k for the cross-frame typology
6. K-Means at natural k — hard cross-frame cluster assignments ("Combined Type" labels)
7. GMM at same k — soft cross-frame membership probabilities
8. Cosine distance on the reduced KPI set — cross-frame similarity matrix; top-10 overall peers per CBSA
9. Cross-frame overlap check: compare frame-specific cluster assignments to identify "diverging from themselves" metros (e.g. high Livability cluster but low Opportunity cluster)
10. Written interpretation using both the clustering KPIs and the full descriptive KPI set: what do cross-frame outliers look like? Which CBSAs are most coherent across frames vs. most contradictory?

**Key outputs:**
- Combined cluster label per CBSA ("Combined Type")
- GMM soft memberships for the combined model
- Cross-frame cosine similarity: top-10 overall peers per CBSA
- Cross-frame overlap flag: CBSAs where frame-specific cluster assignments diverge meaningfully
- Ranked cross-frame divergence heuristic candidate list — the primary review surface for metros where the three frame stories conflict, hybridize, or sit at cluster edges

**Key questions to answer:**
- Do the cross-frame clusters largely reproduce one frame's structure, or do they reveal genuinely new groupings?
- Which CBSAs are internally coherent (same cluster tier across all three frames) vs. genuinely contradictory?
- Does the combined similarity matrix produce more useful peer sets than any single-frame matrix alone?

### Tasks

- [x] Concatenate the standardized KPI vectors from all three frames into the combined input matrix
- [x] Run a heavy PCA pass on the combined vector — retain KPIs that contribute meaningfully (scree plot + loadings review); drop redundant or low-communality KPIs from the clustering input set; document every drop with rationale
- [x] Write `exploration/intelligence_framework/phase_5_cross_frame_integration/R/run_phase5_cross_frame.R` — canonical cross-frame build using the PCA-reduced KPI set for clustering; carry all original KPIs as descriptive context columns in the output
- [x] Write `exploration/intelligence_framework/phase_5_cross_frame_integration/cross_frame_model.qmd` — review notebook over built artifacts; include PCA diagnostic visuals (scree, loadings heatmap, variance explained) as the first section
- [x] Produce cross-frame cosine similarity matrix on the reduced KPI set; top-10 overall peers per CBSA
- [x] Produce cross-frame overlap flag; rank CBSAs by degree of frame divergence
- [x] Write outputs to `exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_scores.parquet` — scoring columns use the reduced set; descriptive KPI columns carried alongside for interpretation
- [x] Produce ranked Deep Dive candidate list from cross-frame analysis
- [x] Confirm Jacksonville and Richmond VA appear in the candidate set (or document why they're selected despite ranking)

**Progress note:** The completed Phase 5 build runs from `exploration/intelligence_framework/phase_5_cross_frame_integration/`. The combined model starts from the published `63`-KPI bundle, compares lean `18`-KPI and moderate `35`-KPI reductions, locks the final default to the `35`-KPI set, and calibrates the first full combined typology at `k = 6`. The final outputs include the combined score parquet, PCA and KPI decision logs, cluster calibration comparisons, similarity peers, overlap flags, named cluster profiles, and a ranked cross-frame divergence heuristic candidate list. That candidate list is intentionally not a generic market-quality ranking; it is a review surface for metros where frame divergence, hybrid cluster membership, and cluster-edge behavior are strongest. Jacksonville, FL appears in the final candidate list at rank `95`, and Richmond, VA appears at rank `380`, so both are present but not top-ranked under the current divergence-focused scoring.

**Expected outputs:**
- `outputs/cross_frame_scores.parquet`
- `outputs/cross_frame_phase5_pca_loadings.csv` — full loading matrix; basis for the drop decisions
- `outputs/cross_frame_phase5_pca_variance.csv` — cumulative variance explained
- `outputs/cross_frame_phase5_kpi_decisions.csv` — one row per KPI: kept/dropped, reason, communality
- `outputs/cross_frame_phase5_cluster_count_calibration.csv`
- `outputs/cross_frame_phase5_similarity_top10.csv`
- `outputs/cross_frame_phase5_overlap_flags.csv`
- `outputs/cross_frame_phase5_candidate_list.csv`

**Deliverable:** `phase_5_cross_frame_integration/R/run_phase5_cross_frame.R` builds the canonical cross-frame artifacts, and `phase_5_cross_frame_integration/cross_frame_model.qmd` reviews them with combined cluster visuals, similarity, overlap analysis, and divergence-heuristic candidate interpretation. Primary output feeds Deep Dive market selection.

---

## Phase 6 — Trajectory + Divergence Analysis

**Status:** Not started
**Depends on:** Phases 2–5 complete (uses both raw KPI time series AND calibrated frame scores)
**Goal:** Add a temporal lens to the static cross-frame picture. Find which CBSAs are moving — diverging from or converging toward the national mean — and how fast. The primary output is a ranked Deep Dive candidate list. Articles 7 and 8 are publishable findings that surface from that analysis.

---

### Architecture

**Two simultaneous passes, both equally weighted:**

1. **Momentum pass** — velocity and acceleration. Which CBSAs are changing fastest, and in which direction? A metro that is average today but moving fast is as interesting as one that is already an outlier.

2. **Outlier pass** — distance from the national mean. Which CBSAs are furthest from the 401-CBSA average, and are they moving further away or returning toward it?

**Output per CBSA:** a composite trajectory score that combines both passes — high scores mean "far from the mean AND moving fast (in either direction)."

**Convergence is included.** A metro recovering from a distress extreme (bounce-back) or cooling from a hot market (normalization) is analytically as interesting as one diverging. Segment output by direction: diverging-outward vs. converging-inward, and within each, improving vs. declining.

---

### Input sources

**Primary (trajectory input):** Raw KPI time series from the Phase 1 recurring annual core per frame. These are the KPIs that survived the variance filter and have multi-year history in Gold tables.

**Secondary (output expression):** Calibrated Phase 3/4/2 frame scores and Phase 5 cross-frame scores. Trajectory findings are expressed as "this metro's Livability score trajectory is improving / declining" to connect to the published frame architecture.

**KPI coverage rules for Phase 6:**
- **Exclude:** Single-vintage sources — SLD (`walkability_index`, `jobs_access_45min_transit`) and USDA Food Access (`pct_population_low_income_low_access_1_10`). Trajectory is meaningless for one-time baselines.
- **Exclude:** Connecticut CBSAs from any ACS-derived 5-year change metrics (consistent with Phase 4 accepted limitation; document in output). Treat as missing rather than imputing trajectory for affected metros.
- **Include with care:** ZORI (`zori_annual_avg_yoy_pct`) — structural coverage gaps were resolved; carry forward with coverage annotation per CBSA in the output.
- **Default to recurring annual KPI series** for all other trajectory inputs. Single-vintage and one-time sources are carried as static context columns in the output, not as trajectory signals.

---

### Time windows

**Frame-dependent:**

- **Character:** 5-year window only. Demographic and social-fabric metrics are slow-moving; 1-year moves are mostly noise.
- **Livability:** 5-year window only. Health, safety, and infrastructure metrics are structurally slow; 1-year pass is a sensitivity check only.
- **Opportunity:** Both 1-year and 5-year windows, explicitly compared. Flag metros where short-run (1yr) direction contradicts medium-term trend (5yr) — that divergence is itself a finding ("turn signal" metros).

---

### Key patterns to surface

**All four patterns are run as a single trajectory scan — none is pre-ranked. Let the data determine which are most populated and most interesting.**

1. **"Bounce-back" markets** — high 2020 distress (Opportunity KPIs at low values) + fastest 5yr recovery. Converging from below. Article 7.

2. **"Hidden Livability winners"** — affordable + improving health + decent labor, low national profile. CBSAs whose Livability trajectory is improving but whose Phase 5 combined score is still mid-tier (i.e., not already well-known). Diverging-outward in a positive direction. Article 8.

3. **"Diverging from themselves"** — a CBSA where one frame's trajectory is improving while another's is declining. Cross-reference with the Phase 5 cross-frame overlap flag: metros flagged by Phase 5 as positionally divergent AND showing trajectory divergence are the highest-priority Deep Dive candidates.

4. **Fast demographic changers** — CBSAs where Character KPIs are shifting fastest over 5 years. Surface metros where `pct_foreign_born`, `diversity_index`, `pct_ba_plus_change_5yr`, or residential stability metrics are moving fastest relative to the national mean.

5. **Environmental risk outliers** — CBSAs where `fema_risk_score` + `aqi_unhealthy_days` are both moving in the wrong direction. Diverging-outward in a negative direction on two independent Livability axes simultaneously.

---

### File structure

Phase 6 follows the same modular R pattern as prior phases, but the review layer is split into one focused notebook per analysis rather than a single monolith. Each notebook reads pre-built artifacts only.

```
exploration/intelligence_framework/phase_6_trajectory/
  R/
    phase6_config.R                    ← KPI sets, coverage rules, time windows, shared constants
    phase6_frame_build.R               ← load recurring-annual KPI series from Gold; apply coverage rules
    phase6_trajectory_core.R           ← momentum pass + outlier pass; composite trajectory scores; direction segmentation
    phase6_opportunity_turn_signals.R  ← Opportunity-only 1yr vs. 5yr divergence check
    phase6_patterns.R                  ← five pattern filters; pattern summary table
    phase6_candidate_list.R            ← ranked candidate list; Phase 5 overlap enrichment
    run_phase6_trajectory.R            ← canonical runner; sources all modules in order
  notebooks/
    01_trajectory_overview.qmd         ← KPI trajectory heatmaps; frame-level score distributions; direction segmentation
    02_bounce_back.qmd                 ← bounce-back pattern deep dive; Article 7 stub
    03_hidden_livability_winners.qmd   ← hidden winners pattern; Article 8 stub
    04_diverging_from_themselves.qmd   ← cross-frame divergence pattern; Phase 5 overlap enrichment
    05_fast_demographic_changers.qmd   ← Character trajectory fast-movers
    06_environmental_risk_outliers.qmd ← environmental risk outliers; dual-axis movement
    07_candidate_list.qmd              ← ranked Deep Dive candidate list; combined pattern scoring; JAX + RVA check
    08_opportunity_turn_signals.qmd    ← Opportunity 1yr vs. 5yr divergence matrix
  outputs/
    trajectory_scores.parquet          ← one row per CBSA; all trajectory columns (canonical)
    phase6_kpi_trajectory_long.csv     ← long-format per-CBSA per-KPI trajectory; interpretation layer
    phase6_pattern_summary.csv         ← one row per pattern; CBSA count + top-10 examples
    phase6_opp_turn_signals.csv        ← Opportunity 1yr vs. 5yr divergence output
    phase6_candidate_list.csv          ← ranked Deep Dive candidate list (primary Phase 6 output)
```

---

### Build sequence

**Runner:** `R/run_phase6_trajectory.R` sources all `R/phase6_*.R` modules in order and writes all outputs. The notebooks read from `outputs/` only — no Gold table queries inside notebooks.

1. `phase6_frame_build.R` — load recurring-annual KPI series from Gold; apply coverage rules (drop CT from ACS change metrics, drop SLD and USDA single-vintage sources, carry ZORI with per-CBSA annotation flag)
2. `phase6_trajectory_core.R` — compute 1yr and 5yr change per KPI per CBSA (frame-dependent); compute z-score position and z-score of change against 396-CBSA universe; combine into composite trajectory score (equal weight, momentum + outlier); segment CBSAs into 4-way direction buckets
3. `phase6_opportunity_turn_signals.R` — Opportunity only: flag CBSAs where 1yr direction contradicts 5yr trend
4. `phase6_patterns.R` — apply five pattern filters; write `phase6_pattern_summary.csv`
5. `phase6_candidate_list.R` — join Phase 5 `cross_frame_phase5_overlap_flags.csv`; compute combined candidate score; write `phase6_candidate_list.csv`

---

### Output format

**Columns per CBSA in `trajectory_scores.parquet`:**

- `cbsa_code`, `cbsa_name`, `census_division`
- Per-frame composite trajectory score (signed): `character_trajectory_score`, `livability_trajectory_score`, `opportunity_trajectory_score`
- Per-frame trajectory direction: `character_direction`, `livability_direction`, `opportunity_direction` (4-way: diverging-improving / diverging-declining / converging-improving / converging-declining)
- Opportunity divergence flag: `opp_turn_signal`
- Phase 5 overlap rank: `phase5_overlap_rank` (joined from Phase 5 output)
- Pattern flags: `is_bounce_back`, `is_hidden_livability_winner`, `is_diverging_from_themselves`, `is_fast_demographic_changer`, `is_environmental_risk_outlier`
- `candidate_score` — combined Deep Dive candidate score (weighted sum of pattern flags × trajectory strength)
- `ct_exclusion_flag` — TRUE for CBSAs excluded from ACS change metrics
- `zori_coverage_flag` — TRUE for CBSAs where ZORI was imputed or annotated

---

### Tasks

**Runner and modules:**
- [x] Write `R/phase6_config.R` — KPI sets per frame (recurring annual only), coverage rules, time window constants
- [x] Write `R/phase6_frame_build.R` — load Gold tables; apply coverage rules; output long-format KPI series per frame
- [x] Write `R/phase6_trajectory_core.R` — momentum + outlier passes; composite score; direction segmentation; write `trajectory_scores.parquet` and `phase6_kpi_trajectory_long.csv`
- [x] Write `R/phase6_opportunity_turn_signals.R` — 1yr vs. 5yr divergence check; write `phase6_opp_turn_signals.csv`
- [x] Write `R/phase6_patterns.R` — five pattern filters; write `phase6_pattern_summary.csv`
- [x] Write `R/phase6_candidate_list.R` — Phase 5 overlap join; candidate scoring; write `phase6_candidate_list.csv`
- [x] Write `R/run_phase6_trajectory.R` — sources all modules in order

**Review notebooks (each reads `outputs/` only):**
- [x] Write `notebooks/01_trajectory_overview.qmd` — KPI heatmaps, score distributions, direction segmentation
- [x] Write `notebooks/02_bounce_back.qmd` — bounce-back pattern; Article 7 stub findings
- [x] Write `notebooks/03_hidden_livability_winners.qmd` — hidden winners pattern; Article 8 stub findings
- [x] Write `notebooks/04_diverging_from_themselves.qmd` — cross-frame divergence; Phase 5 overlap enrichment
- [x] Write `notebooks/05_fast_demographic_changers.qmd` — Character fast-movers
- [x] Write `notebooks/06_environmental_risk_outliers.qmd` — dual-axis environmental risk movement
- [x] Write `notebooks/07_candidate_list.qmd` — ranked candidate list; JAX + RVA position check
- [x] Write `notebooks/08_opportunity_turn_signals.qmd` — Opportunity 1yr vs. 5yr divergence matrix

**Documentation:**
- [x] Write `README.md` in `phase_6_trajectory/` — methodology guide covering direction segmentation, trajectory scoring, pattern defaults, candidate ranking logic, and coverage limitations

**Deliverable:** `R/run_phase6_trajectory.R` builds all canonical Phase 6 artifacts. Eight focused review notebooks cover each analysis independently. `phase6_candidate_list.csv` is the primary output — a ranked Deep Dive candidate list enriched with Phase 5 cross-frame context. Feeds Phase 7 Zone Methodology market selection, Article 7 (bounce-back markets), and Article 8 (hidden Livability winners).

---

## Phase 7 — Zone Methodology Definition

**Status:** Not started
**Depends on:** Phases 3–5 frame definitions (needs frame cluster labels and scored KPI vectors)
**Goal:** Define the tract-level clustering approach that produces the Zone Analysis section of every Metro Deep Dive. Test it against Jacksonville and Richmond VA in parallel.

**Clustering architecture:**
Three cluster models, built and compared:
1. **Character zones** — demographic archetype at tract level (who lives here)
2. **Opportunity zones** — economic momentum at tract level (what's happening here)
3. **Cross-theme zones** — the primary map shown in the Deep Dive report; blends all three frames

**Input candidates (tract level):**
- Character: race/ethnicity shares, `median_age`, `pct_foreign_born`, `pct_ba_plus`, `pct_same_house`, `pop_weighted_density_sqmi`
- Livability: `pct_rent_burden_30plus`, `rent_to_income`, `value_to_income`, housing vintage; `aqi_median` + `fema_risk_score` where available at tract
- Opportunity: `income_pc_growth_5yr`, home price appreciation (`hpi_5yr_pct`), `pct_unemployment_rate`, permit density; `is_opportunity_zone` flag from `gold.dim_policy_designations`

**Methodology options to evaluate:**
- K-means on standardized tract metrics (simple, interpretable — start here)
- Hierarchical clustering (better for natural group count discovery)
- Latent class analysis (probabilistic, handles mixed types — evaluate if k-means feels fuzzy)

**Target zone label set (6–8 types, evaluate against what data produces):**
- Core Hub — dense, diverse, high-activity urban core
- Established Residential — stable, owner-occupied, slow-changing
- Transitional / Emerging — demographic shift, rising prices, mixed signals
- Affordable Fringe — lower cost, lower income, accessible to workforce
- Knowledge / Creative Corridor — high education, professional, younger population
- Growth Periphery — fast-growing suburban, new construction, family-oriented
- Distressed — declining population, high poverty, disinvestment signals

**National vs. per-market decision:** Build the national model first. Per-market calibration can follow if the national model produces incoherent results for a specific market. National consistency is the stronger long-term product.

**Two-market stress test:** Run the same methodology against Jacksonville and Richmond VA simultaneously. If the zone labels feel coherent in both markets, the national model holds. If one market produces incoherent results, document why — that's a methodology post in itself (Article 9).

**Literature review (required before finalizing):**
- Identify 3–4 published neighborhood typology frameworks (Urban Land Institute zone classifications, NCRC community types, Esri Tapestry segments, academic tract-level clustering studies)
- Document what they used as inputs, how many clusters, and what labels
- Note where our approach differs and why

### Tasks

- [ ] Write `exploration/intelligence_framework/phase_7_zone_methodology/zone_methodology.qmd` using Jacksonville and Richmond VA as test markets
- [ ] Build all three cluster models; compare outputs side-by-side
- [ ] Test whether `is_opportunity_zone` flag from `gold.dim_policy_designations` produces meaningful overlap with the Distressed zone type
- [ ] Document literature review in `docs/zone_methodology_notes.md`
- [ ] Write a final cluster map for both markets with a written rationale for the chosen methodology

**Deliverable:** `zone_methodology.qmd` with dual-market test. The validated methodology becomes the template for every subsequent Deep Dive. Feeds Article 9.

---

## Phase 8 — Catalog Finalization and DuckDB Promotion

**Status:** Not started
**Depends on:** All prior phases
**Goal:** Two parallel workstreams: (1) verify and finalize the semantic layer — every `status: placeholder` entry promoted to `status: calibrated`; (2) build the R scripts that load all intelligence outputs into DuckDB as production data products.

**Note on catalog updates:** Individual frame catalog entries (`intelligence_catalog.yml`) are updated at the end of each Phase 2–4 notebook — not deferred to Phase 8. Phase 8 is a *verification and promotion* pass, not a catch-up pass. By the time Phase 8 runs, most catalog entries should already be at `status: calibrated`.

---

### Workstream 1 — Semantic Layer Verification

**Work per catalog entry:**
- Confirm `inputs` list matches the final empirically-tested KPI set from the relevant phase notebook
- Confirm `methodology` description matches the actual approach (hierarchical → K-Means → GMM, hierarchical weighted scoring, cosine similarity)
- Confirm `calibration_notes` field is populated with what the analysis produced and why inputs were chosen
- Confirm `benchmark_strategy` field is set (national, regional, peer cluster)
- Set `status` to `calibrated` if not already done

**Companion catalog updates:**
- `theme_catalog.yml` — remove metrics that didn't survive variance/correlation filters
- `question_catalog.yml` — add questions that surfaced during analysis
- `metric_catalog.yml` — add any derived metrics created during calibration (growth rates, RPP-adjusted versions, etc.)

### Workstream 2 — DuckDB Data Product Scripts

One R script per data product. Each script reads the corresponding parquet from `outputs/`, applies any final transformations, and writes to the appropriate Gold or scores schema in DuckDB. These scripts are the production pipeline — they replace the parquets as the authoritative output once they're validated.

**Scripts to build:**

| Script | Source parquet | Target table | Notes |
|---|---|---|---|
| `load_livability_scores.R` | `phase_3_livability_calibration/outputs/livability_scores.parquet` | `gold.intelligence_livability` | Cluster labels, GMM probs, topic/subject/composite scores, percentile ranks, top-10 peers |
| `load_opportunity_scores.R` | `phase_4_opportunity_calibration/outputs/opportunity_scores.parquet` | `gold.intelligence_opportunity` | Same structure as Livability |
| `load_character_scores.R` | `phase_2_character_calibration/outputs/character_scores.parquet` | `gold.intelligence_character` | Same structure |
| `load_cross_frame_scores.R` | `phase_5_cross_frame/outputs/cross_frame_scores.parquet` | `gold.intelligence_cross_frame` | Combined cluster, cross-frame similarity, overlap flags |
| `load_zone_assignments.R` | Zone methodology outputs | `gold.intelligence_zones` | Tract-level zone labels (after Phase 7) |

**Schema notes:**
- All intelligence Gold tables join to the CBSA spine on `cbsa_code`
- Zone table joins to the tract dimension on `geoid`
- Percentile ranks are stored as integers (0–100); raw z-scores stored alongside for downstream flexibility
- GMM soft membership probabilities stored as individual columns (`prob_cluster_1` … `prob_cluster_k`) — not as arrays, for DuckDB compatibility

### Tasks

**Semantic layer:**
- [ ] Verify all `intelligence_catalog.yml` entries are at `status: calibrated`; promote any that were missed during phases
- [ ] Write `exploration/intelligence_framework/docs/intelligence_calibration_notes.md` summarizing key decisions across all phases
- [ ] Update `theme_catalog.yml` to remove low-variance / redundant metrics
- [ ] Update `question_catalog.yml` with questions that surfaced during analysis
- [ ] Update `metric_catalog.yml` with any derived metrics created during calibration

**DuckDB scripts:**
- [ ] Write and validate `foundations/loaders/load_livability_scores.R`
- [ ] Write and validate `foundations/loaders/load_opportunity_scores.R`
- [ ] Write and validate `foundations/loaders/load_character_scores.R`
- [ ] Write and validate `foundations/loaders/load_cross_frame_scores.R`
- [ ] Write and validate `foundations/loaders/load_zone_assignments.R`
- [ ] Confirm all five Gold tables are queryable from MotherDuck and accessible to Area Explorer and the Chatbot

**Deliverable:** All `intelligence_catalog.yml` entries at `status: calibrated`. Five Gold intelligence tables in DuckDB. `intelligence_calibration_notes.md` complete. Area Explorer Phase 2 and Chatbot wire-up are now unblocked.

---

## Sequencing and Dependencies

```
Phase 0 — Metric Mapping                 ✓ Complete
    ↓
Phase 1 — Variable Selection             ✓ Complete (metric_selections.md)
    ↓
Phase 3 — Livability Frame Model         (start here — highest publishing value, unblocks Article 1)
    ↓
Phase 4 — Opportunity Frame Model        (completes Article 1 Livability/Opportunity scatter)
    ↓
Phase 2 — Character Frame Model          (third — requires literature review step; does not block Articles 1/3/4/5)
    ↓
Phase 5 — Cross-Frame Combined Model     (depends on Phases 2–4 being stable; produces combined cluster + similarity + overlap)
    ↓
Phase 6 — Trajectory Analysis             (depends on Phases 2–5; uses calibrated frame scores + Phase 5 overlap flags)
    ↓
Phase 7 — Zone Methodology               (depends on Phases 3–5 frame definitions and cluster labels)
    ↓
Phase 8 — Catalog Finalization           (verify semantic layer; build DuckDB loader scripts; promote to Gold)
```

**Execution order rationale:**
- Phase 3 before Phase 4: Livability sub-scores needed to produce the L/O scatter; Phase 4 completes it
- Phase 2 third: Character archetypes don't unblock any other product track; literature review adds lead time
- Phase 5 after Phases 2–4: cross-frame model needs all three frame KPI vectors and cluster labels
- Phase 6 depends on Phases 2–5: it uses calibrated frame scores as output expressions and the Phase 5 overlap flags as direct input to the candidate list
- Phase 7 depends on Phases 3–5 for tract-level zone inputs and CBSA-level frame context
- Phase 8 is the finalization and promotion pass — catalog verification + DuckDB loader scripts; unblocks Area Explorer Phase 2 and Chatbot

---

## File Structure

```
exploration/
  intelligence_framework/
    R/
      utils.R                              ← shared DB connect, CBSA spine; sources visual_library/shared/standards.R
    docs/
      metric_map.md                        ← Phase 0 (complete)
      metric_selections.md                 ← Phase 1 output (complete)
      character_clustering_notes.md        ← Phase 2 literature anchor
      zone_methodology_notes.md            ← Phase 6 literature review
      intelligence_calibration_notes.md    ← Phase 7 summary
    phase_variable_selection/              ← Phase 1 (complete)
      character_variable_selection.qmd
      livability_variable_selection.qmd
      opportunity_variable_selection.qmd
      docs/
        metric_selections.md
    phase_2_character_calibration/         ← Phase 2 (third in execution order)
      R/
        run_phase2_character.R             ← canonical Character build
      outputs/
        character_scores.parquet
      character_frame_model.qmd            ← review notebook over built artifacts
    phase_3_livability_calibration/        ← Phase 3 (first in execution order)
      R/
        run_phase3_livability.R            ← canonical Livability build
      outputs/
        livability_scores.parquet
      livability_frame_model.qmd           ← review notebook over built artifacts
    phase_4_opportunity_calibration/       ← Phase 4 (second in execution order)
      R/
        run_phase4_opportunity.R           ← canonical Opportunity build
      outputs/
        opportunity_scores.parquet
      opportunity_frame_model.qmd          ← review notebook over built artifacts
    phase_5_cross_frame_integration/       ← Phase 5 (after Phases 2–4 are stable)
      R/
        run_phase5_cross_frame.R           ← canonical combined-model build
      outputs/
        cross_frame_scores.parquet
      cross_frame_model.qmd               ← review notebook over built artifacts
    phase_6_trajectory/                    ← Phase 6 (depends on Phases 2–5)
      R/
        phase6_config.R
        phase6_frame_build.R
        phase6_trajectory_core.R
        phase6_opportunity_turn_signals.R
        phase6_patterns.R
        phase6_candidate_list.R
        run_phase6_trajectory.R            ← canonical runner
      notebooks/
        01_trajectory_overview.qmd
        02_bounce_back.qmd
        03_hidden_livability_winners.qmd
        04_diverging_from_themselves.qmd
        05_fast_demographic_changers.qmd
        06_environmental_risk_outliers.qmd
        07_candidate_list.qmd
        08_opportunity_turn_signals.qmd
      outputs/
        trajectory_scores.parquet          ← canonical output
        phase6_candidate_list.csv          ← primary Phase 6 deliverable
    phase_7_zone_methodology/              ← Phase 7
      zone_methodology.qmd
    phase_8_catalog/                       ← Phase 8
      intelligence_calibration_notes.md   ← summary of key decisions across all phases
foundations/
  loaders/
    load_livability_scores.R              ← Phase 8: writes gold.intelligence_livability to DuckDB
    load_opportunity_scores.R             ← Phase 8: writes gold.intelligence_opportunity to DuckDB
    load_character_scores.R               ← Phase 8: writes gold.intelligence_character to DuckDB
    load_cross_frame_scores.R             ← Phase 8: writes gold.intelligence_cross_frame to DuckDB
    load_zone_assignments.R               ← Phase 8: writes gold.intelligence_zones to DuckDB
```

---

## Publishing: Articles from this work

Each article is a Substack post. The Quarto notebook is the source of record and evidence file; the post is the prose adaptation. Articles are not deliverables of this roadmap — they surface during the work. Add to the Publisher queue as findings are confirmed.

| # | Article | Source phase | Key data angle |
|---|---|---|---|
| 1 | The Livability / Opportunity tradeoff | Phases 3 + 4 | High-growth metros tend to be worse places to live. The four-quadrant scatter. Who are the unicorns? |
| 2 | A new map of American metros | Phase 2 | Character archetypes derived from data. Where does your city fit? |
| 3 | The South's hidden health deficit | Phase 3 | Metros that score well on affordability but poorly on health. What the cost-of-living conversation misses. |
| 4 | Your city's industry mix in 2015 predicted your income growth in 2022 | Phase 4 | The industry-as-leading-indicator test using QCEW 2010–2024 backfill. |
| 5 | The hidden variable behind upward mobility | Phase 4 | Social capital (economic connectedness) vs. income growth. Does who you know matter more than industry mix? |
| 6 | The metros that can't make up their mind | Phase 5 | Cross-frame outliers: metros that rank high on one frame and low on another. What "diverging from themselves" looks like. |
| 7 | The bounce-back markets | Phase 6 | Which metros hit hardest in 2020 recovered fastest — and why. |
| 8 | The metros no one is talking about | Phase 6 | Hidden Livability winners: affordable + healthy + decent labor, but no national profile. |
| 9 | The zone that doesn't exist | Phase 7 | The zone methodology post. What happens when you try to classify every neighborhood in America using the same labels. |

---

## What This Roadmap Does Not Cover

- **Chatbot integration:** `intelligence_catalog.yml` gets wired into the chatbot query pipeline after Phase 8 promotes outputs to DuckDB Gold (Track B2 in ROADMAP.md). The five Gold intelligence tables are the prerequisite.
- **Area Explorer dashboards:** Phase 2 of Area Explorer (Intelligence Frames views) is built after Phase 8 completes. The Gold intelligence tables are the data layer for those dashboards.
- **Stoop integration:** Livability and Opportunity scoring feeds Stoop Search after calibration, but that's a Stoop track decision.
- **Track gaps still open:** HMDA (Track 13), IPEDS (Track 10), Track 11 Gold wiring (11.6–11.8), K-12 quality (Track 22) are all noted as gaps in the metric map. The Intelligence Layer work does not pause for them — gaps are flagged in the relevant phase notebooks and revisited if a missing signal turns out to be blocking.
