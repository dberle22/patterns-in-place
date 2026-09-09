# Metro Deep Dive — Explanation Analyses Plan

**Status:** Directional family plan; ready to split into analysis-level specs

**Updated:** 2026-09-09

**Program home:** `metro-deep-dive-program/metro_deep_dive_program.md`, Section 3.2

**Primary planning source:** `metro-deep-dive-program/mdd_classification_workbook.md`

## 1. Purpose

This document defines the first build direction for the ten Explanation
analyses in the Metro Deep Dive program:

- six reusable question analyses: Q1 through Q6
- Regional Role
- Corridor Opportunity Read
- Parcel Watch
- Catchment

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

### 2.2 National-first rule for Q1 through Q6

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

### 2.3 Modes for the four supporting analyses

| Analysis | Primary mode | Reason |
|---|---|---|
| Regional Role | Selected market with national and regional comparison surfaces | The market is the subject; national data supplies its comparative context |
| Corridor Opportunity Read | Selected market and selected structural candidates | It interprets candidates produced upstream; it does not discover national corridors or change membership |
| Parcel Watch | Selected county, optionally filtered to a corridor or district | Parcel schemas and coverage vary by county; the durable method is a standardized county adapter and ranking workflow |
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
geography identities, Phase 7 zones, Corridor Intelligence membership, or
Time-Series results.

DuckDB remains the canonical data layer where managed tables already exist.
Early analysis-specific logic may remain in notebook queries until a second
consumer proves that it should become a shared method or mart.

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
- `silver.bls_oews` is now present for 2025 at CBSA and state grain. Q5 no
  longer has an OEWS ingestion blocker, although it still has a wage/income
  normalization problem to solve.
- County and state IRS migration flows are present for 2012–2022.
- Benchmarking, Time-Series, Phase 7 zone outputs, and the current Geography
  identity/relationship surfaces exist.
- Governed POI and Infrastructure runs now exist for both Richmond and
  Jacksonville.
- Corridor Intelligence Epics 1–3 are complete in the engine-local plan and
  Jacksonville review artifacts exist. Interactive method review,
  calibration, Richmond validation, and the managed consumer handoff remain.
- The Jacksonville Place Intelligence build contains a working catchment,
  tract apportionment, demographic/profile, daytime population, POI, and
  barrier workflow.
- A Jacksonville parcel standardization and screening path exists in legacy
  ROF work, but there is no current cross-county parcel contract or national
  parcel layer in the shared warehouse.

### 3.2 Readiness by analysis

| Analysis | What can start now | Main gate before a complete answer | Planning status |
|---|---|---|---|
| Regional Role | National comparison and selected-market v0 using Position, WAC/RAC, industry, geography, benchmarking, and IRS migration flows | LODES OD for a true commute shed; explicit definitions of each regional lens | Start now as a labeled partial method |
| Q6 One Metro? | National county balance, industry similarity, employment-center, and polycentricity prototype | LODES OD or an equivalent flow matrix for functional integration; a stated integration rule | Prototype now; do not claim integration yet |
| Q1 Supply or Demand | National multi-grain housing diagnostic from existing Gold and Silver tables | A declared submarket unit and rules for reconciling tract stock with Place/county permits and ZCTA price trends | Ready for a v0 spec and notebook |
| Q2 Job-Proximity Gradient | Straight-line v0 using existing tract job-center evidence and ACS tract home-value levels; ZCTA price series can provide supporting trend context | A reusable job-center surface and an explicit tract/ZCTA joining or comparison method | Ready for v0; network travel is a later experiment |
| Q3 Where Growth Lands | Input and coverage audit using tract population and housing histories | A 2010-to-2020 tract harmonization decision and an operational infill/greenfield definition | Geography/method slice first |
| Q4 Daily-Needs Access | Richmond and Jacksonville basket design and access-method pilot from governed POIs | National POI coverage and a validated access definition; network routing only if the pilot shows it is required | Market-pilot ready; not nationally ready |
| Q5 Afford to Live Near Jobs | National prototype using WAC/RAC, tract income/housing, job centers, and the now-present OEWS table | A defensible comparison between household income, job earnings bands, occupational wages, and housing cost | Ready for method design after Q2 |
| Corridor Opportunity Read | Spec the interpretation matrix against current Jacksonville candidate artifacts | Corridor Intelligence calibration, Richmond validation, consumer handoff, and candidate selection in Internal Structure | Requirements ready; execution gated |
| Parcel Watch | Audit and adapt the Jacksonville county workflow; define a standard parcel contract | County parcel acquisition/normalization, eligibility universe, and a selected county or candidate | Conditional; Jacksonville first |
| Catchment | Wrap the existing Jacksonville method in a Marimo method notebook and test more than one point | Decide which current v0 assumptions remain: areal weighting, Euclidean rings, and water-adjusted companion rings | Ready to build first |

## 4. Shared Requirements for Q1–Q6 Notebooks

Each numbered notebook should satisfy the following initial contract unless
its later spec explicitly narrows it.

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
- national distribution or typology derived from sub-CBSA results
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
- test threshold sensitivity nationally before locking a classification
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
counties and metros, and several explicitly named comparison lenses.

**Initial inputs:**

- Position Profile, Peers, and Trajectory outputs
- Benchmarking and Geography identities/rollups
- LODES WAC/RAC jobs, workers, earnings bands, and industry mix
- industry specialization and economic-base measures
- IRS county migration origins, destinations, people, and AGI flows
- Infrastructure context for major interregional connections where useful
- later: LODES OD for commute shed and cross-boundary commuting

**V0 method:** keep four meanings of region separate:

1. Census Division for a stable national benchmark
2. state context where a state comparison is meaningful
3. nearby counties and metros for geographic competition/complementarity
4. functional labor shed once OD exists

Compare the metro's jobs-to-workers balance, industry role, migration exchange,
trajectory, and peer position across those lenses. Do not label WAC/RAC balance
as inflow/outflow; that claim requires flows.

**Minimum outputs:** regional comparison table, jobs/workers balance,
industry-role comparison, IRS origin/destination summary, nearby-metro panel,
and a concise market-role hypothesis with evidence and limitations.

**Later spec must lock:** the nearby-region construction rule, base/traded
industry treatment, minimum migration-flow disclosure rule, comparison order,
and what evidence qualifies a role label.

### 5.2 Q6 — One Metro?

**Question:** Are the CBSA's outlying counties functionally tied to the same
labor market, or are they administratively attached with weak integration?

**Primary analytical unit:** county within CBSA, with internal employment
centers as supporting evidence.

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

**Minimum outputs:** county role table, county integration matrix after OD,
employment-center map, core/outlying comparison, sensitivity table for the
integration rule, and an explicit `integrated`, `mixed`, `weak`, or
`insufficient flow data` result.

**Later spec must lock:** definition of the core, numerator and denominator for
commuting shares, multidirectional versus core-directed integration, treatment
of cross-CBSA flows, polycentricity measure, and classification thresholds.

### 5.3 Q1 — Supply or Demand

**Question:** Where housing is relatively inexpensive, does the evidence point
to abundant supply, weak demand, or a mixed condition?

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

Do not assign county or Place permits to tracts. Do not combine price level and
appreciation into one unlabeled housing-price measure.

**Minimum outputs:** national component distributions, CBSA typology summary,
selected-market supply/demand quadrant, small-area component table, tract map,
supporting permit and ZCTA trend views, and classification sensitivity.

**Later spec must lock:** the operational meaning of `cheap`, submarket unit,
component definitions and weights, time windows, minimum coverage, multi-grain
combination rule, and no-signal rule.

### 5.4 Q2 — Job-Proximity Gradient

**Question:** What does proximity to the market's major employment centers
cost in housing value or rent?

**Primary analytical unit:** tract for job centers and housing-value level;
ZCTA can support market-price trends when its distinct grain remains visible.

**Initial inputs:**

- existing Industry D3 tract job-center evidence from LODES WAC/RAC
- tract geometry and distance-safe spatial operations from Geography
- ACS tract median home value and median rent
- ZCTA Zillow/FHFA price and rent series as an optional supporting lens
- Infrastructure only for a named physical-context experiment

**V0 method:** identify a reproducible set of job centers, calculate
straight-line distance from each residential tract to its nearest or assigned
center, and estimate the price/rent gradient with coverage and residuals. Run
nationally to compare gradient shape and strength, then inspect individual
markets.

Start with straight-line distance. Network distance or travel time is a later
challenger, not a prerequisite. Infrastructure may explain a visible anomaly
but must not be treated as a routing network under its current contract.

**Minimum outputs:** national gradient summary, center inventory, selected-
market center map, binned distance curve, model table, tract residual map, and
sensitivity to center selection and price source.

**Later spec must lock:** center selection rule, treatment of multiple centers,
origin point for tracts, distance bins/model form, housing measure, controls,
minimum observations, and whether gradients are descriptive or adjusted.

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

### 5.7 Q5 — Afford to Live Near Jobs

**Question:** Can households with local incomes afford housing near the
market's stronger job concentrations, and where is the largest mismatch?

**Primary analytical unit:** tract or tract-to-job-center relationship, with
CBSA occupational wages as context rather than false tract precision.

**Initial inputs:**

- Q2 job-center and distance surfaces
- tract LODES WAC/RAC earnings bands and workplace/resident composition
- tract ACS household income, rent, value, and housing burden
- 2025 CBSA/state OEWS wages
- Geography and Benchmarking

**V0 method:** compare tract housing cost and resident income with the earnings
profile of nearby job centers. Use LODES earnings bands for spatial workplace
evidence and OEWS for CBSA occupational wage context. Keep household income,
individual job earnings, and occupational wages separate; any modeled bridge
between them must be explicit.

**Minimum outputs:** national mismatch distribution, job-center affordability
table, selected-market housing/income/job map, residence-versus-workplace
component comparison, affected worker/resident counts where supportable, and
normalization sensitivity.

**Later spec must lock:** affordability standard, household-versus-worker unit,
wage source hierarchy, job-center catchment, housing tenure treatment,
normalization, time alignment, and equity breakdowns.

### 5.8 Corridor Opportunity Read

**Question:** Which already-identified structural candidates deserve deeper
issue attention, and what evidence explains their relevance?

**Primary analytical unit:** a versioned Corridor Intelligence candidate
within one selected market.

**Initial inputs:**

- Internal Structure market anatomy and selected Corridor Intelligence run
- structural candidate, membership, form, edge-evidence, and QA products
- routed Q2, Q4, Q3, Q5, Regional Role, or Trajectory evidence where relevant
- POI and Infrastructure context through their governed handoffs
- later Parcel Watch readiness as a downstream flag, not a candidate score

**V0 method:** compare existing candidates across three evidence families:

1. structural role and connectivity
2. people, jobs, access, and housing conditions
3. current trajectory and issue relevance

The analysis may shortlist and interpret candidates. It may not merge, split,
reassign, or rename them. It should not create one universal Investment Score
before individual evidence families have been tested.

**Minimum outputs:** candidate comparison matrix, selected-candidate profile,
map with core/bridge lineage, evidence-and-caveat table, one-sentence thesis
candidates, and suggested follow-on analyses.

**Later spec must lock:** minimum engine QA status, candidate eligibility,
comparison dimensions, evidence normalization, selection versus ranking,
treatment of no-opportunity results, and handoff to issue-owned naming/stat
blocks.

### 5.9 Parcel Watch

**Question:** Which parcels in a selected county appear underused or otherwise
worth monitoring, and how do they relate to a selected corridor, district, or
other place of interest?

**Primary analytical unit:** standardized parcel, ranked within county first
and optionally filtered or re-ranked within a structural candidate.

This countywide-first definition is an intentional refinement of the earlier
program wording, which described Parcel Watch only as follow-through inside a
selected corridor. A countywide percentile makes the result reusable and keeps
the candidate filter from defining the comparison universe after the fact.

**Initial inputs:**

- county assessor/property records or a licensed normalized parcel source such
  as Regrid
- parcel polygons and durable parcel/source identifiers
- land use, land and improvement value, building area where available, parcel
  area, ownership, last sale, and situs address
- Geography assignment and optional Corridor Intelligence membership
- legacy Jacksonville ROF parcel standardization and screening logic
- optional broker/listing evidence as a dated enrichment layer

County records or a governed parcel provider should be the system of record.
Zillow ZHVI/ZORI are aggregate market series, not parcel records. Scraped
broker listings may add current asking status or listing context, but they
should not be required to reproduce the base parcel ranking.

**V0 method:** standardize one county, define an eligible parcel universe,
derive transparent underuse indicators, rank within county, and expose selected
corridor/district membership. Keep component measures visible instead of
hiding all logic behind one score.

**Minimum outputs:** source and join QA, county parcel inventory, component
ranking table, county map, selected-area filter, candidate detail table, and
data-freshness/provenance fields.

**Later spec must lock:** eligible land uses, underutilization definition,
required versus optional fields, missing-value behavior, score weights or
ranking rule, treatment of parcel assemblages, source licensing/refresh,
county adapter contract, and whether broker listings affect rank or only add
context.

### 5.10 Catchment

**Question:** What population, demographic, housing, employment, amenity, and
physical-context evidence falls within a declared reach of a specific point?

**Primary analytical unit:** point × ring/reach × contributing tract.

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

**Minimum outputs:** resolved point, ring geometries, tract contribution table,
coverage/reliability QA, long metric profile, benchmark table, daytime context,
and optional POI/barrier views.

**Later spec must lock:** point identity and override rules, default rings,
areal versus dasymetric status, metric aggregation rules, median handling,
reliability flags, barrier behavior, and trigger for a routed network method.

## 6. Dependency and Reuse Map

| Shared capability | First Explanation consumer | Later reuse |
|---|---|---|
| Regional comparison surfaces | Regional Role | Q6, Q1–Q5 context, Act 3 regional comparisons |
| LODES OD flow foundation | Q6 or Regional Role | commute sheds, Q5, work-geography themes |
| Housing component cut | Q1 | Q3, Q5, Housing satellite, A2, A7 |
| Reusable job-center surface | Q2 | Q5, Internal Structure, Corridor Opportunity Read |
| Tract temporal harmonization | Q3 | other tract change analyses and hazard/growth themes |
| Daily-needs basket and access method | Q4 | Corridor Opportunity Read and livability summaries |
| Corridor Intelligence consumer surface | Internal Structure | Corridor Opportunity Read, then Parcel Watch scope |
| Standard county parcel adapter | Parcel Watch | later parcel/site products |
| Catchment contribution table | Catchment | Parcel Watch detail, site analyses, point-based issue views |

The promotion rule remains unchanged: keep first-use logic in the analysis;
move it to a shared component or `foundations/` only after a second consumer
uses the interface unchanged.

## 7. Proposed Build Sequence

This sequence separates work that can produce a useful notebook now from work
that should wait for a real upstream contract.

### Wave 0 — Confirm narrow shared inputs

1. Define the common Q1–Q6 Marimo controls and coverage-result vocabulary.
2. Expose the existing Industry D3 job-center logic as a read-only,
   reproducible query surface for Q2 and Q5.
3. Define a first housing component cut without creating a broad Housing
   Engine in advance.
4. Record LODES OD as a shared source gap for Regional Role and Q6; choose one
   of those analyses as the ingest's first consumer when its spec opens.

### Wave 1 — Startable analyses

1. **Catchment:** fastest path to a working Explanation method notebook because
   the method and Jacksonville artifacts already exist.
2. **Q1 Supply or Demand:** strongest national-ready dataset base and high reuse
   for housing themes.
3. **Q2 Job-Proximity Gradient:** start with straight-line proximity and current
   housing measures.
4. **Regional Role v0:** build the comparison and migration surfaces, clearly
   labeling commute-shed content as deferred.
5. **Q4 two-market pilot:** lock the daily-needs basket and simple access method
   using Richmond and Jacksonville before national POI scale-out.

These can overlap in calendar time, but each DuckDB materialization or shared
data-layer change should remain sequential.

### Wave 2 — Analyses that reuse Wave 1 or need one focused foundation gap

1. **Q5 Afford to Live Near Jobs:** reuse Q2 centers/proximity and the Q1
   housing cut; use existing OEWS rather than opening an ingest project.
2. **Q3 Where Growth Lands:** open the tract harmonization and growth-class
   method as one vertical slice.
3. **Q6 One Metro?:** reuse Regional Role, then add OD and integration
   thresholds before treating the answer as complete.
4. **Q4 national run:** acquire/process broader POI coverage only after the
   two-market method review passes.

### Wave 3 — Conditional narrowing methods

1. Complete Corridor Intelligence review, Jacksonville calibration, Richmond
   validation, and the read-only consumer handoff.
2. Run Internal Structure and select candidates that merit explanation.
3. Build **Corridor Opportunity Read** against those fixed candidate IDs.
4. Standardize one Jacksonville county parcel source and build **Parcel
   Watch** countywide, then connect it to selected candidates.
5. Reuse **Catchment** for selected parcels or other issue points only when the
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
3. Q2 Job-Proximity Gradient
4. Regional Role
5. Q4 Daily-Needs Access
6. Q5 Afford to Live Near Jobs
7. Q3 Where Growth Lands
8. Q6 One Metro?
9. Corridor Opportunity Read
10. Parcel Watch

This is a requirements sequence, not a publication order. Position routing
can pull a ready analysis forward for a particular market.

## 9. Decisions to Confirm Before the Child Specs

The plan proceeds with the following defaults, but the choices should be
confirmed when the relevant spec opens:

1. **Meaning of national:** use one method across every covered CBSA and
   retain its small-area evidence, rather than producing only a national
   CBSA-grain ranking.
2. **Regional lenses:** keep Census Division, state, nearby metros/counties,
   peer set, and eventual functional labor shed distinct.
3. **Parcel system of record:** prefer county assessor records or a licensed
   normalized parcel source; keep broker listings optional and dated.
4. **Parcel universe:** begin with all parcels meeting a declared minimum data
   contract, then use land-use eligibility filters appropriate to the question
   rather than assuming every market is a retail screen.
5. **Catchment v0:** carry forward areal Euclidean rings with transparent
   limitations and a water-adjusted companion; treat dasymetric weighting and
   routed reach as challengers that need evidence, not prerequisites.

## 10. Explicit Non-Goals for This Family Plan

- no final equations, score weights, or thresholds
- no new catch-all Spatial or Housing engine
- no automated market routing or issue assembly
- no national parcel acquisition before one county contract works
- no national POI scale-out before Q4's basket and access method are reviewed
- no commuting-integration claims from WAC/RAC without OD
- no investment conclusion from a Corridor Intelligence candidate
- no promotion of the Place Intelligence app as the Catchment product
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
- `metro-deep-dive-program/engines/corridor_intelligence/CONTRACT.md`
- `metro-deep-dive/metro-area-explorer/place_intelligence/METHODS_MEMO.md`
- `metro-deep-dive/metro-area-explorer/place_intelligence/SPEC_PLACE_INTELLIGENCE.md`
- `metro-deep-dive/metro-area-explorer/place_intelligence/TECHNICAL_ARCHITECTURE.md`
- `metro-deep-dive/archive/markets/jacksonville/05_parcels/parcel_standardization/README.md`
