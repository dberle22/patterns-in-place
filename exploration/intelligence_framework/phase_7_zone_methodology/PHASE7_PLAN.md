# Phase 7 — Zone Methodology: Sprint Plan

*Last updated: 2026-06-20*

Full methodology reference: `exploration/intelligence_framework/docs/zone_methodology_notes.md`

---

## Summary

Phase 7 builds the sub-metro zone classification system. It produces:

1. **National zone types** — every tract in the 396-CBSA universe gets a nationally consistent label (e.g. "Knowledge Corridor," "Distressed," "Growth Periphery")
2. **Per-market corridors** — within each Deep Dive market, adjacent same-type tracts are grouped into named corridors using DBSCAN with a hybrid feature + spatial distance
3. **ZCTA rollup** — zone type majority-assigned to ZCTAs from the tract model, for presentation use

Phase 7 is blocked by two data prerequisites in Sprint 0.

---

## Architecture recap

```
Gold tract KPI vector (ACS + LEHD + SLD + EJScreen re-surface)
    → Stage 1: National zone type model (hierarchical → k-means → GMM)
        → Hard zone_type label per tract
        → GMM soft membership probabilities
        → National and CBSA percentile benchmarks
            → Stage 2: Per-market corridor detection (DBSCAN, hybrid distance)
                → Corridor ID per tract within each Deep Dive market
                → Corridor name: {county}_{zone_type}_{rank}
                    → ZCTA rollup (majority-assignment from tract)
```

---

## Sprint 0 — Data Prerequisites

**Status:** Not started  
**Blocks:** Sprint 2 (LEHD blocks Stage 1 Opportunity theme); Sprint 3 (re-surface blocks SLD/EJScreen inputs)  
**Can run in parallel with Sprint 1**

### 0.1 — LEHD/LODES Silver ingestion

LODES WAC (Workplace Area Characteristics) provides jobs per tract by sector and earnings tier. This is the only source of tract-level Opportunity signal beyond ACS income/labor.

**Tasks:**
- [ ] Ingest LODES WAC for all states in the 396-CBSA universe, latest available year (2022)
- [ ] Write `foundations/etl/silver/lodes_wac_silver.R` — download, parse, normalize to `geo_level = 'tract'` grain
- [ ] Write `foundations/etl/gold/gold_lodes_wide.sql` — compute derived KPIs: `jobs_per_resident`, `pct_jobs_high_wage` (CE03 share), `pct_jobs_professional_services`, `jobs_inflow_ratio`
- [ ] Add `lodes_wide` entry to `foundations/semantic_layer/table_catalog.yml`
- [ ] Validate: spot-check Jacksonville (Duval County) and Richmond VA (Chesterfield + Richmond City) tract job counts against known anchor employers
- [ ] Coverage audit: flag tracts with missing LODES rows; document which CBSAs have gaps

**Expected output:** `gold.lodes_wide` — one row per tract per year, job count KPIs ready for zone clustering input

### 0.2 — Tract-level re-surface for SLD and EJScreen

SLD (`walkability_index`, `jobs_access_45min_transit`) and EJScreen (`ejs_pm25`) are tract-native in Silver but rolled up to county/CBSA in the current Gold ETL.

**Tasks:**
- [ ] Add `geo_level = 'tract'` rows to `foundations/etl/gold/gold_transport_built_form_sld.sql` — pull directly from `silver.epa_sld` at tract grain
- [ ] Verify `foundations/etl/gold/gold_environment_wide.sql` already has tract bridge logic; expose `geo_level = 'tract'` rows in the output
- [ ] Run both updated scripts and confirm tract rows are present in `gold.transport_built_form_sld` and `gold.environment_wide`
- [ ] Update `foundations/semantic_layer/table_catalog.yml` entries to add `tract` to `supported_geo_levels` for both tables

---

## Sprint 1 — Methodology + Literature Review

**Status:** Not started  
**Depends on:** Nothing — runs in parallel with Sprint 0  
**Goal:** Lock the KPI input set, zone type label candidates, and DBSCAN parameters before writing any code. Avoid having to re-run the national model because a conceptual decision changed.

### 1.1 — Literature review

Review the four published frameworks and document alignment/divergence:

- [x] Review **NCRC Changing America Neighborhood Typologies (2023)** — document inputs, cluster count, label set, and where ours aligns/diverges
- [x] Review **Urban Displacement Project Neighborhood Change Typologies** — focus on gentrification/displacement framing; how does their Emerging/Transitional type map to ours?
- [x] Skim **Esri Tapestry** documentation — note inputs (proprietary consumer data) and granularity (67 types); document why our approach is analytically distinct
- [x] Review **Moretti "New Geography of Jobs"** — grounding for Knowledge Corridor type and the education/jobs clustering dynamic
- [x] Write up in `docs/zone_methodology_notes.md` under a Literature Review section

### 1.2 — Input KPI finalization

- [ ] Confirm final tract KPI list across all three themes (Character / Livability / Opportunity) — see `docs/zone_methodology_notes.md` KPI table
- [ ] Confirm which LODES WAC fields to derive (pending Sprint 0.1 completion)
- [ ] Document polarity flags for all zone KPIs (some KPIs have different polarity at tract grain vs. CBSA grain — e.g. `vacancy_rate` is negative for clustering interpretation)
- [ ] Write `phase_7_zone_methodology/R/phase7_config.R` — KPI list, polarity flags, source table mappings, coverage rules

### 1.3 — DBSCAN parameter design

- [ ] Define hybrid distance formula: `α × feature_distance + (1−α) × spatial_distance`
- [ ] Document default `α = 0.70` and the rationale
- [ ] Identify R packages: `dbscan` (DBSCAN implementation), `sf` (spatial operations for centroid distances), `spdep` or `rgeoda` (spatial weights if needed)
- [ ] Write corridor naming convention into config: `{county_name}_{zone_type}_{rank}`
- [ ] Document calibration approach for `eps` and `min_samples` — these will be set empirically during the Jacksonville stress test in Sprint 3

---

## Sprint 2 — National Zone Type Model

**Status:** Not started  
**Depends on:** Sprint 0 (LEHD + re-surface complete); Sprint 1 (config locked)  
**Goal:** Build the full Stage 1 national model. Every tract in the 396-CBSA universe gets a zone type label, GMM soft memberships, and benchmarks.

### 2.1 — Tract input frame

- [ ] Write `R/phase7_tract_frame_build.R`
  - Pull all tract rows from: `population_demographics`, `housing_core_wide`, `economics_income_wide`, `economics_labor_wide`, `migration_wide`, `transport_built_form_wide`, `transport_built_form_sld` (tract rows), `environment_wide` (tract rows), `lodes_wide`, `dim_policy_designations`
  - Filter to tracts in the 396 non-PR CBSAs using `xwalk_cbsa_county` → `xwalk_tract_county`
  - Join all KPI tables on `geo_id` (tract GEOID) and latest available year per source
  - Output: one row per tract, all KPI columns, with `cbsa_code` and `county_geoid` attached
- [ ] Write coverage audit: missingness per KPI across the tract universe; flag KPIs with >20% missing; document

### 2.2 — Imputation and standardization

- [ ] Write `R/phase7_imputation.R`
  - Median imputation as default (consistent with Phases 2–5 architecture)
  - KNN imputation only if a KPI has >15% missingness AND clearly non-random pattern
  - Log imputed KPI count and tract count per KPI
  - Standardize all KPIs to z-scores within the national tract universe
  - Apply polarity flags from `phase7_config.R`

### 2.3 — National clustering

- [ ] Write `R/phase7_national_cluster.R`
  - Hierarchical clustering (agglomerative, Ward linkage) on full standardized KPI vector
  - Produce dendrogram; choose natural k from within-cluster variance + silhouette; expect k = 7–10
  - K-means at natural k — hard `zone_type` label per tract
  - GMM at same k — soft membership probabilities per tract
  - Write cluster calibration CSV: cluster sizes, silhouette scores, within-cluster variance
  - Write cluster centroids CSV: mean KPI values per cluster (on standardized scale)
  - Write representative tracts CSV: 5 most central tracts per cluster for label interpretation

### 2.4 — Zone type labeling

- [ ] Inspect cluster centroids; evaluate against draft label set in `docs/zone_methodology_notes.md`
- [ ] Assign human-readable zone type names to each cluster
- [ ] Validate: spot-check representative tracts against known neighborhood identities in Jacksonville and Richmond VA
- [ ] Write label decisions into `phase7_config.R` (cluster number → zone type name mapping)

### 2.5 — Scoring and benchmarks

- [ ] Write `R/phase7_scoring.R`
  - Compute theme scores (Character / Livability / Opportunity) per tract as mean of standardized KPIs within theme
  - Compute national percentile rank per theme and for composite (0–100 within 396-CBSA tract universe)
  - Compute CBSA percentile rank per theme (0–100 within the tract's home CBSA)
  - Compute zone type peer percentile rank (0–100 within tracts sharing the same zone type nationally)

### 2.6 — National model output

- [ ] Write canonical output to `phase_7_zone_methodology/outputs/zone_scores.parquet`
  - `tract_geoid`, `cbsa_code`, `county_geoid`, `geo_name`
  - `zone_type` (hard label)
  - `zone_type_prob_k1 … zone_type_prob_kN` (GMM soft memberships)
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

## Sprint 3 — Deep Dive Market Stress Tests (Jacksonville + Richmond VA)

**Status:** Not started  
**Depends on:** Sprint 2 (national model complete and labeled)  
**Goal:** Run DBSCAN corridor detection for both Deep Dive markets. Validate that zone type labels are coherent when viewed at market level. Lock DBSCAN parameters.

### 3.1 — Jacksonville corridor detection

- [ ] Write `R/phase7_corridor_detection.R` — general DBSCAN runner, parameterized for any CBSA
  - Filter `zone_scores.parquet` to the target CBSA
  - Pull tract centroids from `silver.dim_geo` or geometry source
  - Compute hybrid distance matrix: `α × cosine_distance(KPI_vector) + (1−α) × normalized_spatial_distance(centroid)`
  - Run DBSCAN with initial `eps` and `min_samples` parameters (calibrate against Jacksonville map output)
  - Assign corridor ID per tract within each zone type
  - Generate corridor name: `{county_name}_{zone_type}_{rank}` where rank is by corridor size descending
  - Noise tracts (DBSCAN label = -1) retain their zone type but get `corridor_id = NULL`
- [ ] Write corridor output to `outputs/jax_corridors.csv`
- [ ] Inspect: do corridor boundaries correspond to recognizable Jacksonville neighborhoods or districts?
- [ ] Calibrate `eps` and `min_samples` until corridor maps are coherent; document final parameters

### 3.2 — Richmond VA corridor detection

- [ ] Run `phase7_corridor_detection.R` for Richmond VA CBSA with locked JAX parameters
- [ ] Write corridor output to `outputs/rva_corridors.csv`
- [ ] Inspect: do corridor maps make sense in the Richmond VA context?
- [ ] If JAX parameters produce incoherent Richmond VA results, document why and test a per-market parameter approach

### 3.3 — Zone type validation

- [ ] For both markets: does the national zone type label distribution look reasonable?
  - Do wealthier/denser tracts get Knowledge Corridor or Established Residential labels?
  - Do high-poverty/high-vacancy tracts get Distressed labels?
  - Does the OZ flag correlate with Distressed or Affordable Working Class types?
- [ ] Document any zone type that looks wrong in either market and trace back to centroid to understand why
- [ ] If a zone type is consistently misassigning tracts, flag it for re-labeling or cluster split in Sprint 2

### 3.4 — Review notebook

- [ ] Write `phase_7_zone_methodology/zone_methodology.qmd` — reads `outputs/` only
  - Section 1: National model — k selection, cluster sizes, centroid heatmap, silhouette scores
  - Section 2: Zone type profiles — centroid radar charts, representative tracts, draft label rationale
  - Section 3: Jacksonville — zone type map, corridor detection map, corridor inventory table
  - Section 4: Richmond VA — same structure as Jacksonville section
  - Section 5: Cross-market comparison — zone type distribution in JAX vs. RVA vs. national baseline; which types are over/under-represented?
  - Section 6: Literature anchor comparison — where do our types align/diverge from NCRC, Urban Institute?

---

## Sprint 4 — ZCTA Rollup and Gold Promotion

**Status:** Not started  
**Depends on:** Sprint 3 (labels validated, no major re-labeling needed)

### 4.1 — ZCTA majority-assignment

- [ ] Write `R/phase7_zcta_rollup.R`
  - Join tract zone types to `silver.xwalk_zcta_tract` (weighted many-to-many crosswalk)
  - For each ZCTA, assign the zone type held by the plurality of its constituent tract population
  - Where a ZCTA's tracts are evenly split between two zone types, flag as `mixed` and retain the two largest types and their population shares
  - Write to `outputs/zone_scores_zcta.parquet`
- [ ] Coverage audit: how many ZCTAs have a clean plurality assignment vs. mixed?

### 4.2 — Corridor ZCTA rollup

- [ ] For Deep Dive markets (JAX and RVA): majority-assign corridor ID to ZCTAs using the same crosswalk approach
- [ ] Write to `outputs/jax_corridors_zcta.csv` and `outputs/rva_corridors_zcta.csv`

### 4.3 — Gold promotion scripts

- [ ] Write `foundations/loaders/load_zone_scores.R`
  - Reads `phase_7_zone_methodology/outputs/zone_scores.parquet`
  - Writes to `gold.intelligence_zones` (tract grain)
  - Schema: `tract_geoid`, `cbsa_code`, `zone_type`, GMM probs, theme scores, percentile ranks, `is_opportunity_zone`, corridor columns (NULL for non–Deep Dive tracts)
- [ ] Write `foundations/loaders/load_zone_scores_zcta.R`
  - Reads `outputs/zone_scores_zcta.parquet`
  - Writes to `gold.intelligence_zones_zcta`
- [ ] Add both tables to `foundations/semantic_layer/table_catalog.yml`
- [ ] Validate: confirm both Gold tables are queryable from MotherDuck

### 4.4 — Catalog update

- [ ] Add `intelligence_zones` and `intelligence_zones_zcta` entries to `intelligence_catalog.yml` with `status: calibrated`
- [ ] Update `INTELLIGENCE_LAYER_ROADMAP.md` Phase 7 status to Complete and fill in completed summary

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
        phase7_corridor_detection.R    ← DBSCAN with hybrid distance; parameterized by CBSA
        phase7_zcta_rollup.R           ← majority-assignment from tract to ZCTA
        run_phase7_zones.R             ← canonical runner; sources all modules in order
      zone_methodology.qmd             ← review notebook; reads outputs/ only
      outputs/
        zone_scores.parquet            ← canonical tract output
        zone_scores_zcta.parquet       ← ZCTA rollup
        jax_corridors.csv              ← Jacksonville DBSCAN output
        rva_corridors.csv              ← Richmond VA DBSCAN output
        jax_corridors_zcta.csv
        rva_corridors_zcta.csv
        phase7_cluster_calibration.csv
        phase7_cluster_centroids.csv
        phase7_representative_tracts.csv
        phase7_coverage_audit.csv
        phase7_imputation_log.csv
foundations/
  etl/
    silver/
      lodes_wac_silver.R               ← Sprint 0.1: LODES WAC ingestion
    gold/
      gold_lodes_wide.sql              ← Sprint 0.1: LODES Gold mart
      gold_transport_built_form_sld.sql ← Sprint 0.2: add tract rows
      gold_environment_wide.sql        ← Sprint 0.2: expose tract rows
  loaders/
    load_zone_scores.R                 ← Sprint 4.3: tract Gold promotion
    load_zone_scores_zcta.R            ← Sprint 4.3: ZCTA Gold promotion
```

---

## Sprint dependency map

```
Sprint 0 — Data Prerequisites          (parallel with Sprint 1; blocks Sprint 2)
  0.1 LODES Silver → Gold
  0.2 SLD / EJScreen tract re-surface

Sprint 1 — Methodology + Literature    (parallel with Sprint 0; blocks Sprint 2)
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

Sprint 3 — Market Stress Tests         (depends on 2)
  3.1 Jacksonville corridors
  3.2 Richmond VA corridors
  3.3 Zone type validation
  3.4 Review notebook

Sprint 4 — ZCTA Rollup + Gold          (depends on 3)
  4.1 ZCTA majority-assignment
  4.2 Corridor ZCTA rollup
  4.3 Gold promotion scripts
  4.4 Catalog update
```

---

## Open decisions to revisit during Sprint 2

These are not blocking Sprint 0/1 but must be resolved before Sprint 3:

- **k for the national model** — expected 7–10; chosen empirically from dendrogram + silhouette. Do not pre-specify.
- **DBSCAN `α` parameter** — `0.70` is the starting default; JAX stress test sets the locked value.
- **DBSCAN `eps` and `min_samples`** — calibrated during Sprint 3 against JAX corridor maps; locked before RVA run.
- **Environmental Risk Zone** — may not emerge as a standalone cluster type; may appear as a KPI modifier on other types. Decide after inspecting centroids.
- **`jobs_inflow_ratio` from LODES OD** — include only if the OD file ingestion is tractable within Sprint 0.1; WAC is the priority.
- **Per-market vs. universal DBSCAN parameters** — default is universal (same `eps` and `min_samples` for all markets). If JAX and RVA require different parameters to produce coherent maps, document the per-market approach as the fallback.
