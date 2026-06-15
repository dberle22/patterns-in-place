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

**During Phase 2–4 (notebook phase):** Flat parquet files in `exploration/intelligence_framework/outputs/`. One file per frame with all scored and clustered results.

**After calibration is stable:** Promoted to a Gold-layer scores datamart. This is the prerequisite for Area Explorer Phase 2 (Intelligence Frames views) and the Chatbot wire-up. Promotion happens in Phase 7 (Catalog Finalization).

**Columns per CBSA in the output:**
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

All Quarto notebooks should render to self-contained HTML. Each notebook is the source of record for its phase's findings — the Substack post is a prose adaptation of those findings, not a separate document.

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

**Status:** Not started
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

**Status:** Not started
**Depends on:** Phase 1 metric selections; Architecture decisions (above — locked)
**Execution order:** Third, after Phases 3 and 4. Livability and Opportunity scoring are higher-priority unblocks for Area Explorer and the Chatbot. Character clustering requires a literature review step before labels can be defended, making it the slower pass.

**Goal:** Produce all three outputs for the Character frame in one notebook: cluster labels (archetypes), scored sub-scores + composite percentile, and similarity vectors. This is the same structure as Phases 3 and 4.

**Input set (from Phase 1 metric_selections.md — Character core):**
`diversity_index`, `pct_black_nh`, `pct_asian_nh`, `pct_hispanic`, `pct_age_over_64`, `pct_ba_plus`, `pct_foreign_born`, `pop_weighted_density_sqmi`, `friending_bias`, `civic_engagement_volunteering_rate`, `civic_organizations_per_1000`, `nonprofits_per_100k`, `irs_net_migration_rate`, `pct_moved_diff_st`, `pct_moved_abroad`, `social_associations_per_10k`, `pct_struct_multifam`

**Notebook sequence:**
1. Coverage audit — check missingness per KPI across 401 CBSAs; apply median imputation; log affected KPIs and counts
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

- [ ] Coverage audit and imputation pass for Character KPI set
- [ ] Write `exploration/intelligence_framework/phase_2_character_clustering/character_frame_model.qmd` — full clustering + scoring + similarity pass
- [ ] Document literature anchor comparisons in `docs/character_clustering_notes.md`
- [ ] Produce cosine similarity output: top-10 Character peers per CBSA
- [ ] Update `intelligence_catalog.yml` character entry from placeholder to specified methodology
- [ ] Write outputs to `exploration/intelligence_framework/outputs/character_scores.parquet`

**Deliverable:** `character_frame_model.qmd` with dendrogram, cluster visualization, soft memberships, scored percentiles, similarity matrix, and written interpretation. Feeds Article 2 ("A new map of American metros").

---

## Phase 3 — Livability Frame Model

**Status:** Not started
**Depends on:** Phase 1 metric selections; Architecture decisions (above — locked)
**Execution order:** First. Livability + Opportunity together produce Article 1 (the Livability/Opportunity scatter), which is the highest-value near-term publishable output and the clearest connection to the ROADMAP.md flywheel.

**Goal:** Produce all three outputs for the Livability frame in one notebook: cluster labels (Livability types), scored sub-scores + composite percentile, and similarity vectors.

**Input set (from Phase 1 metric_selections.md — Livability core):**

*Recurring core:*
`value_to_income`, `pct_rent_burden_30plus`, `pov_rate`, `permits_per_1000_housing_units`, `permits_share_units_5_plus`, `pct_struct_mobile`, `pct_struct_small_mf`, `pct_struct_mid_mf`, `premature_death_rate`, `mental_health_provider_ratio`, `drug_overdose_death_rate`, `pct_uninsured_adults`, `preventable_hospital_stay_rate`, `firearm_fatality_rate`, `motor_vehicle_crash_rate`, `pct_commute_walk`, `pct_commute_wfh`, `vacancy_rate`, `pct_hh_0_vehicles`, `pct_no_internet_access`

*Supplemental baseline / coverage-caution (weighted at 0.60–0.75):*
`walkability_index`, `jobs_access_45min_transit`, `pct_population_low_income_low_access_1_10`, `pop_weighted_density_sqmi`, `unhealthy_days`, `fema_risk_score`

**Subject structure and initial weights:**
- `Affordability`: 0.25 — topics: Price Pressure, Housing Burden, Poverty Context, Housing Supply, Housing Structure Mix
- `Health & Safety`: 0.25 — topics: Health Outcomes, Health Behavior & Access, Violence & Injury
- `Access & Infrastructure`: 0.25 — topics: Commute & Mode, Vehicle Access, Housing Slack, Digital Access, Walkability baseline, Food Access baseline, Built-Form Proxy
- `Physical Environment`: 0.25 — topics: Air Pollution, Climate Hazard Risk (both coverage-caution weighted)

**Notebook sequence:**
1. Coverage audit — check missingness per KPI across 401 CBSAs; apply median imputation; log affected KPIs and counts
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
- Environmental risk axis: does `fema_risk_score` add non-redundant signal beyond `unhealthy_days`?
- Livability / Opportunity scatter stub: produce with Livability percentile on one axis; complete with Opportunity scores after Phase 4 (Article 1)

**Smell test:** Does the Affordability topic rank NYC / coastal metros at the bottom and Midwest interior metros near the top? If not, revisit polarity or weighting before proceeding.

### Tasks

- [ ] Coverage audit and imputation pass for Livability KPI set
- [ ] Assign polarity flags to all Livability KPIs
- [ ] Write `exploration/intelligence_framework/phase_3_livability_calibration/livability_frame_model.qmd` — full clustering + scoring + similarity pass
- [ ] Test Southern markets health hypothesis: affordability sub-score vs. health sub-score scatter
- [ ] Test environmental risk axis: `fema_risk_score` vs. `unhealthy_days` non-redundancy check
- [ ] Produce Livability/Opportunity scatter stub (complete after Phase 4)
- [ ] Produce cosine similarity output: top-10 Livability peers per CBSA
- [ ] Update `intelligence_catalog.yml` Livability entries from placeholder to specified methodology
- [ ] Write outputs to `exploration/intelligence_framework/outputs/livability_scores.parquet`

**Deliverable:** `livability_frame_model.qmd` with dendrogram, cluster visualization, soft memberships, topic/subject/composite scores, percentile ranks, similarity matrix, and written interpretation. Two publishable findings: Livability/Opportunity scatter (Article 1, completed with Phase 4), Health vs. Affordability scatter (Article 3).

---

## Phase 4 — Opportunity Frame Model

**Status:** Not started
**Depends on:** Phase 1 metric selections; Architecture decisions (above — locked)
**Execution order:** Second, immediately after Phase 3. Opportunity scores complete the Livability/Opportunity scatter (Article 1).

**Goal:** Produce all three outputs for the Opportunity frame in one notebook: cluster labels (Opportunity types), scored sub-scores + composite percentile, and similarity vectors.

**Input set (from Phase 1 metric_selections.md — Opportunity core):**
`income_pc_growth_5yr`, `pct_unemployment_rate`, `lfpr`, `pov_rate_change_5yr`, `qcew_private_avg_wkly_wage`, `hpi_5yr_pct`, `hpi_yoy_pct`, `zori_annual_avg_yoy_pct`, `pop_growth_5yr`, `irs_net_migration_rate`, `irs_net_agi`, `permits_per_1000_housing_units`, `permits_share_units_5_plus`, `productivity_growth_5yr`, `industry_concentration_hhi`, `bfs_business_application_rate_per_1000_establishments`, `cbp_estabs_per_1000_residents`, `pct_ba_plus_change_5yr`, `lq_professional`, `lq_information`, `lq_manufacturing`, `pct_real_gdp_information`

**Subject structure and initial weights:**
- `Resident Opportunity`: 0.33 — topics: Income Growth, Wage Levels, Labor Market Tightness, Poverty & Inclusion, Intergenerational Mobility Proxy
- `Market / Investor Opportunity`: 0.33 — topics: Home Price Appreciation, Rent Growth, Population Growth, Migration & Wealth Flows, Permit Activity
- `Business & Industry Opportunity`: 0.33 — topics: GDP Growth, Industry Concentration, Human Capital Momentum, Business Formation, Establishment Density, Location Quotient Specialization, Sector GDP Mix

**Note on ZORI coverage:** `zori_annual_avg_yoy_pct` has ~48% topic-level coverage once level fields are included. Carry the YoY growth field only; impute missing CBSAs at the national median. Flag this as a coverage-caution KPI in the output.

**Note on cross-frame overlap:** `permits_per_1000_housing_units`, `irs_net_migration_rate`, and `pov_rate` appear in both Livability and Opportunity. This is intentional — they serve different conceptual roles in each frame. Acknowledge in the notebook; do not remove.

**Notebook sequence:**
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

- [ ] Coverage audit and imputation pass for Opportunity KPI set; flag ZORI coverage issue explicitly
- [ ] Assign polarity flags to all Opportunity KPIs
- [ ] Write `exploration/intelligence_framework/phase_4_opportunity_calibration/opportunity_frame_model.qmd` — full clustering + scoring + similarity pass
- [ ] Test industry-as-leading-indicator hypothesis longitudinally (QCEW 2010–2024 backfill)
- [ ] Test social capital → income growth hypothesis: `economic_connectedness` vs. `income_pc_growth_5yr`
- [ ] Test 1yr vs. 5yr signal divergence across resident and market subjects
- [ ] Flag CBSA OZ exposure as contextual field
- [ ] Complete Livability/Opportunity scatter (four-quadrant plot) using Phase 3 percentiles
- [ ] Produce cosine similarity output: top-10 Opportunity peers per CBSA
- [ ] Update `intelligence_catalog.yml` Opportunity entries from placeholder to specified methodology
- [ ] Write outputs to `exploration/intelligence_framework/outputs/opportunity_scores.parquet`

**Deliverable:** `opportunity_frame_model.qmd` with dendrogram, cluster visualization, soft memberships, topic/subject/composite scores, percentile ranks, similarity matrix, and written interpretation. Three publishable findings: Livability/Opportunity four-quadrant scatter (Article 1), industry mix as leading indicator (Article 4), social capital as hidden differentiator (Article 5).

---

## Phase 5 — Trajectory + Divergence Analysis

**Status:** Not started
**Depends on:** Phase 1 reduced metric sets (does not require calibrated scores from Phases 2–4)
**Goal:** Find the CBSAs that are moving away from the national mean and accelerating. This builds the Deep Dive candidate backlog and directly feeds market selection.

**Work:**
- For each metric that survived the variance filter (Phases 1–2), identify CBSAs that are 1.5+ standard deviations from the national mean AND moving further away over the last 5 years
- Segment by direction: improving outliers vs. declining outliers
- Output: a ranked list of "most interesting" CBSAs per frame

**Key patterns to surface:**
- "Bounce-back" markets: high 2020 distress + fastest recovery (Opportunity story — Article 6)
- "Hidden Livability winners": affordable + good health + decent labor, no national profile (Article 7)
- "Diverging from themselves": a market where one frame is improving while another deteriorates (the most interesting Deep Dive candidates)
- Fast demographic changers: CBSAs where Character metrics are shifting fastest
- Environmental risk outliers: CBSAs where `fema_risk_score` + `aqi_unhealthy_days` are both moving in the wrong direction — enabled by new sources

### Tasks

- [ ] Write `exploration/intelligence_framework/trajectory_analysis.qmd` — divergence analysis per frame, outlier identification, quadrant plots
- [ ] Produce ranked candidate list for Deep Dive market selection (one list per frame, then combined)
- [ ] Confirm Jacksonville and Richmond VA appear in the candidate set (or document why they're selected despite ranking)
- [ ] Flag markets "diverging from themselves" as the highest-priority Deep Dive candidates

**Deliverable:** `trajectory_analysis.qmd`. A ranked candidate list for Deep Dive market selection. Feeds Article 6 (bounce-back markets) and Article 7 (hidden Livability winners).

---

## Phase 6 — Zone Methodology Definition

**Status:** Not started
**Depends on:** Phases 3–5 frame definitions
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

**Two-market stress test:** Run the same methodology against Jacksonville and Richmond VA simultaneously. If the zone labels feel coherent in both markets, the national model holds. If one market produces incoherent results, document why — that's a methodology post in itself (Article 8).

**Literature review (required before finalizing):**
- Identify 3–4 published neighborhood typology frameworks (Urban Land Institute zone classifications, NCRC community types, Esri Tapestry segments, academic tract-level clustering studies)
- Document what they used as inputs, how many clusters, and what labels
- Note where our approach differs and why

### Tasks

- [ ] Write `exploration/intelligence_framework/zone_methodology.qmd` using Jacksonville and Richmond VA as test markets
- [ ] Build all three cluster models; compare outputs side-by-side
- [ ] Test whether `is_opportunity_zone` flag from `gold.dim_policy_designations` produces meaningful overlap with the Distressed zone type
- [ ] Document literature review in `docs/zone_methodology_notes.md`
- [ ] Write a final cluster map for both markets with a written rationale for the chosen methodology

**Deliverable:** `zone_methodology.qmd` with dual-market test. The validated methodology becomes the template for every subsequent Deep Dive. Feeds Article 8.

---

## Phase 7 — Catalog Finalization

**Status:** Not started
**Depends on:** All prior phases
**Goal:** Translate all calibration decisions from Phases 3–7 into the formal semantic layer. Every `status: placeholder` entry gets promoted to `status: calibrated`.

**Work per entry:**
- Update `inputs` list to reflect the Phase 2–reduced, empirically-tested metric set
- Update `methodology` description with the actual approach (k-means, weighted blend, sub-score dashboard, etc.)
- Add `calibration_notes` field documenting what the analysis produced and why inputs were chosen
- Add `benchmark_strategy` field (national, regional, peer cluster)
- Change `status` to `calibrated`

**This also drives updates to:**
- `theme_catalog.yml` — remove metrics that didn't survive variance/correlation filters
- `question_catalog.yml` — add questions that the analysis surfaced as interesting
- `metric_catalog.yml` — add any derived metrics created during calibration (growth rates, RPP-adjusted versions, etc.)

### Tasks

- [ ] Update all entries in `foundations/semantic_layer/intelligence_catalog.yml` to `status: calibrated`
- [ ] Write `exploration/intelligence_framework/docs/intelligence_calibration_notes.md` summarizing key decisions and what they replaced
- [ ] Update `theme_catalog.yml` to remove low-variance / redundant metrics
- [ ] Update `question_catalog.yml` with questions that surfaced during analysis
- [ ] Update `metric_catalog.yml` with any derived metrics created during calibration

**Deliverable:** All `intelligence_catalog.yml` entries at `status: calibrated`. `intelligence_calibration_notes.md` complete.

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
Phase 5 — Trajectory Analysis            (can start after Phase 1 — needs reduced metrics, not calibrated scores)
    ↓
Phase 6 — Zone Methodology               (depends on Phases 2–4 frame definitions)
    ↓
Phase 7 — Catalog Finalization           (depends on all prior phases; promotes outputs to Gold scores datamart)
```

**Execution order rationale:**
- Phase 3 before Phase 4: Livability sub-scores are needed to produce the L/O scatter; Phase 4 completes it
- Phase 2 third: Character archetypes don't unblock any other product track; literature review adds lead time
- Phase 5 can run in parallel with Phases 2–4 once Phase 1 is done (needs reduced metrics, not scores)
- Cross-frame combined similarity model is built in Phase 7, after all three frame models are stable

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
    outputs/                               ← scored + clustered parquet files (promoted to Gold in Phase 7)
      livability_scores.parquet            ← Phase 3 output
      opportunity_scores.parquet           ← Phase 4 output
      character_scores.parquet             ← Phase 2 output
      cross_frame_scores.parquet           ← Phase 7 combined model
    phase_variable_selection/              ← Phase 1 (complete)
      character_variable_selection.qmd
      livability_variable_selection.qmd
      opportunity_variable_selection.qmd
      docs/
        metric_selections.md
    phase_2_character_clustering/          ← Phase 2 (third in execution order)
      character_frame_model.qmd            ← clustering + scoring + similarity in one pass
    phase_3_livability_calibration/        ← Phase 3 (first in execution order)
      livability_frame_model.qmd           ← clustering + scoring + similarity in one pass
    phase_4_opportunity_calibration/       ← Phase 4 (second in execution order)
      opportunity_frame_model.qmd          ← clustering + scoring + similarity in one pass
    phase_5_trajectory/
      trajectory_analysis.qmd
    phase_6_zone_methodology/
      zone_methodology.qmd
    phase_7_catalog/
      cross_frame_model.qmd               ← combined similarity + cross-frame overlap check
      (catalog update scripts)
```

---

## Publishing: Articles from this work

Each article is a Substack post. The Quarto notebook is the source of record and evidence file; the post is the prose adaptation. Articles are not deliverables of this roadmap — they surface during the work. Add to the Publisher queue as findings are confirmed.

| # | Article | Source phase | Key data angle |
|---|---|---|---|
| 1 | The Livability / Opportunity tradeoff | Phase 2 + 4 | High-growth metros tend to be worse places to live. The four-quadrant scatter. Who are the unicorns? |
| 2 | A new map of American metros | Phase 3 | Character archetypes derived from data. Where does your city fit? |
| 3 | The South's hidden health deficit | Phase 4 | Metros that score well on affordability but poorly on health. What the cost-of-living conversation misses. |
| 4 | Your city's industry mix in 2015 predicted your income growth in 2022 | Phase 5 | The industry-as-leading-indicator test using QCEW 2010–2024 backfill. |
| 5 | The hidden variable behind upward mobility | Phase 5 | Social capital (economic connectedness) vs. income growth. Does who you know matter more than industry mix? |
| 6 | The bounce-back markets | Phase 6 | Which metros hit hardest in 2020 recovered fastest — and why. |
| 7 | The metros no one is talking about | Phase 6 | Hidden Livability winners: affordable + healthy + decent labor, but no national profile. |
| 8 | The zone that doesn't exist | Phase 7 | The zone methodology post. What happens when you try to classify every neighborhood in America using the same labels. |

---

## What This Roadmap Does Not Cover

- **Chatbot integration:** `intelligence_catalog.yml` gets wired into the chatbot query pipeline after calibration is complete (Track B2 in ROADMAP.md).
- **Area Explorer dashboards:** Phase 2 of Area Explorer (Intelligence Frames views) is built after this work completes. The calibrated scores become the data layer for those dashboards.
- **Stoop integration:** Livability and Opportunity scoring feeds Stoop Search after calibration, but that's a Stoop track decision.
- **Track gaps still open:** HMDA (Track 13), IPEDS (Track 10), Track 11 Gold wiring (11.6–11.8), K-12 quality (Track 22) are all noted as gaps in the metric map. The Intelligence Layer work does not pause for them — gaps are flagged in the relevant phase notebooks and revisited if a missing signal turns out to be blocking.
