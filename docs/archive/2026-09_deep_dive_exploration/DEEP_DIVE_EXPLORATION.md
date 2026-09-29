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

**Answer**
We're writing for all 3 but the primary audience is the curious researcher / data nerd. This is what I am and it's the cleanest for me to write for myself. The investor and the person wholives there or wants to are good secondary readers. For these though we can have different sub-products or sections. For the investor we can point to the sections about the local economy, and as we develop our writing we can find certain writing that works for them. The person who lives there or wants to probably doesn't want to start with a major deep dive, they're probably interested in how the market compares to others so this is where articles such as "best places to retire to" become valuable. But this audience is also highly dependent on the persona of the reader which can make it a challenge for a specific deep dive.

So all in all our main readership is other people that are generally interested in cities and data nerds.

### What makes it different from a Wikipedia article or a real estate report?

Most market reports are either (a) surface-level demographic summaries with no analytical spine, or (b) narrowly investor-focused with no cultural or qualitative depth. What we have that they don't:

- Three intelligence frames that create a structured vocabulary for analyzing any market (Character / Livability / Opportunity)
- A spatial layer that connects neighborhood-level patterns to metro-level narratives
- A comparative framework — every metric is benchmarked against peers and national, not presented in isolation
- An analytical point of view — we're willing to say something definitive, not just present data

**Question to settle:** What is the "so what" of a Metro Deep Dive? After reading it, what should the reader know or be able to do that they couldn't before?

**Answer**
This will emerge from the first Deep Dive rather than being defined upfront.
Three working hypotheses to test against Jacksonville:

1. Structural explanation — after reading this, you understand the mechanism
   behind a market's trajectory, not just the outcome. Most people know *that*
   a market grew or declined; few know *why* and whether those forces are
   still active.

2. Cross-frame tension — the most valuable finding is the contradiction the
   headline numbers hide. A market where Opportunity is high but Livability
   is deteriorating tells a more interesting story than one where all frames
   point the same direction.

3. The zone analysis is the "so what" — CBSA averages are well-covered
   elsewhere. What we uniquely produce is the sub-market breakdown: where
   inside this metro are conditions improving, stagnating, or diverging?
   This is the hardest thing to replicate and the strongest differentiator.

Working assumption: Hypothesis 3 is the strongest, because the zone analysis
is what no standard market report produces. Hypotheses 1 and 2 are the framing
that makes the zone findings land. Test against Jacksonville: does the zone map
tell you something the CBSA averages didn't?


### What's the right length and format?

Options on the spectrum:
- **Short-form Substack post** — 800–1,200 words, 3–5 charts, one focused thesis. Fast to produce, shareable. Loses depth.
- **Long-form Substack piece** — 3,000–5,000 words, 10–15 charts, section-by-section walkthrough. Newsletter-style. Good for the first few reports while methodology is being established.
- **PDF report** — Traditional format, shareable as a document. Better for an investor or researcher audience. More work to lay out well.
- **Interactive Streamlit document** — Rich but requires deployment infrastructure. Higher effort; better for Phase 2.

**Question to settle:** What's the first format? Probably long-form Substack for the first report — iterating on format is easier than iterating on methodology.

**Answer**
Let's start with a long-form Substack style post. This gives us room to test out different formats and sections. Short form posts belong in our Content engine and a PDF or Streamlit report are too much effort and too rigid at this point, they can be longer term goals but not the place to start.

---

## Part 2 — The Intelligence Framework

The three frames are the analytical spine of everything. Before we build anything, we need working definitions that we actually believe in. This section is where we explore what they should be.

These three themes are organizational that answer questions about a place, but they are not scorecards. These are analytical lenses that contain sub-topics that require real analysis to interpret.

It's ok for there to be blurred lines between our themes, I think all three of these things are intertwined and that's part of a broader long term thesis we can work on.

### Character — What kind of place is this and who does it attract?

Character is the most qualitative frame and the hardest to score. It's trying to answer: what does it feel like to be in this place, and what makes it distinct?

To focus it more, Character is Identity-focused. About the texture, composition, and social fabric of a place. Not ordinal — metros aren't better or worse on Character, they're different. Though it is true that some metros can score higher or lower on certain sub-topics.

**Sub-Topics**
- Demographic composition (race, age, education, nativity, migration)
- Social fabric & civic identity (Social Capital Index, institutions)
- Recreation & cultural amenities (Points layer eventually)

**Key Metrics**
- Race and ethnicity shares (underlying data, not composite diversity index)
- Median age
- Share foreign-born
- Educational attainment (BA+, HS graduation)
- Net migration rate and composition
- Social Capital Index (JEC) — when ingested

**Current approach:** Demographic profile types (archetypes) derived from a cluster model. Labels like "Young & Diverse," "Established Families," "Creative Class."
   **Update** We've adde an Analytical Approaches section that should help with this. It makes sense to use a clustering model to derive profile types, but it's still important for us to look at many of the key metrics and not try to reduce the whole section to one label.

**Things to explore:**
- Are demographic archetypes the right unit, or is there a better way to characterize a place? What does a "Creative Class" CBSA actually look like vs. a "College Town" — are those distinguishable in the data, or do they blur together?
   - This is a valuable unit but it's not the end all be all. We'll need to evaluate our data to see what come up with for these archetypes, and we should find relevant analytical literature on this so we can compare our findings to the consensus and align our language to how people think about classifying markets.
- What's the relationship between demographic character and cultural character? A place can be demographically similar to another but feel totally different. How much of that is captured in the data vs. requiring the POI/cultural layer?
   - This is they value add of the POI/cultural layer. There might be some demographic info such as languages spoken, immigration rates, family background, education that can speak to this, but for the most part this comes from POI. And even so, this is probably most interesting when we get to sub-market zones such as neighborhoods, places, or custom zones.
- At CBSA grain, what metrics produce the most interesting and defensible differentiation? Diversity index, median age, share foreign-born, education attainment, net migration composition — which of these actually split CBSAs into coherent groups?
- Is "Character" a score at all, or is it fundamentally a label / taxonomy? A Young & Diverse metro doesn't have a "higher Character score" than an Established Families metro — they're just different. How do we handle a frame that isn't naturally ordinal?
   - This is a label, but inside of that label we can create some different scores as well. Let's explore our data to see what's possible. One thinking could be museums per 100k people or something like that as a proxy, but we'll need to think through that more. High level though, the key is getting a good label / taxonomy.
- What are the 5–8 Character archetypes that feel right at CBSA grain? (vs. NTA grain, which Stoop uses) The labels from the NTA-level work may not translate directly to metro scale.
   - We need to review our data more to see what we come up with. We should also identify relevant literature on this subject for inspiration and a way to ground our research. Also, CBSA level labels are interesting but this probably gets even more interesting when we get into the makeup of sub-market areas.

**Hypotheses to test:**
- High diversity index + young median age + high share foreign-born → "Immigrant Gateway" or similar
- High college attainment + young median age + high net in-migration of young adults → "Creative Class / Knowledge Hub"
- Low diversity + older median age + low migration + high homeownership → "Established / Rooted"
- High college enrollment relative to population → "College Town"

**Data gaps that affect Character at CBSA grain:** POI/cultural layer not yet available at national scale. Character scoring at CBSA grain will be purely demographic until the per-market Points framework is built.

**Key Researchers:**
- **Robert Putnam** is a Harvard political scientist, best known for Bowling Alone (2000) — his central argument is that American social capital has been in long-term decline since the 1960s, measured by falling membership in civic organizations, declining voter turnout, less church attendance, fewer dinner parties, and weaker neighborhood ties. He coined the distinction between:

Bonding capital — strong ties within homogeneous groups (family, ethnic community, church congregation)
Bridging capital — weaker ties that connect across different groups (cross-class friendships, diverse civic associations)
His framework is why the JEC index uses metrics like nonprofit density, congregation counts, and voter turnout — they're all proxies for organized civic life. The tension he identifies between bonding and bridging is directly relevant to us: a metro can have high within-group cohesion but low cross-group connection, which reads very differently for a Deep Dive.

His later book Our Kids (2015) extended this to opportunity and class stratification, which is where his work starts to bleed into our Opportunity frame.
- **Richard Florida** (The Rise of the Creative Class, 2002) — his "Creative Class" taxonomy is the most direct precedent for our archetype labels. He clusters metros by concentration of workers in creative occupations and uses a "Bohemian Index" and "Gay Index" as proxies for openness and tolerance. His work is useful and influential but has been substantially critiqued — the Creative Class label predicts gentrification and displacement as much as it predicts prosperity. Know his framework; don't adopt it uncritically.
- **Enrico Moretti** (The New Geography of Jobs, 2012) — argues that US metros are diverging into two types: knowledge hubs (high-skill, high-wage, expensive) and everywhere else. His "Great Divergence" thesis is the structural backdrop for our Character + Opportunity cross-frame analysis. He's also the source of the "multiplier effect" idea — each new knowledge-economy job creates ~5 local service jobs — which shapes how we think about industry mix in Opportunity.
- **William Julius Wilson** (The Truly Disadvantaged, 1987; When Work Disappears, 1996) — the essential counterweight to Florida. His work on concentrated poverty, neighborhood effects, and the collapse of industrial-era social structures in Black urban communities explains a lot of what the demographic data shows in Rust Belt metros. Relevant for Character (social fabric breakdown), Livability (concentrated poverty), and the Zone Analysis (distressed zone typology).
- **Alan Berube & Elizabeth Kneebone** (Brookings) — their work on suburban poverty and the spatial distribution of disadvantage is the most directly relevant to our zone methodology. The Confronting Suburban Poverty in America (2013) framework influences how we should think about "Affordable Fringe" and "Distressed" zone types.
- **Raj Chetty** (Opportunity Insights) — his work on intergenerational mobility and neighborhood effects is the empirical backbone behind the Social Capital Atlas we're ingesting. His finding that where you grow up has measurable effects on long-run income, independent of family income, is the core justification for our zone analysis as a product.

**In Summary** Putnam gives us the Social Fabric vocabulary. Florida gives us the archetype language (with caveats). Moretti gives us the structural economic divergence thesis. Wilson gives us the ground-level counternarrative. Chetty gives us the empirical evidence that place actually matters at the neighborhood level — which is the whole justification for what we're building.

---

### Livability — Can you live a functional life here?

Conditions-focused. About whether the physical, economic, and social infrastructure of a place supports daily life.

Livability is about quality of daily life. The question: can you afford to live here, and is the day-to-day experience good?

**Sub-Topics**
1. **Affordability** — housing cost burden, rent-to-income, home price relative to income; most data-rich dimension
2. **Health** — life expectancy, chronic disease rates, mental health, physical inactivity (CHR now live)
3. **Safety** — injury deaths, violence outcomes (CHR covers this; city-level crime data is per-market only)
4. **Access & Infrastructure (transit, walkability, food, basic services)** — commute times, transit access, walkability (ACS commute data live; EPA SLD not yet)
5. **Education access** — HS graduation, college access (CHR + ACS; K-12 quality not yet available at national grain)
6. **Physical Environment** - Pollution, Adverse Climate Events, Weather

**Key Metrics**
- Rent-to-income ratio
- Housing cost burden rate
- Home value to income ratio
- FMR gap
- CHR health outcomes: life expectancy, chronic disease rates, physical inactivity
- CHR safety: injury deaths, violence measures
- Commute time, share no-vehicle, transit commute share
- HS graduation rate, college attainment share

**Things to explore:**
- Is Livability a single score or a dashboard of sub-scores? A metro can be highly affordable but have poor health outcomes (e.g., some Midwest markets). Collapsing to a single score risks losing the most interesting tension. 
   - It's a mix of sub-scores, collapsing to one score oversimplifies our stories and is anethma to our idea of doing real deep dive work. A single score could be a useful framing for a specific rankings post but not the meat of this kind of deep dive.
- How do we weight affordability vs. other dimensions? Affordability is the most data-rich and the most legible to a general audience, but a Livability score dominated by affordability is basically just an affordability score.
   - Agreed, we will need to run actual analytics as outlined in the Analytics Approach section. But I do not want to overweight on affordability, it's cheap and it's boring.
- Where does Livability end and Opportunity begin? Income growth improves livability (you can afford more) but it's primarily an Opportunity signal. The frames should tell different stories; if they're highly correlated, one is redundant.
   - This is a very valid point, affordability should end at the basics, think housing costs as a percent of income, costs of needs, etc. What is left over from that is a good affordability signal, but once we get past that into growth or investments then we're getting into Opportunity. It's ok for there to be blurred lines between our themes, I think all three of these things are intertwined.
- What's the natural peer group for Livability benchmarking? A Sun Belt market looks worse on affordability if you benchmark it against the Midwest, better if you benchmark against coastal cities. How do we frame benchmarks honestly?
   - We should benchmark at a few levels: Nationally and Regionally are clear benchmarks, within the same state makes a lot of sense too, after that I think we should benchmark against Peer Clustered markets. We do Clustering work for Character, but I think it also makes sense to do a broader benchmark cluster across all themes and metrics to get a "natural" label for benchmarking.

**Hypotheses to test:**
- The Livability / Opportunity tradeoff is real and visible in the data: high-Opportunity metros (fast-growing, high-income) tend to have worse Livability (expensive, congested). Scatter plot this.
- There are "hidden Livability winners" — affordable metros with good health outcomes and decent labor markets that never make the national narrative. Finding these is publishable.
- The health dimension creates the most geographic surprises — Southern states often look strong on other Livability dimensions but weak on health outcomes.

**Data gaps:** EPA SLD (walkability/transit built environment) not yet ingested. Absence makes mobility scoring thin — commute time from ACS is a weak proxy for actual transit access.

**Key Researchers**
**Matthew Desmond** (Evicted, 2016) — the essential read on housing cost burden. His Milwaukee eviction study showed that low-income renters spending 70–80% of income on housing is not exceptional — it's structural. His Eviction Lab at Princeton tracks eviction rates nationally at county grain, which is a metric worth flagging as a future candidate. Relevant to Affordability.

**Alan Mallach** (The Divided City, 2018; Brookings) — works on neighborhood decline, housing abandonment, and the divergence between recovering and still-declining cities post-2008. His frame on "two cities within a city" is the conceptual anchor for our Zone Analysis distressed-vs-transitional typology. Relevant to Affordability and the zone methodology.

**Richard Wilkinson & Kate Pickett** (The Spirit Level, 2009) — their core argument is that income inequality, not average income, drives most health and social outcomes. A metro with high median income but extreme inequality will have worse health outcomes than a more equal metro with lower median income. This is the theoretical justification for why we should look at cost burden and poverty distribution, not just medians. Relevant to Health and the Livability/Opportunity cross-frame tension.

**Robert Sampson** (Great American City, 2012) — Chicago-based longitudinal study of neighborhood effects. His finding that neighborhood-level concentrated disadvantage is self-reinforcing and affects health, crime, and educational outcomes even after controlling for individual characteristics is the empirical backbone behind why zone-level analysis matters. Relevant to Safety and the zone methodology.

**Douglas Massey & Nancy Denton** (American Apartheid, 1993) — foundational on residential segregation. Their dissimilarity index and isolation index are the standard measures for how racially and economically segregated a metro is. Segregation is a Livability metric we don't currently have in the map — high segregation means the metro-level average conceals dramatically different lived experiences by neighborhood. Worth flagging as a future input.

**Reid Ewing** (University of Utah, smart growth research) — the leading empirical researcher on sprawl, walkability, and health outcomes. His work establishes the link between built environment characteristics (density, street connectivity, land use mix) and outcomes like obesity, driving fatality rates, and mental health. This is the theoretical grounding for why Access & Infrastructure belongs in Livability, not just as a transportation metric.

---

### Opportunity — Is this a place where things are happening?

Trajectory-focused. About economic momentum, market signals, and whether conditions are improving for residents, investors, and businesses.

Opportunity is about momentum and potential. The question: is this a market where economic conditions are improving, and is there upside?

**Sub-Topics**
1. **Resident opportunity** — income growth, wage levels, labor market tightness, poverty trends
2. **Market / investor opportunity** — home price appreciation (FHFA HPI now live), rent growth (Zillow ZORI live), population growth, building permit activity
3. **Business & industry opportunity** — GDP growth, industry mix and specialization (QCEW now live), business formation rates (CBP/BFS not yet)

**Key Metrics**
- Income growth (1yr, 5yr)
- Wage levels
- Unemployment rate
- Poverty rate change
- Home price appreciation (FHFA HPI)
- Rent growth (Zillow ZORI)
- Building permit activity
- GDP growth
- Industry HHI, sector share changes (QCEW)

**Things to explore:**
- Three sub-lenses is a lot. Are they all necessary, or do two of them capture most of the signal? Resident and Market opportunity might move together closely enough that they can be combined.
   - I think they are, we don't need to repeat ourselves too much and can see how they land, but it's the right place to start.
- What's the right time horizon for Opportunity scoring? A market that was hot 5 years ago but is cooling is very different from one that's just starting to move. Both 1-year and 5-year indicators are needed, but how do we weight them?
   - Good question, we will need to see how the data bares this out.
- Opportunity Zones: now in the platform. How much analytical weight do they deserve? OZ designation is a policy flag, not a market signal — a tract is designated because it was distressed, not because it's opportunistic. The interesting question is: which OZ tracts have the highest momentum metrics despite their distress designation?
   - It's an input but until we find the analytical value we don't need to overthink this. The designation could be helpful since it means that there may be extra tax dollars or breaks for this area which can help with investors.
- The QCEW industry data is now live and deep (43M rows, 2010–2024). Industry specialization and concentration are strong Opportunity signals. What does industry mix tell us about a metro's long-run trajectory that income/GDP alone doesn't?
   - Good question, it will depend on the industry type. If the market is heavily weighted in industries of the future like tech or advanced manufacturing then that is a great sign vs a market focused on services or agriculture. We should review relevant economic and sociological literature on this subject.
- Does Opportunity work at CBSA grain, or does it only become meaningful at sub-CBSA grain (tract/zip)? A CBSA average might look flat while masking a very hot inner core and a declining periphery.
   - It works at both grains but will look different. We should be able to find hotter markets and then can deep dive into where is the best places in those markets, at the same time a week market can have areas that can surprise us. So we will need to look at both and really understand the dynamics within the market.

**Hypotheses to test:**
- Industry mix is the leading indicator that income and GDP growth lag. Markets with growing tech/professional services concentrations in 2015 showed the strongest income growth by 2022. QCEW vs. BEA growth correlation study.
- The "bounce-back" markets — metros with high 2020 distress that recovered fastest — are the most interesting Opportunity story. Who bounced back and why?
- OZ + high momentum = a real signal worth publishing. Find the Opportunity Zone tracts where every metric is moving the right direction.

**Key Researchers** 
**Edward Glaeser** (Triumph of the City, 2011; Survival of the City, 2021 with David Cutler) — the most directly relevant for Opportunity at CBSA grain. His core argument is that dense, educated cities are engines of innovation and wage growth precisely because proximity enables knowledge spillovers between workers. His empirical work shows that a 10% increase in a city's density correlates with a 2.4% higher productivity. For us: density and education concentration aren't just Character inputs — they're Opportunity predictors. His work is also the theoretical grounding for why industry mix matters; cities that attract high-human-capital industries create compounding advantages. Relevant across all three Opportunity sub-lenses.

**Daron Acemoglu & James Robinson** (Why Nations Fail, 2012) — their institutions framework applies at the metro level too. Cities with inclusive economic institutions (property rights, rule of law, competitive markets) tend to generate sustained opportunity; extractive institutions produce short-run booms that collapse. This is less directly applicable to our metrics but is useful framing for why some "hot" metros have fragile opportunity stories — they're riding a single industry or a policy tailwind, not a structural advantage. Relevant when interpreting Business & Industry signals.

**Timothy Bartik** (W.E. Upjohn Institute) — the empirical researcher most focused on what local economic development policies actually work and for whom. His work on place-based interventions and "good jobs" (jobs with career ladders, wage growth, stability) is the most rigorous take on Resident Opportunity. His key finding: aggregate job growth in a metro doesn't necessarily improve conditions for existing low-income residents — it depends on who gets the jobs. Relevant to Resident Opportunity; a useful check on reading income growth as unambiguously positive.

**Raj Chetty** (already in Character) — his Opportunity Atlas work is directly applicable here too. His finding that some metros have much higher intergenerational mobility than others — even after controlling for income — is an Opportunity metric we don't yet have in the map. The "probability of reaching the top income quintile if born in the bottom quintile" is the most powerful single Opportunity metric for residents that exists. It's in the Opportunity Atlas dataset we're already planning to ingest for Social Capital. Worth surfacing as a distinct Opportunity metric, not just a Character one.

**Wolfgang Streeck** & varieties of capitalism literature — more macro, but useful for the industry mix analysis. His framework distinguishes "liberal market economies" (flexible, finance-driven, fast-moving) from "coordinated market economies" (manufacturing-heavy, long-term oriented). At the metro level, this maps to whether a city's economic base is in tradeable goods (manufacturing, tech) vs. non-tradeable services (retail, healthcare, hospitality). Tradeable sectors drive wage growth for the whole metro; non-tradeable sectors don't. This is the theoretical backbone for why QCEW industry composition analysis is worth doing — not all job growth is equal.

**Richard Florida** (again) — his later, more self-critical work is relevant here. The New Urban Crisis (2017) walks back some of Creative Class optimism and argues that knowledge-economy success creates winner-take-most dynamics where a few "superstar cities" capture most of the gains. His "urban inequality paradox" — the most successful cities also have the worst inequality and displacement — is exactly the Opportunity/Livability cross-frame tension we want to test in the data.

**David Autor** (MIT, "The Work of the Past, Work of the Future", 2019) — the leading researcher on labor market polarization. His finding that automation and globalization have hollowed out middle-skill jobs (creating an hourglass labor market of high-skill + low-skill work with a collapsed middle) is directly observable in QCEW industry and occupation data. For Opportunity: a metro with growing high-skill employment and growing low-skill employment but a shrinking middle-skill tier looks healthy in aggregate but is structurally fragile. This is a sophisticated read of QCEW data that goes beyond simple sector share analysis.

### Analytical Approach
Three-step exploratory sequence applied to each theme's input metrics, run in exploration/ notebooks. Character first, then Livability, then Opportunity.

**Step 1 — Variance analysis** Which metrics have meaningful spread across CBSAs? Low-variance inputs don't differentiate and get dropped early.

**Step 2 — Correlation analysis** Among high-variance inputs, which are redundant? Produces a reduced, defensible input set. Example: if diversity index and share foreign-born move together tightly, use underlying race data instead of composite scores.

**Step 3 — Clustering** Unsupervised clustering on the reduced input set. Key test: do the resulting groups feel coherent and nameable, or do they just reflect population size and geography?

**Guiding principle:** No priors imposed on the data. Let the analysis surface structure rather than fitting data to intuitions — especially important for Character where intuitions about cities are strong and potentially wrong.

#### Question Bank
These are some of the kye questions we will be looking to answer in and across each theme to help refine our thinking. they are grouped by different types of analytical work.

**Factual / Descriptive** — establishes baseline; answers "what is true here?"
- What is the demographic composition of this metro — race, age, education, nativity?
- Which metros have the highest rent burden?
- Which metros have the highest share of foreign-born residents?
- What is the current unemployment rate and labor force participation across metros?
- Where is permit activity highest?

**Comparative** — benchmarks one place against peers, region, or national; answers "how does this place stack up?"
- How has the demographic profile of this metro changed over the last 10 years?
- Which metros are aging fastest vs. getting younger?
- How do Southern metros compare on health outcomes vs. affordability vs. the national average?
- Which metros have bounced back fastest from 2020 employment losses?
- Where is GDP growth broad-based vs. concentrated in one sector?

**Trend / Trajectory** — tracks change over time; answers "where is this heading?"
- Where is cost burden worsening fastest despite flat income growth?
- Where is educational attainment rising fastest?
- Which metros have the most demographic diversity, and is that diversity growing or stable?
- Which metros are cooling after a period of strong appreciation?
- Where is poverty rate declining fastest?

**Tension / Analytical** — two signals point in opposite directions; answers "what's the real story here?"
- Where is wage growth outpacing rent growth — genuine resident gains vs. paper appreciation?
- Which metros have strong affordability but weak health outcomes?
- Which metros look demographically similar but feel structurally different — and why?
- Which Opportunity Zone tracts show strong momentum despite their distress designation?
- Where is permit activity signaling real supply response vs. lagging demand?

**Discovery / Synthesis** — surfaces surprising or overlooked patterns; answers "what would you not have guessed?"
- Which overlooked metros score well across most Livability dimensions?
- Which metros have the best combination of affordability and health outcomes?
- Which industry mixes correlate with the strongest long-run income growth?
- What migration patterns are reshaping the demographic character of fast-growing metros?
- Which metros look like outliers on one frame but not the others — and what explains it?

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
   - What the market looks like today, with key points mapped such as highways, universities, etc.

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
   - I think Zones are a key component as this is where we go beyond looking at a market as a whole and starting to breakdown the inner components of a market. But a Zone can be Places, Zip Codes, or a custom clustering. We can start easier with Places and Zips, then flesh out different clustering options. Though I think it makes sense to invest in some clustering ideas early on.
- How long is each section? Aim for 400–600 words per frame section + 3–4 charts = roughly 3,000–4,000 words total for the full report.
   - Yes, this makes sense for the final write-up but honestly we will probably produce much more content than this which is a good thing.
- Does the report need a "methods" appendix, or does that live separately on the platform site?
   - That can live separately as a standalone appendix article.

### Deep Dive Analytical Approach

Distinct from the methodology-building work above. This is the analytical
sequence for actually building a report on a specific market.

To be defined after Phase A is complete — the methodology work will surface
what the right questions and analyses are. Placeholder for now.

Key difference from the methodology approach: where the methodology work
asks "which metrics differentiate across all CBSAs?", the Deep Dive work
asks "what is the specific story of this market, and what data supports it?"


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

**Answer**
Both. I want to stress-test our template and ideas, but still have interest. Jacksonville makes a lot of sense as a place to start. We can use Richmond, VA as a back-up and companion piece so we're learning about a new market too.

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
   - Honestly, we should produce both. And then a mix of them. I think we need to validate what our data looks like and find a good cross between the different themes. We can create a cluster per theme, and then a cross-theme cluster.
   Presentation hierarchy: the cross-theme cluster is the primary zone map shown in the report. Per-theme clusters are analytical inputs used to build it, and optional deep-dive views in the interactive Area Explorer. Not all cluster views belong in every report — editorial judgment applies.

- Should zones be defined independently per market, or should we aim for a consistent national zone taxonomy that applies across all markets? National consistency is more powerful for comparison; per-market is more precise.
   - I would prefer that we start with a national model, I think this is the cleanest method long term, and if we do by market then we can identify certain areas as belonging to one label when it doesn't make that much sense. If we find that a national model doesn't work well or has gaps in certain markets we can create by-market models and compare the differences.
- How many zone types? The ROF used 4–5 types. 6–8 feels like the right range for a full Intelligence Frame zone model.
   - 6-8 feels right to me as well, but we should review relevant literature and see what number of clusters bear out when we run our analyses.
- What are the zone type labels? Draft set to evaluate: (I'm good with this draft set, but we should identify relevant literature to help us validate and think about this further.)
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

We will need to do further research on these different methodological options. We need to identify relevant studies and learn from what they've done and see what methods make the most sense.

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

## Next Steps

### Phase 0 - Mapping KPIs to data

Before we start any analysis we will need to map our expected metrics and KPIs to our existing data tables so Phase A can be seamless.

### Phase A — National Landscape (exploration/, before picking a market)

The broad analysis pass. Produces findings, feeds the methodology,
and builds a defensible backlog of markets worth a Deep Dive.

1. Variance + distribution pass across all Gold metrics at CBSA grain
   — which metrics have meaningful spread vs. too uniform to differentiate?
   → produces the reduced metric set for each frame

2. Livability / Opportunity scatter across all CBSAs
   — test the tradeoff hypothesis; find the four quadrants
   → publishable standalone; informs both scoring models

3. Character clustering — first pass
   — k-means or hierarchical on demographic inputs; evaluate archetype labels
     against what actually emerges
   → validates (or revises) the draft label set

4. Trajectory analysis — divergence from national average
   — for metrics that survive the variance filter, which CBSAs are moving
     away from the mean (in either direction) and accelerating?
   → builds the backlog of interesting markets to investigate;
     does not feed the methodology directly

5. Literature review
   — 3–4 relevant frameworks on metro classification, neighborhood typology,
     zone clustering; document what's been done and where our approach differs

### Phase B — Market Selection (after Phase A)

Pick Jacksonville and Richmond based on what the national data actually shows,
not just on prior intuition. Confirm data coverage for both.

### Phase C — First Deep Dive (Jacksonville)

Build the report on top of what Phase A produced. National context is already
done; the Deep Dive applies it to one market and tells the story.
The Jacksonville zone analysis is the stress-test for the zone methodology.
Richmond is the companion piece — a fresh market, a second data point.

