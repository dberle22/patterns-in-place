# Phase 7 — Zone Methodology: Sprint Plan

*Last updated: 2026-07-01*

Full methodology reference: `exploration/intelligence_framework/docs/zone_methodology_notes.md`

---

## Summary

Phase 7 builds the sub-metro zone classification system. It produces:

1. **National zone types** — every tract in the current full tract base gets a nationally consistent label
2. **Tract intelligence mart promotion** — the canonical tract output is materialized to `mart_intelligence.intelligence_zones`
3. **ZCTA rollup** — tract labels are rolled up to ZCTAs for presentation and downstream lookup use
4. **Optional deep-dive corridor workflow** — per-market DBSCAN corridor detection remains available for true market deep dives, but it is no longer a Phase 7 completion gate

Sprint 0 through Sprint 4 are now complete for the canonical Phase 7 deliverable. The tract and ZCTA zone surfaces are both materialized in `mart_intelligence`, while DBSCAN corridor work remains optional for true Deep Dive markets.

---

## Architecture recap

```
Gold tract KPI vector (ACS + LEHD + SLD + EJScreen/FEMA tract promotion)
    → Stage 1: National zone type model (hierarchical → k-means → GMM)
        → Hard zone_type label per tract
        → GMM soft membership probabilities
        → National and CBSA percentile benchmarks
            → Tract promotion to mart_intelligence.intelligence_zones
                → ZCTA rollup (majority-assignment from tract)
                    → Optional Stage 2 deep-dive corridor detection (DBSCAN, hybrid distance)
```

---

## Sprint 0 — Data Prerequisites

**Status:** Complete  
**Outcome:** The Phase 7 input surface now carries tract-ready LODES, SLD, EJScreen, and FEMA fields into `gold.intelligence_zone_inputs`. Tract SLD remains a one-time `2021` baseline rather than part of the recurring ACS transport panel, but it is now included in the exploratory tract frame because live tract coverage is high enough to support it.

### 0.1 — LEHD/LODES Silver ingestion

LODES WAC (Workplace Area Characteristics) provides jobs per tract by sector and earnings tier. This is the only source of tract-level Opportunity signal beyond ACS income/labor.

**Tasks:**
- [x] Ingest the current live LODES WAC snapshot carried by the Phase 7 build (`2023` in the present Gold surface)
- [x] Write `foundations/etl/silver/lehd_lodes_silver.R` — download, parse, normalize to tract-first Silver WAC/RAC tables
- [x] Write `foundations/etl/gold/gold_economics_lodes.sql` — compute derived KPIs: `jobs_per_resident`, `pct_jobs_high_wage` (CE03 share), `pct_jobs_professional_services`
- [x] Add `economics_lodes_wide` entry to `foundations/semantic_layer/table_catalog.yml`
- [x] Document current LODES Phase 7 coverage in EDA: the three retained LODES KPIs each miss `3,013` tracts (`3.9%`) in the current `78,199`-tract frame, which is acceptable for the initial model pass
- [x] Move anchor-employer spot-checks for Jacksonville and Richmond VA to Sprint 2 / Sprint 3 interpretation rather than keeping Sprint 0 open on a manual validation task

**Expected output:** `gold.economics_lodes_wide` — one row per geography-year with tract-ready job count KPIs available for zone clustering input

### 0.2 — Tract environmental promotion closeout

EJScreen (`ejs_pm25`) and FEMA (`fema_risk_score`) are now surfaced at tract grain in governed Gold and carried into the Phase 7 tract frame. Tract SLD also now joins into the exploratory tract frame from `gold.transport_built_form_sld`; it remains a one-time `2021` baseline and the residual tract gap is still concentrated in Connecticut, but the national overlap with the Phase 7 tract base is now high enough to support EDA and KPI evaluation.

**Tasks:**
- [x] Verify `foundations/etl/gold/gold_environment_wide.sql` already has tract bridge logic; expose `geo_level = 'tract'` rows in the output
- [x] Confirm `foundations/semantic_layer/table_catalog.yml` now advertises tract support for `environment_wide`
- [x] Carry tract `ejs_pm25` and `fema_risk_score` into `gold.intelligence_zone_inputs`
- [x] Revisit tract SLD after the live overlap audit and carry `walkability_index` plus `jobs_access_45min_transit` into `gold.intelligence_zone_inputs`

---

## Sprint 1 — Methodology + Literature Review

**Status:** Complete  
**Depends on:** Nothing  
**Goal:** Lock the KPI input set, zone type label candidates, and DBSCAN parameters before writing any code. Avoid having to re-run the national model because a conceptual decision changed.

### 1.1 — Literature review

Review the four published frameworks and document alignment/divergence:

- [x] Review **NCRC Changing America Neighborhood Typologies (2023)** — document inputs, cluster count, label set, and where ours aligns/diverges
- [x] Review **Urban Displacement Project Neighborhood Change Typologies** — focus on gentrification/displacement framing; how does their Emerging/Transitional type map to ours?
- [x] Skim **Esri Tapestry** documentation — note inputs (proprietary consumer data) and granularity (67 types); document why our approach is analytically distinct
- [x] Review **Moretti "New Geography of Jobs"** — grounding for Knowledge Corridor type and the education/jobs clustering dynamic
- [x] Write up in `docs/zone_methodology_notes.md` under a Literature Review section

### 1.2 — Input KPI finalization

**Status:** Complete

**EDA recommendations to lock now:**
- [x] Update the modeling-universe language across Phase 7 docs to the current full tract base carried by `gold.intelligence_zone_inputs`, not the legacy `396`-CBSA framing. As of `2026-07-01`, the live Phase 7 frame is `78,199` tracts across `925` CBSAs.
- [x] Keep the tract momentum fallbacks `pct_ba_plus_change_3yr` and `pov_rate_change_3yr` for Phase 7. Do not block on tract-safe five-year harmonization.
- [x] Keep the retained LODES WAC trio in the initial clustering vector: `jobs_per_resident`, `pct_jobs_high_wage`, `pct_jobs_professional_services`. Do not block Sprint 2 on LODES OD or `jobs_inflow_ratio`.
- [x] Drop `median_gross_rent` from the initial clustering vector. Coverage is only `94.2%`, the null pattern is real source sparsity, and it is redundant with better-covered housing value / burden signals.
- [x] Drop `pct_commute_transit` from the initial clustering vector. It has weak within-CBSA discriminatory power (`0.27` within/national ratio) and is strongly overlapping with density / zero-vehicle structure.
- [x] Keep `pop_weighted_density_sqmi`, but treat it as a log-transform candidate and revisit only if it dominates the Knowledge Corridor / urban-core separation too heavily.
- [x] Finalize the default clustering contract at `22` KPIs after the tract-level PCA pass. The lean default keeps one strong representative per latent dimension rather than carrying all plausible neighboring proxies.
- [x] Keep `walkability_index` in the default clustering vector, but move `jobs_access_45min_transit` to sensitivity-check status after the PCA rerun showed it was mostly absorbed by the broader urbanity / accessibility bundle.
- [x] Treat the remaining data cleanup items as Sprint 2 prep, not Sprint 0 blockers: duplicate-income-column app bug, negative unemployment values, zero-denominator `NaN` handling, and the `14`-tract join miss concentrated in county `36103` / CBSA `35620`

**Sprint 1.2 output: locked 22-KPI default clustering vector**

- [x] Confirm final tract KPI list across all three themes (Character / Livability / Opportunity) — see `docs/zone_methodology_notes.md` KPI table
- [x] Translate the EDA and PCA decisions into the canonical KPI table in `docs/zone_methodology_notes.md`
- [x] Document polarity flags for all zone KPIs in `phase_7_zone_methodology/R/phase7_config.R`
- [x] Document the SLD treatment rule in config: `walkability_index` is retained as a one-time `2021` baseline KPI with a visible Connecticut-heavy coverage note, while `jobs_access_45min_transit` moves to sensitivity-check status
- [x] Write `phase_7_zone_methodology/R/phase7_config.R` — KPI list, polarity flags, source table mappings, coverage rules

### 1.3 — DBSCAN parameter design

**Status:** Complete

- [x] Define hybrid distance formula: `α × feature_distance + (1−α) × spatial_distance`
- [x] Document default `α = 0.70` and the rationale
- [x] Identify R packages: `dbscan` (DBSCAN implementation), `sf` plus `proxy` (spatial operations and cosine-distance support), `spdep` or `rgeoda` as optional spatial-weights backups
- [x] Write corridor naming convention into config: `{county_name}_{zone_type}_{rank}`
- [x] Document calibration approach for `eps` and `min_samples` — keep both unset in config until the Jacksonville stress test in Sprint 3, then lock them from k-distance review plus corridor-map coherence checks

---

## Sprint 2 — National Zone Type Model

**Status:** Complete  
**Depends on:** Sprint 0 (complete); Sprint 1 (config locked)  
**Goal:** Build the full Stage 1 national model. Every tract in the current full tract base gets a zone type label, tract-scale benchmarks, and review artifacts. `k = 7` is now the chosen Sprint 2 structure, the label map is wired into the code path, and GMM remains optional rather than blocking the tract model pass.

**Sprint 2 shipped summary (`2026-07-01`):**
- [x] Added the full modular package for Phase 7: `README.md`, `R/phase7_helpers.R`, `R/phase7_tract_frame_build.R`, `R/phase7_imputation.R`, `R/phase7_national_cluster.R`, `R/phase7_scoring.R`, `R/run_phase7_zone_model.R`, and `zone_methodology.qmd`
- [x] Ran the Sprint 2 build end to end and wrote the tract outputs in `phase_7_zone_methodology/outputs/`
- [x] Landed a tract-scale clustering adaptation: hierarchical calibration now runs on a `5,000`-tract sample because a full `78,199 × 78,199` distance matrix exceeds local memory, while the final k-means labels still run on the full tract matrix
- [x] Made GMM optional and skipped it by default for the current tract pass after we agreed it was low-value relative to the compute cost at this grain
- [x] Closed the Sprint 2 naming decision in code: the current run now writes the agreed `k = 7` label set into `zone_scores.parquet` and the descriptive audit outputs
- [x] Added a descriptive-only tract audit path for held-out naming fields (`median_age`, `diversity_index`, race/ethnicity shares, `median_home_value`, `median_hh_income`) so label review can use richer tract context without changing the clustering vector

### 2.1 — Tract input frame

- [x] Write `R/phase7_tract_frame_build.R`
  - Pull all tract rows from: `population_demographics`, `housing_core_wide`, `economics_income_wide`, `economics_labor_wide`, `migration_wide`, `transport_built_form_wide`, `transport_built_form_sld` (tract rows), `environment_wide` (tract rows), `economics_lodes_wide`, `dim_policy_designations`
  - Start from the full tract backbone currently materialized in `gold.intelligence_zone_inputs`, with `cbsa_code` and `county_geoid` attached through `xwalk_cbsa_county` → `xwalk_tract_county`
  - Join all KPI tables on `geo_id` (tract GEOID) and latest available year per source, with SLD explicitly treated as a tract baseline slice rather than a recurring annual panel
  - Output: one row per tract, all KPI columns, with `cbsa_code` and `county_geoid` attached
- [x] Write coverage audit: missingness per KPI across the tract universe; flag KPIs with >20% missing; document
  - Current tract coverage confirms the expected Sprint 1 pattern: `pct_unemployment_rate` is the weakest retained KPI at `90.5%`, LODES WAC fields remain at `96.1%`, and no retained KPI crosses the `20%` missing threshold

### 2.2 — Imputation and standardization

- [x] Write `R/phase7_imputation.R`
  - Median imputation as default (consistent with Phases 2–5 architecture)
  - KNN imputation only if a KPI has >15% missingness AND clearly non-random pattern
  - Log imputed KPI count and tract count per KPI
  - Standardize all KPIs to z-scores within the national tract universe
  - Apply polarity flags from `phase7_config.R`
  - Current implementation keeps the tract pass on median imputation only and logs any KPI that would qualify for a later KNN review rather than widening Sprint 2 scope

### 2.3 — National clustering

- [x] Write `R/phase7_national_cluster.R`
  - Hierarchical clustering (agglomerative, Ward linkage) now runs on a `5,000`-tract calibration sample because a full national tract distance matrix exceeds local memory
  - Produce candidate-`k` calibration from within-cluster variance + silhouette; the current provisional run selects `k = 7`
  - K-means at provisional `k` — hard `zone_type` label per tract on the full `78,199`-tract matrix
  - GMM at same k — made optional and skipped by default for the tract-scale Sprint 2 pass
  - Write cluster calibration CSV: cluster sizes, silhouette scores, within-cluster variance
  - Write cluster centroids CSV: mean KPI values per cluster (on standardized scale)
  - Write representative tracts CSV: 5 most central tracts per cluster for label interpretation

### 2.4 — Zone type labeling

- [x] Inspect cluster centroids; evaluate against draft label set in `docs/zone_methodology_notes.md`
- [x] Assign human-readable zone type names to each cluster
- [x] Validate: light spot-check representative tracts and zone distributions against Jacksonville and Richmond VA
- [x] Write label decisions into `phase7_config.R` (cluster number → zone type name mapping)
  - The current code path now writes the agreed Sprint 2 decision-point names: `Entry-Market Neighborhoods`, `Emerging Knowledge Districts`, `Knowledge Corridor`, `Established Residential`, `Mixed-Income Middle Neighborhoods`, `Working Neighborhoods`, and `Commercial Core / Jobs Center`

### 2.5 — Scoring and benchmarks

- [x] Write `R/phase7_scoring.R`
  - Compute theme scores (Character / Livability / Opportunity) per tract as mean of standardized KPIs within theme
  - Compute national percentile rank per theme and for composite (0–100 within the current tract universe)
  - Compute CBSA percentile rank per theme (0–100 within the tract's home CBSA)
  - Compute zone type peer percentile rank (0–100 within tracts sharing the same zone type nationally)

### 2.6 — National model output

- [x] Write canonical output to `phase_7_zone_methodology/outputs/zone_scores.parquet`
  - `tract_geoid`, `cbsa_code`, `county_geoid`, `geo_name`
  - `zone_type` (hard label)
  - `zone_type_prob_k1 … zone_type_prob_kN` (currently placeholder `NA` columns while GMM is disabled by default)
  - Theme scores: `character_score`, `livability_score`, `opportunity_score`
  - Percentile ranks: national, CBSA, zone type peer — per theme and composite
  - `is_opportunity_zone` flag (from `dim_policy_designations`)
  - All standardized KPI columns retained for interpretation

**Expected outputs:**
- `outputs/zone_scores.parquet` — canonical output (one row per tract)
- `outputs/phase7_cluster_calibration.csv` — cluster sizes, silhouette, within-cluster variance
- `outputs/phase7_cluster_centroids.csv` — mean KPI values per zone type
- `outputs/phase7_representative_tracts.csv` — 5 most central tracts per zone type
- `outputs/phase7_coverage_audit.csv` — missingness per KPI across tract universe
- `outputs/phase7_imputation_log.csv` — which KPIs triggered imputation, how many tracts affected

---

## Sprint 3 — Optional Deep Dive Validation Workflow

**Status:** Optional / not required for Phase 7 closeout  
**Depends on:** Sprint 2 (national model complete and labeled)  
**Goal:** Provide a reusable market-level validation workflow for true Deep Dive work. This sprint is intentionally decoupled from the Phase 7 tract and ZCTA deliverables.

### 3.1 — Deep Dive corridor runner

- [ ] Write `R/phase7_corridor_detection.R` — general DBSCAN runner, parameterized for any CBSA
  - Filter `zone_scores.parquet` to the target CBSA
  - Pull tract centroids from `silver.dim_geo` or geometry source
  - Compute hybrid distance matrix: `α × cosine_distance(KPI_vector) + (1−α) × normalized_spatial_distance(centroid)`
  - Run DBSCAN with initial `eps` and `min_samples` parameters
  - Assign corridor ID per tract within each zone type
  - Generate corridor name: `{county_name}_{zone_type}_{rank}` where rank is by corridor size descending
  - Noise tracts (DBSCAN label = -1) retain their zone type but get `corridor_id = NULL`
- [ ] Write one market-specific corridor output per Deep Dive run, e.g. `outputs/jax_corridors.csv`
- [ ] Calibrate `eps` and `min_samples` only when a market is actively under review; do not lock a universal setting in Phase 7 by default

### 3.2 — Market coherence checks

- [ ] For an active Deep Dive market, review whether the tract-level zone labels and any DBSCAN corridors align with known neighborhood structure
- [ ] Compare the market's tract mix with the national baseline and flag any surprising over- or under-represented zone types
- [ ] Use the descriptive-only KPI audit as the first naming and interpretation check before escalating to corridor-level review

### 3.3 — Optional review notebook extensions

- [ ] Write `phase_7_zone_methodology/zone_methodology.qmd` — reads `outputs/` only
  - Section 1: National model — k selection, cluster sizes, centroid heatmap, silhouette scores
  - Section 2: Zone type profiles — centroid radar charts, representative tracts, draft label rationale
  - Section 3: Optional market module — zone type map, corridor detection map, corridor inventory table
  - Section 4: Literature anchor comparison — where do our types align/diverge from NCRC and related references?

---

## Sprint 4 — ZCTA Rollup and Intelligence Mart Promotion

**Status:** Complete  
**Depends on:** Sprint 2 (tract model complete and promoted)  
**Goal:** Finish Phase 7 by rolling tract labels to ZCTA, promoting the ZCTA output into the intelligence mart, and documenting the tract-to-ZCTA methodology. Sprint 3 remains optional and does not block this path.

### 4.1 — ZCTA majority-assignment

- [x] Write `R/phase7_zcta_rollup.R`
  - Uses `silver.xwalk_zcta_tract` with `rel_weight_pop`
  - Assigns the dominant zone type only when weighted share is `> 50%`; otherwise labels the ZCTA as `Mixed Zone`
  - Carries the full per-cluster weighted share vector into the output so thresholds and naming can be revisited later without recomputing the tract join
  - Writes `outputs/zone_scores_zcta.parquet`
- [x] Coverage audit: how many ZCTAs have a clean plurality assignment vs. mixed?

### 4.2 — ZCTA mart promotion

- [x] Write `foundations/loaders/load_zone_assignments.R`
  - Reads `phase_7_zone_methodology/outputs/zone_scores.parquet`
  - Writes the canonical tract output to `mart_intelligence.intelligence_zones`
  - Keeps tract-grain fields intact, including the final `k = 7` zone labels, theme scores, percentile context, and standardized KPI columns
- [x] Write `foundations/loaders/load_zone_scores_zcta.R`
  - Reads `outputs/zone_scores_zcta.parquet`
  - Writes to `mart_intelligence.intelligence_zones_zcta`
- [x] Add the ZCTA mart table to `foundations/semantic_layer/table_catalog.yml`
- [x] Validate: confirm both mart tables are queryable from downstream tools

### 4.3 — Catalog and workflow update

- [x] Add `intelligence_zones` to `foundations/semantic_layer/table_catalog.yml`
- [x] Add the tract mart entry to `foundations/semantic_layer/README.md`
- [x] Add `intelligence_zones_zcta` to `foundations/semantic_layer/README.md` and `table_catalog.yml`
- [x] Update `INTELLIGENCE_LAYER_ROADMAP.md` and related notes after the ZCTA mart is active

---

## File structure

```
exploration/
  intelligence_framework/
    docs/
      zone_methodology_notes.md        ← methodology reference (written)
    phase_7_zone_methodology/
      PHASE7_PLAN.md                   ← this file
      R/
        phase7_config.R                ← KPI list, polarity flags, source mappings, corridor naming
        phase7_tract_frame_build.R     ← pull and join all tract KPI tables
        phase7_imputation.R            ← coverage audit, median imputation, z-score standardization
        phase7_national_cluster.R      ← hierarchical → k-means → GMM; calibration outputs
        phase7_scoring.R               ← theme scores, national/CBSA/peer percentile ranks
        phase7_corridor_detection.R    ← optional DBSCAN deep-dive runner; parameterized by CBSA
        phase7_zcta_rollup.R           ← majority-assignment from tract to ZCTA
        run_phase7_zone_model.R        ← canonical runner; sources all modules in order
      zone_methodology.qmd             ← review notebook; reads outputs/ only
      outputs/
        zone_scores.parquet            ← canonical tract output
        zone_scores_zcta.parquet       ← ZCTA rollup
        jax_corridors.csv              ← optional Jacksonville DBSCAN output
        rva_corridors.csv              ← optional Richmond VA DBSCAN output
        phase7_cluster_calibration.csv
        phase7_cluster_centroids.csv
        phase7_representative_tracts.csv
        phase7_coverage_audit.csv
        phase7_imputation_log.csv
foundations/
  etl/
    silver/
      lehd_lodes_silver.R              ← Sprint 0.1: LODES WAC/RAC ingestion
    gold/
      gold_economics_lodes.sql         ← Sprint 0.1: LODES Gold mart
      gold_transport_built_form_sld.sql ← Sprint 0.2: tract SLD baseline carried into the initial KPI vector
      gold_environment_wide.sql        ← Sprint 0.2: expose tract rows
  loaders/
    load_zone_assignments.R            ← Sprint 4.2: tract mart promotion
    load_zone_scores_zcta.R            ← Sprint 4.2: ZCTA mart promotion
```

---

## Sprint dependency map

```
Sprint 0 — Data Prerequisites          (complete)
  0.1 LODES Silver → Gold
  0.2 EJScreen / FEMA tract promotion closeout

Sprint 1 — Methodology + Literature    (complete)
  1.1 Literature review
  1.2 KPI finalization + config
  1.3 DBSCAN parameter design

Sprint 2 — National Zone Type Model    (depends on 0 + 1)
  2.1 Tract input frame
  2.2 Imputation + standardization
  2.3 National clustering
  2.4 Zone type labeling
  2.5 Scoring + benchmarks
  2.6 Output

Sprint 3 — Optional Deep Dive Workflow (depends on 2; not a Phase 7 gate)
  3.1 Deep Dive corridor runner
  3.2 Market coherence checks
  3.3 Optional review notebook extensions

Sprint 4 — ZCTA Rollup + Mart          (depends on 2)
  4.1 ZCTA majority-assignment
  4.2 ZCTA mart promotion
  4.3 Catalog and workflow update
```

---

## Open decisions to revisit after tract promotion

These are not blocking the tract mart and can be revisited during optional deep-dive validation:

- **k for the national model** — expected 7–10; chosen empirically from dendrogram + silhouette. Do not pre-specify.
- **DBSCAN `α` parameter** — `0.70` is the starting default; lock only if a Deep Dive corridor workflow is actively being used.
- **DBSCAN `eps` and `min_samples`** — calibrate against the first active deep-dive market rather than treating them as national Phase 7 requirements.
- **`jobs_inflow_ratio` from LODES OD** — keep out of the initial model pass unless we later decide the added commute-flow signal is worth the extra ETL and wider missingness risk.
- **Per-market vs. universal DBSCAN parameters** — if different Deep Dive markets need different settings to produce coherent maps, document the per-market approach and keep it outside the canonical tract mart.
