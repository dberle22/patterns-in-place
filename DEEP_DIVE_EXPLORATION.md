# Metro Deep Dive + Intelligence — Exploration Questions

*A working doc for the thinking we want to do before building. These are questions, hypotheses, and ideas to explore — not specs. The goal of this exploration is to emerge with: a clear Intelligence Framework definition, a report structure we're excited about, and a first market to publish.*

---

## Part 1 — What Is a Metro Deep Dive?

Before we decide what to build, we need to be sharp on what makes a Metro Deep Dive worth reading. These are the framing questions.

### Who reads it and why?

The report serves multiple potential audiences with different needs:

- **The curious researcher / data nerd:** Wants to understand how a city actually works — not just the headline stats, but the structural patterns underneath. Wants to be surprised by something.
- **The investor or operator:** Evaluating a market for a specific decision (where to open, where to invest, where to hire). Wants benchmarks and momentum signals.
- **The person who lives there or wants to:** Wants to understand the place they're in or considering. Wants the data to confirm or challenge their intuition.

**Question to settle:** Is there a primary audience, or are we writing for all three? The answer shapes what we lead with and how much we explain.

### What makes it different from a Wikipedia article or a real estate report?

Most market reports are either (a) surface-level demographic summaries with no analytical spine, or (b) narrowly investor-focused with no cultural or qualitative depth. What we have that they don't:

- Three intelligence frames that create a structured vocabulary for analyzing any market (Character / Livability / Opportunity)
- A spatial layer that connects neighborhood-level patterns to metro-level narratives
- A comparative framework — every metric is benchmarked against peers and national, not presented in isolation
- An analytical point of view — we're willing to say something definitive, not just present data

**Question to settle:** What is the "so what" of a Metro Deep Dive? After reading it, what should the reader know or be able to do that they couldn't before?

### What's the right length and format?

Options on the spectrum:
- **Short-form Substack post** — 800–1,200 words, 3–5 charts, one focused thesis. Fast to produce, shareable. Loses depth.
- **Long-form Substack piece** — 3,000–5,000 words, 10–15 charts, section-by-section walkthrough. Newsletter-style. Good for the first few reports while methodology is being established.
- **PDF report** — Traditional format, shareable as a document. Better for an investor or researcher audience. More work to lay out well.
- **Interactive Streamlit document** — Rich but requires deployment infrastructure. Higher effort; better for Phase 2.

**Question to settle:** What's the first format? Probably long-form Substack for the first report — iterating on format is easier than iterating on methodology.

---

## Part 2 — The Intelligence Framework

The three frames are the analytical spine of everything. Before we build anything, we need working definitions that we actually believe in. This section is where we explore what they should be.

### Character — Who is this place?

Character is the most qualitative frame and the hardest to score. It's trying to answer: what does it feel like to be in this place, and what makes it distinct?

**Current approach:** Demographic profile types (archetypes) derived from a cluster model. Labels like "Young & Diverse," "Established Families," "Creative Class."

**Things to explore:**
- Are demographic archetypes the right unit, or is there a better way to characterize a place? What does a "Creative Class" CBSA actually look like vs. a "College Town" — are those distinguishable in the data, or do they blur together?
- What's the relationship between demographic character and cultural character? A place can be demographically similar to another but feel totally different. How much of that is captured in the data vs. requiring the POI/cultural layer?
- At CBSA grain, what metrics produce the most interesting and defensible differentiation? Diversity index, median age, share foreign-born, education attainment, net migration composition — which of these actually split CBSAs into coherent groups?
- Is "Character" a score at all, or is it fundamentally a label / taxonomy? A Young & Diverse metro doesn't have a "higher Character score" than an Established Families metro — they're just different. How do we handle a frame that isn't naturally ordinal?
- What are the 5–8 Character archetypes that feel right at CBSA grain? (vs. NTA grain, which Stoop uses) The labels from the NTA-level work may not translate directly to metro scale.

**Hypotheses to test:**
- High diversity index + young median age + high share foreign-born → "Immigrant Gateway" or similar
- High college attainment + young median age + high net in-migration of young adults → "Creative Class / Knowledge Hub"
- Low diversity + older median age + low migration + high homeownership → "Established / Rooted"
- High college enrollment relative to population → "College Town"

**Data gaps that affect Character at CBSA grain:** POI/cultural layer not yet available at national scale. Character scoring at CBSA grain will be purely demographic until the per-market Points framework is built.

---

### Livability — Is this a good place to live?

Livability is about quality of daily life. The question: can you afford to live here, and is the day-to-day experience good?

**Proposed sub-dimensions:**
1. **Affordability** — housing cost burden, rent-to-income, home price relative to income; most data-rich dimension
2. **Health** — life expectancy, chronic disease rates, mental health, physical inactivity (CHR now live)
3. **Safety** — injury deaths, violence outcomes (CHR covers this; city-level crime data is per-market only)
4. **Mobility & Built Environment** — commute times, transit access, walkability (ACS commute data live; EPA SLD not yet)
5. **Education access** — HS graduation, college access (CHR + ACS; K-12 quality not yet available at national grain)

**Things to explore:**
- Is Livability a single score or a dashboard of sub-scores? A metro can be highly affordable but have poor health outcomes (e.g., some Midwest markets). Collapsing to a single score risks losing the most interesting tension.
- How do we weight affordability vs. other dimensions? Affordability is the most data-rich and the most legible to a general audience, but a Livability score dominated by affordability is basically just an affordability score.
- Where does Livability end and Opportunity begin? Income growth improves livability (you can afford more) but it's primarily an Opportunity signal. The frames should tell different stories; if they're highly correlated, one is redundant.
- What's the natural peer group for Livability benchmarking? A Sun Belt market looks worse on affordability if you benchmark it against the Midwest, better if you benchmark against coastal cities. How do we frame benchmarks honestly?

**Hypotheses to test:**
- The Livability / Opportunity tradeoff is real and visible in the data: high-Opportunity metros (fast-growing, high-income) tend to have worse Livability (expensive, congested). Scatter plot this.
- There are "hidden Livability winners" — affordable metros with good health outcomes and decent labor markets that never make the national narrative. Finding these is publishable.
- The health dimension creates the most geographic surprises — Southern states often look strong on other Livability dimensions but weak on health outcomes.

**Data gaps:** EPA SLD (walkability/transit built environment) not yet ingested. Absence makes mobility scoring thin — commute time from ACS is a weak proxy for actual transit access.

---

### Opportunity — Is this a place where things are happening?

Opportunity is about momentum and potential. The question: is this a market where economic conditions are improving, and is there upside?

**Proposed sub-dimensions:**
1. **Resident opportunity** — income growth, wage levels, labor market tightness, poverty trends
2. **Market / investor opportunity** — home price appreciation (FHFA HPI now live), rent growth (Zillow ZORI live), population growth, building permit activity
3. **Business opportunity** — GDP growth, industry mix and specialization (QCEW now live), business formation rates (CBP/BFS not yet)

**Things to explore:**
- Three sub-lenses is a lot. Are they all necessary, or do two of them capture most of the signal? Resident and Market opportunity might move together closely enough that they can be combined.
- What's the right time horizon for Opportunity scoring? A market that was hot 5 years ago but is cooling is very different from one that's just starting to move. Both 1-year and 5-year indicators are needed, but how do we weight them?
- Opportunity Zones: now in the platform. How much analytical weight do they deserve? OZ designation is a policy flag, not a market signal — a tract is designated because it was distressed, not because it's opportunistic. The interesting question is: which OZ tracts have the highest momentum metrics despite their distress designation?
- The QCEW industry data is now live and deep (43M rows, 2010–2024). Industry specialization and concentration are strong Opportunity signals. What does industry mix tell us about a metro's long-run trajectory that income/GDP alone doesn't?
- Does Opportunity work at CBSA grain, or does it only become meaningful at sub-CBSA grain (tract/zip)? A CBSA average might look flat while masking a very hot inner core and a declining periphery.

**Hypotheses to test:**
- Industry mix is the leading indicator that income and GDP growth lag. Markets with growing tech/professional services concentrations in 2015 showed the strongest income growth by 2022. QCEW vs. BEA growth correlation study.
- The "bounce-back" markets — metros with high 2020 distress that recovered fastest — are the most interesting Opportunity story. Who bounced back and why?
- OZ + high momentum = a real signal worth publishing. Find the Opportunity Zone tracts where every metric is moving the right direction.

---

## Part 3 — Report Structure

A proposed section structure for the first Metro Deep Dive. This is a starting point to stress-test.

```
1. The Headline (2–3 paragraphs)
   What's the one thing someone should know about this market?
   What's the tension or surprise that makes this market worth writing about?

2. Market Overview
   - Population and growth (5yr, 10yr)
   - Where it sits nationally: benchmark vs. peers on 4–6 key metrics
   - Peer CBSA selection rationale

3. Character Frame
   - Demographic profile: who lives here
   - Archetype label + what drives it
   - What's changed over 10 years — migration, age shift, diversity trend
   - 2–3 charts

4. Livability Frame
   - Affordability: cost burden, rent-to-income, home price vs. income
   - Health snapshot (CHR)
   - Mobility: commute patterns, transit access (where data allows)
   - 3–4 charts

5. Opportunity Frame
   - Labor market: unemployment, LFPR, wage levels, job growth
   - Economic momentum: GDP growth, income growth, industry mix
   - Housing market: price appreciation, permit activity, rent trends
   - 3–4 charts

6. Zone Analysis
   - Sub-market breakdown at ZCTA or tract grain
   - Which parts of the metro are hot, stable, transitional, distressed?
   - Map + zone profile table

7. The Takeaway
   - What does the full picture add up to?
   - What's the strongest signal for each frame?
   - What to watch next
```

**Questions about this structure:**
- Is a Zone Analysis section required for the first report, or can we publish Phase 1 (Overview + 3 Frames) first and add Zones in Phase 2? Zones require the most methodology work. Might be cleaner to separate.
- How long is each section? Aim for 400–600 words per frame section + 3–4 charts = roughly 3,000–4,000 words total for the full report.
- Does the report need a "methods" appendix, or does that live separately on the platform site?

---

## Part 4 — First Market Selection

The first report sets the template. It should be:
- **Analytically interesting:** Not a generic Sun Belt growth story everyone's already read. There should be a tension or surprise.
- **Data-complete:** Good coverage across all Gold tables. Avoid markets where key BEA/BLS series are sparse.
- **Personally motivating:** Something we're curious about, not just technically convenient.
- **Not too complex:** First report should validate the template, not push all its edges.

**Jacksonville considerations:**
- We have existing ROF work (zone/parcel methodology established)
- But ROF is retail/commercial focused — the Intelligence Frame story hasn't been told for Jacksonville yet
- May feel like "old work" to revisit; might be more motivating to pick something fresh
- Strong case for starting here anyway: data is known, the zone patterns are familiar, and the retail opportunity angle adds a distinctive layer that purely-demographic markets lack

**Candidate market criteria (to evaluate):**
- Population 500K–3M CBSA (large enough to be interesting, small enough to navigate)
- Strong data coverage in Gold (no major BEA/BLS gaps)
- A real tension between the three frames (e.g., high Opportunity but declining Livability, or high Livability but flat Opportunity)
- Either a market we know personally, or one with a strong narrative angle

**Markets worth evaluating first:**
- Jacksonville, FL — existing work, distinctive retail + demographics story
- Nashville, TN — classic growth/affordability tension; well-documented; maybe too obvious
- Richmond, VA — underrated; interesting Character profile; good data coverage
- Raleigh-Durham, NC — strong Opportunity story; knowledge economy transition
- Pittsburgh, PA — "bounce-back" narrative; decline + revival; strong Character history
- Louisville, KY — overlooked Midwest; interesting affordability + health tension
- Salt Lake City, UT — fast growth + unusual demographic Character + policy dimensions

**Question:** Are we picking a market that tells the most interesting story, or one that best stress-tests the template? First report probably needs to do both.

---

## Part 5 — Zone Analysis Deep Dive

Zones are the most technically ambitious part of the report and the most distinctive output. This is where we need the most methodology thinking.

### What is a zone?

A zone is a cluster of census tracts within a metro that share a consistent set of characteristics. The goal is to produce labels that are:
- **Intuitive:** Someone who lives in the market can recognize their neighborhood in the description
- **Actionable:** Useful for investment, site selection, or policy decisions
- **Reproducible:** The same methodology produces consistent results across different markets

### What are we clustering on?

The ROF prototype used retail-specific inputs (vacancy, zoning, parcel characteristics). For the Intelligence Frame approach, the inputs should reflect the full picture:

**Character inputs (who lives here):**
- Demographic composition: diversity index, median age, share foreign-born, education attainment
- Migration: net in-migration rate, population growth

**Livability inputs (what's it like to live here):**
- Affordability: rent-to-income, cost burden rate, home value relative to income
- Density and built form: housing unit density, housing age (stock vintage)

**Opportunity inputs (what's happening here):**
- Economic momentum: income growth, poverty rate change
- Housing market: home price appreciation, permit activity
- Labor: employment density, industry mix

**Open questions:**
- Which inputs should dominate? Character-heavy clustering produces demographic archetypes. Opportunity-heavy clustering produces investment heat maps. Both are interesting but they're different products.
- Should zones be defined independently per market, or should we aim for a consistent national zone taxonomy that applies across all markets? National consistency is more powerful for comparison; per-market is more precise.
- How many zone types? The ROF used 4–5 types. 6–8 feels like the right range for a full Intelligence Frame zone model.
- What are the zone type labels? Draft set to evaluate:
  - **Core Hub** — dense, diverse, high-activity urban core
  - **Established Residential** — stable, owner-occupied, slow-changing
  - **Transitional / Emerging** — demographic shift, rising prices, mixed signals
  - **Affordable Fringe** — lower cost, lower income, accessible to workforce
  - **Knowledge / Creative Corridor** — high education, office/lab uses, younger population
  - **Growth Periphery** — fast-growing suburban, new construction, family-oriented
  - **Distressed** — declining population, high poverty, disinvestment signals

**Methodology options:**
- K-means clustering on standardized tract-level metrics (simple, interpretable)
- Hierarchical clustering (better for discovering natural group count)
- Latent class analysis (probabilistic; better handles mixed data types)
- The ROF used a scoring + threshold approach (rule-based rather than statistical) — simpler but less generalizable

---

## Part 6 — Content and Writing Ideas

Findings from Deep Dive work that could become standalone posts:

- **The Livability / Opportunity tradeoff:** Are the markets with the best economic momentum also the hardest places to afford to live? Scatter plot study across 200+ CBSAs.
- **Hidden Livability winners:** Metros with strong health outcomes, low cost burden, decent labor markets — but no national profile. Who are they?
- **Opportunity Zones that aren't distressed anymore:** Find OZ tracts where every metric is moving the right direction. The policy designation lags the market.
- **Industry mix as a leading indicator:** Does QCEW industry composition in year N predict income growth in year N+5? A longitudinal test with the full QCEW backfill (2010–2024 now live).
- **Character archetypes at metro scale:** A taxonomy of US CBSAs by demographic profile type. Which archetype is most common? Which has the best Opportunity outcomes?
- **The zone that doesn't exist:** A methodology post on how we build tract-level zone types and what they reveal that CBSA-level averages hide.

---

## Immediate Next Steps for This Exploration

1. Answer the framing questions in Part 1 — audience, format, "so what"
2. Pick the first market and confirm data coverage
3. Run the ranking and distribution discovery analyses in `exploration/` across all CBSAs (runnable now on existing Gold data)
4. Stress-test the Character archetype labels against actual CBSA data — do they cluster cleanly?
5. Run the Livability / Opportunity scatter to test the tradeoff hypothesis
6. From the above, draft working definitions for all three Intelligence frames
7. Draft the first report outline for the selected market
