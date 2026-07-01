# Zone Methodology Notes

*Last updated: 2026-07-01*

This document is the canonical methodology reference for Phase 7: the Zone Methodology. It captures the design decisions, data architecture, algorithmic choices, and literature anchors that govern how Patterns in Place classifies sub-metro areas into zone types and corridors.

---

## What we are building

Phase 7 produces two complementary analytical products from a single tract-level model:

1. **National zone types** — a consistent label set assigned to every tract in the current full tract base carried by the Phase 7 Gold build, with CBSA context attached through the tract-to-county-to-CBSA crosswalk. Labels mean the same thing everywhere. A "Knowledge Corridor" tract in Jacksonville is directly comparable to a "Knowledge Corridor" tract in Richmond VA or Chicago. This is the primary output and the foundation for cross-market Deep Dive comparisons.

2. **Per-market corridor detection** — within each Deep Dive market, adjacent or near-adjacent tracts sharing the same zone type are grouped into named corridors. Corridors are a secondary visual layer for Deep Dive maps and narrative. They do not define the zone type; they identify where clusters of same-type tracts are geographically concentrated within a specific market.

A third derivative layer exists for presentation only:

3. **ZCTA rollup** — once the tract model is stable, zone type labels are majority-assigned to ZCTAs via the tract-to-ZCTA crosswalk. ZCTAs are a presentation convenience (readers recognize ZIP codes); the analytic base is always the tract model.

---

## Two-stage architecture

### Stage 1 — National zone type model (k-means / hierarchical)

**Grain:** One row per census tract. Universe: the full current tract base materialized for Phase 7, with CBSA context attached where the tract backbone maps into `silver.xwalk_cbsa_county`.

**Algorithm:** Same hierarchical → k-means → GMM pipeline used in Phases 2–5, applied at tract grain across the full current tract base.

- Hierarchical clustering (agglomerative) to discover natural k from the data — dendrogram + silhouette
- K-means at natural k for hard zone type labels
- GMM at same k for soft membership probabilities (captures tracts genuinely between types)

**Expected k:** 7–10 zone types. More than the CBSA-level models because within-metro heterogeneity is real and meaningful. Fewer than Esri Tapestry's 67 because interpretability and narrative defensibility matter more than granularity.

**Output per tract:**
- `zone_type` — hard cluster label (national)
- `zone_type_prob_k1 … zone_type_prob_kN` — GMM soft membership probabilities
- Full KPI vector (standardized) retained for interpretation

### Stage 2 — Per-market corridor detection (DBSCAN)

**Grain:** One row per tract, filtered to a single CBSA. Run independently for each Deep Dive market.

**Algorithm:** DBSCAN with a hybrid distance metric combining feature similarity and spatial proximity.

**Hybrid distance:**

```
distance(tract_i, tract_j) = α × feature_distance(i, j) + (1 − α) × spatial_distance(i, j)
```

- `feature_distance` — cosine distance on the standardized KPI vector (same vectors used in Stage 1 clustering)
- `spatial_distance` — Euclidean distance between tract centroids, normalized within the CBSA
- `α = 0.70` as the default (feature-primary, spatially bounded); revisit if corridor maps look unreasonably fragmented

**Why DBSCAN over k-means for Stage 2:**
- k is not known in advance — the number of Knowledge Corridor clusters in Jacksonville is data-driven, not pre-specified
- Noise points are valid — tracts that don't belong to any coherent corridor are labeled as noise rather than forced into a cluster
- Non-contiguous corridors are acceptable — two tracts can share a corridor if they're both near similar tracts, even if there's a small gap between them

**DBSCAN parameters:** `eps` (neighborhood radius) and `min_samples` (minimum tracts to form a corridor) are calibrated per-market in the Jacksonville and Richmond VA stress tests. The defaults are a starting point; the stress tests produce the locked calibration.

**Corridor naming convention:**

```
{county_name}_{zone_type}_{rank}
```

Example: `Duval_Knowledge_Corridor_1`, `Duval_Knowledge_Corridor_2`, `Chesterfield_Affordable_Working_Class_1`

Rank is assigned by corridor size (number of tracts), descending. This is a stored identifier — not a curated human name. Deep Dive narrative may reference the name of a recognizable neighborhood instead, but the stored key is always systematic.

---

## KPI input set

Zone clustering operates on three KPI themes. Unlike the CBSA-level frames (which were split into three independent models), zone clustering uses a combined KPI vector — closer in spirit to Phase 5 than to Phases 2–4. The themes are kept visible in the output for interpretive use, but the clustering input is the full combined vector.

Sprint 1.2 is now locked at a **22-KPI clustering contract**. That contract incorporates the coverage audit, correlation review, within-CBSA variance checks, and the tract-level PCA pass documented in `phase_7_zone_methodology/eda_notes.md`.

### Theme A — Character (who lives here)

All from ACS via existing Gold tables. Full tract coverage apart from the small denominator-driven `NaN` family already documented in the Phase 7 EDA notes.

| KPI | Table | Notes |
|---|---|---|
| `pct_hispanic`, `pct_black_nh`, `pct_asian_nh` | `population_demographics` | |
| `pct_age_over_64` | `population_demographics` | |
| `pct_ba_plus` | `population_demographics` | |
| `pct_same_house` | `migration_wide` | Residential stability proxy |
| `owner_occ_rate` | `housing_core_wide` | |
| `pop_weighted_density_sqmi` | `transport_built_form_wide` | |

**Dropped from the default clustering vector after Sprint 1.2 review:**

- `diversity_index` — useful as a descriptive summary, but redundant once the tract race / ethnicity shares are already retained
- `pct_foreign_born` — weaker within-CBSA signal and largely absorbed into the broader urbanity / composition bundle
- `pct_struct_multifam` — strongly overlaps with `owner_occ_rate`

### Theme B — Livability (what it's like to live here)

ACS core has full tract coverage. EJScreen is tract-native in Silver and now surfaces tract rows in Gold. FEMA NRI has tract-native staging and tract rows in Silver / Gold after the tract promotion pass. SLD now also has tract rows in governed Silver / Gold via the `2021` baseline table, with the remaining tract gap concentrated in Connecticut rather than spread nationally. CHR health metrics are county-only and excluded.

| KPI | Table | Tract available | Notes |
|---|---|---|---|
| `pct_rent_burden_30plus` | `housing_core_wide` | ✅ | |
| `vacancy_rate` | `housing_core_wide` | ✅ | |
| `pct_commute_walk` | `transport_built_form_wide` | ✅ | |
| `walkability_index` | `transport_built_form_sld` | ✅ | One-time `2021` tract baseline. Retained as the cleaner SLD accessibility / built-form representative |
| `pct_no_internet_access` | `social_infra_wide` | ✅ | |
| `ejs_pm25` | EJScreen (silver re-surface) | ✅ | Tract-native in Silver and now promoted into `gold.environment_wide` |
| `fema_risk_score` | FEMA NRI (silver re-surface) | ✅ | Tract staging is now promoted into Silver and surfaced in `gold.environment_wide` |
| `is_opportunity_zone` | `dim_policy_designations` | ✅ | Binary flag; carried as context, not in clustering KPI vector |

**Dropped from the default clustering vector after Sprint 1.2 review:**

- `median_gross_rent` — highest missingness in the live table and largely redundant with stronger affordability context fields
- `median_home_value` — interpretable, but overlaps with the broader SES bundle and was cut to keep the tract vector lean
- `pct_hh_0_vehicles` — heavily absorbed by the same latent structure as density and walkability
- `pct_commute_transit` — weak within-CBSA signal and strongly overlapping with density / auto-access structure
- `jobs_access_45min_transit` — tract coverage is now acceptable, but PCA suggests it is mostly duplicative once `walkability_index` and density are already present

*Excluded: CHR health outcomes (`premature_death_rate`, `drug_overdose_death_rate`, etc.) — county-level source only, no tract equivalent.*

### Theme C — Opportunity (what's happening here economically)

ACS provides income and labor at tract grain. LEHD/LODES provides the jobs-side signal that ACS cannot — jobs per resident, job sector mix, and commute inflow/outflow. **LEHD is a data prerequisite for Phase 7 and must be added to Gold before Phase 7 runs.**

| KPI | Table | Tract available | Notes |
|---|---|---|---|
| `pov_rate` | `economics_income_wide` | ✅ | |
| `pov_rate_change_3yr` | `economics_income_wide` | ✅ | Current fallback momentum window; 5-year version remains a longer-term harmonization target |
| `pct_unemployment_rate` | `economics_labor_wide` | ✅ | ACS-based |
| `pct_ba_plus_change_3yr` | `population_demographics` | ✅ | Current fallback human-capital momentum proxy; 5-year version remains a longer-term harmonization target |
| `jobs_per_resident` | `economics_lodes_wide` | ✅ | Jobs center vs. bedroom community |
| `pct_jobs_high_wage` | `economics_lodes_wide` | ✅ | Share of jobs in CE03 earnings tier |
| `pct_jobs_professional_services` | `economics_lodes_wide` | ✅ | Knowledge economy sector mix |

**Dropped from the default clustering vector after Sprint 1.2 review:**

- `median_hh_income` — still valuable for interpretation and scoring context, but PCA showed it was one of the more replaceable fields once `pct_ba_plus` and `pov_rate` were retained
- `jobs_inflow_ratio` — still out of scope for the initial model pass because WAC is the priority and the current jobs-side vector is already adequate without the OD extension

### Locked 22-KPI clustering vector

The default Phase 7 clustering pass should use the following `22` KPIs.

**Character (`8`)**

- `pct_hispanic`
- `pct_black_nh`
- `pct_asian_nh`
- `pct_age_over_64`
- `pct_ba_plus`
- `pct_same_house`
- `owner_occ_rate`
- `pop_weighted_density_sqmi`

**Livability (`7`)**

- `pct_rent_burden_30plus`
- `vacancy_rate`
- `pct_commute_walk`
- `walkability_index`
- `pct_no_internet_access`
- `ejs_pm25`
- `fema_risk_score`

**Opportunity (`7`)**

- `pov_rate`
- `pct_unemployment_rate`
- `pov_rate_change_3yr`
- `pct_ba_plus_change_3yr`
- `jobs_per_resident`
- `pct_jobs_high_wage`
- `pct_jobs_professional_services`

This is the lean default contract for clustering. `median_hh_income`, `median_home_value`, `diversity_index`, and `jobs_access_45min_transit` remain useful descriptive context fields and can still be used in sensitivity checks, centroid interpretation, and downstream profiling even though they are no longer in the default clustering vector.

*Excluded: FHFA HPI, ZORI, BPS permits, QCEW, IRS migration — none available at tract grain.*

---

## Data prerequisites

Two data gaps must be resolved before Phase 7 can run:

**1. LEHD/LODES Silver → Gold ETL (required)**

LODES WAC (Workplace Area Characteristics) and OD (Origin-Destination) tables are public, tract-level, and cover 2002–2022 for all 50 states. This is a new Silver ingestion + Gold mart. The WAC table is the priority (job counts by sector and earnings tier per tract). The OD table is secondary (commute inflow/outflow).

This is a data engineering prerequisite, not an analytical prerequisite. It can run in parallel with Phase 7 planning. Phase 7 Stage 1 build is blocked until LODES WAC Gold rows exist for the current tract base carried by the Phase 7 input table.

**2. Tract-level transport / environment promotion (resolved for current EDA; SLD remains a baseline layer)**

Phase 7 needs tract-grain livability and environmental context, but the three source families are not all at the same readiness level:
- `gold_environment_wide.sql` now exposes tract rows for `EJScreen` and `FEMA NRI`
- `silver.fema_nri` now includes tract rows promoted from `staging.fema_nri_tract`
- tract `EJScreen` and tract `FEMA NRI` are therefore live in governed Gold and available for Phase 7
- `silver.epa_sld` and `gold_transport_built_form_sld.sql` now include tract rows for the `2021` SLD baseline
- `staging.epa_sld_rest` still exists as a REST-backed prototype that preserves both `GEOID10` and `GEOID20`, but the current governed tract path is already live through the Census BG relationship bridge

The remaining tract gap for SLD is no longer a broad national tract-backbone failure. Live overlap now shows `83,220 / 84,121` tract-backbone matches and `77,300 / 78,199` matches on the current Phase 7 tract frame, with almost all residual misses concentrated in Connecticut metros. That means tract SLD is now viable for exploratory KPI evaluation, though we should still treat it as a one-time baseline layer and keep the Connecticut edge case visible in coverage review.

---

## Draft zone type label set

To be evaluated against what the data produces — labels are not pre-specified, they are assigned after inspecting cluster centroids. These are the expected types based on prior CBSA-level work and published neighborhood typology frameworks.

| Draft label | Character profile | Livability profile | Opportunity profile |
|---|---|---|---|
| **Knowledge Corridor** | High BA+, high density, younger | Low vacancy, walkable, transit-accessible | High jobs/resident, professional sector, income growth |
| **Established Residential** | Older, owner-occupied, low mobility | Low burden, stable | Low jobs/resident, low change |
| **Emerging / Transitional** | Increasing diversity, younger in-movers | Rising rents, some burden | Income change positive, gentrification signals |
| **Affordable Working Class** | Mixed race/ethnicity, moderate BA+, renters | Moderate burden, lower rents | Jobs present but lower wage, stable labor |
| **Distressed** | High poverty, lower BA+, renters | High burden, high vacancy, poor access | Low income, high unemployment, declining |
| **Growth Periphery** | Family-oriented, newer housing, moderate BA+ | Low burden (relatively), newer stock | Permit activity, population growth |
| **Jobs Center / Commercial Core** | Low residential population | Low residential density | Very high jobs/resident, mixed sector |
| **Environmental Risk Zone** | Varies | High EJ burden, high FEMA risk | Often lower income |

*"Environmental Risk Zone" may not emerge as a standalone type — it may appear as a modifier on other types. The EJ and FEMA KPIs are in the clustering vector, but environmental risk may cross-cut rather than define a zone type.*

---

## Benchmark strategy

Each tract is benchmarked at three levels (mirroring the CBSA benchmark architecture):

1. **National:** percentile rank within all tracts in the current tract universe loaded for Phase 7
2. **CBSA:** percentile rank within the tract's home CBSA — "how does this tract rank within its own metro?"
3. **Zone type peers:** percentile rank within tracts sharing the same zone type nationally

The CBSA benchmark is the most important for Deep Dive use: it answers "is this a strong or weak Knowledge Corridor relative to other Knowledge Corridors in this metro?"

---

## Literature anchors

Sprint 1.1 literature review is complete. Full review with alignment/divergence analysis and data gap inventory:  
→ [`docs/zone_methodology_literature_review.md`](zone_methodology_literature_review.md)

**Key findings from the review:**

- **NCRC Gentrification Series (2019–2025):** Rule-based threshold classifier using ACS income, home value, education, and HMDA lending data. Central city tracts only. Our Emerging/Transitional type ≈ their "Gentrifying" category; our Distressed type ≈ their "Eligible/Non-gentrifying." High input overlap with our platform; their addition we lack is HMDA mortgage lending data.
- **Urban Displacement Project (UC Berkeley, 2015–2020+):** Eight-stage rule-based decision tree using income relative to regional median, Zillow HVI/ZRI for price change, and ACS stability proxies. Metro-by-metro, not a consistent national model. Our CBSA percentile rank architecture reproduces the relative income threshold logic. Their addition we lack: Zillow HVI/ZRI for rent and home value change at tract grain.
- **Esri Tapestry (2024):** 67 segments at block-group grain using ACS demographics + proprietary MRI-Simmons consumer survey data. Commercial product for marketing. Confirms our 7–10 type target is deliberate parsimony. Consumer behavior data is not our objective and is explicitly out of scope.
- **Moretti "The New Geography of Jobs" (2012):** Metro-scale labor economics research — not a tract typology. Intellectual foundation for the Knowledge Corridor type. Our LODES WAC KPIs (`pct_jobs_professional_services`, `pct_jobs_high_wage`, `jobs_per_resident`) are the tract-level operationalization of his brain hub concept. His analysis operates entirely at the MSA level — our model reveals the within-metro spatial structure his work obscures.

**Frameworks referenced in PHASE7_PLAN but clarified here:**
- "NCRC Changing America Neighborhood Typologies (2023)" → refers to the NCRC Gentrification and Neighborhood Change research series; the closest current report is *Displaced by Design* (2025).
- "Urban Institute Neighborhood Change Typologies" → the published tract-level typology with Emerging/Transitional framing is the Urban **Displacement** Project at UC Berkeley, not the Urban Institute.

**Data gaps surfaced by the review** (variables in the literature absent from our platform):

| Variable | Source | Phase 7 impact |
|---|---|---|
| HMDA mortgage lending activity (loan counts, denial rates by tract) | NCRC | Not blocking; future signal for displacement risk |
| Zillow Home Value Index / Rent Index (tract/ZIP) | UDP | Not blocking; useful for trajectory; not public-domain |
| Net change in low-income households below 80% AMI | UDP | Computable from ACS income quintile data; not in scope for Phase 7 |
| Eviction filing rates (Princeton Eviction Lab) | Displacement literature broadly | Not blocking; relevant to Distressed type validation |
| USPTO patent counts at tract grain | Moretti | Out of scope; relevant for future Knowledge Corridor validation |
| Brown University LTDB (harmonized decennial Census 1970–2020) | NCRC | Only relevant if longitudinal tract analysis added in a future phase |

- **REDCAP/SKATER spatial clustering literature** — Guo (2008); `rgeoda` R package. Methodological grounding for the spatially-constrained clustering alternative to DBSCAN. Not yet reviewed.

---

## What this methodology does not cover

- **Chatbot zone-level queries:** Zone types will be materialized in Gold but are not wired into the chatbot query pipeline in Phase 7. That is a Phase 8+ decision once labels are calibrated and stable.
- **Area Explorer zone layer:** Deep Dive zone maps are standalone outputs. Area Explorer integration with zone types is a future product track.
- **ZCTA-grain model:** ZCTAs are derived by majority-assignment from the tract model. A separate ZCTA clustering pass may be run for comparison, but it is not the primary model and would not be used for production scoring.
- **Temporal trajectory at zone level:** Phase 6 trajectory analysis operates at CBSA grain. Zone-level trajectory (is this corridor gentrifying?) is a natural next step but is not part of Phase 7 scope.
