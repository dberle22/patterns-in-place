# Intelligence Layer Roadmap

*The Intelligence Layer is the analytical core of Patterns in Place: the scoring models, archetypes, and zone classifications that make the three frames (Character, Livability, Opportunity) say something meaningful. This roadmap covers the work from raw metrics to publishable Deep Dive findings. It is ordered by dependency, not by calendar.*

---

## What we're building

The Intelligence Layer is not a single artifact — it's a stack of decisions that compound:

```
Gold tables (facts)
    → Metric selection (which inputs differentiate?)
        → Scoring calibration (which inputs cluster or score coherently?)
            → intelligence_catalog.yml (formalized, not final)
                → Zone methodology (tract-level clustering)
                    → First Deep Dive (Jacksonville)
```

Every entry in `foundations/semantic_layer/intelligence_catalog.yml` is currently `status: placeholder`. The goal of this roadmap is to move them to `status: calibrated` through actual analysis — not through upfront spec work.

---

## Phase 0 — Metric Mapping (prerequisite)

**Goal:** Know exactly which Gold table fields map to each frame's key metrics before writing a single notebook. Saves dead ends.

**Work:**
- Walk each frame's metric list from `DEEP_DIVE_EXPLORATION.md` against the Gold table columns in `foundations/data_dictionary/layers/gold/`
- Flag any metric that lacks a Gold column (data gap) vs. those that are query-ready
- Document the mapping in a single reference file: `exploration/intelligence_framework/docs/metric_map.md`

**Output:** A confirmed, gap-annotated metric map per frame. Any missing metric is flagged for Track 6–14 foundations work or deferred to Phase 2.

**Key gaps already known:**
- EPA Smart Location Database (walkability/transit) — Track 9, not ingested
- Social Capital Index — Track 14, not ingested
- K-12 quality data — not available at national grain
- POI/cultural layer — deferred to Deep Dive Points framework

---

## Phase 1 — Variance + Distribution Pass (national landscape)

**Goal:** Identify which metrics actually differentiate across CBSAs. Low-variance inputs don't earn a place in a scoring model.

**Scope:** CBSA grain only. ~380 CBSAs with population ≥ 100K.

**Work per frame:**

### Character
Run distributions on all Character metrics from `theme_catalog.yml`:
- Demographic composition: `median_age`, `pct_foreign_born`, `pct_ba_plus`, `diversity_index`, race/ethnicity shares
- Rootedness: `pct_same_house`, `mobility_rate`, `pct_moved_diff_st`
- Built form: `owner_occ_rate`, `pct_struct_multifam`, `pop_weighted_density_sqmi`

Look for: bimodality, geographic clustering, metrics that just reflect population size (drop those).

### Livability
Run distributions on all Livability metrics:
- Affordability: `pct_rent_burden_30plus`, `rent_to_income`, `value_to_income`, `rent_to_rpp_income`
- Mobility: `pct_commute_transit`, `mean_travel_time`, `pct_hh_0_vehicles`
- Health (CHR): life expectancy, chronic disease rates, physical inactivity
- Housing supply: `vacancy_rate`, `permits_per_1000_housing_units`

Look for: regional patterning in health outcomes (Southern markets hypothesis), affordability bimodal split (coastal vs. interior).

### Opportunity
Run distributions on all Opportunity metrics:
- Income/wages: `income_pc_growth_5yr`, `median_hh_income`, `lfpr`
- Economic output: `real_gdp_growth_5yr`, `productivity_growth_5yr`
- Housing market: FHFA HPI appreciation, Zillow ZORI growth, permit activity
- Industry: `industry_concentration_hhi`, sector share changes (QCEW)

Look for: the leading indicator hypothesis (industry mix predicts income growth), bounce-back markets post-2020.

**Deliverable:** One notebook per frame (`exploration/intelligence/character_variance.Rmd`, `livability_variance.Rmd`, `opportunity_variance.Rmd`). Each produces a ranked table of metrics by variance + a brief written interpretation. Metrics with low variance are flagged for removal from scoring models.

---

## Phase 2 — Correlation Pass (reduce redundancy)

**Goal:** Among high-variance inputs, find which ones are redundant. The goal is a defensible, non-redundant input set for each frame.

**Work:**
- Correlation matrix for each frame's surviving metrics
- Flag pairs above 0.75 correlation — pick the more interpretable metric from each pair
- Example from the exploration doc: if `diversity_index` and `pct_foreign_born` move together tightly, use underlying race shares rather than composite scores

**Specific pairs to test:**
- Character: `diversity_index` vs. `pct_foreign_born` vs. race shares
- Livability: `rent_to_income` vs. `pct_rent_burden_30plus` vs. `rent_to_rpp_income` (RPP-adjusted is probably more defensible)
- Opportunity: `real_gdp_growth_5yr` vs. `income_pc_growth_5yr` vs. `pop_growth_5yr` — are these independent signals or measuring the same thing?
- Cross-frame: Livability / Opportunity correlation test — if they move together, one frame is redundant. The hypothesis is that high-Opportunity metros (fast-growing, high-income) have worse Livability (expensive, congested). Scatter plot this as a standalone publishable finding.

**Deliverable:** Reduced metric sets per frame, documented in `exploration/intelligence/metric_selections.md`. This is the direct input to Phase 3. Update `intelligence_catalog.yml` input lists to reflect the reduction.

---

## Phase 3 — Character Clustering (archetypes)

**Goal:** Derive the metro-level Character archetypes from data, not from intuition. Validate (or revise) the draft label set.

**Input set (pending Phase 2 reduction):**
Candidates: `median_age`, race/ethnicity shares, `pct_foreign_born`, `pct_ba_plus`, `pct_same_house`, `mobility_rate`, `pct_struct_multifam`, `pop_weighted_density_sqmi`

**Methodology sequence:**
1. Standardize all inputs (z-score)
2. Hierarchical clustering first — use dendrogram to identify natural group count (k=5? k=7? don't assume)
3. K-means at the natural k — evaluate cluster coherence (within-cluster variance, silhouette scores)
4. Label each cluster: do the emerging groups feel coherent and nameable? Do they match any of the draft labels below?

**Draft label set to evaluate against:**
- Immigrant Gateway — high diversity + high foreign-born + younger age
- Creative Class / Knowledge Hub — high BA+, younger age, high in-migration of young adults
- Established / Rooted — low diversity, older age, low mobility, high homeownership
- College Town — high college enrollment relative to population
- Sunbelt Growth — fast population growth, younger, newer housing stock
- Rust Belt / Industrial — older vintage housing, declining population, mixed education

**Key test:** Do the resulting groups feel coherent and nameable, or do they just reflect population size and region? If size is dominating, normalize for it.

**Literature anchor:** Identify 2–3 published metro classification frameworks (Brookings, Pew Research metro typologies, Moretti's "Great Divergence") and document where our clusters align or diverge. This is required before labeling — we need to know if our "Immigrant Gateway" cluster matches what the literature calls that.

**Deliverable:** `exploration/intelligence/character_clustering.Rmd` with cluster visualization, label evaluation, and written interpretation. Update `intelligence_catalog.yml` character entry from placeholder to a specified methodology with justified inputs.

---

## Phase 4 — Livability Scoring Calibration

**Goal:** Decide whether Livability is a single score, a dashboard of sub-scores, or both — and what the inputs and weights are.

**The prior answer from DEEP_DIVE_EXPLORATION.md:** Sub-scores, not a single number. Collapsing to one score loses the most interesting tensions (e.g., affordable market with poor health outcomes).

**Work:**

1. **Affordability sub-score:** Build and validate. Primary inputs: `rent_to_rpp_income`, `pct_rent_burden_30plus`, `value_to_income`. Test: does the score rank metros in a way that passes the smell test? (NYC bottom, Midwest mid-tier, Sun Belt moving down over time)

2. **Health sub-score (CHR-based):** Build from CHR metrics — life expectancy, chronic disease rates, physical inactivity, injury deaths. Test the geographic hypothesis: Southern markets score worse on health despite performing better on affordability. If confirmed, this is publishable.

3. **Mobility sub-score:** Currently very thin without EPA Smart Location Database. Use ACS commute metrics (`pct_commute_transit`, `mean_travel_time`, `pct_hh_0_vehicles`) as a weak proxy. Flag this as incomplete until Track 9 (EPA SLD) is ingested.

4. **Livability / Opportunity scatter:** For every CBSA, plot Livability composite vs. Opportunity composite. Test the tradeoff hypothesis. Find the four quadrants:
   - High Livability + High Opportunity → the "unicorn" metros
   - High Livability + Low Opportunity → "pleasant but stagnant"
   - Low Livability + High Opportunity → "high-growth, expensive" (the classic Sun Belt tension)
   - Low Livability + Low Opportunity → the real distress cases
   
   This scatter is a standalone publishable finding. Target for the content pipeline.

**Benchmarking decision:** Score each CBSA against national median, regional median, and peer cluster (from Character clustering). Don't just present raw scores — every metric needs a benchmark to be meaningful.

**Deliverable:** `exploration/intelligence/livability_calibration.Rmd`. Updated `intelligence_catalog.yml` Livability entries with justified inputs and weights. One publishable chart: the Livability / Opportunity scatter.

---

## Phase 5 — Opportunity Scoring Calibration

**Goal:** Define the three Opportunity sub-lenses (Resident, Market, Business) and validate that they tell different stories.

**Work:**

1. **Resident Opportunity:** Income growth trajectory is the spine. `income_pc_growth_5yr` + `lfpr` + `pct_unemployment_rate`. Test: does this sub-score identify markets where residents are materially better off vs. 5 years ago?

2. **Market / Investor Opportunity:** FHFA HPI appreciation + Zillow ZORI rent growth + `pop_growth_5yr` + `irs_net_migration_rate` + `permits_per_1000_housing_units`. Test: does this flag the markets that were "hot" in 2021–2023? Does it now show cooling?

3. **Business / Industry Opportunity:** QCEW industry mix is the distinctive input. `industry_concentration_hhi` (lower = more diversified), sector share changes (is the market growing professional services? losing manufacturing?). Key hypothesis: industry mix in 2015 predicts income growth by 2022. Test this longitudinally with the QCEW backfill (2010–2024).

4. **Time horizon test:** 1-year signals vs. 5-year signals tell different stories. A market hot in 2021 but cooling in 2024 is very different from one that's just starting to move. Both horizons needed — weight toward 5-year for structural story, 1-year for momentum signal.

5. **OZ analysis:** Which Opportunity Zone tracts show strong momentum metrics despite their distress designation? This is a later tract-level analysis, but flag the CBSA-level OZ exposure rate as a data point now.

**Deliverable:** `exploration/intelligence/opportunity_calibration.Rmd`. Updated `intelligence_catalog.yml` Opportunity entries. Publishable finding: the industry-mix-as-leading-indicator test.

---

## Phase 6 — Trajectory + Divergence Analysis

**Goal:** Find the CBSAs that are moving away from the national mean and accelerating. This builds the Deep Dive candidate backlog.

**Work:**
- For each metric that survived the variance filter (Phases 1–2), identify CBSAs that are 1.5+ standard deviations from the national mean AND moving further away over the last 5 years
- Segment by direction: improving outliers vs. declining outliers
- Output: a ranked list of "most interesting" CBSAs per frame — the markets where something structural is happening

**Key patterns to surface:**
- "Bounce-back" markets: high 2020 distress + fastest recovery (Opportunity story)
- "Hidden Livability winners": affordable + good health + decent labor, but no national profile
- "Diverging from themselves": a market where one frame is improving while another deteriorates (the most interesting Deep Dive candidates)
- Fast demographic changers: CBSAs where Character metrics are shifting fastest (migration composition changing, aging accelerating)

**Deliverable:** `exploration/intelligence/trajectory_analysis.Rmd`. A ranked candidate list for Deep Dive market selection. This directly feeds the Phase B market selection decision in the broader roadmap.

---

## Phase 7 — Zone Methodology Definition

**Goal:** Define the tract-level clustering approach that produces the Zone Analysis section of every Metro Deep Dive.

This is the hardest methodology work and the most distinctive output. Do it for Jacksonville as the stress-test.

**Clustering architecture:**
Three cluster models, built and compared:
1. **Character zones** — demographic archetype at tract level (who lives here)
2. **Opportunity zones** — economic momentum at tract level (what's happening here)
3. **Cross-theme zones** — the primary map shown in the Deep Dive report; blends all three frames

**Input candidates (tract level):**
- Character: race/ethnicity shares, median age, `pct_foreign_born`, `pct_ba_plus`, `pct_same_house`, `pop_weighted_density_sqmi`
- Livability: `pct_rent_burden_30plus`, `rent_to_income`, `value_to_income`, housing vintage
- Opportunity: `income_pc_growth_5yr`, home price appreciation, `pct_unemployment_rate`, permit density

**Methodology options to evaluate:**
- K-means on standardized tract metrics (simple, interpretable, start here)
- Hierarchical clustering (better for natural group count discovery)
- Latent class analysis (probabilistic, handles mixed types — evaluate if k-means clusters feel fuzzy)

**Target zone label set (6–8 types, evaluate against what data produces):**
- Core Hub — dense, diverse, high-activity urban core
- Established Residential — stable, owner-occupied, slow-changing
- Transitional / Emerging — demographic shift, rising prices, mixed signals
- Affordable Fringe — lower cost, lower income, accessible to workforce
- Knowledge / Creative Corridor — high education, professional, younger population
- Growth Periphery — fast-growing suburban, new construction, family-oriented
- Distressed — declining population, high poverty, disinvestment signals

**National vs. per-market decision:** Build the national model first. Per-market calibration can follow if the national model produces incoherent results for a specific market. National consistency is the stronger long-term product.

**Literature review (required before finalizing):**
- Identify 3–4 published neighborhood typology frameworks (Urban Land Institute zone classifications, NCRC community types, Esri Tapestry segments, academic tract-level clustering studies)
- Document what they used as inputs, how many clusters, and what labels
- Note where our approach differs and why

**Deliverable:** `exploration/intelligence/zone_methodology.Rmd` using Jacksonville as the test market. Final cluster map for Jacksonville's tracts, with a written rationale for the chosen methodology. This becomes the template for every subsequent market.

---

## Phase 8 — Catalog Finalization + intelligence_catalog.yml Update

**Goal:** Translate all calibration decisions from Phases 3–7 into the formal semantic layer. Every `status: placeholder` entry gets promoted to `status: calibrated`.

**Work per entry:**
- Update `inputs` list to reflect the Phase 2–reduced, empirically-tested metric set
- Update `methodology` description with the actual approach (k-means, weighted blend, sub-score dashboard, etc.)
- Add `calibration_notes` field documenting what the analysis produced and why inputs were chosen
- Add `benchmark_strategy` field (national, regional, peer cluster)
- Change `status` to `calibrated`

**This also drives updates to:**
- `theme_catalog.yml` — remove metrics that didn't survive the variance/correlation filters
- `question_catalog.yml` — add questions that the analysis surfaced as interesting
- `metric_catalog.yml` — add any derived metrics created during calibration (growth rates, RPP-adjusted versions, etc.)

**Deliverable:** All `intelligence_catalog.yml` entries at `status: calibrated`. A short `intelligence_calibration_notes.md` summarizing the key decisions and what they replaced.

---

## Sequencing and Dependencies

```
Phase 0 — Metric Mapping          (no dependencies; start now)
    ↓
Phase 1 — Variance Pass           (depends on Phase 0 metric map)
    ↓
Phase 2 — Correlation Pass        (depends on Phase 1 outputs)
    ↓
Phase 3 — Character Clustering    ← can run in parallel with Phases 4+5
Phase 4 — Livability Calibration  ← can run in parallel with Phases 3+5
Phase 5 — Opportunity Calibration ← can run in parallel with Phases 3+4
    ↓ (all three complete)
Phase 6 — Trajectory Analysis     (depends on reduced metric sets from Phase 2)
    ↓
Phase 7 — Zone Methodology        (depends on Phase 3–5 frame definitions)
    ↓
Phase 8 — Catalog Finalization    (depends on all prior phases)
```

Phases 3, 4, and 5 can run in parallel after Phase 2. Phase 6 can start as soon as Phase 2 is done — it only needs the reduced metric set, not the scores themselves. Phase 7 is the last major methodology work; Phase 8 is the write-up pass.

---

## File Structure

```
exploration/
  intelligence_framework/
    docs/
      metric_map.md                   ← Phase 0 output (complete)
      metric_selections.md            ← Phase 2 output
      intelligence_calibration_notes.md ← Phase 8 summary
    character_variance.Rmd          ← Phase 1
    livability_variance.Rmd         ← Phase 1
    opportunity_variance.Rmd        ← Phase 1
    character_clustering.Rmd        ← Phase 3
    livability_calibration.Rmd      ← Phase 4
    opportunity_calibration.Rmd     ← Phase 5
    trajectory_analysis.Rmd         ← Phase 6
    zone_methodology.Rmd            ← Phase 7
```

---

## Content and Publishing Angles (from this work)

The Intelligence Layer work produces several publishable standalone findings. Track these as they emerge — they feed the Publisher content queue.

| Finding | Phase | Target |
|---|---|---|
| Livability / Opportunity scatter (the tradeoff) | Phase 4 | Substack post |
| Hidden Livability winners | Phase 6 | Substack post |
| Character archetypes at metro scale | Phase 3 | Substack post |
| Industry mix as leading indicator | Phase 5 | Substack post |
| The zone that doesn't exist (methodology post) | Phase 7 | Substack + LinkedIn |
| Bounce-back markets post-2020 | Phase 6 | Substack post |

These posts are not deliverables of this roadmap — they're outputs that surface during the work. Add them to the Publisher queue as they become ready.

---

## What This Roadmap Does Not Cover

- **Chatbot integration:** The `intelligence_catalog.yml` gets wired into the chatbot query pipeline as a separate step after calibration is complete (Track B2 in ROADMAP.md).
- **Area Explorer dashboards:** Phase 2 of Area Explorer (Intelligence Frames views) is built after this work completes. The calibrated scores become the data layer for those dashboards.
- **Stoop integration:** Livability and Opportunity scoring feeds Stoop Search after calibration, but that's a Stoop track decision.
- **Track 6–14 data gaps:** If analysis in Phases 1–5 reveals that a missing Track (EPA SLD, JEC Social Capital) is blocking a key signal, that triggers a targeted foundations sprint — but the Intelligence Layer work does not pause waiting for it.
