# Richmond, VA — Deep Dive Spec

**Market:** Richmond-Petersburg, VA CBSA (GEOID 40060)
**Census Division:** South Atlantic
**Status:** Planning — ad hoc first pass, codify after
**Last updated:** 2026-07-12

### Resolved decisions

| Decision | Resolution |
|---|---|
| AI exposure source | Felten et al. Data Appendix B (NAICS-4-digit AIIE scores) — same source as the publisher AI series. GS scores are SOC major groups only, not joinable to NAICS without approximation. |
| LODES commute data | Ingest OD files when we reach S04a regional role. WAC/RAC already ingested at tract grain; OD is the next step for flow maps. |
| Map rendering | Static maps for now. Tool (R or Python) decided per section; no lock required. |

This document is the working spec for the Richmond issue. It is not a final plan — it's a starting point for the ad hoc build. Sections get updated as we learn what the data actually shows. Decisions made here that prove durable get promoted to the template; decisions that were Richmond-specific stay here.

---

## How to Read This Spec

Each section below covers one piece of the issue: what question it answers, what data it needs, what visual(s) it produces, and what needs to be built vs. what already exists. A **Build needed** block at the end of each section calls out the actual work items.

Sections are organized by Act, matching the delivery structure. Within each section, ideas beyond the first-pass minimum are marked **Stretch** — good candidates if the data motivates them, not commitments.

---

## Act 1 — Identity

*Goal: orient the reader. Where does Richmond sit nationally, why does it exist, who does it resemble?*

---

### S01 — Market Fingerprint

**Question:** How does Richmond sit nationally across character, livability, and opportunity simultaneously?

**What it produces:**
- Top-line stat boxes: population, income per capita, GDP, life expectancy, region, Intelligence Framing Cluster
- Radar chart: 6–8 KPIs, percentile-normalized against ~400 CBSAs, national median overlay
- One-line verdict directly under the chart
- Compact percentile table: KPI | raw value | national percentile | rank

**KPI selection (to decide before building):**
Axis order is locked after market #1 — this is the editorial decision that propagates to every future issue. Draft selection below; needs deliberate sign-off before the radar renders.

| Frame | KPI | Rationale |
|---|---|---|
| Character | `pct_ba_plus` | Educational attainment — clean, comparable, structurally revealing |
| Character | `median_age` | Age structure — single number, intuitive for lay readers |
| Character | `pop_growth_5yr` | Population trajectory as a character signal |
| Livability | `life_expectancy` | Single best health outcome summary |
| Livability | `rent_to_income` | Affordability burden — more comparable across metros than raw gross rent |
| Livability | `walkability_index` | Built environment proxy |
| Opportunity | `income_pc_growth_5yr` | Growth trajectory over income stock |
| Opportunity | `hpi_5yr_pct` | Market momentum |
| Opportunity | `real_gdp_growth_5yr` | Economic output growth |

9 KPIs is workable but slightly crowded for a radar. Consider trimming `median_age` or `pop_growth_5yr` after seeing the shape — both carry similar signals. `diversity_index` dropped: single-number compression of a multi-axis distribution, hard to explain and hard to compare.

**Top-line stat boxes** (fixed across every issue — not on the radar):
`pop_total`, `calc_income_pc`, `real_gdp_total`, `life_expectancy`, region, Intelligence Framing Cluster label. Median gross rent goes here, not the radar.

All KPIs are in Gold and used in frame calibration. No new data sourcing needed.

**Data sources:**
- `gold.character_wide`, `gold.livability_wide`, `gold.opportunity_wide` — frame KPI values at CBSA grain
- `exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_scores.parquet` — frame percentile ranks and Intelligence Framing Cluster label

**Build needed:**
- [ ] Pull Richmond row + national distribution for the 6–8 candidate KPIs
- [ ] Compute national percentile ranks
- [ ] Confirm KPI selection and lock axis order
- [ ] Render radar using chart engine (scatter or custom radar) + percentile table
- [ ] Write the one-line verdict after seeing the shape

---

### S02 — History Box

**Question:** Does Richmond's founding logic still show in the data?

**The angle:** Richmond's origin story runs through three threads — state capital (1780), tobacco economy (19th–20th century), and Civil War capital. All three leave data traces: state government is still a major employer, financial services grew from tobacco wealth (Altria HQ, historic banking), and the built environment carries that layered history. The interesting test is whether the government/finance legacy still shows in the current LQ profile (spoiler from the pilot notes: professional services is a rising star, not manufacturing or information).

**Format:** 150–250 word boxed narrative. This is editorial, not analytical — pull from Virginia historical records, city/CBSA Wikipedia, or regional planning documents.

**Forward link:** Connect to the LQ quadrant in S04 — "the government-adjacent professional services cluster still drives X% of specialization."

**Build needed:**
- [ ] Draft the history box narrative (research pass, ~1 hour)
- [ ] Confirm the forward link destination once S04 LQ results are in hand

---

### S03 — Peer Markets

**Question:** Who does Richmond structurally resemble, who is diverging fastest, and is any peer a plausible future state?

**What it produces:**
- Peer table: 5 nearest peers by cosine similarity, biggest similarity dimension, biggest divergence dimension
- One dumbbell chart vs. the single most instructive peer
- Forward-analog paragraph if one credibly exists

**Method:** Cosine similarity scores are already computed in the intelligence framework phase 5 outputs — query the cross-frame parquet rather than rerunning the similarity engine. Confirm whether the stored scores are frame-level (three separate similarity vectors) or a combined cross-frame vector; if frame-level, a short weighted aggregation step produces the single ranking. Run a second pass on 5yr growth rate slopes to surface trajectory peers separately from structural peers.

**Richmond hypothesis:** Likely structural peers are mid-size South Atlantic metros with government/professional service bases — Raleigh (aspirational divergence on tech), Louisville, Greensboro, perhaps Richmond-adjacent metros like Charlottesville or Fredericksburg. Trajectory peers may differ.

**Data sources:**
- `exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_scores.parquet` — cross-frame similarity scores, already computed
- `exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_phase5_combined_input_matrix.parquet` — full KPI input matrix if we need to rerun on a different feature set

**Build needed:**
- [ ] Run cosine similarity on z-scored KPI vectors for Richmond vs. all ~400 CBSAs
- [ ] Separate run on trend slopes (5yr growth rates) to surface trajectory peers
- [ ] Pull top 5 by level similarity, check for forward-analog candidate in slope peers
- [ ] Decide featured peer for dumbbell chart once results are in
- [ ] Render peer table (gt) + dumbbell chart

---

## Act 2 — Engine and Fabric

*Goal: what drives Richmond, and what does life here look like?*

---

### S04a — Industry Makeup and Regional Role

**Question:** What is Richmond disproportionately good at, are those specializations growing or fading, and what role does it play in the broader Virginia/South Atlantic economy?

**What it produces (fixed spine):**
- LQ quadrant chart: LQ (x) vs. YoY employment growth (y), four quadrants, labeled by sector
- Exposure scorecard: top 8–10 sectors by employment share × AI exposure index × policy sensitivity flags
- Regional role summary sentence: inflow/outflow ratio, top origin tracts, characterization (attractor / bedroom / self-contained)

**From the pilot notes:** Professional services, transportation/utilities, and construction are the early leads. Information and manufacturing sit below LQ 1.25. Government is present but via the state capital effect. This makes Richmond's story more "stable civic economy with services growth" than "tech transition."

**Sectors to watch:**
- `Professional & Business Services` — likely rising star
- `Transportation & Utilities` — likely mature strength (port + rail history)
- `Construction` — growth signal, ties to housing supply
- `Finance & Insurance` — worth checking, given Altria/capital wealth legacy
- `Government` (if in QCEW) — structural anchor, not a specialization per se

**Regional role:** Richmond sits between Northern Virginia (high-wage tech attractor) and the Hampton Roads military complex. It likely functions as a sub-regional services hub and receives some workforce from the Richmond–Petersburg periphery while losing residents to the NoVA corridor. The inflow/outflow ratio from LEHD LODES is the one-number test.

**What's already in Gold:**
`gold.economics_industry_wide` already has LQs computed (`lq_professional`, `lq_construction`, etc.) from QCEW private employment vs. national shares, plus BEA real GDP by sector (`real_gdp_professional`, `real_gdp_information`, etc.) and BEA earnings by sector. The LQ quadrant chart is mostly a query — no new computation needed. YoY growth requires comparing two years of the same table.

**Data sources:**
- `gold.economics_industry_wide` — LQs, QCEW employment, BEA sector GDP, all at CBSA grain. Latest year 2024 for QCEW; BEA GDP lags by ~1 year.
- `staging.lehd_lodes_wac` + `staging.lehd_lodes_rac` — already ingested at tract grain. WAC = jobs at workplace tract; RAC = jobs at residence tract. CBSA-level inflow/outflow ratio derivable from these without OD. OD ingestion is the next step for a true flow map (marked as separate build item).
- IRS migration flows — in Gold via `gold.social_fabric_wide` (`irs_net_migration`, `irs_net_agi`) for net flows; state-of-origin detail requires the IRS SOI migration tables directly.

**Exposure scorecard:** Use Felten Data Appendix B (NAICS-4-digit AIIE scores) — resolved. The scorecard column in S04a gets the sector-level AIIE weighted by Richmond's QCEW employment share. S04b builds the full occupation-level crosswalk on top.

**Build needed:**
- [ ] Query `gold.economics_industry_wide` for Richmond: LQs + YoY growth (latest two years); assign quadrant labels
- [ ] Render LQ quadrant scatter
- [ ] Derive inflow/outflow ratio from WAC vs. RAC at Richmond CBSA level from staging tables
- [ ] Download Felten Data Appendix B; join to QCEW sector employment shares; compute sector-level AIIE for Richmond
- [ ] Build exposure scorecard table: sector | emp share | AIIE score | policy flags
- [ ] Write regional role summary sentence
- [ ] *(Separate build)* Ingest LODES OD files for Virginia; derive tract-to-tract flow map

---

### S04b — AI Exposure Deep Dive

**Question:** Which of Richmond's specializations are most exposed to AI-driven employment displacement, and where does that show up across occupation types vs. sector GDP contribution?

**Why Richmond is interesting here:** Richmond's professional services and finance legacy employs a high share of office and knowledge workers — precisely the occupations that Felten et al. score highest for AI exposure. Unlike a manufacturing-heavy metro where automation risk is blue-collar, Richmond's risk profile is white-collar. That's the story.

**What it produces:**
- Exposure scatter: sectors plotted by (AI exposure score, employment share) — bubbles sized by sector GDP contribution
- Occupation breakdown: within the highest-exposure sectors, which occupation groups dominate? (ACS occupation mix × Felten scores)
- One-paragraph synthesis: "X% of Richmond employment sits in high-exposure industries; within those industries, Y occupation types are most at risk"

**This is the theme engine.** Once built for Richmond, this engine (NAICS→SOC→Felten crosswalk + sector GDP weight) is reusable for every subsequent market. It also yields a standalone national thematic piece: AI exposure mapped across all 400 CBSAs.

**What's already in Gold:**
`gold.economics_occupation_wide` has OEWS 2025 data rolled into 4 buckets (management_professional, service, production_transportation, other) with STEM flag, employment counts, wages, and LQs — already at CBSA grain. The bucket grain is too coarse for Felten SOC-level joining, so this section uses `silver.bls_oews` directly for the detailed SOC employment mix within Richmond.

**Data sources:**
- `silver.bls_oews` — detailed SOC-level occupation employment for Richmond CBSA (2025 vintage). This is the input for the Felten AIOE crosswalk.
- Felten et al. Data Appendix A — AIOE scores by 6-digit SOC (occupation-level). Download from `github.com/AIOE-Data/AIOE`.
- Felten et al. Data Appendix B — AIIE scores by 4-digit NAICS (already used in S04a). Needed here to cross-check sector vs. occupation exposure.
- `gold.economics_industry_wide` — BEA sector GDP shares for bubble sizing.

**Note on ACS occupation × industry:** ACS does carry an industry × occupation cross-tab (B24010 series) but it's at broad SOC and broad NAICS groups, not fine-grained enough for this analysis. Use OEWS (`silver.bls_oews`) instead — it has detailed SOC at CBSA grain and is the same source the AI Exposure Brief specifies for Article 2.

**Build needed:**
- [ ] Pull Richmond CBSA rows from `silver.bls_oews`; keep detailed SOC (o_group = 'detailed')
- [ ] Download Felten Data Appendix A (AIOE by SOC); join to OEWS on 6-digit SOC code
- [ ] Compute employment-weighted AIOE per broad sector for Richmond
- [ ] Render bubble scatter: x = AIOE, y = employment share, size = BEA sector GDP contribution
- [ ] Identify top 2–3 occupation groups driving exposure within highest-exposure sectors
- [ ] Write synthesis paragraph
- [ ] *(Stretch)* Run same crosswalk for all 400 CBSAs → national AI exposure map (yields standalone thematic article)

**Stretch:** Run the same crosswalk for all 400 CBSAs → national thematic map. This is the "build once, ship three ways" payoff but is not required for the Richmond issue to ship.

---

### S05 — Built Environment and Social Fabric

**Question:** What does the physical and social structure of Richmond look like, and where are the access gaps and amenity anchors?

**What it produces:**
- Tract-level amenity/accessibility proxy score (carry forward to S09 corridors)
- Infrastructure map: roads, rail, transit, key POIs — showing the spatial skeleton of the metro
- Housing stock + vacancy spatial layer: where is the housing concentrated, where is it vacant?
- Cultural fabric narrative: 2–3 paragraphs on what makes Richmond itself (arts, food, VCU/UR anchor, James River)

**Two-pass approach:**

*Pass 1 (now — Gold data only):*
- Compute tract-level proxy score from Gold: z-score average of `walkability_index`, `jobs_access_45min_transit`, `pct_commute_transit`, `pct_commute_walk`
- Pull housing stock mix (`pct_struct_multifam`, `pct_struct_small_mf`, etc.) and vacancy rate at tract grain from `gold.intelligence_zone_inputs`
- Identify high-access vs. low-access tracts directionally; note where vacancy clusters relative to access
- Static choropleth rendered in Python (geopandas + matplotlib) or R (sf + ggplot2)

*Pass 2 (OSM layer — build when we reach this section):*
- Road network + transit lines via `osmnx` (Python) or `osmdata` (R) — both produce static map output
- POI layers: parks, groceries, hospitals, cultural venues
- Replace proxy score with distance-based amenity score once POI geometry is in hand
- Static export via matplotlib/geopandas or tmap/ggplot2; decision deferred until we start this section

**Richmond spatial hypotheses:**
- Fan District / Scott's Addition / Manchester are the arts/food anchors; likely high walkability, lower vacancy
- Southside Richmond (below the James) likely shows lower transit access; worth checking if vacancy also concentrates there
- VCU Medical Campus as a major institutional anchor in the near-west — healthcare employment cluster feeds into S04a

**Housing stock + vacancy angle:**
This is the bridge between S05 and S06. The static picture (stock mix, current vacancy by tract) lives here. The dynamic picture (permits vs. population growth over time) moves to S06. The analytical question: does vacancy concentrate in low-access areas (expected) or in high-access areas with declining demand (more interesting)?

**Data sources:**
- `gold.intelligence_zone_inputs` — tract-level walkability, transit access, commute mode, housing stock
- `gold.transport_built_form_wide` — metro-level transit and built form context
- `gold.social_infra_wide` — social institutions context
- OSM/Overpass (when geometry pipeline ready)

**Build needed:**
- [ ] Compute tract-level proxy score (z-score average, 4 inputs from `gold.intelligence_zone_inputs`)
- [ ] Pull vacancy rate and housing stock mix at tract grain
- [ ] Map: choropleth of proxy score by tract + vacancy overlay
- [ ] Draft cultural fabric narrative (Richmond: VCU, James River, Scott's Addition, arts scene)
- [ ] Note POI map as deferred pending geometry pipeline

---

## Act 3 — Dynamics

*Goal: how is Richmond changing, and what does that change signal?*

---

### S06 — Trend Analysis

**Question:** Where is Richmond accelerating or decelerating relative to national trends, and what internal dynamics are reshaping the picture?

**What it produces:**
- Small multiples: 4–6 panels, metro line vs. national line, indexed to common base year, inflection points annotated
- Each series classified: Converging / Diverging / Inflecting
- Narrative lead = the strongest inflection
- Forward-looking sentence connecting dynamics to the opportunity funnel in Act 4

**Series candidates (pick 4–6 based on what's most interesting once data is in):**

| Series | Source | Hypothesis |
|---|---|---|
| Permits vs. population growth | Building Permits Survey + ACS | Supply lagging demand? Permits per 1k housing units vs. national rate |
| Home price appreciation (HPI) | FHFA / `hpi_5yr_pct` | RVA has appreciated steadily; how does the trajectory compare? |
| Rent growth (ZORI) | Zillow via Gold | Has rent growth accelerated post-COVID faster than national? |
| Income per capita growth | ACS vintages | Converging toward NoVA-driven Virginia median, or plateauing? |
| Sector GDP composition change | BEA / Gold | Is the professional services share growing at the expense of manufacturing? |
| Unemployment rate trajectory | QCEW / BLS | Recovery pace vs. national post-2020 |

**The composition change visual (your item 3):**
Sector GDP composition change over time is best shown as a **bump chart** (rank change by sector, year over year) or a **stacked area** (share shift). The R `parcat` approach works if the question is "which sectors moved between discrete tiers" — e.g., did construction go from below-median to top-quartile GDP share? That framing makes the categorical flow legible.

Recommendation: build the bump chart first (already in the visual library as `bump_chart.py`). If the data shows interesting tier-crossing behavior, add the parcat panel as a companion. Building parcat from scratch is new chart engine work; only worth it if the story demands it.

**What's already in Gold:**
BEA sector GDP time series is already in `gold.economics_industry_wide` (`real_gdp_professional`, `real_gdp_information`, etc.) going back multiple years — the sector composition bump chart pulls directly from this table, no new ingestion needed. HPI, ZORI, and income growth are in `gold.opportunity_wide` or `gold.housing_market_wide`.

**Data sources:**
- `gold.economics_industry_wide` — BEA sector GDP time series for composition change; QCEW employment series for unemployment trajectory
- `gold.housing_market_wide` — FHFA HPI, ZORI rent growth, permit data
- `gold.opportunity_wide` — income per capita time series
- Building Permits Survey — check `gold.housing_market_wide` first; pull from Census API if not available as a time series

**Build needed:**
- [ ] Pull time series for the 4–6 candidate series; index to common base year (2010 or 2015)
- [ ] Compute metro vs. national slope; classify each series
- [ ] Flag inflections programmatically (rolling slope change)
- [ ] Render small-multiples panel (faceted line chart, metro + national)
- [ ] For sector GDP composition: pull BEA sector GDP series for Richmond CBSA; render bump chart
- [ ] Write narrative lead on strongest inflection; close with forward sentence to Act 4

---

### S07 — Data Take Sidebar

**Question:** Why is Richmond weird on X?

**What it produces:** 1–2 boxed sidebars, each with one chart and ~100 words.

**Method:** Run the outlier scan — flag every Gold KPI where Richmond sits in the national top or bottom decile. Hand-pick the one or two that are surprising *given the Intelligence Framing Cluster*. A government-heavy mid-South metro being below-median on walkability is not a Data Take. The same metro being top-decile on business formation rate would be.

**Hypotheses to test:** These are guesses to validate against the scan output, not commitments.
- Richmond's economic connectedness (Opportunity Atlas social capital metric) may be low relative to its income level — a civic inequality story given the racial geography of the metro
- Friending bias or economic connectedness split between urban core and suburbs — if the scan flags it, it's the most interesting story in the issue
- Business application rate — if Richmond is forming businesses faster than peers, that's a growth signal worth a box

**Build needed:**
- [ ] Run outlier scan: all Gold KPIs at Richmond CBSA, flag national top/bottom decile
- [ ] Cross-reference with Intelligence Framing Cluster to score "surprisingness"
- [ ] Hand-pick 1–2; write boxes; render one chart each

---

## Act 4 — Opportunity Funnel

*Goal: where specifically are the opportunities within Richmond?*

**Act 4 scope decision:** The build approach says Acts 1–3 is a valid first issue. For Richmond, the recommendation is to attempt S08 zone construction as a first pass and use it to settle the methodology, but treat S09 corridors and S10 parcels as stretch goals that can ship in a follow-on piece or as the methodology matures.

---

### S08 — Zone Archetypes

**Question:** What mix of zone types does Richmond contain, and how does that compare to other markets?

**What it produces:**
- Archetype choropleth: tracts colored by zone archetype
- Benchmarked composition bar: % of zones by archetype vs. series average (initially just Richmond)
- One-paragraph composition story

**Method decision:** HDBSCAN is the recommended first candidate per the template (handles varying density natively, near drop-in for the existing DBSCAN tract cluster work). Run it on tract centroids weighted by dominant archetype from the Intelligence Layer clustering.

**Archetype names must be locked before publishing.** Don't name them until we've seen the Richmond output and confirmed the labels make sense for the full series.

**Data sources:**
- `gold.intelligence_zone_inputs` — tract-level clustering inputs
- Intelligence framework tract cluster assignments from `exploration/intelligence_framework/outputs/`

**Build needed:**
- [ ] Load Richmond tract cluster assignments from intelligence framework outputs
- [ ] Run HDBSCAN on tract centroids; inspect zone shapes for pathologies (stringy zones, fragments)
- [ ] If shapes are poor: try rook adjacency + minimum zone size filter before switching methods
- [ ] Assign dominant archetype per zone from tract labels
- [ ] Render choropleth + composition bar
- [ ] Lock archetype names before publishing

---

### S09 — Zone Corridors *(Stretch — target for follow-on)*

**Question:** Which contiguous zone clusters represent investable corridors?

**Deferred** until S08 zone construction is settled and an Investment Score threshold is defined. The corridor work requires zones to exist and score against a threshold — neither is locked yet.

**When ready:**
- Cross-reference S05 amenity proxy score with zone Investment Scores
- Name 2–4 corridors that clear the threshold and sit along identifiable infrastructure
- Richmond hypotheses: Broad Street corridor (Fan→Museum District→Scott's Addition), Hull Street (Southside emerging), Staples Mill Road (northwest industrial conversion)

---

### S10 — Parcel Watch *(Conditional — low probability for market #1)*

Parcel data availability for Richmond CBSA is unconfirmed. Regrid or Henrico/Chesterfield county open data would be needed. Mark as blocked until checked.

---

## Open Decisions

These need answers before the corresponding section can ship. Items marked **blocks build** cannot be worked around.

| Decision | Blocks | Status |
|---|---|---|
| Lock fingerprint KPI selection and axis order | S01 radar | **Draft locked above** — 9 KPIs across 3 frames. Sign-off needed before rendering. |
| AI exposure source | S04a scorecard, S04b | **Resolved: Felten et al.** Appendix B for industry (S04a), Appendix A for occupation (S04b). |
| LODES OD ingestion | S04a flow map, S05 commute shed | **Resolved: ingest OD when we reach that section.** WAC/RAC ratio is the first-pass regional role number. |
| Map rendering tool and format | S05, S08 | **Resolved: static maps.** Tool (Python/R) decided per section when we build it. |
| BEA sector GDP time series in Gold | S06 bump chart | **Confirmed: already in `gold.economics_industry_wide`**. No new ingestion. |
| ACS occupation × industry at CBSA grain | S04b | **Resolved: use `silver.bls_oews` instead.** ACS cross-tab is too coarse; OEWS has detailed SOC at CBSA grain. |
| HDBSCAN parameters for Richmond | S08 | Open — decide after running it |
| Lock archetype names | S08 publish | Open — don't decide until output is in hand |
| S09/S10 scope | Act 4 | Recommendation: S08 only for issue 1 |

---

## Potential Additional Ideas

Not committed, not scoped — ideas worth keeping visible in case the data motivates them or we have capacity.

**Racial geography and investment score overlay.** Richmond has one of the most historically significant racial geographies of any Southern metro — the redlining history, the highway displacement of Jackson Ward, the ongoing North/South James divergence. If Investment Scores are spatially concentrated in ways that correlate with race or historic redlining grades, that's both analytically interesting and editorially important to name. Would sit in S08 or S09 as a callout.

**IRS migration flow visualization.** Richmond draws from an interesting geographic funnel: Hampton Roads students, NoVA professionals priced out, DC transient population. IRS net AGI flows by origin state could be shown as a Sankey or chord diagram. Useful for the "regional role" narrative in S04a.

**Business formation momentum.** BFS business application rate over time — if Richmond is forming businesses faster than its peer cluster, it's a growth signal that doesn't show in the income or employment numbers yet. Natural Data Take candidate but could expand into a full S06 panel.

**Vacant land / underutilized parcels (preview).** Even if S10 doesn't ship for market #1, a brief qualitative note on where surface parking and vacant lots concentrate in Richmond (Scott's Addition pre-redevelopment, Southside corridors) would prime readers for the corridor thesis without requiring the full parcel screen methodology.

**Commute shed visualization.** LEHD LODES OD files (confirmed for ingestion when we reach S04a) can produce a flow map from Richmond's top employer tracts to their surrounding origin tracts. Shows the bedroom-community-vs-attractor question visually rather than as a single ratio. Render as a static flow map with line weight proportional to worker volume.
