# Metro Deep Dive: Template Guidance

**Patterns in Place** | Format guidance for Metro Deep Dive issues
**Version:** 1.0 | For use on the first deep dive and refinement thereafter

---

## How to Use This Document

Each section below specifies its **type** (Analysis or Report), the **questions to answer** or the **most effective presentation**, the **method**, and the **deliverable**. Sections marked FIXED SPINE appear in identical format in every issue. Sections marked FLEX can adapt to the market. Sections marked CONDITIONAL run only when data supports them.

**Reading order of the issue:** Verdict, then Acts 1 through 4, with the Data Take sidebar placed wherever it fits best editorially.

---

## Opening: The Market Verdict

**Type:** Report | FIXED SPINE
**Written last, placed first.**

A 3 to 4 sentence thesis covering: market archetype, trajectory, headline risk, headline opportunity. Every claim in the verdict must be defended somewhere in the issue. This is what makes the piece skimmable and gives it a spine of argument rather than a tour of charts.

**Template:**
> [Metro] is a [archetype descriptor] market that is [trajectory statement]. Its economy runs on [top specializations], which face [headline exposure]. The opportunity: [corridor or trend-based thesis].

---

# Act 1: Identity

## Section 1: Market Fingerprint

**Type:** Report | FIXED SPINE

**Job:** Anchor how the market sits nationally in one visual.

**Presentation:**
- Radar chart of 6 to 8 KPIs, percentile-normalized against the national CBSA distribution
- **Axis order is locked across all issues** so shapes become comparable series to series
- Overlay the national median polygon as a reference shape
- One-line verdict sentence directly under the chart (the chart anchors, the sentence interprets)
- Compact table below: KPI, raw value, national percentile, national rank

**Method:**
- Select one to two KPIs per Gold pillar (Economics, Population, Affordability, Housing)
- Percentile rank each against all CBSAs; orient all axes so outward = "more of the trait," not "better" (avoid value judgments baked into geometry)

**Deliverable:** Radar + verdict line + percentile table. Nothing else. Resist additions.

**Open decision for issue 1:** Final KPI selection and axis order. This propagates through every future issue; decide deliberately.

---

## Section 2: History Box

**Type:** Report | FLEX

**Job:** Find the founding economic logic and test whether it still shows in the data.

**Presentation:** A 150 to 250 word boxed narrative, not a full section. Source from the city website or Wikipedia.

**The one analytical question:** Does the founding reason for the city (port, rail junction, resource, state capital) still appear in the present-day industry mix or built form?
- If yes: one forward link ("the port still drives X% of employment, see Section 4")
- If no: that is also a finding, a market that outgrew its origin story

**Cut rule:** History that explains present data stays. History that does not gets cut.

---

## Section 3: Peer Markets

**Type:** Analysis | FLEX

**Questions to answer:**
1. Who are the five nearest markets in KPI space?
2. On which dimensions does the closest peer diverge most?
3. Is any peer plausibly "this market five years from now"?

**Method:**
- Cosine similarity on z-scored Gold KPI vectors
- Run twice: once on **levels** (structural similarity) and once on **trend slopes** (trajectory similarity)
- The forward-analog check: does a trajectory-peer sit further along in levels? If so, it is a candidate future state and the section's editorial payoff
- Optional: PCA before similarity to decorrelate related KPIs; document the choice either way

**Presentation:**
- Small table: peer, similarity score, biggest similarity, biggest difference
- One paired comparison chart (dumbbell or dual radar) against the single most instructive peer only, not all five

**Deliverable:** Peer table + one comparison chart + forward-analog paragraph if one exists.

---

# Act 2: Engine and Fabric

## Section 4: Industry Makeup

**Type:** Analysis | FIXED SPINE (quadrant chart + exposure scorecard)
**This is the analytical heart of the issue.**

**Questions to answer:**
1. **What is this market disproportionately good at?** Location quotients by NAICS from QCEW; flag LQ > 1.25 as specializations.
2. **Are the specializations growing or dying?** Plot LQ (x) against employment growth (y). Four quadrants: rising stars, mature strengths, emerging bets, declining legacies. This is the section centerpiece; it answers two questions in one chart.
3. **Where do people actually go to work?** LEHD LODES origin-destination flows. Present as a job center map, or defer mapping and report inflow/outflow ratio and top destination tracts.
4. **What is exposed?** Concentration-times-exposure scorecard.

**Exposure scorecard method:**
- Rows: major industries (top 8 to 10 by employment share)
- Columns: employment share, AI exposure (map NAICS to a published index such as Felten et al. or Webb), policy sensitivity flags (trade dependence, federal employment share, port reliance, rate sensitivity)
- Drive toward a single summary sentence: "X% of employment sits in high-exposure industries"

**Presentation:** Quadrant chart (centerpiece), heat-style scorecard table, one paragraph on commute geography.

**Deliverable:** LQ quadrant chart + exposure scorecard + summary exposure sentence.

---

## Section 5: Built Environment

**Type:** Report with one embedded analysis | FLEX

**Job (report):** Map the physical structure of the market.
- Base layers from OpenStreetMap via Overpass API: highways, rail, transit, airports, ports
- POI layers: parks, groceries, hospitals, cultural venues

**Job (analysis):** Convert the map into a livability finding.
- Compute per-zone amenity access: share of population within threshold distance of transit, groceries, parks
- Produce a per-zone amenity score; **carry this score into Section 9 (Corridors)**

**Question to answer:** Do amenity-rich zones and investment-scored zones overlap or diverge?
- Overlap confirms the score; **divergence is the more interesting finding** (amenity-rich but low-scored zones are potential mispricing and future corridor candidates)

**Presentation:** One clean infrastructure + POI map, one amenity-vs-score scatter or bivariate map, short interpretation paragraph.

**Deliverable:** Metro map + amenity score by zone + overlap/divergence finding.

---

# Act 3: Dynamics

## Section 6: Trend Analysis

**Type:** Analysis | FLEX

**Framing rule:** Every trend must be classified as one of three answers:
1. **Converging** to the national trend
2. **Diverging** from the national trend
3. **Inflecting** (slope changed sign or magnitude in the last 2 to 3 years)

This framing prevents the section from becoming "here are some line charts."

**Method:**
- Sources: ACS vintages, Building Permits Survey, FHFA or Zillow HPI, QCEW time series
- Index each series to a common base year; plot metro vs. national
- Flag inflections programmatically (rolling slope comparison) and make the strongest inflection the narrative lead

**High-value pairing:** Permits vs. population growth. A supply response lagging demand is an investment thesis in a single chart.

**Presentation:** Small multiples, 4 to 6 panels maximum, metro line vs. national line, inflection points annotated.

**Deliverable:** Small-multiples panel + inflection narrative lead + convergence/divergence classification per series.

---

## Section 7: Data Take Sidebar

**Type:** Analysis | FLEX, rotating
**Recurring format hook, visually boxed as a sidebar. Placement flexible within the issue.**

**Question (always the same):** Why is this market weird on X?

**Method:**
- Automated outlier scan: flag every Gold KPI where the metro sits in the national top or bottom decile
- From the flagged list, hand-pick one or two that are **surprising given the market's archetype** (a cheap market being cheap is not a Data Take; a cheap market with top-decile income growth is)

**Presentation:** One chart, roughly 100 words, boxed. Strict budget keeps ad hoc analysis bounded.

**Deliverable:** One to two boxed sidebars per issue.

---

# Act 4: Opportunity Funnel

## Section 8: Zone Archetypes

**Type:** Report | FIXED SPINE (composition bar)

**Job:** Report the composition of the market's zones using the established methodology (tract clustering + spatial grouping into zones).

**Presentation:**
- Choropleth of zones colored by archetype
- Composition bar: percent of zones (or population) by archetype
- **Benchmark the composition against the average across all metros run to date.** The benchmark is what converts a legend into a finding: "an unusually high share of transitioning zones" is the story

**Archetype naming rule:** Cluster labels are durable and reused across every metro (e.g., established affluent, transitioning, industrial, student-adjacent). Readers build pattern recognition issue to issue; never rename per market.

### Zone Construction Methodology: Three Candidate Approaches

Zones are spatial groupings of tracts. Three viable methods, all compatible with the existing tract clustering work to varying degrees. Decision pending review of issue 1 results.

**Option A: DBSCAN over tract cluster assignments (current approach)**
- **How it works:** Density-based clustering on tract centroids, run within each archetype label, groups spatially dense runs of same-archetype tracts into zones.
- **Ties to existing work:** Full reuse. Consumes tract cluster labels directly; archetype vocabulary carries through unchanged.
- **Strengths:** Already built; noise labeling filters isolated one-off tracts, which can be a feature.
- **Weaknesses:** eps is distance-based while tract geometry varies urban-to-suburban, so a single eps over-merges dense cores and fragments the periphery. Requires per-metro recalibration.
- **If used:** Make recalibration rule-based, not eyeballed. Example: eps = fixed multiple of the metro's median 4th-nearest-neighbor centroid distance, or the k-distance elbow. The parameter differs per market but the procedure is identical everywhere, which preserves cross-metro comparability and defensibility.

**Option B: HDBSCAN (recommended first candidate)**
- **How it works:** Hierarchical density-based clustering; extracts clusters across varying density levels, eliminating eps entirely.
- **Ties to existing work:** Near drop-in replacement for Option A. Same two-step architecture, same tract cluster labels as input, same archetype vocabulary. `hdbscan` library or sklearn's HDBSCAN.
- **Strengths:** Handles varying density natively, so dense urban cores and sparse suburbs are treated correctly within the same metro, which is exactly the geometry problem with Option A. min_cluster_size transfers across markets far better than eps.
- **Weaknesses:** Still centroid-based (no true contiguity guarantee); still produces noise points to handle deliberately.

**Option C: SKATER (spatially constrained regionalization)**
- **How it works:** Builds a minimum spanning tree over the tract contiguity graph weighted by feature dissimilarity, then prunes into contiguous regions. Clusters and regionalizes in one step.
- **Ties to existing work:** Partial. Replaces the assignment step rather than consuming cluster labels, but reuses the same standardized feature matrix (`spopt.region.Skater` on the existing GeoDataFrame). Archetype vocabulary survives via post-hoc labeling: tag each region by its dominant tract archetype. Tighter variant: feed SKATER the tracts' distances to existing cluster centroids instead of raw features, making regions homogeneous in archetype space.
- **Strengths:** True contiguity guarantee; no density parameters; statistically principled regions.
- **Weaknesses:** Requires specifying the number of regions per metro, trading the eps problem for an n_clusters problem. Bypasses the existing cluster assignments as direct input.

**Decision guidance:** Ranked HDBSCAN, rule-calibrated DBSCAN, SKATER. Prior contiguity-based attempts in JAX had issues (specifics not documented); when revisiting, diagnose the failure mode first, since stringy zones and single-tract fragments have cheap fixes (rook adjacency, minimum zone size) while merging across barriers like rivers or highways points back toward density methods. Ship whichever produces sensible zones for issue 1; document the choice and parameters in the methodology note.

**Deliverable:** Archetype choropleth + benchmarked composition bar + one-paragraph composition story.

---

## Section 9: Zone Corridors

**Type:** Analysis | FIXED SPINE (stat block format)
**The payoff section.**

**Questions to answer, per corridor:**
1. What defines it spatially (which arterial, which transit line, from Section 5)?
2. What archetype mix is it (from Section 8)?
3. What is the trend direction of its tracts (from Section 6)?
4. What is the catalyst or risk?

**Method:**
- Corridors = contiguous zones clearing an Investment Score threshold, aligned along infrastructure from Section 5
- Cross-reference the amenity score from Section 5: corridors combining rising scores with amenity access (or amenity mispricing) are the strongest theses
- Name each corridor; names are editorial assets

**Presentation:** 2 to 4 corridors, each with:
- A zoomed map crop
- A **standardized stat block:** zone count, population, Investment Score range, dominant archetype, trend direction, one-line thesis

The standardized stat block matters more than any single analysis. It makes corridors comparable across issues and builds format credibility.

**Deliverable:** 2 to 4 named corridors with map crops and stat blocks.

---

## Section 10: Parcel Watch

**Type:** Analysis | CONDITIONAL (runs only when county parcel data supports it)

**Question:** Within the top corridor, which parcels are underutilized relative to their zone?

**Method:**
- Source: Regrid or county open data, scoped to top corridor(s) only
- Screen: improvement-to-land assessed value ratio below the corridor median, filtered by permissive use codes
- Sanity-check against area trend direction from Section 6

**Presentation:** Table of 5 to 10 parcels (address/APN, use code, improvement-to-land ratio, zone archetype) + a corridor-level map with parcels marked.

**Fallback:** When data does not support this section, end the issue at corridors with a short "further exploration" note. Consistent quality beats forced completeness.

**Deliverable:** Parcel screen table + map, or the fallback note.

---

## Fixed Spine Summary

These elements appear in **identical format in every issue**:

| Element | Section |
|---|---|
| Market Verdict (3 to 4 sentences, top of issue) | Opening |
| Fingerprint radar, locked axis order + percentile table | 1 |
| LQ quadrant chart + exposure scorecard | 4 |
| Benchmarked zone composition bar | 8 |
| Corridor stat blocks | 9 |

Everything else flexes by market. The spine is what turns individual deep dives into a comparable series.

---

## Shared Engines (Build Once)

Three reusable components cover most of the analytical work:

1. **Distance engine:** z-scored feature vectors + cosine similarity. Serves Section 3 (metro peers) and underpins cluster interpretation in Section 8.
2. **Spatial layer:** OSM/Overpass ingestion + adjacency graph + per-zone spatial metrics. Serves Sections 5, 8, and 9.
3. **Time series engine:** indexed metro-vs-national series + inflection detection. Serves Sections 6, 7, and trend inputs to 9.

---

## Issue 1 Checklist

- [ ] Lock fingerprint KPI selection and radar axis order (propagates to all future issues)
- [ ] Confirm archetype names are final before publishing (renaming later breaks series continuity)
- [ ] Write the exposure scorecard NAICS-to-index mapping once; reuse forever
- [ ] Define the Investment Score threshold for corridor qualification and document it
- [ ] Draft the corridor stat block template
- [ ] Verify parcel data availability for the chosen metro before promising Section 10
- [ ] Write the Market Verdict last; check every claim traces to a section