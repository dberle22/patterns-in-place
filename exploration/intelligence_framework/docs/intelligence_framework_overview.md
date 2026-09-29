# The Intelligence Framework

*Consolidated reference: rationale, architecture, per-frame methodology, outputs, and known limitations.*

**Sources synthesized:** `foundations/semantic_layer/intelligence_catalog.yml`, `foundations/semantic_layer/theme_catalog.yml`, `INTELLIGENCE_LAYER_ROADMAP.md`, `exploration/intelligence_framework/docs/*`, `metro-deep-dive/docs/intelligence_framework_review_question_bank.md`.

**Last updated:** 2026-08-26

---

## 1. Why this exists

Patterns in Place makes a claim that's easy to assert and hard to earn: that a metro area can be *understood*, not just described. Raw metrics (median rent, unemployment rate, population growth) answer narrow questions one at a time. They don't answer "what kind of place is this," "is this a good place to build a life or a business," or "which metros are actually like this one."

The Intelligence Framework exists to turn ~200 raw KPIs spread across Gold tables into three durable, comparable answers per metro:

1. **What kind of place is this?** (cluster label — a type)
2. **How does it rank?** (composite percentile score — a position)
3. **What else is like it?** (similarity — a peer set)

These three outputs, repeated across three conceptual lenses — **Character**, **Livability**, **Opportunity** — plus a combined **Cross-Frame** view, are the analytical backbone for the Metro Deep Dive series, the Area Explorer product, the Chatbot, and the Substack publishing queue. Every Deep Dive question ("is this a good time to move to Richmond," "what's Jacksonville's peer set," "is this metro diverging from itself") routes through this scoring model rather than being answered ad hoc from raw metrics.

### Why three frames instead of one score

A single "best place to live" score collapses distinctions that matter and are often in tension with each other — a metro can be a great place to build wealth and a rough place to live day-to-day (see Article 1, the Livability/Opportunity tradeoff). Splitting into three frames keeps those tensions visible instead of averaging them away:

- **Character** — who lives here and what makes the metro structurally distinct (demographics, social fabric, civic identity, built form). Explicitly **descriptive, not normative** — there is no "good" or "bad" Character score.
- **Livability** — do day-to-day conditions here support quality of life (affordability, health, access, physical environment).
- **Opportunity** — economic prospects for residents, investors, and businesses (income trajectory, market momentum, industry structure).

A fourth, derived view — **Cross-Frame** — looks at all three simultaneously to find metros that are internally coherent versus metros that are "diverging from themselves" (e.g., great Opportunity, poor Livability).

### Why the same machinery for all three

Every frame uses the identical build pipeline: same imputation rule, same standardization, same three-stage clustering sequence, same scoring hierarchy, same similarity method. This is a deliberate constraint, not a limitation — it means a reader (or a downstream engineer) only has to learn the method once, and any two frames' outputs are directly comparable in *how* they were produced, even though what they measure differs. The catalog docstring is explicit about this: "Architecture is locked" — decisions are made once, in the roadmap, and phase notebooks are not supposed to relitigate them.

---

## 2. How it works in practice — shared architecture

This section describes the pipeline every frame (and, with variations noted, the zone model) runs through. It's documented as the "locked" architecture in `INTELLIGENCE_LAYER_ROADMAP.md`.

### 2.1 Universe

All CBSAs (metro areas) with population ≥ 100,000 are included in every model. **CBSAs are never dropped for missing data** — missingness is handled per-KPI (impute or drop the KPI), not per-CBSA (drop the metro). The intent is a stable, complete universe every metro can be benchmarked against.

> **Note:** the roadmap specifies 401 CBSAs at this population floor; the actually-published frame marts use 396 (Puerto Rico excluded); the Phase 7 tract/ZCTA zone surface uses a larger 925-CBSA universe including micropolitan-adjacent tracts. See [§6.1](#61-universe-consistency) — this inconsistency is unresolved and documented as a limitation, not a decision.

### 2.2 Missing data — imputation

**Default:** median imputation. Replace a missing KPI value with the national median for that KPI across the published universe.

**Escalation rule:** KNN imputation is considered only when a KPI has >15% missingness *and* the missing pattern is clearly non-random (e.g., a source that systematically excludes small metros). In practice, every calibrated frame to date has stayed on median imputation — KNN has not been invoked.

**What gets dropped instead:** if a KPI's coverage problem is severe enough, the KPI is dropped from the model entirely (with a documented rationale) rather than imputed. Every imputation and drop event is meant to be logged — which KPIs, how many CBSAs affected.

### 2.3 Standardization and polarity

Every KPI is z-scored before clustering or scoring. Each KPI also carries a **polarity** flag:

- **Positive** — higher is better (`life_expectancy`, `lfpr`, `income_pc_growth_5yr`)
- **Negative** — lower is better (`premature_death_rate`, `pct_rent_burden_30plus`, `pct_unemployment_rate`)

Polarity only matters for **scoring**: negative-polarity KPIs are sign-flipped before rolling into sub-scores, so a higher composite score always means "better" on every axis. Polarity is irrelevant to **clustering and similarity** — distance metrics are direction-agnostic, so no sign-flip happens there.

### 2.4 Clustering — three passes, one input

Every frame runs the same three-stage sequence on the same standardized KPI vectors:

1. **Hierarchical agglomerative clustering** — discovers the natural number of clusters (`k`) from a dendrogram. This is diagnostic, not the published output.
2. **K-Means at natural k** — produces the hard, one-label-per-CBSA cluster assignment used for publication (e.g., "Superstar Knowledge Capitals"). Labels are assigned *after* inspecting cluster centroids — never pre-specified.
3. **Gaussian Mixture Model (GMM) at the same k** — produces soft membership probabilities per CBSA across all k clusters. This is what lets you say "Austin is 68% Knowledge Hub, 28% Sun Belt Growth, 4% other" instead of forcing a single label onto a metro that's genuinely a hybrid.

All three outputs are retained. Hard labels are the default for display; soft memberships are the default for analysis and for identifying metros that sit at cluster boundaries.

### 2.5 Scoring — hierarchical weighted rollup

Score flows upward through four levels:

```
KPI z-score (sign-flipped if negative polarity)
    → Topic score        (mean of KPI z-scores within topic)
        → Subject score      (weighted mean of topic scores within subject)
            → Frame composite    (weighted mean of subject scores)
                → Percentile rank (0–100 within the published universe)
```

**Subject weights** — equal across subjects within a frame for the initial model (e.g., Livability = 25% each across Affordability / Health & Safety / Access & Infrastructure / Physical Environment).

**Topic weights within a subject:**

```
raw_topic_weight = coverage_share × reliability_factor
topic_weight = subject_weight × (raw_topic_weight / sum(raw_topic_weights in subject))
```

Reliability factors: `core` = 1.00, `supplemental_baseline` = 0.75, `coverage_caution` = 0.60. A topic built on shakier or newer data literally counts for less in the rollup.

**KPI weights within a topic** — equal split across the KPIs marked `model_role: core` for that topic. (`sensitivity` and `descriptive` KPIs ride along for interpretation and audit but don't carry independent scoring weight; `dropped` KPIs are excluded entirely — see [§2.7](#27-kpi-roles)).

**Output:** a 0–100 percentile rank within the current published universe — the public-facing number — plus retained topic- and subject-level sub-scores for drill-down.

### 2.6 Similarity — cosine on the same vectors

**Method:** cosine distance on the standardized KPI vectors — the same vectors used for clustering and scoring.

**Why cosine, not Euclidean:** cosine measures whether two metros are *shaped* the same way across the metric profile (directional similarity), not whether they're similar in absolute magnitude. The design intent is "do these metros look like each other," not "are these metros the same size."

**Three similarity surfaces:**

1. **Frame-specific** — three independent matrices (Character peers, Livability peers, Opportunity peers), each computed on that frame's KPI vector alone.
2. **Cross-frame combined** — one matrix computed on the concatenated vector across all three frames: "who's most like this metro, period."
3. **Cross-frame overlap check** — not a similarity matrix at all, but a comparison of *cluster label* assignments across frames, to flag metros that are typical on one frame and an outlier on another ("diverging from themselves").

Each CBSA carries a top-10 peer list per surface in the promoted marts.

### 2.7 KPI roles

Every KPI in `intelligence_catalog.yml` carries a `model_role`:

- **`core`** — drives clustering and carries scoring weight
- **`sensitivity`** — included in clustering as a robustness check but not scoring-weighted
- **`descriptive`** — retained for interpretation/narrative but excluded from both clustering and scoring
- **`dropped`** — excluded from the model entirely; kept in the catalog as a documented decision, not deleted, so the redundancy call is auditable later

This is how a frame can carry, say, 26 KPIs in its catalog entry while only a subset actually drives the clustering math — the catalog is the full audit trail, not just the final input list.

### 2.8 Benchmarking

Every score is benchmarked at three levels: **national** (percentile within the full universe), **census division** (percentile within the CBSA's Census Division, 9 divisions), and **cluster peers** (percentile within CBSAs sharing the same cluster label). Custom peer sets (user-defined or size-matched) are supported as an optional fourth layer but aren't part of the default model.

### 2.9 Cross-frame overlap is intentional, not a bug

Several KPIs deliberately appear in more than one frame because the same fact supports different stories depending on the lens:

| KPI | Appears in | Because |
|---|---|---|
| `pov_rate` | Livability + Opportunity | household burden vs. trajectory context |
| `irs_net_migration_rate` | Character + Opportunity | residential stability vs. market momentum |
| `permits_per_1000_housing_units` | Livability + Opportunity | housing supply vs. market activity |
| `economic_connectedness` | Character + Opportunity | social fabric vs. mobility proxy |
| `pop_weighted_density_sqmi` | Character + Livability | built form vs. access proxy |

This overlap is preserved by design. The Cross-Frame model's job (not the individual frames') is to surface where that overlap becomes redundancy at the composite level.

---

## 3. Build method — how a frame actually gets built

Each frame is built as an independent, modular pipeline, all following the same file pattern established in Phase 3 (Livability) and reused for Phases 2, 4, and 5:

```
phase_N_<frame>_calibration/
  R/
    phase_N_config.R          ← constants, KPI sets
    phase_N_catalog_audit.R   ← confirm catalog KPIs match Gold columns
    phase_N_frame_build.R     ← pull + assemble the KPI frame
    phase_N_imputation.R      ← coverage audit + median imputation
    phase_N_redundancy.R      ← correlation / PCA redundancy pass
    phase_N_modeling.R        ← clustering + scoring + similarity
    phase_N_hypotheses.R      ← frame-specific hypothesis tests
    run_phase_N_<frame>.R     ← canonical runner; sources all modules in order
  <frame>_frame_model.qmd     ← review notebook — reads outputs/, does NOT re-query Gold
  outputs/
    <frame>_scores.parquet    ← canonical scored output
    <frame>_similarity_top10.csv
    <frame>_cluster_centroids.csv
    <frame>_cluster_count_calibration.csv
    <frame>_gmm_summary.csv
    ...plus audit outputs (completeness, imputation, redundancy)
```

**The separation that matters:** the runner script (`R/run_phase_N_*.R`) is the source of truth for the build — it's the only thing that touches Gold tables and writes canonical artifacts. The `.qmd` review notebook is read-only against those artifacts — it exists for visual QA, cluster interpretation, and written narrative, and is never allowed to silently re-derive numbers the runner didn't produce. This means the calibration is fully reproducible from the runner alone, and the review notebook can be re-rendered any time without rerunning the model.

**Canonical build sequence** (same shape for every frame):

1. Coverage audit against the semantic catalog's KPI list
2. Assign / confirm polarity flags
3. Median-impute, logging every affected KPI × CBSA
4. Standardize (z-score) all inputs
5. Redundancy pass (correlation matrix + PCA diagnostic) — informs which KPIs get `model_role: dropped`, but the final call is manual and theory-grounded, not automated. PCA is a diagnostic tool here, never the scoring method itself — this is a deliberate interpretability choice.
6. Hierarchical clustering → natural k
7. K-Means at natural k → hard labels
8. GMM at natural k → soft memberships
9. Name clusters from centroid inspection (+ literature anchor for Character)
10. Score: topic → subject → composite → percentile
11. Cosine similarity → top-10 peers
12. Frame-specific hypothesis tests
13. Written interpretation with named metro examples

**Promotion:** only the final scored parquet moves downstream. During calibration, phase-local `outputs/` folders are the source of record. Once stable, an R loader script (`foundations/loaders/load_<frame>_scores.R`) reads that parquet, normalizes column names to stable semantic aliases, and writes it into DuckDB under the `mart_intelligence` schema — a dedicated downstream product-mart layer, not "Gold-on-Gold." Gold stays the raw KPI source; `mart_intelligence` is the scored/derived layer built on top of it.

**The catalog is updated per phase, not deferred.** `intelligence_catalog.yml`'s own docstring says this explicitly: each Phase 2–4 notebook is expected to update its own catalog entry from `status: placeholder` to `status: calibrated` with populated `calibration_notes` and `natural_k` — Phase 8 only verifies and promotes, it doesn't do the catch-up work itself.

---

## 4. The frames

### 4.1 Character — Phase 2

*Who lives here and what makes it structurally distinct. Explicitly descriptive, not normative.*

- **Final k:** 7 · **KPI set:** full 17-KPI bundle retained (no pair crossed the redundancy threshold)
- **Subjects (equal weight, 50/50):** Demographics, Social Fabric
- **Demographics topics:** Race & Ethnicity, Age Structure, Educational Attainment, Nativity & Citizenship, Population Density
- **Social Fabric topics:** Social Capital, Nonprofits & Civic Organizations, Residential Stability, Social Associations, Built Form, Household Structure
- **Cluster labels** (literature-anchored against Brookings metro typologies, Pew community framing, and Moretti's knowledge-economy divergence — see `character_clustering_notes.md`):
  - Global Knowledge Capitals
  - Retirement And Lifestyle Havens
  - College And Civic Anchors
  - Established Community Anchors
  - Immigrant Growth Corridors
  - Rooted Heartland Centers
  - Interior Family Opportunity Hubs
- **Why the literature anchor step exists (and only for Character):** Livability and Opportunity can lean on present-condition or forward-economic metrics that are self-justifying — a metro either has high rent burden or it doesn't. Character is a pure typology question ("what *kind* of metro is this"), which is inherently more interpretive, so its labels need external grounding before they're defensible in print. The anchor review found the current 7-type map directionally consistent with all three reference frameworks, while adding a combination (demographic composition + civic structure + rootedness in one typology) none of the three anchors combine on their own.
- **Imputation note:** Waterbury-Shelton, CT required bounded median imputation for 4 `social_fabric_wide` KPIs due to a single missing source row — the only named imputation event in Character.
- **Open interpretive question carried in the roadmap:** whether "Established Community Anchors" and "Interior Family Opportunity Hubs" are substantively distinct enough narratively, even though the clustering structure supports keeping them separate.

### 4.2 Livability — Phase 3

*Whether day-to-day conditions support quality of life. First frame built — highest publishing priority (unblocks Article 1).*

- **Final k:** 6 · **KPI set:** full 26-KPI bundle retained after PCA/correlation review
- **Subjects (equal weight, 25% each):** Affordability, Health & Safety, Access & Infrastructure, Physical Environment
- **Affordability topics:** Price Pressure, Housing Burden, Poverty Context, Housing Supply, Housing Structure Mix
- **Health & Safety topics:** Health Outcomes, Health Behavior & Access, Violence & Injury
- **Access & Infrastructure topics:** Commute & Mode, Vehicle Access, Housing Slack, Digital Access, Walkability Baseline, Food Access Baseline, Built-Form Proxy
- **Physical Environment topics:** Air Pollution, Climate Hazard Risk, Hazard Exposure — all three carry `coverage_caution` reliability (weighted at 0.60), reflecting real coverage gaps in EJScreen/FEMA data
- **AQI decision:** `aqi_median` replaced `aqi_unhealthy_days` as the default clustering KPI — more interpretable than a zero-heavy rare-event count where AQI data is thin.
- **Smell test used to sanity-check the model:** does the Affordability topic rank NYC / coastal metros near the bottom and Midwest interior metros near the top? (Confirmed.)
- **Hypothesis tests carried in the catalog:**
  - *Southern health deficit* — do metros that score well on Affordability score poorly on Health & Safety? (Article 3)
  - *Environmental risk axis* — does `fema_risk_score` add non-redundant signal beyond the AQI metric?
- **Imputation note:** median imputation applied to 6 KPIs in the final run.

### 4.3 Opportunity — Phase 4

*Economic prospects for residents, investors, and businesses. Second frame built — completes Article 1's four-quadrant scatter with Livability.*

- **Final k:** 6 · **KPI set:** reduced 20-KPI clustering set (holds out `pct_real_gdp_information` and `permits_per_1000_housing_units` — both overlap with stronger retained signals, though both are kept as `descriptive` for scoring/context)
- **Subjects (equal weight, 33% each):** Resident Opportunity, Market & Investor Opportunity, Business & Industry Opportunity
- **Resident topics:** Income Growth, Wage Levels, Labor Market Tightness, Poverty & Inclusion, Intergenerational Mobility Proxy
- **Market topics:** Home Price Appreciation, Rent Growth, Population Growth, Migration & Wealth Flows, Permit Activity
- **Business & Industry topics:** GDP Growth, Industry Concentration, Human Capital Momentum, Business Formation, Establishment Density, Location Quotient Specialization, Sector GDP Mix, Sector Employment Mix
- **Cluster labels:** Superstar Knowledge Capitals, Broad-Based Opportunity Hubs, Emerging Momentum Markets, Industrial Rebound Markets, Uneven Transition Markets, Thin-Base Distressed Markets
- **k=6 vs k=5 tradeoff (explicit, documented):** k=6 slightly trails k=5 on K-Means silhouette score but was chosen anyway because it preserves a narratively useful subtype split and a stronger hierarchical structure — an explicit case of favoring interpretability over the marginal quantitative metric.
- **Coverage-caution KPI:** `zori_annual_avg_yoy_pct` (Rent Growth) — retained despite being the frame's weakest-coverage core KPI (see [§6 findings](#6-known-limitations--open-questions), a review question flags this needs a coverage-bias check).
- **`economic_connectedness`** is retained as a hypothesis/audit signal only — not in the default clustering set, pending direct mobility data (Opportunity Atlas) expansion.
- **Hypothesis tests:** industry mix as a leading indicator of income growth (Article 4), social capital vs. income growth (Article 5), 1yr vs. 5yr signal divergence, Opportunity Zone exposure overlay.

### 4.4 Cross-Frame — Phase 5

*A combined model built from the concatenated KPI vectors of all three frames. Depends on Character, Livability, and Opportunity all being stable first.*

- **Final k:** 7 · **KPI set:** reduced 35-KPI bundle (from a 63-KPI combined pool, refreshed after Livability's AQI swap)
- **Not three frames averaged into one** — a fresh clustering + similarity pass on the concatenated standardized vectors, run through its own PCA reduction to drop redundant/low-communality KPIs before clustering (dropped KPIs are carried forward as descriptive-only columns, never lost)
- **Cluster labels:** Entrepreneurial Strain Markets, High-Amenity Knowledge Civics, Stable Affordable Heartland Markets, Inland Strain Corridors, Global Knowledge Gateways, Aging Amenity Expansion Markets, Sun Belt Opportunity Engines
- **Primary purpose:** feed the **overlap check** — comparing each CBSA's frame-specific cluster assignments to find metros that are "diverging from themselves" (e.g., high Opportunity cluster tier but low Livability cluster tier). This divergence list is the primary Deep Dive candidate feed, not a generic "best overall metro" ranking.
- **Promoted context fields:** `frame_percentile_gap`, `top_frame`, `bottom_frame`, `overlap_profile` — designed so a downstream product can say *which* frame is pulling a metro's overall picture in which direction, not just that divergence exists.
- **This is where the article "The metros that can't make up their mind" (Article 6) comes from.**

---

## 5. Beyond the static frames: Trajectory and Zones

The two catalogs referenced above (`intelligence_catalog.yml`, `theme_catalog.yml`) describe the **static CBSA-grain frame scoring system** (Phases 1–5, 8). Two further phases extend the Intelligence Layer beyond that snapshot:

### 5.1 Phase 6 — Trajectory (movement over time)

Where Phases 2–5 answer "where does this metro sit right now," Phase 6 answers "which direction is it moving, and how fast." It runs two equally-weighted passes per CBSA — a **momentum pass** (velocity/acceleration of change) and an **outlier pass** (distance from the national mean, and whether that distance is growing or shrinking) — combined into a composite trajectory score, segmented into four directions: diverging-improving, diverging-declining, converging-improving, converging-declining. Convergence (bounce-back, cooling-off) is treated as analytically as interesting as divergence.

Time windows are frame-dependent: Character and Livability use a 5-year window only (their underlying metrics move slowly; 1-year noise isn't signal); Opportunity uses both 1-year and 5-year windows explicitly compared, flagging "turn signal" metros where the short-run direction contradicts the medium-term trend.

Five pattern filters run as a single scan (none pre-ranked): bounce-back markets (Article 7), hidden Livability winners (Article 8), diverging-from-themselves (cross-referenced with the Phase 5 overlap flag — this intersection is the highest-priority Deep Dive candidate signal in the whole framework), fast demographic changers, and dual-axis environmental risk outliers.

**Output:** `phase6_candidate_list.csv` — a ranked Deep Dive candidate list enriched with Phase 5 cross-frame context. This, not a frame percentile, is the operational answer to "which metro should we write about next."

### 5.2 Phase 7 — Zones (sub-metro, tract-grain classification)

Zones answer a different question than the CBSA frames: not "how does this metro compare to others" but "what does the inside of this metro look like." One combined KPI vector per census tract (closer in spirit to the Cross-Frame model than to the independent CBSA frames), run through the same hierarchical → K-Means → GMM sequence, locked at k=7 zone types:

- Entry-Market Neighborhoods
- Emerging Knowledge Districts
- Knowledge Corridor
- Established Residential
- Mixed-Income Middle Neighborhoods
- Working Neighborhoods
- Commercial Core / Jobs Center

Zone types are a **national model** — a "Knowledge Corridor" tract means the same thing in Jacksonville, Richmond, or Chicago, which is what makes cross-market Deep Dive comparison possible. A ZCTA-grain rollup (for reader-friendly ZIP-code presentation) inherits a tract's dominant zone only when that zone exceeds 50% of the HUD population-weighted tract mix within the ZCTA; otherwise it's labeled `Mixed Zone`. The separate Corridor Intelligence Engine owns reproducible within-market grouping: same-zone tracts form candidate cores, while governed Geography, Infrastructure, aggregate POI composition, and conservative bridge rules refine membership before each candidate is classified as a corridor or district. Its first method and systematic IDs are planned under `metro-deep-dive-program/engines/corridor_intelligence/`; the original per-market DBSCAN design is retained only as pilot evidence and is not a dependency of the canonical tract/ZCTA marts.

Zone methodology has its own literature anchor review (NCRC gentrification typologies, UC Berkeley's Urban Displacement Project, Esri Tapestry, Moretti) — see `zone_methodology_notes.md` and `zone_methodology_literature_review.md`.

---

## 6. The two catalogs as one system

`intelligence_catalog.yml` and `theme_catalog.yml` describe the same underlying frames from two different angles, and the framework only works end-to-end because they stay in sync.

| | `intelligence_catalog.yml` | `theme_catalog.yml` |
|---|---|---|
| **Purpose** | The scoring model itself | User-facing topic browsing |
| **Consumers** | The R build pipeline, the semantic layer's methodology documentation | Area Explorer, the Chatbot |
| **Structure** | frame → subject → topic → KPI, with weights, polarity, reliability, `model_role` | theme → topic → metric list, with `intelligence_frame_topic: true/false` |
| **Contains dropped KPIs?** | Yes — every KPI ever considered, tagged `dropped`, as an audit trail | No — dropped KPIs are removed; only metrics with standalone query value are retained |
| **Granularity of truth** | Which KPIs *actually drive* the cluster/score math | Which metrics a reader can browse *about* a topic, whether or not they're in the model |

The `intelligence_frame_topic: true` flag on a `theme_catalog.yml` topic is the join key back to the modeling layer — it marks "this browsable topic corresponds 1:1 to a topic inside `intelligence_catalog.yml`'s frame definition," versus topics like `population_size_and_growth` (Character) or `social_capital_signal` (Opportunity) that exist for browsing/context but are explicitly `intelligence_frame_topic: false` because they aren't part of that frame's scoring model.

Practically: `theme_catalog.yml` topics generally carry *more* metrics than the corresponding `intelligence_catalog.yml` topic, because a metric with independent narrative or query value (e.g., `median_home_value`, `pct_ba_plus_change_5yr` shown standalone) stays browsable even after being marked `descriptive` or `dropped` in the modeling catalog. The intelligence outputs themselves (`livability_percentile_rank`, `character_cluster`, the four Livability sub-scores, etc.) are surfaced at the top of each `theme_catalog.yml` theme as `intelligence_outputs` — the bridge from "here's a browsable topic" to "here's the model's verdict."

---

## 7. Known limitations and open questions

This section is deliberately not resolved here — it's the standing list of methodological gaps identified in the 2026-08-04 review question bank (`metro-deep-dive/docs/intelligence_framework_review_question_bank.md`) that should be treated as open, named risks rather than settled decisions. Anything published externally off these outputs inherits whichever of these are still unresolved at publish time.

### 6.1 Universe consistency
Three different universe counts appear across the documentation: 396 CBSAs (frame calibration notes, actually published), 401 CBSAs (roadmap architecture spec, population-floor definition), and 925 CBSAs / 78,199 tracts (Phase 7 zone surface). It is not established anywhere that a downstream consumer can read which universe a given percentile was computed against, or what happens to a published percentile if the universe later changes.

### 6.2 Similarity method is unvalidated
Cosine similarity on standardized (z-scored) vectors is close to correlation — it measures **profile shape**, not level or size. Two metros with the same relative pattern at very different intensities read as highly similar. This may be the intended behavior ("peer" meaning structurally similar, not scale-comparable) but that intent is not explicitly documented anywhere, and:
- The peer sets have never been validated against naive baselines (same population tier, same state, same Census division).
- No size/scale variable is in the KPI vector, so peer lists can pair very differently sized metros — defensible, but unstated.
- Similarity is currently levels-only; the Deep Dive template's planned "forward analog" (trajectory-peer via trend-slope similarity) has not been built.
- It's unconfirmed whether frame-level similarity and cross-frame similarity use identical standardization, even though the Research Tool presents them side by side as comparable.

This is flagged in the question bank as the single largest gap between the current method and a publishable one.

### 6.3 Character's composite score
Character is documented as "descriptive, not normative," but it runs through the same scoring machinery as Livability and Opportunity, including sign-flipped polarity and a percentile rank. What a high Character composite score is supposed to *mean* — if anything — is not defined. This is flagged as the most likely place an unintended value judgment enters a frame explicitly meant not to carry one.

### 6.4 Cluster stability and centroid separability
Cluster stability (bootstrap resampling, repeated K-Means with different seeds) has not been tested for any frame. A metro's published cluster label may or may not be robust to resampling — this is currently unknown rather than confirmed either way. Similarly, centroid separability (which KPIs actually distinguish each cluster) hasn't been reported per cluster per frame; a cluster not separable on any interpretable KPI would be a modeling artifact rather than a market type.

### 6.5 GMM soft memberships are inconsistent across frames
Character has tuned GMM soft memberships. Whether Livability and Opportunity have equivalent soft memberships (not just hard cluster labels) is not confirmed as consistently populated.

### 6.6 Weighting sensitivity untested
Subject and topic weights are currently equal-weighted by design ("initial model"). No sensitivity check has been run to see how much frame percentile ranks would move under a plausible alternative weighting. If rankings are stable under reweighting, that's a strong, publishable claim; if not, that's important to know before rankings are published as if they were precise.

### 6.7 Vintage spread inside a "snapshot"
Each frame mart is described as a static CBSA-grain snapshot, but its underlying KPIs span very different real-world vintages (Social Capital Atlas ~2022, EJScreen 2024, FEMA NRI 2025, USDA food access 2019 on 2010 tract boundaries, AQI spanning 2016–2025). The framework does not currently report, per frame, the total vintage spread of its inputs.

### 6.8 Data-quality flags aren't propagated downstream
Imputed values, coverage-caution KPIs, and Connecticut/BEA-affected metros are documented in phase-local audit outputs, but it is not confirmed whether a downstream consumer (Area Explorer, Chatbot, a Deep Dive writer) can identify, at the point of use, that a specific metro's cluster or score depended on imputed or low-coverage data.

### 6.9 Remaining Phase 8 follow-up
One Phase 8 task is explicitly still open: MotherDuck validation that all `mart_intelligence` tables (including the Phase 7 tract/ZCTA marts) are actually queryable by Area Explorer and the Chatbot.

---

## 8. Quick reference — where things live

| What | Where |
|---|---|
| Scoring model definition | `foundations/semantic_layer/intelligence_catalog.yml` |
| User-facing topic browsing | `foundations/semantic_layer/theme_catalog.yml` |
| Full roadmap + locked architecture decisions | `INTELLIGENCE_LAYER_ROADMAP.md` |
| Phase build code + outputs | `exploration/intelligence_framework/phase_N_*/` |
| Cross-phase calibration summary | `exploration/intelligence_framework/docs/intelligence_calibration_notes.md` |
| Character literature anchor | `exploration/intelligence_framework/docs/character_clustering_notes.md` |
| Zone methodology | `exploration/intelligence_framework/docs/zone_methodology_notes.md` + `zone_methodology_literature_review.md` |
| Open methodological questions | `metro-deep-dive/docs/intelligence_framework_review_question_bank.md` |
| Production query layer | DuckDB schema `mart_intelligence.*` |
