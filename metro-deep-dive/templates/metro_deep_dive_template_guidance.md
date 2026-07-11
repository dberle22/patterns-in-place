# Metro Deep Dive: Template Guidance

**Patterns in Place** | Format guidance for Metro Deep Dive issues
**Version:** 2.0 | Revised 2026-07-11

---

## How to Use This Document

Each Act is organized around a **core question**. The sections inside each Act are the analytical moves that answer it. Some moves are fixed across every issue — they produce the comparable layer that makes this a series rather than a pile of one-off reports. Others flex to wherever the data leads in a given market.

**Fixed Spine** — identical format in every issue. Lock it now; changing it later breaks comparability.
**Flex** — structure is consistent, but angle, emphasis, and which sub-questions get airtime depend on the market.
**Conditional** — runs only when data supports it.

**Reading order:** Verdict → Act 1 → Act 2 → Act 3 → Act 4. Data Take sidebars placed wherever they fit best editorially.

The three intelligence frames — **Character**, **Livability**, and **Opportunity** — are not section headers. They are the analytical lenses that organize which KPIs belong to each cluster of the radar. Within Acts 2–4, they inform which questions to prioritize, but the story follows the data.

**This document is a living playbook.** The fixed spine sections are settled; the flex sections describe what we know works so far. As we work more markets, new angles, methods, and section types will get added. When something proves out in a market, it gets documented here so subsequent markets can inherit it.

---

## Opening: The Market Verdict

**Type:** Report | FIXED SPINE | Written last, placed first.

**Core question:** What is this place and why does it matter right now?

A 3 to 4 sentence thesis: market archetype, trajectory, headline risk or opportunity. Every claim must be traceable to a section. This makes the piece skimmable and gives it an argument rather than a tour of charts.

**Template:**
> [Metro] is a [archetype descriptor] market that is [trajectory statement]. Its economy runs on [top specializations], with [headline exposure or tailwind]. The opportunity: [corridor or trend-based thesis].

---

# Act 1: Identity

**Core question:** What is this place?

Act 1 establishes the market's fundamental character — where it stands nationally, why it exists, and who it resembles. The goal is orientation, not depth. Depth comes in Acts 2 and 3.

*Sections in this act are largely settled. The KPI selection within the radar and the peer comparison angle are the main per-market decisions.*

---

## Section 1: Market Fingerprint

**Type:** Report | FIXED SPINE

**Job:** Anchor how this market sits nationally in one visual — across character, livability, and opportunity dimensions simultaneously.

**Presentation:**
- Radar chart of 6 to 8 KPIs, percentile-normalized against the national CBSA distribution
- KPIs are drawn from the three intelligence frames: **2 to 3 from Character, 2 to 3 from Livability, 2 to 3 from Opportunity**
- **Axis order is locked across all issues** so shapes become comparable series to series
- National median polygon as a reference overlay
- One-line verdict sentence directly under the chart
- Compact table below: KPI, raw value, national percentile, national rank

**Top-line stat boxes** (above or alongside the radar — fixed across every issue):
- Total population
- Income per capita
- GDP (or GMP)
- Life expectancy
- Region / CBSA classification
- **Intelligence Framing Cluster** (the cross-frame k-means label from Phase 5: e.g., "High-Wage Stable Growth")

**Method:**
- Pull from existing Gold layer KPIs already used in Character, Livability, and Opportunity frame calibration
- Select per-frame KPIs that best reveal this market's shape relative to national peers — the selection is per-market but the axis slots are locked
- Orient all axes so outward = "more of the trait," not "better"; avoid value judgments baked into geometry
- Percentile-rank against all ~400 CBSAs

**Deliverable:** Top-line boxes + radar + verdict line + percentile table. Nothing else. Resist additions.

**Open decision for issue 1:** Final KPI selection and axis order. This propagates through every future issue; decide deliberately.

---

## Section 2: History Box

**Type:** Report | FLEX

**Job:** Find the founding logic of this place and test whether it still shows in the data.

**The one analytical question:** Does the founding reason for the city (port, rail junction, resource extraction, state capital, military base) still appear in the present-day industry mix, built form, or cultural identity?
- If yes: one forward link to the section where that founding logic shows up (e.g., "the port still drives X% of employment — see Section 4")
- If no: that is also a finding — a market that outgrew its origin story

**Format:** 150 to 250 word boxed narrative. Source from city website, Wikipedia, or regional histories. This is editorial, not analytical.

**Cut rule:** History that explains present data stays. History that doesn't, gets cut.

---

## Section 3: Peer Markets

**Type:** Analysis | FLEX

**Core questions:**
1. Who are this market's five nearest structural peers?
2. On which dimensions does the closest peer diverge most — and what does that divergence signal?
3. Is any peer plausibly "this market in five years"?

**Method:**
- Cosine similarity on z-scored Gold KPI vectors (or intelligence frame scores)
- Run on **levels** (structural similarity) and on **trend slopes** (trajectory similarity)
- Forward-analog check: does a trajectory-peer sit further along in levels? If so, it is a candidate future state and the section's editorial payoff
- PCA before similarity is optional; document the choice either way

**Presentation:**
- Small table: peer, similarity score, biggest similarity dimension, biggest divergence dimension
- One paired comparison chart (dumbbell or dual radar) against the single most instructive peer only — not all five
- Forward-analog paragraph if one credibly exists

**Deliverable:** Peer table + one comparison chart + forward-analog paragraph (if warranted).

---

# Act 2: Engine and Fabric

**Core question:** What drives this place, and what does life here actually look like?

Act 2 has three sides. The first is economic — what does this market specialize in, how does it fit into the broader regional and national economy, and what is exposed? The second is the commute and migration geography — how does the market connect to and draw from the region around it? The third is the physical and cultural fabric — what does the built environment look like and what kind of place is this to live in? Together they answer why someone would work, live, or invest here.

*The industry and exposure analysis is settled as fixed spine. The regional role framing and cultural fabric sections are newer additions — expect the methods and presentation to develop as we work more markets.*

---

## Section 4: Industry Makeup and Regional Role

**Type:** Analysis | FIXED SPINE (quadrant chart + exposure scorecard)

**This is the analytical heart of the issue.**

**Core questions:**
1. What is this market disproportionately good at?
2. Are those specializations growing or fading?
3. What role does this market play in its broader region and state economy? Is it a supplier, an attractor, a bedroom community, a logistics node?
4. Where do people actually go to work — and where do they come from?
5. What is exposed — to automation, to policy shifts, to trade?

**Method:**
- Location quotients by NAICS from QCEW; flag LQ > 1.25 as specializations
- Plot LQ (x) against employment growth (y): four quadrants — rising stars, mature strengths, emerging bets, declining legacies. This is the section centerpiece.
- LEHD LODES origin-destination flows: inflow/outflow ratio, top origin and destination tracts, or a job center map. High inflow = regional attractor; high outflow = bedroom community; balanced = self-contained. The ratio is a one-number summary of the market's regional role.
- IRS migration flows or ACS migration data: where are people coming from and going? Net migration by origin state or region tells you whether this market is gaining or losing population to peers.
- Exposure scorecard: rows = major industries (top 8 to 10 by employment share); columns = employment share, AI exposure index (Felten et al., Webb, or equivalent — cite explicitly), policy sensitivity flags (trade dependence, federal share, port reliance, rate sensitivity)

**Regional role framing:** The commute and migration data together answer "how does this market fit into the region?" A market that imports workers but exports residents is a different story than one that does both. Name the role explicitly — it becomes part of the market's identity.

**Summary target:** A single sentence on exposure ("X% of employment sits in high-exposure industries") and one on regional role ("Richmond draws X% of its workforce from outside the CBSA and exports net Y residents to Northern Virginia").

**Deliverable:** LQ quadrant chart + exposure scorecard + regional role paragraph + summary sentences. (Quadrant chart and scorecard are fixed spine; commute and migration treatment is flex.)

---

## Section 5: Built Environment and Social Fabric

**Type:** Report with embedded analysis | FLEX

Act 2's second side. The physical and cultural structure of the market — infrastructure, access, and the social institutions and amenity draw that make this place itself.

**Built environment (report):**
- Map the physical structure: highways, rail, transit, airports, ports from OpenStreetMap/Overpass
- POI layers: parks, groceries, hospitals, cultural venues
- Per-zone amenity access score: share of population within threshold distance of transit, groceries, parks — **carry this score forward into Section 9 (Corridors)**

**Social and cultural fabric (flex narrative):**
- What are the dominant social institutions? (universities, hospitals, military, religious anchors, civic organizations)
- What is the cultural identity — arts, food, sports, regional character?
- What does this place attract in terms of tourism, conventions, or talent migration?
- Does the founding identity from Section 2 still show up here?

The built and social halves inform each other. A walkable downtown with no cultural draw reads differently than one with a thriving food and arts scene. The analysis should reflect that.

**Key analytical question:** Do amenity-rich zones and investment-scored zones overlap or diverge?
- Overlap confirms the investment score
- Divergence is often the more interesting finding — amenity-rich but low-scored zones are potential mispricing candidates

**Presentation:** Infrastructure + POI map, amenity-vs-score scatter or bivariate map, short cultural fabric narrative (2 to 3 paragraphs or boxed sidebar).

**Deliverable:** Metro map + amenity score by zone + overlap/divergence finding + cultural fabric summary.

---

# Act 3: Dynamics

**Core question:** How is this market changing, and what does that change mean?

Act 3 is about time. Where has this market been accelerating or decelerating relative to national trends? What internal dynamics — within the metro — are reshaping the economic and demographic picture? And how does all of that fit into the broader regional story?

*The converging/diverging/inflecting framing and the small-multiples format are settled. Which series lead and how much regional context to include are per-market calls. The Data Take sidebar is intentionally open — it will become whatever the data makes interesting.*

---

## Section 6: Trend Analysis

**Type:** Analysis | FLEX

**Framing rule:** Every trend gets classified as one of three answers:
1. **Converging** to the national trend
2. **Diverging** from the national trend
3. **Inflecting** — slope changed sign or magnitude in the last 2 to 3 years

This framing prevents the section from becoming "here are some line charts."

**Core questions:**
- What is accelerating or decelerating relative to national peers?
- Where is the market leading, where is it lagging?
- How does the regional context shape what's happening? (Is this a metros-within-a-growing-region story, or a metros-bucking-a-regional-decline story?)
- What do the internal dynamics suggest is coming next?

**Method:**
- Sources: ACS vintages, Building Permits Survey, FHFA or Zillow HPI, QCEW time series
- Index each series to a common base year; plot metro vs. national
- Flag inflections programmatically (rolling slope comparison); make the strongest inflection the narrative lead
- Regional framing: how do neighboring metros or the broader metro division compare? The regional picture sometimes explains what the national comparison obscures.

**High-value pairing:** Permits vs. population growth. A supply response lagging demand is an investment thesis in a single chart.

**Presentation:** Small multiples, 4 to 6 panels maximum, metro vs. national, inflection points annotated.

**Deliverable:** Small-multiples panel + inflection narrative lead + convergence/divergence classification per series. The section should end with a sentence about what the dynamics collectively suggest for the opportunity funnel in Act 4.

---

## Section 7: Data Take Sidebar

**Type:** Analysis | FLEX, rotating
**Recurring format hook. Visually boxed. Placement flexible within the issue.**

**Question (always the same):** Why is this market weird on X?

**Method:**
- Automated outlier scan: flag every Gold KPI where the metro sits in the national top or bottom decile
- Hand-pick one or two that are **surprising given the market's archetype** — a cheap market being cheap is not a Data Take; a cheap market with top-decile income growth is

**Presentation:** One chart, roughly 100 words, boxed. Strict budget keeps ad hoc analysis bounded.

A Data Take that recurs across multiple markets is a theme candidate — the promotion path to a standalone national piece or a recurring spine element.

**Deliverable:** One to two boxed sidebars per issue.

---

# Act 4: Opportunity Funnel

**Core question:** Where are the specific opportunities within this market, and for whom?

Act 4 zooms in. It takes everything Act 1–3 established about the metro's character, economy, and trajectory and translates it into a sub-market picture — where people live, where business activity concentrates, where the investment thesis is most legible. The goal is analytical precision: not "this city has opportunity" but "this corridor, this zone type, under these conditions."

*Zone archetypes and corridor stat blocks are fixed spine. The zone construction methodology is still being decided — issue 1 will settle it. Parcel Watch is conditional on data availability.*

---

## Section 8: Zone Archetypes

**Type:** Report | FIXED SPINE (composition bar)

**Job:** Report the market's zone composition using the established clustering methodology, and benchmark it against the series.

**Core questions:**
- What mix of zone types does this market contain?
- How does that mix compare to other markets run so far?
- What does the composition itself suggest about opportunity concentration?

**Presentation:**
- Choropleth of zones colored by archetype
- Composition bar: percent of zones (or population) by archetype
- **Benchmark against the average across all metros run to date** — the benchmark converts a legend into a finding: "an unusually high share of transitioning zones" is a story

**Archetype naming rule:** Labels are durable and reused across every metro. Readers build pattern recognition issue to issue. Never rename per market.

### Zone Construction Methodology

Zones are spatial groupings of tracts. Three candidate approaches, all compatible with existing tract clustering work to varying degrees.

**Option A: DBSCAN over tract cluster assignments (current approach)**
- Groups spatially dense runs of same-archetype tracts into zones using density-based clustering on tract centroids
- Full reuse of existing tract labels; noise labeling filters isolated tracts
- Weakness: eps is distance-based while tract geometry varies urban to suburban — requires per-metro recalibration. Make recalibration rule-based (e.g., eps = fixed multiple of the metro's median 4th-nearest-neighbor centroid distance), not eyeballed

**Option B: HDBSCAN (recommended first candidate)**
- Hierarchical density-based clustering; handles varying density natively without eps
- Near drop-in replacement for Option A; same two-step architecture, same archetype vocabulary
- Weakness: centroid-based, no true contiguity guarantee; noise points require deliberate handling

**Option C: SKATER (spatially constrained regionalization)**
- Builds a minimum spanning tree over the tract contiguity graph, then prunes into contiguous regions
- True contiguity guarantee; no density parameters
- Weakness: requires specifying number of regions per metro; bypasses existing cluster assignments as direct input

**Decision guidance:** Ranked HDBSCAN, rule-calibrated DBSCAN, SKATER. Diagnose any prior contiguity-based failure mode before re-attempting; stringy zones and single-tract fragments have cheap fixes (rook adjacency, minimum zone size) while cross-barrier merges point back toward density methods. Ship whichever produces sensible zones for issue 1; document the choice and parameters in the methodology note.

**Deliverable:** Archetype choropleth + benchmarked composition bar + one-paragraph composition story.

---

## Section 9: Zone Corridors

**Type:** Analysis | FIXED SPINE (stat block format)

**The payoff section.**

**Core questions (per corridor):**
1. What defines it spatially — which arterial, which transit line?
2. What archetype mix does it contain?
3. What is the trend direction of its tracts?
4. What is the catalyst or risk — and for what kind of investor or operator?

**Method:**
- Corridors = contiguous zones clearing an Investment Score threshold, aligned along infrastructure from Section 5
- Cross-reference amenity score from Section 5: corridors combining rising scores with amenity access (or amenity mispricing) are the strongest theses
- Consider cultural fabric from Section 5: an emerging corridor adjacent to an arts district or anchor institution reads differently than a purely residential one
- Name each corridor; names are editorial assets

**Presentation:** 2 to 4 corridors, each with:
- A zoomed map crop
- A **standardized stat block:** zone count, population, Investment Score range, dominant archetype, trend direction, one-line thesis

The stat block format matters more than any single analysis. It makes corridors comparable across issues and builds format credibility.

**Deliverable:** 2 to 4 named corridors with map crops and stat blocks.

---

## Section 10: Parcel Watch

**Type:** Analysis | CONDITIONAL (runs only when county parcel data supports it)

**Core question:** Within the top corridor, which specific parcels are underutilized relative to their zone?

**Method:**
- Source: Regrid or county open data, scoped to top corridor(s) only
- Screen: improvement-to-land assessed value ratio below corridor median, filtered by permissive use codes
- Sanity-check against area trend direction from Section 6

**Presentation:** Table of 5 to 10 parcels (address/APN, use code, improvement-to-land ratio, zone archetype) + corridor map with parcels marked.

**Fallback:** When parcel data doesn't support this section, end at corridors with a short "further exploration" note. Consistent quality beats forced completeness.

**Deliverable:** Parcel screen table + map, or the fallback note.

---

## Fixed Spine Summary

These elements appear in identical format in every issue:

| Element | Section |
|---|---|
| Market Verdict (3 to 4 sentences) | Opening |
| Top-line stat boxes (population, income, GDP, life expectancy, region, Intelligence Cluster) | 1 |
| Fingerprint radar, locked axis order + percentile table | 1 |
| LQ quadrant chart + exposure scorecard | 4 |
| Benchmarked zone composition bar | 8 |
| Corridor stat blocks | 9 |

Everything else flexes by market. The spine is what turns individual deep dives into a comparable series.

---

## Shared Engines (Build Once)

1. **Distance engine:** z-scored feature vectors + cosine similarity. Serves Section 3 (metro peers) and underpins cluster interpretation in Section 8.
2. **Spatial layer:** OSM/Overpass ingestion + adjacency graph + per-zone spatial metrics. Serves Sections 5, 8, and 9.
3. **Time series engine:** indexed metro-vs-national series + inflection detection. Serves Sections 6, 7, and trend inputs to 9.

---

## Issue 1 Checklist

- [ ] Lock fingerprint KPI selection and radar axis order (2 to 3 per frame; propagates to all future issues)
- [ ] Confirm archetype names are final before publishing (renaming later breaks series continuity)
- [ ] Write the exposure scorecard NAICS-to-index mapping once; cite source explicitly; reuse forever
- [ ] Define the Investment Score threshold for corridor qualification and document it
- [ ] Draft the corridor stat block template
- [ ] Verify parcel data availability for the chosen metro before promising Section 10
- [ ] Write the Market Verdict last; check every claim traces to a section
