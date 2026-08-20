# Intelligence Framework — Review Question Bank

**Last updated:** 2026-08-04
**For:** an agent with full repo access to the Intelligence Framework phases, `semantic_layer/`, and `mart_intelligence`
**Purpose:** verify the published framework against its own documentation, and surface the methodological choices that need to be defensible before any of this is published externally

## How to use this

These are diagnostic questions, not build tasks. The output should be a written findings memo, not code changes. Where a question has a clear answer in the repo, state it and cite the file. Where it does not, say so — an undocumented choice is itself a finding.

**Priority order:** Section B first. The similarity method is the foundation of the peer sets used across Area Explorer, the Research Tool, the Deep Dive template §3, and a planned research article. If it has a problem, everything downstream inherits it.

---

## A — Universe and coverage

**A1.** Three different universes appear across the documentation: `396` CBSAs in the calibration notes and cross-frame plan, `401` CBSAs in the Research Tool roadmap and platform framing, and `925` CBSAs / `78,199` tracts in the Phase 7 zone surface. Establish which is authoritative for each mart, whether the differences are intentional (Puerto Rico exclusion, population floor, micropolitan inclusion), and whether any downstream product assumes the wrong one.

**A2.** Percentile ranks are computed within the published universe. Confirm what happens to published percentiles if the universe changes. Is the universe version recorded anywhere a downstream consumer can read?

**A3.** `zori_annual_avg_yoy_pct` is documented as retained "with coverage caution." Report its actual coverage rate, which CBSAs lack it, and whether the metros missing it are systematically different (smaller, non-metro-adjacent, particular divisions). If coverage is correlated with market type, its inclusion biases Opportunity scores in a patterned way rather than randomly.

**A4.** For each frame, report the KPI with the worst coverage and how missingness is handled in scoring versus in clustering. These may not be the same path.

---

## B — Similarity method (highest priority)

**B1.** Cosine similarity is computed on standardized KPI vectors. Confirm whether standardization is z-scoring across the full universe. If so, note that cosine on mean-centered data is closely related to correlation — it measures **profile shape**, not level. Two metros with the same relative pattern at very different intensities will read as highly similar. Was this deliberate? Document the reasoning or flag it as an open choice.

**B2.** Does the KPI vector include any size or scale variable (population, total employment, GDP level)? Report whether the published top-10 peer lists pair metros of very different size, and give concrete examples. If size is excluded, that is defensible but must be stated — "peer" then means structurally similar, not comparable in scale.

**B3.** Has the peer set ever been validated out of sample against naive baselines? Specifically: do cosine peers outperform same-population-tier, same-state, or same-Census-division groupings on any holdout criterion? If no validation exists, say so plainly. This is the single largest gap between the current method and a publishable one.

**B4.** Similarity is currently computed on **levels** only. The Deep Dive template §3 specifies running it twice — on levels and on **trend slopes** — and using the comparison to identify a "forward analog" (a trajectory-peer that sits further along in levels). Report whether Phase 5 or Phase 6 outputs can support a slope-based similarity run without new modeling, and what would be required if not.

**B5.** The Cross-Frame model uses a combined `35`-KPI bundle drawn from frames that individually use `17`, `26`, and `22` KPIs. Report the overlap: which KPIs appear in more than one frame, and whether any are effectively double-weighted in the combined vector. Also report whether correlated KPIs were decorrelated (PCA or otherwise) before the combined similarity run, since the template raises this as an explicit open choice.

**B6.** Confirm whether frame-level similarity (Livability peers, Opportunity peers, Character peers) and cross-frame similarity use identical method and standardization. Any difference should be documented, because the Research Tool Peers tab presents them side by side as if comparable.

---

## C — Clustering and k selection

**C1.** Final k values are `7` (Character), `6` (Livability), `6` (Opportunity), `7` (Cross-Frame), `7` (zones). Report how each was selected and what diagnostics were run — elbow, silhouette, gap statistic, or visual inspection of the hierarchical dendrogram.

**C2.** Report whether cluster stability was tested. Bootstrap resampling with adjusted Rand index, or repeated K-Means with different seeds, would each answer this. If a metro's cluster assignment flips across resamples, its published label is not a fact about the metro.

**C3.** GMM soft memberships are produced for Character. The Research Tool feedback log asks whether Livability and Opportunity also have them. Confirm whether soft memberships exist for all frames, and if not, why Character was treated differently.

**C4.** Cluster names are literature-anchored (Brookings, Pew, Moretti) for Character. Report whether Livability, Opportunity, and Cross-Frame names have equivalent grounding or were assigned interpretively. Names are durable editorial assets and are reused across every published issue, so their provenance matters.

**C5.** For each frame, report the cluster centroid profile — which KPIs actually distinguish each cluster. A cluster that is not separable on any interpretable KPI is a modeling artifact, not a market type.

---

## D — Scoring, weighting, polarity

**D1.** The scoring hierarchy runs KPI z-scores to topic scores to subject scores to frame composites. Report the weights at each level. Are they equal-weighted, or are there explicit weights in `intelligence_catalog.yml`? If equal, note that topics with more constituent KPIs may be implicitly downweighted or upweighted depending on how the rollup is implemented.

**D2.** Run a sensitivity check: how much do frame percentile ranks move under a reasonable alternative weighting? If the ranking is stable, that is a strong claim worth making publicly. If it is not, that is important to know before publishing rankings.

**D3.** Negative-polarity KPIs are sign-flipped for Livability and Opportunity so higher means better. Character is documented as descriptive rather than normative but uses the same machinery. Report whether Character produces a composite score, and if so, what a high Character score is supposed to mean. This is the most likely place for an unintended value judgment to enter a frame that is explicitly meant not to carry one.

**D4.** Report which KPIs are marked `core`, `sensitivity`, `descriptive`, and `dropped` in `intelligence_catalog.yml`, and confirm the published models use only what the calibration notes say they use.

**D5.** Character retained its full `17`-KPI bundle after redundancy review while Opportunity was reduced. Report the redundancy criteria applied in each case and whether they were consistent across frames.

---

## E — Imputation and data quality

**E1.** Two imputation events are documented: bounded median imputation for four `social_fabric_wide` KPIs for Waterbury-Shelton, CT, and median imputation for six KPIs in the final Livability run. Report the full imputation inventory — every CBSA and KPI affected, across all frames.

**E2.** Confirm whether imputation happens before or after standardization. Median-imputing a raw value and then z-scoring is not the same as imputing the z-score, and the difference affects cluster assignment.

**E3.** Report whether imputed values are flagged anywhere a downstream product can read them. A metro whose cluster assignment depends on imputed KPIs should be identifiable, particularly before it is written about.

**E4.** Report how many CBSAs have any imputed KPI in any published frame, as a share of the universe.

---

## F — Vintage and time

**F1.** The marts are documented as static CBSA-grain snapshots. But the underlying KPIs span very different vintages — Social Capital Atlas is a static 2022 release, EJScreen is 2024 only, FEMA NRI is 2025, USDA food access is 2019 and built on 2010 tract boundaries, AQI runs 2016–2025. Report the vintage of every KPI in each published frame vector and the total spread. A "snapshot" assembled from sources spanning six or more years should say so.

**F2.** Report how Phase 6 trajectory analysis reconciles with static frame marts. If trajectory is computed on a different KPI set or a different universe than the published frames, the Research Tool is presenting two surfaces that do not correspond.

**F3.** The Research Tool feedback log reports the Phase 6 KPI trajectory heatmap is empty for all metros due to an `int64` versus string CBSA code mismatch. Confirm whether this is fixed. If not, report whether the same type mismatch exists anywhere else in the mart contract.

---

## G — Zones

**G1.** The ZCTA rollup assigns the dominant tract zone only when one zone exceeds `50%` of the HUD population-weighted tract mix, otherwise `Mixed Zone`. Report what share of ZCTAs land in `Mixed Zone` nationally. If it is a large majority, the ZCTA mart carries little signal and downstream products should be told.

**G2.** Zone types are a national model applied within markets. Report the distribution of the seven zone types across markets — specifically, how many markets contain all seven, and whether some types are effectively absent outside large metros. The Deep Dive §8 composition benchmark depends on this being a meaningful national distribution.

**G3.** The Deep Dive template §8 benchmarks a market's zone composition "against the average across all metros run to date." Confirm whether a national zone composition distribution already exists as a computed artifact. If it does, the template's accumulating-benchmark language is obsolete and should be corrected — the benchmark is available for issue one.

**G4.** Per-market DBSCAN corridor detection is documented as optional Deep Dive workflow rather than a mart dependency. Report whether any corridor artifacts exist for Richmond or Jacksonville, and whether the `eps` calibration rule discussed in the zone methodology notes was ever implemented or left as a proposal.

**G5.** Report which of the three zone construction options — DBSCAN, HDBSCAN, SKATER — the published Phase 7 output actually uses, and whether the alternatives were tested or only discussed.

---

## H — Downstream contract

**H1.** The calibration notes list a remaining follow-up: MotherDuck validation that `mart_intelligence` tables, including the Phase 7 tract and ZCTA marts, are queryable by Area Explorer and the Chatbot. Report current status.

**H2.** Report whether `metric_catalog.yml` covers the Intelligence mart's scored and raw columns, or only Gold-layer metrics. The Research Tool feedback log identifies this as a gap forcing a hand-coded display-name dictionary in `config.py`.

**H3.** Report whether any product hardcodes cluster names, k values, or peer counts rather than reading them from the semantic layer. These are exactly the values most likely to change on recalibration.

**H4.** The cross-frame similarity plan proposes promoting peers as a long table (`mart_intelligence.intelligence_cross_frame_peers`) rather than wide `top10_peer_*` columns. Report whether any current consumer would break if that promotion happened, and whether the wide columns would then be redundant.

---

## Deliverable

A written findings memo organized by these sections, with:

- a direct answer per question, citing the file or artifact that supports it
- an explicit "not documented" for anything the repo does not answer
- a short list at the end of the findings that would block external publication of the peer sets or the frame rankings

Do not fix anything found. Report first.