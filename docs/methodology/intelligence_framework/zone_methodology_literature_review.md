# Zone Methodology — Literature Review

*Sprint 1.1 — Phase 7*  
*Completed: 2026-06-25*

This document covers the four frameworks listed in the Phase 7 Sprint 1.1 task. For each framework it records: what they measure, how they measure it, what data they use, and where our approach aligns or diverges. A data gap section at the end surfaces variables that appear across the literature but are absent from our current platform.

---

## 1. NCRC Gentrification and Neighborhood Change Research (2019–2025)

**Reference:** Richardson, J. and Mitchell, B. *Shifting Neighborhoods: Gentrification and Cultural Displacement in American Cities* (2019); *Gentrification and Disinvestment 2020* (2020); *Displaced by Design: Fifty Years of Gentrification and Black Cultural Displacement in US Cities* (2025).  
**Publisher:** National Community Reinvestment Coalition (NCRC)  
**Links:**
- [Displaced by Design (2025)](https://ncrc.org/displaced-by-design/)
- [NCRC Gentrification main page](https://ncrc.org/gentrification/)
- [Gentrification and Disinvestment 2020](https://ncrc.org/gentrification20/)
- [Shifting Neighborhoods (2019)](https://ncrc.org/shifting-neighborhoods-gentrification-and-cultural-displacement-in-american-cities/)
- [Companion: American Neighborhood Change in the 21st Century — U of Minnesota (2019)](https://law.umn.edu/institute-metropolitan-opportunity/studies/housing-and-planning/american-neighborhood-change)

**Note on "Changing America Neighborhood Typologies (2023)":** No NCRC report with this exact title exists. The PHASE7_PLAN reference likely points to this series. The 2025 *Displaced by Design* report is the most current and comprehensive version.

### What they built

A longitudinal tract-level classification system that identifies whether a neighborhood is gentrifying and whether that gentrification is displacing Black residents and other low-income communities. Covers central city tracts only (~27,000 tracts); not a comprehensive national typology for suburban or exurban tracts.

### Methodology

Rule-based threshold classification — not cluster analysis. Two eligibility criteria must be met at baseline (year 2000), followed by threshold crossing over the subsequent decade:

- **Eligible to gentrify:** tract must be below the 40th percentile of metropolitan-area home values AND household incomes as of 2000
- **Gentrifying:** eligible tracts that crossed the 60th percentile in both home value increases AND college graduate share growth over the subsequent decade
- **Rebound:** gentrifying areas showing rising professional/higher-income residents alongside lower cultural displacement metrics
- **Non-gentrifying:** eligible tracts that did not cross the gentrification threshold

The companion University of Minnesota report uses four types: Economic Expansion (with low-income displacement), Economic Decline (with low-income concentration), Low-Income Concentration, and Low-Income Displacement.

### Input variables

| Variable | Our equivalent |
|---|---|
| Median household income (relative to metro area median) | `median_hh_income` in `economics_income_wide` |
| Median home value | `median_home_value` in `housing_core_wide` |
| Pct. with college degree (BA+) | `pct_ba_plus` in `population_demographics` |
| Professional/managerial employment share | Partially: `pct_jobs_professional_services` (LODES, pending ETL) |
| Racial/ethnic composition and change | `pct_black_nh`, `pct_hispanic`, `pct_asian_nh` in `population_demographics` |
| Mortgage lending activity (HMDA) | **Not in our platform** — see Data Gaps section |

**Data sources:** Brown University Longitudinal Tract Database (LTDB), U.S. Decennial Census, ACS 5-year estimates, HMDA mortgage lending data.

### Geographic grain

Census tract (central city tracts only).

### Alignment with our approach

| Dimension | Notes |
|---|---|
| Geographic grain | ✅ Same — census tract |
| Core input variables | ✅ High overlap on ACS demographics, income, housing value, education |
| Change-over-time signals | ✅ We compute `pct_ba_plus_change_5yr` and `pov_rate_change_5yr` — aligns with their gentrification tracking |
| Zone type alignment | Our **Emerging / Transitional** type directly maps to their "Gentrifying" category; our **Distressed** type maps to their "Eligible / Non-gentrifying" category |
| CBSA universe | ⚠️ Their scope is central city tracts only; ours covers all tracts across 396 CBSAs including suburbs and exurbs |

### Divergence

- **Methodology:** They use rule-based thresholds; we use unsupervised clustering. This is intentional — their goal is to track a specific process (gentrification); ours is to describe what a neighborhood currently is across multiple dimensions, not just whether it is gentrifying.
- **Temporal design:** Their method requires a before/after comparison anchored to year 2000. We model the current state of tracts using multi-year ACS and recent LODES data — a snapshot model, not a longitudinal one. Phase 6 (trajectory) handles temporal change at CBSA grain, and Phase 7 does not attempt longitudinal tract classification.
- **Missing in theirs:** They do not include transportation access, environmental burden, job density, or sector mix. Our clustering vector is substantially broader.
- **Racial displacement:** They explicitly track displacement of Black residents as a primary outcome variable. We include racial composition but do not attempt to classify tracts by displacement outcome — that would require housing displacement data (Zillow, Eviction Lab) we do not currently have at tract grain.

---

## 2. Urban Displacement Project (UDP) Displacement Typologies

**Reference:** Zuk, M., Chapple, K. et al. *Displacement and Gentrification Typologies* (2015, updated 2020). UC Berkeley College of Environmental Design.  
**Links:**
- [Urban Displacement Project — main site](https://www.urbandisplacement.org/)
- [UDP displacement-typologies GitHub (methodology + code)](https://github.com/urban-displacement/displacement-typologies)
- [UDP Replication Methodology PDF (2020)](https://www.urbandisplacement.org/wp-content/uploads/2021/07/udp_replication_project_methodology_10.16.2020-converted.pdf)
- [SF Bay Area typology map](https://www.urbandisplacement.org/maps/sf-bay-area-gentrification-and-displacement/)

**Note on "Urban Institute":** The PHASE7_PLAN references "Urban Institute Neighborhood Change Typologies," but the canonical publicly documented tract-level typology with the Emerging/Transitional framing is the **Urban Displacement Project** at UC Berkeley, not the Urban Institute. They are separate organizations. The Urban Institute does produce neighborhood change analyses but does not publish a comparable typology map product.

### What they built

An eight-type decision tree classification that places each census tract on a spectrum from stable affordable housing to hyper-exclusive displacement. The primary use case is mapping gentrification risk for local advocacy and housing policy. Open-source, replicable methodology. Currently covers the SF Bay Area, Los Angeles, Seattle, Austin, Portland, and select other metros; not a full national model.

### Methodology

Rule-based decision tree classification — not cluster analysis. The primary split is tract income relative to the regional median:

**Low-income track** (tract median household income below 80% of regional median):
1. Low-Income / Susceptible to Displacement — stable but vulnerable
2. At Risk of Gentrification — early change signals
3. Early / Ongoing Gentrification — active loss of low-income households
4. Advanced Gentrification — formerly low-income, now substantially transformed
5. Ongoing Displacement — low-income household loss without classic gentrification signals (disinvestment context)

**Moderate-to-high-income track** (tract median HHI at or above 80% of regional median):
6. Stable Moderate / Middle Income — no strong pressure
7. Stable / Advanced Exclusive — long-term high-income neighborhood
8. Super Gentrification / Advanced Exclusion — median HHI at 200%+ of regional median; hyper-exclusive

### Input variables

| Variable | Our equivalent |
|---|---|
| Median household income (relative to regional median — 80% and 200% thresholds) | `median_hh_income` in `economics_income_wide`; we compute CBSA percentile ranks which can reproduce the relative threshold logic |
| Net change in low-income household counts (displacement proxy) | **Not directly available** — requires ACS microdata or administrative records to count households below 80% AMI |
| Zillow Home Value Index (2012–2017) | **Not in our platform** — see Data Gaps section |
| Zillow Rent Index (2012–2017) | **Not in our platform** — see Data Gaps section |
| Share college-educated | `pct_ba_plus` in `population_demographics` |
| Racial/ethnic composition change | `pct_black_nh`, `pct_hispanic`, `pct_asian_nh` (current snapshot; not change-over-time at tract grain) |
| Overall population stability | `pct_same_house` in `migration_wide` ≈ residential stability proxy |

**Data sources:** U.S. Decennial Census, ACS 5-year estimates, Zillow Home Value Index, Zillow Rent Index.

### Geographic grain

Census tract (metropolitan areas, variable coverage by city).

### Alignment with our approach

| Dimension | Notes |
|---|---|
| Geographic grain | ✅ Same — census tract |
| Income-relative-to-metro benchmarking | ✅ We compute CBSA percentile ranks per theme — effectively the same relative position logic |
| Zone type alignment | Their stages 1–3 map to our **Distressed** → **Affordable Working Class** → **Emerging / Transitional** types; stages 6–7 map to our **Established Residential**; stage 8 maps to a high end of our **Knowledge Corridor** type |
| Stability proxy | ✅ `pct_same_house` serves the same function as their residential stability input |

### Divergence

- **Methodology:** Same note as NCRC — rule-based thresholds vs. our unsupervised clustering. Their typology is a policy intervention tool designed to identify where displacement risk is highest. Ours is a descriptive spatial typology covering a broader set of neighborhood attributes.
- **Trajectory focus:** UDP is fundamentally a before/after classification designed to identify directional change (a neighborhood moving from type 2 to type 3 is the key output). Our Phase 7 model is a current-state snapshot; trajectory analysis is deferred to future phases.
- **Zillow data:** Their home price and rent change signals rely on Zillow HVI and ZRI at tract grain. We do not currently ingest Zillow at tract grain. This is a meaningful gap for displacement risk analysis — see Data Gaps.
- **Scope:** UDP is metro-by-metro, not a consistent national classification. We classify all 396 CBSAs using a single national model — this means our zone types mean the same thing cross-market, while UDP labels are relative to each metro's own distribution.
- **Missing in theirs:** No environmental burden, walkability, transit access, or job sector composition. No DBSCAN corridor detection — their output is tract-by-tract classification with no spatial corridor grouping layer.

---

## 3. Esri Tapestry Segmentation (2024)

**Reference:** Esri Tapestry Segmentation. Annual updates; current version is 2024.  
**Links:**
- [Esri Tapestry product page](https://www.esri.com/en-us/arcgis/products/data/data-portfolio/tapestry-segmentation)
- [ArcGIS documentation](https://doc.arcgis.com/en/esri-demographics/latest/esri-demographics/esri-tapestry.htm)
- [2024 Methodology Statement PDF](https://content.esri.com/esri_content_doc/dbl/us/j9941_tapestry_segmentation_methodology_2024_final.pdf)
- [2024 Segments and Groups Reference PDF](https://content.esri.com/support/downloads/other_/2024/2024_usa_esri_tapestry_segments_and_groups.pdf)

### What they built

A commercial geodemographic segmentation system that classifies every U.S. census block group (~220,000+ block groups) into one of 67 lifestyle segments. Block groups are then rolled up to other geographies. Designed for retail site selection, marketing targeting, and audience profiling — not for policy analysis of neighborhood health or displacement.

### Structure

- **67 segments** organized into **14 LifeMode groups** (e.g., *Affluent Estates*, *Uptown Individuals*, *Rustbelt Traditions*, *Next Wave*) and **6 Urbanization groups**
- Segment names are lifestyle-branded: *Laptops and Lattes*, *Top Tier*, *Rooted Rural*, *Fresh Ambitions*, *College Towns*, *Dorms to Diplomas*
- Urbanization groups provide a simpler urban-suburban-rural cut across the 67 segments

### Methodology

Proprietary geodemographic cluster analysis applied to all U.S. block groups simultaneously. Internally homogeneous, externally heterogeneous segments. Esri does not publish its specific algorithm (assumed to be an iterative k-means or mixture model variant). The 67-type solution is the production granularity; Esri also publishes a 14-group rollup for simpler applications.

### Input variables

| Variable | Our equivalent |
|---|---|
| Age and life stage | `pct_age_over_64` in `population_demographics` (partial) |
| Education level | `pct_ba_plus` in `population_demographics` |
| Household income and wealth | `median_hh_income` in `economics_income_wide` |
| Homeownership and housing tenure | `owner_occ_rate` in `housing_core_wide` |
| Household composition and family structure | Partial — `pct_struct_multifam` is a structural proxy; no direct family-type KPI |
| Consumer behavior and purchasing patterns (MRI-Simmons surveys) | **Not in our platform and not our objective** |
| Car ownership | `pct_hh_0_vehicles` in `transport_built_form_wide` (inverse proxy) |
| Residential density and urbanization | `pop_weighted_density_sqmi` in `transport_built_form_wide` |
| Employment and occupation | Partially — `pct_jobs_professional_services` (LODES, pending ETL) |

**Data sources:** U.S. Census, ACS, Esri Updated Demographics (proprietary current-year estimates), MRI-Simmons consumer survey data.

### Geographic grain

Census block group (~220,000 nationally) — finer than our tract grain.

### Why Tapestry differs from our approach

Tapestry is analytically distinct from our methodology in three ways:

1. **Consumer behavior layer:** Tapestry blends census demographics with proprietary consumer purchase survey data (MRI-Simmons). This optimizes for marketing utility — a segment's profile tells you what its residents *buy*, not just who they are. Our platform uses no consumer data and makes no attempt to profile purchasing patterns.

2. **Purpose:** Tapestry is designed for commercial applications (retail site selection, advertising audience targeting). It is optimized for marketing differentiation. Our zone types are designed to describe neighborhood economic structure, livability, and opportunity in a way that is useful for real estate investment analysis and market narrative.

3. **67 types at block-group grain:** Tapestry's 67 types exist to maximize marketing differentiation across very fine geography. Our expected 7–10 types at tract grain prioritize interpretability, narrative defensibility, and cross-market comparability. A system with 67 types cannot be used in a readable investor brief.

### Alignment

| Dimension | Notes |
|---|---|
| Core demographic inputs | ✅ High overlap — education, income, housing tenure, density, car ownership are in both |
| Geographic grain | ⚠️ Tapestry is block-group; we are tract. Our grain is coarser but appropriate for the investment and policy use cases we serve |
| Clustering methodology | ✅ Tapestry confirms that geodemographic cluster analysis at 7–10+ types is a viable and established approach for neighborhood classification |
| Granularity benchmarking | ✅ Tapestry sets the upper bound of what is achievable with granular inputs (67 types) — confirms our 7–10 type target is deliberate parsimony, not a data limitation |

### Divergence

- No policy or equity orientation — no poverty rate, no environmental burden, no OZ flag, no job-side signal
- No DBSCAN corridor layer — all spatial grouping is implicit in the block group assignment
- Proprietary consumer data means results are not reproducible from public data sources

---

## 4. Enrico Moretti — The New Geography of Jobs (2012)

**Reference:** Moretti, E. *The New Geography of Jobs*. Houghton Mifflin Harcourt, 2012. ISBN 978-0-547-75011-8.  
**Supporting papers:**
- Moretti, E. "Local Multipliers." *American Economic Review*, 100(2): 373–377, 2010. DOI: [10.1257/aer.100.2.373](https://www.aeaweb.org/articles?id=10.1257%2Faer.100.2.373)
- Moretti, E. "Local Labor Markets." NBER Working Paper No. 15947, 2010. [nber.org/papers/w15947](https://www.nber.org/papers/w15947)
- Moretti, E. and Thulin, P. "Local Multipliers and Human Capital in the United States and Sweden." *Industrial and Corporate Change*, 22(1): 339–362, 2013. [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2043140)

**Links:**
- [Book page — Berkeley](https://moretti.econ.berkeley.edu/book)
- ["Local Multipliers" — AEA](https://www.aeaweb.org/articles?id=10.1257%2Faer.100.2.373)
- [Stanford GSB interview](https://www.gsb.stanford.edu/insights/enrico-moretti-geography-jobs)

### What this is

Moretti's work is not a neighborhood typology system — it is a body of economic research on why skilled workers and innovation-sector jobs concentrate geographically, and what the macroeconomic consequences of that concentration are. It is the intellectual foundation for our **Knowledge Corridor** zone type.

### Key arguments

**Brain hubs vs. abandoned places:** Among ~320 U.S. metropolitan areas, Moretti identifies roughly 15–20 "brain hubs" — metros like San Francisco, Boston, Austin, Raleigh-Durham, and Washington D.C. — where college-educated workers concentrate, the innovation sector is large, and wages are high across all skill levels. At the other pole are what he calls "abandoned places" — metros like Flint, Youngstown, and Bakersfield — with low college-educated shares, diminished manufacturing, and persistent wage stagnation. These poles diverge over time rather than converging.

**The local multiplier effect:** For each new high-tech job created in a city, approximately **5 additional jobs** are created in local non-traded services — roughly 2 going to college-educated workers (doctors, lawyers) and 3 going to workers without college degrees. This is the core quantitative finding from the 2010 AER paper. The manufacturing multiplier is substantially lower.

**Self-reinforcing clustering:** Knowledge economy activity is sticky — once a metro attracts innovation firms and workers, knowledge spillovers, thick specialized labor markets, and venture capital availability make it easier to attract more. This is the mechanism behind divergence.

**Geography as a wage determinant:** A high school graduate earns ~7% more for every 10% increase in college graduates in their city. Your employer, education, and demographic group matter for wages — but so does your zip code.

### Data and methodology

- U.S. Census, CPS, BLS Quarterly Census of Employment and Wages (QCEW)
- ~8 million workers, 320 metropolitan areas, 30-year window (1980–2010)
- Bartik-style shift-share instruments for causal identification
- USPTO patent data as innovation output proxy

**Geographic grain:** Metropolitan Statistical Area — not tract or sub-metro. Moretti's entire argument operates at the city level.

### What "Knowledge Corridor" actually means

The term *Knowledge Corridor* does not appear to be a Moretti coinage. It is primarily used as a regional economic development label for the Hartford-Springfield CT/MA corridor. We are using the phrase in a different and more specific sense: a sub-metro zone type identifying tracts within a metro that host the high-BA, high-wage, high-jobs-density clustering Moretti describes at the city scale. Moretti's concepts map to our type's expected centroid profile; the label itself is our own.

### Alignment with our approach

| Dimension | Notes |
|---|---|
| Intellectual foundation for Knowledge Corridor | ✅ Direct — Moretti defines the economic logic behind why high-BA, innovation-sector tracts cluster spatially and produce wage spillovers |
| LODES job-side KPIs | ✅ `pct_jobs_high_wage`, `pct_jobs_professional_services`, `jobs_per_resident` are the tract-level operationalizations of Moretti's metro-scale brain hub concept |
| Local multiplier and `jobs_inflow_ratio` | ✅ `jobs_inflow_ratio` captures the commute-in dynamic that characterizes a jobs center — related to (though not identical to) Moretti's multiplier logic |
| Human capital momentum | ✅ `pct_ba_plus_change_5yr` captures the temporal trajectory Moretti shows drives long-run wage divergence |

### Divergence

- **Scale:** Moretti operates entirely at MSA level. We disaggregate to the tract — Moretti's brain hub metro may contain Knowledge Corridor tracts alongside Distressed and Growth Periphery tracts. Our model reveals the within-metro spatial structure that Moretti's metro-level analysis obscures.
- **Moretti has no zone type for the losing side:** His "abandoned places" concept is metro-scale. Within a brain hub metro, distressed tracts are invisible in his framework. Our Distressed zone type exists precisely to capture that within-metro inequality.
- **No environmental or livability layer in Moretti:** His research is purely labor economics — no environmental burden, walkability, housing affordability, or transit access variables.
- **Static snapshot vs. multiplier dynamics:** Our model produces a current-state zone type label. It does not attempt to estimate the forward multiplier effect Moretti documents. That would require longitudinal data and a causal identification strategy outside Phase 7 scope.

---

## Data Points in the Literature — Absent from Our Platform

The following variables appear in one or more of the frameworks reviewed above and are either absent from our current Gold layer or only partially available. These represent gaps worth tracking for future data engineering consideration.

| Variable | Source in literature | Platform status | Notes |
|---|---|---|---|
| **HMDA mortgage lending activity** (loan origination counts, denial rates, lending volume by tract) | NCRC gentrification series — used as validation layer for post-2000 analysis | Not ingested | HMDA is public (CFPB FFIEC), tract-level, annual. Would be a meaningful addition for displacement risk and investment activity signals. Not blocking Phase 7. |
| **Zillow Home Value Index (tract or ZIP)** | UDP displacement typologies — primary home price change signal | Not ingested | Zillow API or bulk download required. Useful for gentrification trajectory. Not a public domain dataset in the same sense as ACS/LODES. |
| **Zillow Rent Index (tract or ZIP)** | UDP displacement typologies — primary rent change signal | Not ingested | Same as above. Rent burden in ACS (`pct_rent_burden_30plus`) is a partial substitute, but it doesn't capture the rate of rent change. |
| **Net change in low-income household counts below 80% AMI** | UDP — used as direct displacement proxy | Not computed | Requires ACS microdata or a derived household income distribution estimate. ACS publishes income quintile shares, which could approximate this with careful engineering. |
| **Eviction filing rates** | Not in these four frameworks but appears frequently in displacement research (Eviction Lab, Princeton) | Not ingested | Tract-level eviction data from Princeton's Eviction Lab is publicly available for many states. Highly relevant for Distressed type validation. |
| **Consumer behavior / lifestyle segmentation data** | Esri Tapestry (MRI-Simmons consumer surveys) | Not applicable — by design | We do not use proprietary consumer data. Noted only for completeness. Not a gap — it is a deliberate boundary. |
| **Innovation sector employment share at tract grain** | Moretti's metro-level brain hub analysis — operationalized by us via LODES WAC pending ETL | In progress (Sprint 0.1) | `pct_jobs_professional_services` from LODES WAC is the planned operationalization. Blocked on Sprint 0.1 ETL completion. |
| **USPTO patent counts or tech firm establishment counts at tract/ZIP grain** | Moretti uses patents as innovation output proxy at MSA level | Not ingested | Patent data is geocodable to the inventor/assignee address, which can be aggregated to tract. This is a data engineering investment, not a simple ingestion. Out of scope for Phase 7 but worth noting as a future signal for Knowledge Corridor type validation. |
| **Decennial Census longitudinal harmonized data (LTDB)** | NCRC uses Brown University LTDB for 1970–2020 tract comparability | Not ingested | LTDB normalizes decennial census counts to 2010 tract boundaries. Relevant only if we pursue longitudinal tract trajectory analysis in a future phase. Not blocking Phase 7, which is a current-state snapshot model. |

---

## Summary alignment matrix

| Dimension | NCRC | UDP | Esri Tapestry | Moretti |
|---|---|---|---|---|
| **Our zone type most similar to theirs** | Emerging/Transitional ≈ Gentrifying; Distressed ≈ Eligible/Non-gentrifying | Stages 1–5 map to Distressed → Emerging; Stages 6–8 map to Established/Knowledge | 67 segments → many overlap with our 7–10; *Top Tier* ≈ Knowledge Corridor, *City Commons* ≈ Affordable Working Class, *Economic BedRock* ≈ Distressed | Brain hub ≈ metro containing Knowledge Corridor tracts |
| **Input overlap with us** | High (income, education, housing, race) | High (income, housing, stability) | Moderate (education, income, tenure, density, car ownership) | Low (metro-level labor economics only) |
| **What they have that we lack** | HMDA lending data | Zillow HVI/ZRI, low-income HH change | Consumer behavior (not our objective) | Causal multiplier estimates, patent data |
| **What we have that they lack** | Transportation access, jobs/sector, environmental burden, walkability | Same as NCRC, plus OZ designation | Poverty, vacancy, EJ burden, OZ, transit | Sub-metro spatial structure (tract grain), environmental + livability |
| **Methodology gap** | Rule-based thresholds → we use clustering | Rule-based decision tree → we use clustering | Proprietary clustering at BG grain → we use open-source clustering at tract grain | MSA regression → we disaggregate to tract |
| **Geographic scope** | Central city tracts only | Metro-by-metro (not national consistent) | National, all BGs | National, MSA level |

---

*This document fulfills Sprint 1.1 of Phase 7. The KPI finalization task (Sprint 1.2) should reference the data gaps table above when confirming which LODES WAC fields to include and whether any external data (HMDA, Zillow) should be added before the national model runs.*
