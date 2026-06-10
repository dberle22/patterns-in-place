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

## Phase 2 — Character Clustering (archetypes)

**Status:** Not started
**Depends on:** Phase 1 metric selections
**Goal:** Derive metro-level Character archetypes from data, not from intuition. Validate or revise the draft label set.

**Input set (pending Phase 2 reduction):**
Candidates: `median_age`, race/ethnicity shares, `pct_foreign_born`, `pct_ba_plus`, `pct_same_house`, `mobility_rate`, `pct_struct_multifam`, `pop_weighted_density_sqmi`, `economic_connectedness`, `civic_engagement_volunteering_rate`

**Methodology sequence:**
1. Standardize all inputs (z-score)
2. Hierarchical clustering first — use dendrogram to identify natural group count (k=5? k=7? don't assume)
3. K-means at the natural k — evaluate cluster coherence (within-cluster variance, silhouette scores)
4. Label each cluster: do the emerging groups feel coherent and nameable?

**Draft label set to evaluate against:**
- Immigrant Gateway — high diversity + high foreign-born + younger age
- Creative Class / Knowledge Hub — high BA+, younger age, high in-migration of young adults
- Established / Rooted — low diversity, older age, low mobility, high homeownership
- College Town — high college enrollment relative to population
- Sunbelt Growth — fast population growth, younger, newer housing stock
- Rust Belt / Industrial — older vintage housing, declining population, mixed education

**Key test:** Do groups reflect structural differences, or just population size and region? If size is dominating, normalize for it.

**Literature anchor (required before labeling):** Identify 2–3 published metro classification frameworks (Brookings, Pew Research metro typologies, Moretti's "Great Divergence") and document where clusters align or diverge.

### Tasks

- [ ] Write `exploration/intelligence_framework/character_clustering.qmd` — dendrogram, k-means clustering, cluster visualization, label evaluation, written interpretation
- [ ] Document literature anchor comparisons in a `docs/character_clustering_notes.md`
- [ ] Evaluate whether `economic_connectedness` from Social Capital Atlas changes cluster shapes vs. demographic-only inputs
- [ ] Update `intelligence_catalog.yml` character entry from placeholder to specified methodology with justified inputs

**Deliverable:** `character_clustering.qmd` with cluster visualization, label evaluation, written interpretation. Feeds Article 2.

---

## Phase 3 — Livability Scoring Calibration

**Status:** Not started
**Depends on:** Phase 1 metric selections
**Goal:** Define Livability sub-scores. The prior answer: sub-scores, not a single number. Collapsing to one score loses the most interesting tensions.

**Sub-scores to build:**

1. **Affordability sub-score:** `rpp_real_pc_income` + `pct_rent_burden_30plus` + `value_to_income`. Test: does it rank metros in a way that passes the smell test? (NYC bottom, Midwest mid-tier, Sun Belt moving down over time)

2. **Health sub-score (CHR-based):** `life_expectancy` + `premature_death_rate` + `physical_inactivity` + `adult_obesity` + `drug_overdose_death_rate`. Test the geographic hypothesis: Southern markets score worse on health despite performing better on affordability. If confirmed, this is publishable (Article 3).

3. **Safety sub-score:** `homicide_rate` + `motor_vehicle_crash_rate`. Distinct from health — safety is about external risk, not lifestyle outcomes.

4. **Environment sub-score:** `fema_risk_score` + `aqi_unhealthy_days` + `ej_pm25`. New — enabled by FEMA NRI and EPA AQI / EJScreen. Test: does this create a meaningful axis that separates Sun Belt / Gulf Coast markets from others?

5. **Mobility sub-score:** `pct_commute_transit` + `mean_travel_time_min` + `pct_hh_0_vehicles`. Currently thin — EPA SLD walkability adds signal once joined. Flag as incomplete but include with available ACS metrics.

**Benchmarking:** Score each CBSA against national median, regional median, and peer cluster (from Phase 3). Raw scores without benchmarks are meaningless.

**The Livability / Opportunity scatter** (from Phase 2) is reproduced here with the calibrated sub-scores. Find the four quadrants:
- High Livability + High Opportunity → the "unicorn" metros
- High Livability + Low Opportunity → "pleasant but stagnant"
- Low Livability + High Opportunity → "high-growth, expensive" (classic Sun Belt tension)
- Low Livability + Low Opportunity → the real distress cases

### Tasks

- [ ] Write `exploration/intelligence_framework/livability_calibration.qmd` — build and validate five sub-scores, plot distributions and named metro examples, produce composite
- [ ] Test the Southern market health hypothesis: affordability vs. health sub-score scatter
- [ ] Test the environmental risk axis: does `fema_risk_score` add non-redundant signal beyond AQI?
- [ ] Produce the Livability / Opportunity scatter with calibrated scores (publishable output — Article 1)
- [ ] Document benchmark strategy (national + regional + peer cluster)
- [ ] Update `intelligence_catalog.yml` Livability entries with justified inputs and weights

**Deliverable:** `livability_calibration.qmd`. Updated catalog. Two publishable charts: Livability/Opportunity scatter (Article 1), Health vs. Affordability scatter (Article 3).

---

## Phase 4 — Opportunity Scoring Calibration

**Status:** Not started
**Depends on:** Phase 1 metric selections
**Goal:** Define three Opportunity sub-lenses and validate they tell different stories.

**Sub-scores to build:**

1. **Resident Opportunity:** `income_pc_growth_5yr` + `lfpr` + `pct_unemployment_rate` + `gini_index`. Test: does this identify markets where residents are materially better off vs. 5 years ago? Does the gini index reveal that growth is concentrated vs. broad-based?

2. **Market / Investor Opportunity:** `hpi_5yr_pct` + `hpi_yoy_pct` + `pop_growth_5yr` + `irs_net_migration_rate` + `permits_per_1000_housing_units`. Test: does this flag the markets that were "hot" in 2021–2023? Does it now show cooling?

3. **Business / Industry Opportunity:** `industry_concentration_hhi` + sector share changes (QCEW) + `bfs_business_application_rate_per_1000_establishments` + `productivity_growth_5yr`. Key hypothesis: industry mix in 2015 predicts income growth by 2022. Test this longitudinally with the QCEW backfill (2010–2024). This is the industry-as-leading-indicator test (Article 4).

4. **Time horizon test:** 1-year signals vs. 5-year signals. Weight toward 5-year for structural story, 1-year for momentum signal.

5. **OZ analysis:** Flag CBSA-level OZ exposure rate (`pct_oz_tracts` from `gold.dim_policy_designations`) as a contextual data point. Which high-momentum markets have significant OZ exposure?

6. **Social capital as Opportunity signal:** Test `economic_connectedness` as a predictor of income growth trajectory. Does it add signal beyond industry mix? This directly feeds Article 5.

### Tasks

- [ ] Write `exploration/intelligence_framework/opportunity_calibration.qmd` — build and validate three sub-lenses, test industry-as-leading-indicator hypothesis longitudinally
- [ ] Test the social capital → income growth hypothesis: `economic_connectedness` vs. `income_pc_growth_5yr` scatter
- [ ] Test the momentum vs. structure split: does 1yr signal tell a different story from 5yr for the same metros?
- [ ] Flag CBSA OZ exposure as a contextual field
- [ ] Update `intelligence_catalog.yml` Opportunity entries with justified inputs and weights

**Deliverable:** `opportunity_calibration.qmd`. Updated catalog. Two publishable findings: industry mix as leading indicator (Article 4), social capital as hidden differentiator (Article 5).

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
Phase 1 — Variable Selection             (start now — variance + correlation + PCA, one notebook per frame)
    ↓
Phase 2 — Character Clustering  ←→ Phase 3 — Livability Calibration  ←→ Phase 4 — Opportunity Calibration
(parallel after Phase 1)
    ↓
Phase 5 — Trajectory Analysis            (can start after Phase 1 — needs reduced metrics, not calibrated scores)
    ↓
Phase 6 — Zone Methodology               (depends on Phases 2–4 frame definitions)
    ↓
Phase 7 — Catalog Finalization           (depends on all prior phases)
```

Phase 5 can run in parallel with Phases 2–4 once Phase 1 is done.

---

## File Structure

```
exploration/
  intelligence_framework/
    R/
      utils.R                              ← shared DB connect, CBSA spine; sources visual_library/shared/standards.R
    docs/
      metric_map.md                        ← Phase 0 (complete)
      metric_selections.md                 ← Phase 1 output
      character_clustering_notes.md        ← Phase 2 literature anchor
      zone_methodology_notes.md            ← Phase 6 literature review
      intelligence_calibration_notes.md    ← Phase 7 summary
    phase_variable_selection/              ← Phase 1
      character_variable_selection.qmd
      livability_variable_selection.qmd
      opportunity_variable_selection.qmd
      docs/
        metric_selections.md
    phase_2_character_clustering/
      character_clustering.qmd
    phase_3_livability_calibration/
      livability_calibration.qmd
    phase_4_opportunity_calibration/
      opportunity_calibration.qmd
    phase_5_trajectory/
      trajectory_analysis.qmd
    phase_6_zone_methodology/
      zone_methodology.qmd
    phase_7_catalog/
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
