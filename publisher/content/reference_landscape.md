# Reference Landscape
**Last updated:** 2026-06-30

Who's writing about what we're writing about. Use this to enter existing conversations rather than starting from scratch, to understand what angles are already covered, and to find communities where the work might land.

---

## Track 1 — Technical Writing (data infrastructure, ETL, analytics engineering)

### Publications and platforms

**dbt blog / dbt Labs** — The canonical home for analytics engineering writing. Posts on modeling philosophy, semantic layers, and data warehouse design get wide circulation. The dbt Slack community (~50k members) is where practitioners discuss real problems. Our semantic layer and catalog architecture is directly relevant here.

**DuckDB blog and community** — DuckDB has an active blog and Discord. Posts on using DuckDB as a local analytical warehouse, embedded analytics, and performance at moderate scale (our use case exactly) are well received. The team is responsive and the community is growing fast.

**Towards Data Science (Medium)** — High volume, variable quality, but strong SEO. Good for reaching data scientists and analysts who are searching for tutorials. Technical posts with real code and real data do well.

**Substack — technical data writers to know:**
- *Count* (by Randy Au) — thoughtful data science practice, measurement, and tooling
- *The Analytics Engineering Roundup* (by Tristan Handy, dbt Labs) — analytics engineering philosophy
- *Data Patterns* — data engineering practice
- *Locally Optimistic* — analytics engineering and data team culture

**LinkedIn** — Stronger than expected for technical data content. Posts with a concrete finding or a counterintuitive lesson from building something real perform well. The analytics engineering and data engineering communities are active.

### Communities

- **dbt Slack** — #analytics-engineering, #modeling, #show-and-tell channels. Good for sharing what you built.
- **DuckDB Discord** — Small, technical, responsive. Good for sharing novel use cases.
- **r/datascience, r/dataengineering** — Hit or miss but large audiences. Works when the post is genuinely useful, not promotional.
- **Hacker News** — High bar, high upside. Analytical tools and novel data architectures get traction when the writing is direct and the work is real.

---

## Track 2 — Data Analysis Writing (metros, housing, neighborhoods, economic geography)

### Publications worth knowing

**City Observatory** (cityobservatory.org) — Joe Cortright's site. Data-driven urban policy analysis, usually 800–1500 words, always anchored to a specific number. Covers housing affordability, city economic divergence, and neighborhood change. The L/O scatter finding and the Southern health deficit both fit directly into the conversations they're having.

**Sightline Institute** (sightline.org) — Pacific Northwest focus but national reach on housing and land use. Strong on zoning, supply, and affordability. Data-heavy, policy-oriented.

**Bloomberg CityLab** — Long-form urban journalism with data. Higher production bar but they link to external analysis and data tools. Getting cited here is more realistic than pitching.

**The Urbanist** (theurbanist.org) — Seattle-based but national coverage. More advocacy-oriented but receptive to data analysis that supports urbanism arguments.

**Strong Towns** — Chuck Marohn's platform. Focus on financial resilience of cities, development patterns, and the math of how places grow. A different angle from ours but the audience cares about the same cities.

**Brookings Metro** — Think tank. Long-form, rigorous, heavily cited. Not a place to pitch but a source to engage with and cite. Their metro economic research overlaps with our framing.

**Urban Institute** — Similar to Brookings. Their neighborhood change and housing research is directly adjacent to Phase 7 zone methodology.

**Planetizen** — Urban planning news and analysis aggregator. They cover new research and data tools. A good place to appear once the Area Explorer is public.

### Substacks and independent writers doing adjacent work

- **Jerusalem Demsas** (The Atlantic, formerly Vox) — Housing and cities. Wide reach, data-literate audience.
- **Henry Grabar** (Slate) — Urban policy and transportation. Covers affordability and housing supply.
- **The Overshoot** (by Matthew Klein) — Macro economics with data depth. Not cities-specific but the audience is analytically serious.
- **Construction Physics** (by Brian Potter) — Long-form deep dives on how things are built. Approach is a model: pick one subject, go deep, show your work. The intellectual parallel to what a Metro Deep Dive should be.
- **Works in Progress** — Long essays on progress, urbanism, and economic geography. High quality bar, wide reach among people who care about cities.

### Communities

- **Reddit:** r/urbanplanning (~500k), r/cityporn (for map/data visuals), r/AskUrbanists, r/Economics
- **X/Twitter:** Urban planning and housing Twitter has a real community. Accounts like @mims, @ScottWentland, @ULI, @MarketUrbanist. Data visualization with maps gets shared widely.
- **Substack Notes** — The network effect is real for discovery. Short-form observations or chart previews that link to full posts work well here.
- **LinkedIn** — Less expected for this track but urban policy and real estate professionals are active. Works better for the "professional angle" on data findings (e.g., what this means for investors or economic developers).

### Academic and research adjacent

- **NCRC** (ncrc.org) — National Community Reinvestment Coalition. Their gentrification and neighborhood change research directly overlaps with Phase 7. Engaging with their work (citing, responding) is a credible entry point.
- **Urban Displacement Project** (urbandisplacement.org) — UC Berkeley. Direct methodological overlap with Phase 7. Noting where our approach diverges from theirs is a publishable angle.
- **National Association of Realtors Research** — They publish metro-level data. A different angle but overlapping audience for some findings.
- **JCHS (Joint Center for Housing Studies at Harvard)** — Annual State of the Nation's Housing report. Their data and framing are what journalists cite. Understanding their framing helps you respond to it.

---

## What's missing in the existing landscape

This is the gap worth writing into:

1. **No one is publishing a nationally consistent multi-frame metro typology.** Brookings and Urban Institute do metro rankings, but single-axis. Esri Tapestry does neighborhood segmentation but it's proprietary and commercial. NCRC and UDP do gentrification classification but rule-based and limited in scope. Our approach — unsupervised clustering across three frames, 396 CBSAs, with soft memberships and cosine similarity peers — is genuinely novel.

2. **Sub-metro spatial analysis that's reproducible from public data.** NCRC and UDP use this methodology but in limited geographies. A national zone typology built entirely from ACS, LODES, SLD, and EJScreen is a contribution the literature doesn't have yet.

3. **The combination of technical rigor and accessible writing.** Most rigorous urban analysis is behind paywalls or in academic formats. Most accessible urban writing is light on methodology. The gap is writing that shows the work and explains why it matters — which is the Construction Physics model applied to cities.
