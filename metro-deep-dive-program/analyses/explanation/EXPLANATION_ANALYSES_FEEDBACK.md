# Explanation Analyses Plan — Feedback for Claude Code Agent

**Purpose of this doc:** Notes and feedback on `EXPLANATION_ANALYSES_PLAN.md`, organized by section. For each analysis, this captures what we want out of it, the visuals and methods under consideration, and any corrections to the plan as drafted. Also captures broader feedback on the doc that isn't specific to one analysis.

Notes are recorded as close to verbatim (in meaning and wording) as possible; organization only.

Sections 5 and 9 below are the author's notes. The final section, **Synthesis**, is an assistant-written structural read of those notes against the plan — useful orientation for an agent picking this up cold, but not authoritative. Where the two conflict, the notes win.

---

## Section 9 — Decisions to Confirm Before the Child Specs

### 1. Meaning of "national"

One national method for all markets, which we then use for individual CBSA runs. We should also keep CBSA-specific outputs.

This really means: we have one national method, and the notebooks are centered around establishing that national method and then running it. These notebooks aren't necessarily all going to produce a national analysis — although some of them will, which we'll get into for each of the individual analyses.

### 2. Regional lenses

Agreed — the geography engine should control this long term.

### 3. Parcel system of record

Prefer free county or state assessor sources instead of any paid source. A paid/licensed source would require its own engine to build. Start with a manual file for now.

### 4. Parcel universe

Start with a manual universe first. Try using assessor data, or scrape Zillow, brokers, or foreclosure lists to get a list of properties.

### 5. Catchment v0

Agreed for v0. Long term, we can build this up further.

---

## Section 5 — Analysis Requirements

### Regional Role

This is similar to the Position analysis — let's use it as more of a workbench.

**Defining "region"**

The biggest thing is defining region. There are a few ideas to test out, which will act as filters for the report; we'll run each to see the differences across the different types of regions.

1. **Census divisions** — Easy to explain, understand, and produce. The downside is edge markets: does Richmond, VA really fit more into the South Atlantic than the broader area around DC, which would also include Maryland and Delaware?
2. **State** — Clear, but states can be tiny. If it's a Delaware metro area, you're not really looking at much.
3. **Nearby counties and metro areas** — Can make a lot of sense, but needs a good methodology. Idea: identify state borders within X number of miles, then get all CBSAs and counties from those states. This way we use both state boundaries (for maps) and physical proximity.
4. **Functional labor sheds** — Interesting, but this is more of an output of this analysis than an upfront filter/something defined here.
5. **Mega regions** — A newer concept for us, but really interesting — think the eleven mega regions in the United States. This is new to our repo and would need to be brought in manually; it would only really work for markets within those eleven mega regions.

**Output analyses (using the defined region as input)**

- **Regional comparison** — Comparison table and map that puts the market into context. Select KPIs for the table and for map color. This is the closest to our Position products.
- **Job/worker balance** — Could be interesting, or might not amount to much. A map showing inflows and outflows into the market.
- **Industry role comparison** — Shows what the market specializes in and compares it to the rest of the region. Especially interesting to see how the comparison changes with the region definition — e.g., based on one region, how does it make up the overall share versus others?
- **IRS and LODES origin/destination** — Show as maps of how people move in and out of the market, whether more permanent (IRS-type moves) or more like commuting patterns (LODES).
- **Nearby metro comparison** — An extension of the benchmarks.
- **Infrastructure map** — Should also produce this, to compare built environment and networks.
- **Market role hypothesis and analysis** — Something to write up manually based on what comes out of the above.

**Notebook build approach**

This notebook should be built to define the components first and reuse what we already have. Start with a single market, build to see how it's working. Most of these aren't really national builds — aside from making sure it's scalable across multiple markets. One option: a setup notebook that defines things, and a separate run notebook that does the actual analysis.

### Q6 One Metro?

This analysis is focused on whether the metro structure is really one metro. It can evaluate if outlying counties belong in the metro, but it could also be more interesting to evaluate whether there are multiple anchor cities, and to evaluate the 15-minute-city concept as a proxy for the number of city centers. (We'll keep coming back to the 15-minute concept — it's very popular in the literature right now.)

So this might be more interesting to think of as outputting commute flows, job corridors, and amenity clusters to understand if it's a single metro. The metric can be what's outlined above — commute flows, job corridors, and amenity clusters. That expands the scope but makes the question more clear, if not multiple questions.

### Q1 Supply or Demand

First needs to define what "inexpensive" means, both nationally and locally. It should be a function of cost versus local and national wages.

We should also define broad market signals, then go submarket with scores for supply versus demand and the relationship to cost. This is a good opportunity to practice our regression analysis skills.

This will be a national analysis on housing — one of those analyses where it can really be nationalized. Once the national analysis is done, we can get into market-specific analyses.

We should make maps of the submarket metrics and highlight cheap areas — both cheap and expensive. We can also create quadrant graphs of submarket areas, and also of CBSAs.

**Main outputs under consideration:**

- Relative cost distributions (box plots or similar)
- Supply-versus-demand formula, with some sort of "overheating index" score
- Quadrant graphs (scatter) of key relationships between variables
- Maps of local areas with key metrics
- Classifications of tracts and ZIP codes

### Q2 Job-Proximity Gradient

This is one where we create a national method, but the focus is local application. First step is creating job clusters/centers. Then we can create tract gradients for housing based on physical proximity first, network effect second. Then we can check housing costs and the relationship of proximity to cost — a regression could make sense here, both for cost and also just for things like number of people living there.

It's a nice extension of housing supply and demand, and fits well with the 15-minute concept from Q6.

Big outputs: maps, bins, and the regression equation. We definitely need a good, reusable definition for what a "job center" is here.

### Q3 Where Growth Lands

Very similar to Job-Proximity, but instead we're looking at growth compared to historic density and built environment — greenfield versus infill. We need a good standard for infill versus greenfield, then the analysis is how growth rates and permits compare against that. It also gets into the relationship between permits and population growth.

It's a nice supplement to what we're already building with 15-minute cities. This can get into how those have changed — what are new 15-minute cities, is growth happening within those or outside of those, that kind of thing.

### Q5 Afford to Live Near Jobs

Almost exactly the same as Q2, but looks at cost instead of housing units. In many ways it's a combination of them, or two sides of the same coin.

Open question: are these really separate questions? They are, but do we treat them separately? The inputs and outputs are really the same. This one is focused on the closest locations to jobs — or maybe it isn't, and it should just be made a metric within Q2. Is it about how close people are, or is it really just the cost of being close to your job? It's the same data, but a slightly different flavor and look at it.

### Q4 Daily-Needs Access

This seems like another method for fleshing out the 15-minute city concept — this time focusing on POIs and where people live compared to those, and the types of POIs. This will be another way to create corridors, this time focused on the different kinds of POIs.

Similar set of outputs to the other questions — clusters, centers, maps, distributions, that kind of thing. Very interesting concept, but very similar to what we're already doing. Feels like we're getting to a place where we're seeing a lot of reusability.

### Corridor Opportunity Read

We've given up on the Corridor Intelligence engine, but it seems like our analyses are actually building toward this concept anyway, via the 15-minute cities work. We should revisit this one as a summary of the previous questions we've been working on and answering.

Overall, most of these analyses have a standard setup but should be applied per market and tuned through the notebook build. So Corridor Opportunity Read could be dropped toward the end of this sequence, functioning more like a summary of everything above — but it should not exist as its own standalone analysis sitting on top of a Corridor Intelligence engine, since we've dropped that engine. It now looks like our analyses are building toward that concept organically instead.

### Parcel Watch

This is interesting — could be thought of in two parts.

1. **A running watch list of parcels** — where we're scripting Zillow or other brokers to get a list of parcels we want to be watching.
2. **The bigger analytical question** — getting county assessor property records, normalizing them, and creating a standard data schema (pricing, land use, etc.). Then comparing that to where parcels sit and creating some sort of heuristic for whether this is a candidate parcel for purchase — e.g., is it beneath a certain cost, has it not sold in X years, does it have a certain land use, is it within X of certain things, etc.

So generally, this is honestly less of an analytical notebook and more of an analytical method — for ingesting parcel data, normalizing it, then mapping and analyzing it to see if it's worth potentially investing in.

Catchment is a separate analytical process — doesn't build on top of Parcel Watch, but is used very closely with it.

### Catchment

We've already done a lot of work on this. The big thing is porting over the work already done in the property analyzer from the old Metro Deep Dive folder — geocoding points, building Euclidean rings around them, and getting the tract-ring weight tables. We're currently using areal weighting, but we might want to update that in a v2 to be more density-based. Overall, need to nail down the main metrics that go into this.

Catchment becomes really helpful as we move away from bigger question-style analyses into looking at specific properties. It could also be a good place to start, since we've already done a lot of this work.

It's also useful as a second-part piece of the 15-minute-city work: identify the center point, then use catchment as a way to identify what's within X distance of it.

So those are the two areas to look at for Parcel Watch and Catchment.


---

## Synthesis — Structural Read of These Notes vs. the Plan

*Assistant-written orientation for an agent picking this up cold. Not authoritative; the notes above take precedence.*

### The notes quietly restructure the family

The plan treats Q1–Q6 as six independent questions, unified only by a shared notebook contract. The notes reveal they aren't independent — Q2, Q3, Q4, Q5, and Q6 all run on the same spine: **define centers or clusters → measure distance/access from them → measure what varies across that gradient** (cost, units, growth, POIs). The author flags this himself at Q4 ("we're getting to a place where we're seeing a lot of reusability").

This is the biggest gap between the notes and the plan. The plan's promotion rule — keep logic local until a second consumer proves reuse — is designed for incidental overlap. This isn't incidental: five consumers are visible before a line is written. **The job-center/cluster surface and the distance/gradient method should be specified once, deliberately, before Q2 opens** — not discovered on the third notebook. The plan buries this in Wave 0 item 2 ("expose the existing Industry D3 job-center logic as a read-only query surface"); it should be elevated to the first real piece of work.

The 15-minute city concept is doing a lot of load-bearing work across Q2, Q3, Q4, Q6, and Catchment. If it's the spine, define it once with an explicit operational definition — otherwise five notebooks will each grow a slightly different version.

### Q5 answers its own open question

The notes ask whether Q2 and Q5 are really separate. Under the shared-spine framing, they're one analysis with two dependent variables — housing units and housing cost. Keeping them separate mainly buys two publication hooks, which is a real benefit, but that's an **issue-layer** decision, not an analysis-layer one.

### Regional Role got more interesting

The plan lists four region lenses as definitional housekeeping. The notes turn region definition into the analysis's actual subject — most visibly in the industry-role note, where the point is how the specialization read *changes* as the boundary moves. That's a better analysis than the one the plan describes, and a publishable finding on its own.

Two changes from the plan worth carrying forward:
- **Functional labor shed is demoted** from an upfront lens to an output of the analysis.
- **Megaregions are added** as a fifth lens. This is the risky one: manual, incomplete national coverage, less institutional backing than the other four. Include as a labeled fifth lens; do not block on it.

### The Wave 3 blockage is removed

The plan gates Corridor Opportunity Read — and by extension Parcel Watch's scope — behind Corridor Intelligence calibration, Richmond validation, and a consumer handoff. Dropping the engine and letting corridors emerge from the Q2/Q4 cluster work eliminates that dependency chain. **Wave 3 largely dissolves.** What remains is Parcel Watch, which was never genuinely gated on corridors.

Corridor Opportunity Read moves to the end of the sequence as a *summary* of the preceding questions, not a standalone analysis with its own engine dependency.

### Two tensions to hold explicitly

1. **National-first is over-specified.** The Section 9 note softens the rule: these establish a national *method*, but most aren't national *analyses*. The plan's uniform two-mode contract (national coverage table, national distribution, threshold sensitivity for every Q) doesn't fit that. Q1 genuinely is national. Regional Role and Catchment are not. Make this explicit so national scaffolding isn't built into notebooks that don't need it.

2. **Free assessor sources mean a per-county adapter, permanently.** That's the accepted cost of the Section 9 decision, and it's precisely why Parcel Watch is **engine-shaped rather than notebook-shaped** — which is how the notes describe it.

### Program fit

Q1 and Q2 are the two analyses carrying regression work. They are the most likely of the ten to become standalone methods pieces rather than only Deep Dive sections.