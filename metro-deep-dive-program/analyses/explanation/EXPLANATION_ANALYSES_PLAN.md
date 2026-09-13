# Metro Deep Dive — Explanation Analyses Plan

**Status:** Directional family plan; ready to split into analysis-level specs

**Updated:** 2026-09-11

**Revision note:** This version incorporates `EXPLANATION_ANALYSES_FEEDBACK.md`.
The material changes are: the 15-minute access method becomes a shared spine
defined in Q2 and re-run by later questions with different center inputs; Q2 and
Q5 merge into one analysis with two dependent variables; Corridor Intelligence is
dropped as an engine dependency and Corridor Opportunity Read becomes a closing
synthesis; Parcel Watch splits into a proposed parcel engine plus an analysis on
top of it; Regional Role gains an explicit region-definition step ahead of its
market-role and comparison work; and national scope becomes a per-analysis
declaration rather than a uniform requirement.

**Program home:** `metro-deep-dive-program/metro_deep_dive_program.md`, Section 3.2

**Primary planning source:** `metro-deep-dive-program/mdd_classification_workbook.md`

## 1. Purpose

This document defines the first build direction for the nine Explanation
analyses in the Metro Deep Dive program:

- five reusable question analyses: Q1, Q2, Q3, Q4, Q6
- Regional Role
- Corridor Opportunity Read
- Parcel Watch
- Catchment

Two structural changes from the previous version of this list:

- **Q5 is no longer a separate analysis.** It merges into Q2 as a second
  dependent variable. See Section 5.4.
- **Parcel Watch now sits on a proposed parcel engine.** The ingestion,
  scraping, and normalization work is engine-shaped; the analysis is what runs
  on top of it. See Section 5.8 and Section 12.

It is intentionally one level above an implementation spec. It establishes:

- the question and analytical unit for each analysis
- the first required inputs, reusable components, and known gaps
- what can start now and what is genuinely gated
- the expected notebook mode and minimum useful outputs
- the dependency-aware build sequence
- the decisions each later analysis-level spec must lock

It does not lock formulas, thresholds, final visual designs, issue copy, or
publication selections. Those decisions belong in the individual analysis
specs or, for reader-facing locks, in the issue layer.

## 2. Family Model

### 2.1 What Explanation analyses do

Position analyses say where a metro sits. Explanation analyses test why it
sits there by examining variation and relationships below the CBSA level.
Their primary evidence is usually tract, county, Place, ZCTA, point, corridor,
or parcel grain even when the result is summarized for national comparison.

The analyses are reusable research instruments. They can feed Act 2, Act 3,
or Act 4, but they are not owned by any one act.

### 2.2 National method, not necessarily national analysis

The governing rule is that we build **one national method** and then run it for
individual markets. That is not the same as every analysis producing a national
analysis. Some will — Q1 most clearly. Others establish a method that is
national in the sense of being uniform and reusable, but whose interesting
output is local.

Each analysis therefore declares a **national posture** in its spec:

| Posture | Meaning | Analyses |
|---|---|---|
| National analysis | The national run is itself a result worth reading and publishing | Q1 |
| National method, local application | One declared method applied uniformly; the national run exists to test and calibrate the method, not to be the finding | Q2, Q3, Q4, Q6 |
| Market or point scoped | No national run is expected; reuse comes from consistent method and QA | Regional Role, Corridor Opportunity Read, Parcel Watch, Catchment |

The two-mode notebook contract below remains the **starting scaffold** for the
numbered questions, because it is a good default and costs little to begin with.
It is not a requirement that every analysis carry national surfaces. An analysis
whose posture does not call for a national coverage table, national distribution,
or national threshold sensitivity should say so in its spec and omit them rather
than building scaffolding it will not use.

Each numbered question should become one parameterized Marimo notebook with
two modes:

| Mode | Purpose | Required behavior |
|---|---|---|
| `scope: all` | Develop and test the method nationally | Apply one declared method to every covered CBSA; retain the small-area evidence; show coverage, the national distribution, threshold sensitivity, and market cases |
| `scope: market` | Explain one selected metro in depth | Use the same method and definitions; expose tract/county/Place/ZCTA evidence, maps, component tables, and claim candidates for the selected market |

The national mode is not permission to collapse the question into a CBSA-only
ranking. For example, Q1 should compare metros using summaries derived from
their submarkets, while the selected-market mode should show the submarkets
that produced the summary.

The notebook should support a `no clear signal` result. A method is not useful
if every metro must be forced into a strong conclusion.

Some methods should still be piloted on Richmond and Jacksonville before a
national run. This is especially true for Q4, where only two governed POI runs
currently exist, and for any method whose national scale would make a bad
definition expensive to unwind.

Several analyses are better built as a **setup notebook plus a run notebook** —
one that defines components and one that executes the analysis for a market.
Regional Role is the clearest case. Build against a single market first, confirm
the components work, then confirm it scales across markets.

### 2.3 Modes for the four supporting analyses

| Analysis | Primary mode | Reason |
|---|---|---|
| Regional Role | Selected market, run once per region definition | The market's role and its regional comparison are the subject; region definition is the setup that shapes both, so the market is read through several competing boundaries |
| Corridor Opportunity Read | Selected market, synthesizing the preceding questions | It summarizes corridors that emerged from Q2/Q3/Q4 access work; it does not depend on a corridor engine |
| Parcel Watch | Selected county, optionally filtered to an area of interest | Parcel schemas and coverage vary by county; the durable method is a standardized county adapter, which is engine work rather than notebook work |
| Catchment | One or more selected points | It is a point-centered method; reuse comes from consistent weighting, metrics, and QA rather than an all-market ranking |

### 2.4 Common architecture boundary

The intended pattern is:

`governed datasets and engine outputs`
→ `analysis-owned method`
→ `reusable query/result surfaces`
→ `Marimo exploration and QA`
→ `issue-owned selection and presentation`

Explanation notebooks may define analysis-specific baskets, classifications,
comparisons, and thresholds. They must not locally rewrite source taxonomy,
geography identities, Phase 7 zones, or Time-Series results. Corridor
Intelligence is no longer in this list: it is a paused prototype with no
consumer contract, and corridor work in this family is analysis-local.

DuckDB remains the canonical data layer where managed tables already exist.
Early analysis-specific logic may remain in notebook queries until a second
consumer proves that it should become a shared method or mart.

**One deliberate exception to the promotion rule.** The access/gradient spine in
Section 2.5 has five known consumers before any of them is written. Waiting for
a second consumer to prove reuse would mean discovering the shared method on the
third notebook, after two have already grown incompatible versions. It is
specified once, in Q2, by design.

### 2.5 The shared access spine

Most of the numbered questions run on the same underlying shape:

> **define centers → measure distance or access from them → measure what varies
> across that gradient.**

What changes between questions is the input used to construct the centers and
the dependent variable measured across the gradient. This is the family's main
source of reuse, and the 15-minute-city concept is the frame that connects it.

**The method is defined once, in Q2.** Q2 establishes the operational definition
of a 15-minute city — what a center is, how reach is measured, what counts as
access — using job centers as the center input. Later questions re-run that same
method with a different center input:

| Analysis | Center input | Measured across the gradient |
|---|---|---|
| Q2 | Job centers from LODES WAC/RAC | Housing cost and housing units |
| Q3 | Prior built footprint and existing centers | Growth: population, units, permits |
| Q4 | POI clusters by category | Daily-needs access |
| Q6 | Anchor cities / candidate downtowns | Whether the metro has one center or several |
| Catchment | A declared point | Whatever the point question asks |

This sequencing is deliberate and is itself a test. Re-running one method
against several center-construction inputs tells us whether the 15-minute
definition holds up, or whether it only works for job centers. If Q4's POI-built
centers produce an incoherent result under Q2's method, that is a finding about
the method, not only about Q4.

**Consequences for the build:**

- Q2 must be specified and built before Q3, Q4, and Q6. The spec order in
  Section 8 reflects this.
- Q2's spec must state the definition explicitly enough that a later question can
  adopt it without reinterpretation: center construction rule, reach measure,
  threshold, and what a "center" minimally requires.
- Each later question declares which parts of the spine it adopts unchanged and
  which it deliberately varies, with the reason.
- Straight-line distance remains the v0 reach measure across all of them.
  Network travel time is a single shared challenger, tested once, not
  re-litigated per question.

## 3. Current Readiness Snapshot

This snapshot uses the engine-local documentation and the current shared
DuckDB, not only the older program status table.

### 3.1 Useful inputs already present

- National multi-grain ACS-derived housing, population, migration, and income
  tables cover 2012–2024, including tract rows.
- `gold.housing_core_wide` has tract housing stock, vacancy, value, rent, and
  tenure measures. Building permits are present at CBSA, county, and some
  Place grains, but not tract or ZCTA grain.
- `gold.housing_market_wide`, `silver.fhfa_hpi`, and
  `silver.zillow_zhvi` provide current price series at CBSA, county, and ZCTA
  grains. They do not currently provide a managed tract price series.
- National 2023 LODES WAC/RAC is present at tract, county, state, division,
  and CBSA grains. OD flow data is not present.
- `silver.bls_oews` is now present for 2025 at CBSA and state grain. Q2's
  affordability half no longer has an OEWS ingestion blocker, although it still
  has a wage/income normalization problem to solve.
- County and state IRS migration flows are present for 2012–2022.
- Benchmarking, Time-Series, Phase 7 zone outputs, and the current Geography
  identity/relationship surfaces exist.
- Governed POI and Infrastructure runs now exist for both Richmond and
  Jacksonville.
- Corridor Intelligence is a **paused prototype**. Jacksonville and Richmond
  artifacts are method reference only, not a consumer dependency, consistent with
  `docs/build_sequence.md`. No Explanation analysis should be gated on it.
- The Jacksonville Place Intelligence build contains a working catchment,
  tract apportionment, demographic/profile, daytime population, POI, and
  barrier workflow.
- A Jacksonville parcel standardization and screening path exists in legacy
  ROF work, but there is no current cross-county parcel contract or national
  parcel layer in the shared warehouse.

### 3.2 Readiness by analysis

| Analysis | What can start now | Main gate before a complete answer | Planning status |
|---|---|---|---|
| Regional Role | Build the region-definition lenses, then the market-role and comparison surfaces, against a single market using Position, WAC/RAC, industry, geography, benchmarking, and IRS migration flows | LODES OD for a true commute shed; a manual megaregion layer if that lens is used | Start now; region definition is the first deliverable, role and comparison the payload |
| Q6 One Metro? | National county balance, industry similarity, employment-center, and polycentricity prototype | LODES OD or an equivalent flow matrix for functional integration; Q2's access method for the anchor-city read | Prototype now; do not claim integration yet |
| Q1 Supply or Demand | National multi-grain housing diagnostic from existing Gold and Silver tables | A declared submarket unit, an operational definition of `inexpensive`, and rules for reconciling tract stock with Place/county permits and ZCTA price trends | Ready for a v0 spec and notebook |
| Q2 Job-Proximity and Affordability | Straight-line v0 using existing tract job-center evidence, ACS tract home-value and rent levels, tract income, and 2025 OEWS; ZCTA price series for supporting trend context | A reusable job-center surface, the 15-minute operational definition, and a defensible income/wage/cost comparison | Ready for v0; carries the shared spine, so it gates Q3/Q4/Q6 |
| Q3 Where Growth Lands | Input and coverage audit using tract population and housing histories | A 2010-to-2020 tract harmonization decision, an operational infill/greenfield definition, and Q2's access method | Geography/method slice first; then reuse Q2 |
| Q4 Daily-Needs Access | Richmond and Jacksonville basket design and access-method pilot from governed POIs | National POI coverage, a validated basket, and Q2's access method applied to POI-built centers | Market-pilot ready; not nationally ready |
| Corridor Opportunity Read | Nothing yet; it summarizes the questions above | Q2, Q3, and Q4 producing corridor-shaped results worth synthesizing | Last in sequence; no engine gate |
| Parcel Watch | Audit the Jacksonville ROF workflow to inform the parcel engine's adapter contract | A parcel engine providing normalized assessor data and a listings watch list | Analysis is gated on the proposed engine, not on corridors |
| Catchment | Wrap the existing Jacksonville method in a Marimo method notebook and test more than one point | Decide which current v0 assumptions remain: areal weighting, Euclidean rings, and water-adjusted companion rings | Ready to build first |

## 4. Shared Requirements for the Question Notebooks

This is the **starting scaffold** for each numbered notebook, not a fixed
contract. It is a good default to begin from, and a spec may narrow it — most
often by dropping national surfaces that its declared posture in Section 2.2 does
not call for. Where a spec drops something, it says why.

The QA and interpretation requirements below are the exception: those are a
family-wide floor and apply regardless of posture, because they are about
reproducibility rather than scope.

### Inputs and controls

- `scope`: `all` or `market`
- `cbsa_code` when `scope: market`
- explicit source vintages and method version
- geography and coverage selectors only where they materially affect the
  question
- thresholds exposed for sensitivity review, not for hand-tuning one market
- read-only access to governed engine and mart outputs

### Minimum analysis surfaces

- coverage and provenance summary before interpretation
- national coverage table showing included and excluded CBSAs with reasons
  *(national-posture analyses only)*
- national distribution or typology derived from sub-CBSA results
  *(national-posture analyses only)*
- selected-market component table at the method's native grain
- at least one selected-market map when the question is spatial
- comparison against national, Census Division, and the Act 1 peer set where
  those comparisons are meaningful
- a plain-language result status such as `strong signal`, `mixed`,
  `no clear signal`, or `insufficient coverage`
- a small table of candidate findings for downstream issue review

### QA and interpretation requirements

- preserve the native grain and vintage of every measure
- distinguish levels, changes, rates, counts, and modeled classifications
- do not allocate a non-additive measure without a declared method
- do not treat ZCTAs as postal delivery ZIPs
- do not infer travel, access, or commuting flows from straight-line proximity
- report missing coverage and excluded markets rather than silently narrowing
  the universe
- test threshold sensitivity before locking a classification, nationally where
  the analysis has a national run and across markets otherwise
- keep final chart styling, issue narrative, and featured-market choices out of
  the notebook contract

### Suggested analysis folder shape

```text
explanation/<analysis>/
├── README.md
├── EXPLANATION_<ANALYSIS>_SPEC.md
├── EXPLANATION_<ANALYSIS>_NOTEBOOK.py
├── queries/
└── figures/
    └── <scope-or-market>/
```

A separate headless runner should be added only when the method has stable
expectations worth testing outside Marimo. It is not required to start every
exploratory notebook.

## 5. Analysis Requirements

### 5.1 Regional Role

**Question:** How does this market fit into its broader region economically,
demographically, and functionally?

Regional Role should overlap with Position without duplicating it. Profile,
Peers, and Trajectory supply identity and comparative context; Regional Role
adds external relationships and division of labor.

**Primary analytical unit:** selected CBSA, its member counties, surrounding
counties and metros, read through several competing region definitions.

Like Position, this is best treated as a **workbench** rather than a single
fixed analysis.

**Initial inputs:**

- Position Profile, Peers, and Trajectory outputs
- Benchmarking and Geography identities/rollups
- LODES WAC/RAC jobs, workers, earnings bands, and industry mix
- industry specialization and economic-base measures
- IRS county migration origins, destinations, people, and AGI flows
- Infrastructure context for major interregional connections where useful
- later: LODES OD for commute shed and cross-boundary commuting

**V0 method — three parts, in order.**

The analysis has three subjects, and all three matter. Region definition comes
first because everything downstream depends on it, but it is the setup, not the
point.

**Part 1 — Define the region.** The biggest single piece of work, and genuinely
unsettled. Each definition below acts as a filter on the analysis, and we run
under each to see how the read changes.

| # | Lens | Strength | Weakness |
|---|---|---|---|
| 1 | Census division | Easy to explain, understand, and produce | Edge markets fit badly — does Richmond belong to the South Atlantic, or to the DC/Maryland/Delaware orbit? |
| 2 | State | Clear and legible | States can be small; a Delaware metro's state context is thin |
| 3 | Nearby counties and metros | Often the most meaningful | Needs a real construction rule. Candidate: find state borders within X miles, then take CBSAs and counties from those states — using both state boundaries, which maps read well, and physical proximity |
| 4 | Megaregions | Genuinely interesting framing; the eleven US megaregions | New to the repo, manual to bring in, and only works for markets inside one. Include as a labeled lens; do not block on it |

**Functional labor sheds are an output of this analysis, not an input lens.**
They were previously listed as a fourth definitional lens; they belong on the
output side, produced once LODES OD exists.

**Part 2 — Establish how the market fits.** With a region defined, characterize
the market's actual role within it: what it specializes in, how jobs and workers
balance, where people and money move to and from, and what function it serves
that its neighbors do not. This is the substance of the analysis and the basis of
the market-role hypothesis.

**Part 3 — Compare.** Place the market against the rest of the region and against
nearby metros, through tables and maps. This is the part closest to our Position
products.

Region definition also feeds back into Parts 2 and 3: because each lens produces
a different comparison set, the fit and comparison reads shift as the boundary
moves. The industry-role comparison is the most sensitive to this, and showing
how it changes across lenses is a finding in its own right — but it supplements
the role and comparison work rather than replacing it.

Do not label WAC/RAC balance as inflow/outflow; that claim requires flows.

**Output analyses, each run with the defined region as input:**

- **Regional comparison** — comparison table and map placing the market in
  context. Select KPIs for the table and for map color. Closest to our Position
  products.
- **Job/worker balance** — map of inflows and outflows. May or may not amount to
  much; worth testing.
- **Industry role comparison** — what the market specializes in versus the rest
  of the region. The most sensitive to region definition, and the best place to
  show how the read changes across lenses.
- **IRS and LODES origin/destination** — maps of how people move in and out,
  separating more permanent moves (IRS) from commuting patterns (LODES).
- **Nearby metro comparison** — an extension of the benchmarks.
- **Infrastructure map** — built environment and network comparison.
- **Market role hypothesis** — written up manually from the above.

**Build approach:** define components first and reuse what exists. Start with a
single market and build to see how it works. This is not a national build beyond
confirming it scales across markets. Consider splitting into a setup notebook
that defines the region lenses and components, and a run notebook that executes
the analysis for a market.

**Later spec must lock:** the nearby-region construction rule (the X-mile border
threshold), whether megaregions are in scope for v0, base/traded industry
treatment, minimum migration-flow disclosure rule, and what evidence qualifies a
role label.

### 5.2 Q6 — One Metro?

**Question:** Is this really one metro — and if not, how many centers does it
have?

The scope here is deliberately wider than the original county-integration
framing. Two related questions sit under it:

1. Do the CBSA's outlying counties belong to the same labor market, or are they
   administratively attached with weak integration?
2. Does the metro have multiple anchor cities? This is the more interesting half.

The second question uses the 15-minute-city method from Q2 as a proxy for the
number of city centers: run Q2's access method with anchor cities / candidate
downtowns as the center input, and see how many coherent centers the metro
actually supports. Widening the scope this way makes the question clearer, even
though it is really more than one question.

**Primary analytical unit:** county within CBSA for the integration read;
candidate centers and their access surfaces for the polycentricity read.

**Initial inputs:**

- Regional Role comparison surfaces
- county and tract LODES WAC/RAC
- county industry mix and jobs/resident-workers balance
- existing tract job-center evidence
- Phase 7/Internal Structure context where it helps describe polycentric form
- required for the complete method: LODES OD county-to-county and tract-to-
  workplace flow summaries

**V0 method:** prototype county economic role, employment-center distribution,
industry similarity, and polycentricity nationally. Treat these as structural
evidence, not a functional-integration score. Add OD shares when available,
then test how much each outlying county sends to the core and receives from the
rest of the CBSA.

For the multi-anchor read, the outputs to work from are **commute flows, job
corridors, and amenity clusters** — the same three surfaces that Q2 and Q4
produce. Q6 is largely a re-reading of those at metro scale, asking whether they
resolve into one center or several.

**Minimum outputs:** county role table, county integration matrix after OD,
employment-center map, core/outlying comparison, candidate anchor-city inventory
with its access surfaces, sensitivity table for the integration rule, and an
explicit `integrated`, `mixed`, `weak`, or `insufficient flow data` result.

**Later spec must lock:** definition of the core, numerator and denominator for
commuting shares, multidirectional versus core-directed integration, treatment
of cross-CBSA flows, polycentricity measure, and classification thresholds.

### 5.3 Q1 — Supply or Demand

**Question:** Where housing is relatively inexpensive, does the evidence point
to abundant supply, weak demand, or a mixed condition?

**This is the family's clearest national analysis.** Housing genuinely
nationalizes: build the national analysis first, then move into market-specific
work.

**First task is defining `inexpensive`,** both nationally and locally. It should
be a function of cost versus wages — again both local and national. Nothing else
in the analysis is stable until that definition is.

**Primary analytical unit:** tract for housing stock and resident conditions,
with Place/county permit evidence and ZCTA/county price trends kept as
separate, labeled lenses.

**Initial inputs:**

- `gold.housing_core_wide` for stock, tenure, vacancy, rent/value, and permits
- `gold.housing_market_wide`, `silver.fhfa_hpi`, and Zillow ZHVI/ZORI for
  level and appreciation context
- `gold.population_demographics` and `gold.migration_wide` for demand signals
- Geography relationships and Benchmarking
- Time-Series outputs where an existing governed trend can be reused

**V0 method:** build separate supply and demand component families before any
combined classification. Supply should include stock composition, vacancy,
housing-unit change, and permit intensity at their valid grains. Demand should
include population change, migration, occupancy, price level, and price/rent
appreciation. Use the combination to classify submarkets as supply-supported
affordability, weak-demand affordability, pressure/shortage, or mixed.

Work broad-to-narrow: establish broad market signals first, then go submarket
with supply-versus-demand scores and their relationship to cost.

This is the family's best opportunity to build regression practice, alongside Q2.

Do not assign county or Place permits to tracts. Do not combine price level and
appreciation into one unlabeled housing-price measure.

**Main outputs under consideration:**

- relative cost distributions (box plots or similar)
- a supply-versus-demand formula producing an **overheating index** score
- quadrant scatter graphs of key variable relationships, at both submarket and
  CBSA level
- maps of submarket metrics, highlighting both cheap and expensive areas
- classifications of tracts and ZIP codes

**Minimum outputs:** national component distributions, CBSA typology summary,
selected-market supply/demand quadrant, small-area component table, tract map,
supporting permit and ZCTA trend views, and classification sensitivity.

**Later spec must lock:** the operational meaning of `inexpensive` as a
cost-to-wage function, submarket unit, component definitions and weights, the
overheating index formula, time windows, minimum coverage, multi-grain
combination rule, and no-signal rule.

### 5.4 Q2 — Job Proximity, Housing, and Affordability

**Merged analysis.** This section absorbs what was previously Q5, "Afford to
Live Near Jobs." The two questions ran on identical inputs and outputs and
differed only in dependent variable — housing units versus housing cost. They
are one analysis with two dependent variables. Two separate publication hooks
remain available, but that is an **issue-layer** decision, not a reason to build
two notebooks.

**Question:** What does proximity to the market's major employment centers cost
in housing value or rent, and can households with local incomes afford to live
there?

**This analysis carries the shared access spine.** Its most important output is
not the gradient itself but the reusable operational definition of a 15-minute
city — center construction, reach measure, threshold — that Q3, Q4, Q6, and
Catchment re-run with different center inputs. Specify that definition to be
adopted without reinterpretation.

**Primary analytical unit:** tract for job centers, housing level, and income;
ZCTA can support market-price trends when its distinct grain remains visible.
CBSA occupational wages are context, not tract-level precision.

**Initial inputs:**

- existing Industry D3 tract job-center evidence from LODES WAC/RAC
- tract geometry and distance-safe spatial operations from Geography
- ACS tract median home value, median rent, household income, and housing burden
- tract LODES WAC/RAC earnings bands and workplace/resident composition
- 2025 CBSA/state OEWS wages
- ZCTA Zillow/FHFA price and rent series as an optional supporting lens
- Infrastructure only for a named physical-context experiment

**V0 method, in order:**

1. **Define job centers.** A good, reusable definition is required here, not
   optional — four later analyses depend on it.
2. **Build tract gradients by physical proximity first**, network effects second.
3. **Measure what varies across the gradient** — housing cost, housing units, and
   simple counts like how many people live there.
4. **Estimate the relationship** with regression, for both cost and units,
   reporting coverage and residuals.
5. **Layer in affordability** by comparing tract housing cost and resident income
   against the earnings profile of nearby job centers.

Keep household income, individual job earnings, and occupational wages separate.
Any modeled bridge between them must be explicit.

Start with straight-line distance. Network distance or travel time is a later
challenger, not a prerequisite, and is tested once for the whole family rather
than per question. Infrastructure may explain a visible anomaly but must not be
treated as a routing network under its current contract.

**Minimum outputs:** the reusable job-center and 15-minute definitions, national
gradient summary, center inventory, selected-market center map, binned distance
curve, the regression equation and model table, tract residual map, affordability
mismatch distribution, residence-versus-workplace comparison, and sensitivity to
center selection, price source, and normalization.

**Later spec must lock:** center selection rule and the 15-minute operational
definition, treatment of multiple centers, origin point for tracts, distance
bins/model form, housing measure, controls, minimum observations, whether
gradients are descriptive or adjusted, affordability standard,
household-versus-worker unit, wage source hierarchy, tenure treatment, and time
alignment.

### 5.5 Q3 — Where Growth Lands

**Question:** Is recent population and housing growth landing in infill areas,
greenfield edges, already-developed outer centers, or nowhere?

**Primary analytical unit:** harmonized tract, interpreted against the prior
built footprint and market edge.

**Initial inputs:**

- tract population and housing-unit histories
- Geography temporal edges and tract geometry
- housing structure, density, and vacancy context
- permit evidence at its available Place/county grain as supporting context
- Phase 7 zone types and Infrastructure only as interpretation layers

**V0 method:** first restate comparable population and housing-unit counts on a
declared tract vintage. Then classify growing tracts from their prior density,
location relative to the existing developed footprint, and change in housing
units and population. `Infill` and `greenfield` must be measured conditions,
not labels inferred from whether a tract looks central on a map.

**Minimum outputs:** harmonization QA, national growth-location distribution,
CBSA summary, selected-market tract classification map, population-versus-unit
change table, and a residual/unclassified group.

**Later spec must lock:** comparison years, harmonization basis, growth floor,
developed-footprint baseline, infill/greenfield/outer-center rules, treatment
of large rural tracts, and negative/no-growth classes.

### 5.6 Q4 — Daily-Needs Access

**Question:** Which parts of a metro have practical proximity to a defensible
basket of everyday needs?

**Primary analytical unit:** tract in the national and market summary, derived
from governed POI points and an explicitly defined reach method.

**Initial inputs:**

- declared POI Engine runs and governed taxonomy mappings
- tract identity and geometry from Geography
- population and selected demographic denominators
- Place Intelligence method references
- Infrastructure only if the selected access method names a barrier or
  physical-context requirement

**V0 method:** use Richmond and Jacksonville to define a narrow daily-needs
basket, coverage rules, and a simple proximity/reach measure. Review category
coverage and urban-form sensitivity before acquiring or processing national
POIs. Only after the basket and score survive the two-market test should the
same method scale nationally.

POI counts are inputs, not access. The analysis owns the amenity basket and
reach definition. The POI Engine continues to own source identity, provenance,
classification, and assignment.

**Minimum outputs:** category/mapping coverage, amenity inventory, tract access
components, selected-market access map and distribution, national comparison
after scale-out, sensitivity to basket/reach choices, and an unavailable result
where source coverage is inadequate.

**Later spec must lock:** basket categories, multi-category sufficiency rule,
distance or reach method, scoring and caps, population weighting, urban/rural
comparability, treatment of barriers, and national source/run strategy.

### 5.7 Corridor Opportunity Read

**Reframed.** This is no longer a standalone analysis sitting on top of a
Corridor Intelligence engine. That engine is a paused prototype and has been
dropped as a dependency. Corridors are instead emerging organically from the
15-minute-city work in Q2, Q3, and Q4 — the access spine keeps producing
corridor-shaped results. This analysis becomes the **closing synthesis** of the
questions above, and should run last in the sequence.

**Question:** Taken together, what do the preceding analyses say about which
corridors in this market deserve deeper attention, and why?

**Primary analytical unit:** a corridor-shaped area of interest identified by the
upstream questions, within one selected market.

**Initial inputs:**

- Q2 access, gradient, and affordability surfaces
- Q4 POI clusters and daily-needs corridors
- Q3 growth-location classification
- Regional Role and Trajectory evidence where relevant
- Internal Structure market anatomy
- POI and Infrastructure context through their governed handoffs
- Jacksonville/Richmond Corridor Intelligence artifacts as **method reference
  only**, not as a candidate source

**V0 method:** synthesize across three evidence families:

1. structural role and connectivity
2. people, jobs, access, and housing conditions
3. current trajectory and issue relevance

It should not create one universal Investment Score before individual evidence
families have been tested.

**Minimum outputs:** comparison matrix across identified corridors,
selected-corridor profile, map, evidence-and-caveat table, one-sentence thesis
candidates, and suggested follow-on analyses.

**Later spec must lock:** how a corridor is identified from upstream outputs now
that no engine supplies membership, comparison dimensions, evidence
normalization, selection versus ranking, treatment of no-opportunity results, and
handoff to issue-owned naming/stat blocks.

### 5.8 Parcel Watch

**Split into an engine and an analysis.** The bulk of this work — acquiring
county assessor records, scraping listings, normalizing them into a standard
schema — is ingestion and normalization, not analysis. It is a repeated
per-county pipeline with a contract, which is engine-shaped. A proposed **parcel
engine** is described in Section 12; this section covers only the analysis that
runs on top of it.

The engine owns: assessor acquisition and per-county adapters, the scraped
listings watch list, the normalized parcel schema (pricing, land use, sale
history, ownership, geometry), and provenance/freshness.

The analysis owns: the underuse heuristic, ranking, and interpretation.

**Question:** Which parcels in a selected county appear underused or otherwise
worth monitoring, and how do they relate to an area of interest?

**Primary analytical unit:** standardized parcel, ranked within county first
and optionally filtered or re-ranked within an area of interest.

Countywide-first ranking is intentional: a countywide percentile makes the result
reusable and keeps an area filter from defining the comparison universe after the
fact. Note that the area filter is no longer a Corridor Intelligence candidate —
it is any selected area, including one identified by Q2/Q4 access work.

**Relationship to Catchment:** Catchment is a separate analytical process. It
does not build on Parcel Watch, but the two are used closely together — Catchment
supplies the "what is within X of this parcel" read.

**Initial inputs (supplied by the parcel engine):**

- **free county or state assessor records** as the default. A paid source would
  require its own engine to build, so it is not the starting assumption — but if
  Regrid or a similar national service turns out to be low cost, it is worth a
  look. Keep that as a short exploratory task during engine construction, not a
  prerequisite (see Section 12).
- parcel polygons and durable parcel/source identifiers
- land use, land and improvement value, building area where available, parcel
  area, ownership, last sale, and situs address
- Geography assignment
- legacy Jacksonville ROF parcel standardization and screening logic
- scraped listing evidence (Zillow, brokers, foreclosure lists) as a dated
  enrichment layer

County or state records are the system of record. Zillow ZHVI/ZORI are aggregate
market series, not parcel records. Scraped listings may add current asking status
or listing context, but must not be required to reproduce the base ranking.

**Start with a manual file and a manual universe.** Do not wait for a general
acquisition pipeline. Try assessor data first; where it is not available, a
scraped list from Zillow, brokers, or foreclosure listings is an acceptable
starting universe.

**V0 method:** take one county's normalized parcels, define an eligible universe,
derive transparent underuse indicators, and rank within county. The heuristic is
a candidate-for-purchase screen: is it beneath a certain cost, has it not sold in
X years, does it have a qualifying land use, is it within X distance of things we
care about. Keep component measures visible instead of hiding logic behind one
score.

**Minimum outputs:** source and join QA, county parcel inventory, component
ranking table, county map, selected-area filter, candidate detail table, and
data-freshness/provenance fields.

**Later spec must lock:** eligible land uses, underutilization definition and its
thresholds, required versus optional fields, missing-value behavior, score
weights or ranking rule, treatment of parcel assemblages, refresh cadence, and
whether scraped listings affect rank or only add context.

### 5.9 Catchment

**Question:** What population, demographic, housing, employment, amenity, and
physical-context evidence falls within a declared reach of a specific point?

**Primary analytical unit:** point × ring/reach × contributing tract.

**A lot of this is already built.** The main task is porting the existing work
from the property analyzer in the old Metro Deep Dive folder: geocoding points,
building Euclidean rings, and producing tract-ring weight tables. That makes it a
good place to start the family.

**Two roles beyond the point analysis:**

- It is how the family moves from broad question-style analyses toward specific
  properties — used closely with Parcel Watch, though not built on it.
- It is the second half of the 15-minute-city work: Q2 identifies the center
  point, and Catchment measures what is within X distance of it.

**Initial inputs:**

- point or address with geocoding provenance
- projected ring or later network-reach geometry
- tract geometry and demographic/economic/housing measures
- LODES WAC/RAC for daytime context
- governed POI and Infrastructure outputs where requested
- existing Place Intelligence D1–D3 functions and artifacts

**V0 method:** promote the existing transparent method rather than the app:

- geocode and resolve the point
- build projected Euclidean ring bands
- create a tract-to-ring areal weight table
- aggregate counts and carefully handle rates and medians
- retain baseline rings plus a water-adjusted companion where relevant
- add daytime jobs/workers, POIs, and barrier diagnostics as optional modules

The canonical reusable output is the weight/contribution table. Demographic
profiles and maps are downstream products of that table.

Areal weighting is the current v0. A density-based approach is a candidate for
v2, not a prerequisite. The open item is nailing down which metrics belong in the
standard profile.

**Minimum outputs:** resolved point, ring geometries, tract contribution table,
coverage/reliability QA, long metric profile, benchmark table, daytime context,
and optional POI/barrier views.

**Later spec must lock:** point identity and override rules, default rings,
areal versus dasymetric status, metric aggregation rules, median handling,
reliability flags, barrier behavior, and trigger for a routed network method.

## 6. Dependency and Reuse Map

| Shared capability | First Explanation consumer | Later reuse |
|---|---|---|
| **15-minute access method and center definition** | **Q2 (defined, not discovered)** | **Q3, Q4, Q6, Catchment, Corridor Opportunity Read** |
| Regional comparison surfaces and region lenses | Regional Role | Q6, Q1–Q4 context, Act 3 regional comparisons |
| LODES OD flow foundation | Q6 or Regional Role | commute sheds, work-geography themes |
| Housing component cut | Q1 | Q2 affordability, Q3, Housing satellite, A2, A7 |
| Reusable job-center surface | Q2 | Q6, Internal Structure, Corridor Opportunity Read |
| Tract temporal harmonization | Q3 | other tract change analyses and hazard/growth themes |
| Daily-needs basket and POI clusters | Q4 | Corridor Opportunity Read and livability summaries |
| Normalized parcel schema and county adapter | Parcel engine (Section 12) | Parcel Watch, later parcel/site products |
| Catchment contribution table | Catchment | Parcel Watch detail, site analyses, point-based issue views |

The promotion rule holds for everything except the first row: keep first-use
logic in the analysis and move it to a shared component or `foundations/` only
after a second consumer uses the interface unchanged.

The access method is the deliberate exception. Five consumers are known before
any is written, so it is specified once in Q2 rather than discovered later. See
Section 2.5.

## 7. Proposed Build Sequence

This sequence separates work that can produce a useful notebook now from work
that should wait for a real upstream contract.

The ordering constraint that drives this sequence is the access spine: **Q2
defines the method that Q3, Q4, and Q6 re-run.** Q2 therefore moves ahead of its
consumers.

### Wave 0 — Confirm narrow shared inputs

1. Define the common Marimo controls and coverage-result vocabulary, and have
   each analysis declare its national posture per Section 2.2.
2. Expose the existing Industry D3 job-center logic as a read-only, reproducible
   query surface for Q2.
3. Define a first housing component cut without creating a broad Housing Engine
   in advance.
4. Record LODES OD as a shared source gap for Regional Role and Q6; choose one
   of those analyses as the ingest's first consumer when its spec opens.

### Wave 1 — Startable analyses

1. **Catchment:** fastest path to a working Explanation method notebook. Port the
   property-analyzer work from the old Metro Deep Dive folder.
2. **Q1 Supply or Demand:** strongest national-ready dataset base, the family's
   one true national analysis, and high reuse for housing themes.
3. **Q2 Job Proximity, Housing, and Affordability:** straight-line proximity and
   current housing measures — and, critically, **the 15-minute definition the
   rest of the family will re-run.** Treat that definition as a Wave 1
   deliverable, not a by-product.
4. **Regional Role v0:** build the region-definition lenses first, then the
   market-role and comparison surfaces, labeling commute-shed content as
   deferred.

These can overlap in calendar time, but each DuckDB materialization or shared
data-layer change should remain sequential. Q2's access definition should settle
before Wave 2 opens.

### Wave 2 — Analyses that re-run the spine or need one focused foundation gap

1. **Q4 Daily-Needs Access:** two-market pilot on Richmond and Jacksonville. Lock
   the basket, then apply Q2's access method with POI clusters as the center
   input.
2. **Q3 Where Growth Lands:** open the tract harmonization and growth-class
   method as one vertical slice, then read growth against Q2's access surfaces.
3. **Q6 One Metro?:** reuse Regional Role and apply Q2's method with anchor
   cities as the center input; add OD and integration thresholds before treating
   the answer as complete.
4. **Q4 national run:** acquire/process broader POI coverage only after the
   two-market method review passes.

### Wave 3 — Synthesis and the parcel track

Wave 3 is no longer gated on Corridor Intelligence. Dropping that engine removes
the calibration/validation/handoff chain that previously blocked this wave.

1. **Corridor Opportunity Read:** run last, as a synthesis of Q2, Q3, and Q4.
2. **Parcel engine, then Parcel Watch:** stand up the normalization path for one
   county (Section 12), then build the analysis on top of it. This track is
   independent of the synthesis above and can run in parallel.
3. Reuse **Catchment** for selected parcels or other issue points when the
   question calls for point-centered context.

## 8. Spec Queue and Definition of Ready

An individual analysis is ready for a full implementation spec when:

- its analytical unit and comparison universe are named
- its required source tables or engine products are identified at field/grain
  level
- its blocking versus optional inputs are separated
- the initial method can be described without unresolved ownership conflicts
- a first market or national coverage set is available
- the minimum outputs and QA checks are testable
- any lock that would materially change the result is listed for review

Recommended spec order:

1. Catchment
2. Q1 Supply or Demand
3. **Q2 Job Proximity, Housing, and Affordability** — carries the shared access
   definition, so it must precede items 4, 5, and 6
4. Regional Role
5. Q4 Daily-Needs Access
6. Q3 Where Growth Lands
7. Q6 One Metro?
8. Corridor Opportunity Read
9. Parcel Watch *(after the parcel engine)*

Q5 no longer appears: it is merged into Q2.

This is a requirements sequence, not a publication order. Position routing
can pull a ready analysis forward for a particular market — with one exception:
Q2's access definition should not be leapfrogged by Q3, Q4, or Q6, since they
re-run it.

**Note on `docs/build_sequence.md`:** that document carries its own E1–E10
Explanation ordering which predates these changes. It still lists Q5 separately,
orders Q2 sixth (after Q3 and Q4, which now depend on it), and describes Parcel
Watch as corridor-gated. It should be reconciled with this plan.

## 9. Decisions — Confirmed

These five were open in the previous version and are now settled:

1. **Meaning of national — confirmed with a qualification.** One national method,
   used for individual CBSA runs, with CBSA-specific outputs retained. The
   qualification: these notebooks establish and run a national *method*; they do
   not all produce a national *analysis*. See Section 2.2.
2. **Regional lenses — confirmed.** Keep them distinct, and the geography engine
   should control this long term. Functional labor shed moves from input lens to
   output; megaregions are added as a labeled lens.
3. **Parcel system of record — confirmed with a change.** Free county or state
   assessor sources are the default; a licensed source would require its own
   engine to build. Start with a manual file. A low-cost national service such as
   Regrid remains a short exploratory task during engine construction — a
   possible backup, not the plan of record.
4. **Parcel universe — confirmed with a change.** Start with a manual universe:
   assessor data where available, otherwise a scraped list from Zillow, brokers,
   or foreclosure listings.
5. **Catchment v0 — confirmed.** Areal Euclidean rings carry forward. A
   density-based weighting is a v2 candidate, not a prerequisite.

### Still open

- Whether megaregions are in scope for Regional Role v0, given manual sourcing
  and partial national coverage.
- The X-mile threshold in the nearby-counties region construction rule.
- Which metrics belong in the standard Catchment profile.
- Whether the parcel engine is scaffolded now or after this plan is reviewed
  (Section 12).

## 10. Explicit Non-Goals for This Family Plan

- no final equations, score weights, or thresholds
- no new catch-all Spatial or Housing engine
- no automated market routing or issue assembly
- no national parcel acquisition before one county contract works
- no national POI scale-out before Q4's basket and access method are reviewed
- no commuting-integration claims from WAC/RAC without OD
- no revival of Corridor Intelligence as an engine dependency; corridor work is
  analysis-local and emerges from the access spine
- no investment conclusion from a corridor read
- no *assumption* of a paid parcel source, and no licensing commitment before a
  free-source path has been tried and costed against it
- no promotion of the Place Intelligence app as the Catchment product
- no divergent per-question reinvention of the 15-minute definition
- no final issue graphics or prose

## 11. Primary References for Child Specs

- `metro-deep-dive-program/metro_deep_dive_program.md`
- `metro-deep-dive-program/mdd_classification_workbook.md`
- `metro-deep-dive-program/docs/build_sequence.md`
- `metro-deep-dive/docs/deep_dive_question_bank.md`
- `metro-deep-dive-program/analyses/position/internal_structure/POSITION_INTERNAL_STRUCTURE_SPEC.md`
- `metro-deep-dive-program/engines/geography/CONTRACT.md`
- `metro-deep-dive-program/engines/poi/CONTRACT.md`
- `metro-deep-dive-program/engines/infrastructure/CONTRACT.md`
- `metro-deep-dive-program/engines/corridor_intelligence/CONTRACT.md` *(method
  reference only; paused prototype, not a dependency)*
- `metro-deep-dive/metro-area-explorer/place_intelligence/METHODS_MEMO.md`
- `metro-deep-dive/metro-area-explorer/place_intelligence/SPEC_PLACE_INTELLIGENCE.md`
- `metro-deep-dive/metro-area-explorer/place_intelligence/TECHNICAL_ARCHITECTURE.md`
- `metro-deep-dive/archive/markets/jacksonville/05_parcels/parcel_standardization/README.md`

## 12. Proposed Parcel Engine

**Status: proposed, not scaffolded.** This section records what the engine would
need so the decision to build it can be made deliberately. Nothing under
`engines/` has been created.

### Why an engine rather than a notebook

Parcel Watch's real weight is not analysis — it is ingestion and normalization:
acquiring county assessor records, scraping listings, and reconciling wildly
varying schemas into something stable enough to analyze. That is a repeated,
contracted pipeline with per-source adapters, which is what the other engines in
this repo already look like.

The free-source default (Section 9, item 3) makes this permanent rather than
one-time. Free county and state assessors mean **a per-county adapter forever** —
there is no vendor normalizing them for us. That recurring cost is the accepted
price of avoiding a licensed source, and it is precisely the kind of cost an
engine exists to contain.

### Exploratory task: price a national source

Before committing to per-county adapters indefinitely, spend a short, bounded
effort checking what Regrid or a comparable national parcel service actually
costs. If one is cheap enough, it collapses most of the adapter work and changes
the engine's shape substantially.

Keep it timeboxed and keep it a backup. What to establish: per-county or national
pricing and licensing terms, refresh cadence, field coverage against the schema
below, and whether redistribution terms permit the outputs we want. The
free-source path remains the plan of record unless this comes back clearly
favorable — the question is decided during engine construction, not before it.

### Two parts, matching the two-part framing in the feedback

1. **Listings watch list** — scripted collection from Zillow, brokers, and
   foreclosure listings, producing a running list of parcels to watch. Lighter,
   more volatile, dated on every record.
2. **Assessor normalization** — acquiring county property records and
   normalizing them into a standard schema: pricing, land use, sale history,
   ownership, parcel and building area, geometry, situs address. Heavier, slower
   moving, and the actual system of record.

### What the engine would own

- per-county acquisition adapters and their refresh cadence
- the normalized parcel schema and its field-level contract
- durable parcel and source identifiers
- provenance and data-freshness fields on every record
- Geography assignment
- coverage reporting: which counties exist, at what vintage, with what gaps

### What it would not own

The analysis keeps the interpretation: eligibility filters, the underuse
heuristic and its thresholds, ranking, and any candidate-for-purchase screen.
The engine should not encode a view about which parcels are interesting.

### If green-lit, the first build would be

1. `engines/parcel/README.md` and a first-cut `CONTRACT.md`
2. one county adapter end to end — Jacksonville, reusing the legacy ROF
   standardization logic, since that is the one place a working path already
   exists
3. the normalized schema validated against a second county before the contract
   is treated as stable

A second county matters more than usual here: a schema derived from one assessor
will silently encode that assessor's quirks, and the whole point of the engine is
to absorb cross-county variation.
